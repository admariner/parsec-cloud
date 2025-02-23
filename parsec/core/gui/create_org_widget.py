# Parsec Cloud (https://parsec.cloud) Copyright (c) AGPL-3.0 2016-present Scille SAS
from __future__ import annotations

from typing import Any, Awaitable, Callable

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget
from structlog import get_logger

from parsec._parsec import (
    BackendAddr,
    BackendOrganizationBootstrapAddr,
    DeviceFileType,
    DeviceLabel,
    HumanHandle,
    LocalDevice,
    LocalDeviceCryptoError,
    LocalDeviceError,
    LocalDeviceNotFoundError,
    OrganizationID,
    save_device_with_password_in_config,
)
from parsec.core.backend_connection import (
    BackendConnectionRefused,
    BackendNotAvailable,
    BackendOutOfBallparkError,
)
from parsec.core.config import CoreConfig
from parsec.core.fs.storage import user_storage_non_speculative_init
from parsec.core.gui import validators
from parsec.core.gui.authentication_choice_widget import AuthenticationChoiceWidget
from parsec.core.gui.custom_dialogs import GreyedDialog, show_error
from parsec.core.gui.desktop import get_default_device
from parsec.core.gui.lang import translate as _
from parsec.core.gui.trio_jobs import QtToTrioJob, QtToTrioJobScheduler
from parsec.core.gui.ui.create_org_user_info_widget import Ui_CreateOrgUserInfoWidget
from parsec.core.gui.ui.create_org_widget import Ui_CreateOrgWidget
from parsec.core.invite import InviteAlreadyUsedError, InviteNotFoundError, bootstrap_organization
from parsec.core.local_device import save_device_with_smartcard_in_config

logger = get_logger()


class CreateOrgUserInfoWidget(QWidget, Ui_CreateOrgUserInfoWidget):
    info_filled = pyqtSignal(bool)

    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)
        self.line_edit_user_email.validity_changed.connect(self.check_infos)
        self.line_edit_user_email.set_validator(validators.EmailValidator())
        self.line_edit_user_full_name.validity_changed.connect(self.check_infos)
        self.line_edit_user_full_name.set_validator(validators.UserNameValidator())
        self.line_edit_org_name.validity_changed.connect(self.check_infos)
        self.line_edit_device.setText(get_default_device())
        self.line_edit_device.validity_changed.connect(self.check_infos)
        self.line_edit_device.set_validator(validators.DeviceLabelValidator())
        self.line_edit_org_name.set_validator(validators.OrganizationIDValidator())
        self.line_edit_backend_addr.set_validator(validators.BackendAddrValidator())
        self.line_edit_backend_addr.validity_changed.connect(self.check_infos)
        self.check_accept_contract.clicked.connect(self.check_infos)
        self.radio_use_commercial.toggled.connect(self._switch_server)
        self.radio_use_custom.toggled.connect(self._switch_server)
        self.radio_use_commercial.setChecked(True)

    def _are_inputs_valid(self) -> bool:
        return bool(
            self.line_edit_user_email.is_input_valid()
            and self.line_edit_user_full_name.is_input_valid()
            and self.line_edit_org_name.is_input_valid()
            and self.line_edit_device.is_input_valid()
            and (
                (self.radio_use_commercial.isChecked() and self.check_accept_contract.isChecked())
                or (
                    self.radio_use_custom.isChecked()
                    and self.line_edit_backend_addr.is_input_valid()
                )
            )
        )

    def _switch_server(self, _: Any) -> None:
        if self.radio_use_commercial.isChecked():
            self.widget_custom_backend.hide()
            self.widget_contract.show()
        else:
            self.widget_contract.hide()
            self.widget_custom_backend.show()
        self.check_infos()

    def check_infos(self, _: None = None) -> None:
        self.info_filled.emit(self._are_inputs_valid())

    @property
    def backend_addr(self) -> BackendAddr | None:
        return (
            BackendAddr.from_url(self.line_edit_backend_addr.text(), allow_http_redirection=True)
            if self.radio_use_custom.isChecked()
            else None
        )


class CreateOrgWidget(QWidget, Ui_CreateOrgWidget):
    # These signals are no longer used to propagate
    # Trio job status. We keep them and emit manually
    # because our tests still rely on them.
    req_success = pyqtSignal()
    req_error = pyqtSignal()

    def __init__(
        self,
        jobs_ctx: QtToTrioJobScheduler,
        config: CoreConfig,
        start_addr: BackendOrganizationBootstrapAddr | None,
    ) -> None:
        super().__init__()
        self.setupUi(self)
        self.jobs_ctx = jobs_ctx
        self.config = config
        self.create_job: QtToTrioJob[LocalDevice] | None = None
        self.dialog: GreyedDialog[CreateOrgWidget] | None = None
        self.status: tuple[LocalDevice, DeviceFileType, str] | None = None
        self.new_device: LocalDevice | None = None

        self.current_widget: CreateOrgUserInfoWidget | AuthenticationChoiceWidget = (
            CreateOrgUserInfoWidget()
        )
        self.current_widget.info_filled.connect(self._on_info_filled)
        self.main_layout.addWidget(self.current_widget)

        self.button_validate.setEnabled(False)
        self.button_validate.clicked.connect(self._on_next_clicked)

        self.button_validate.setText(_("ACTION_CREATE_ORG"))

        self.start_addr = start_addr

        if self.start_addr:
            self.current_widget.line_edit_org_name.setText(self.start_addr.organization_id.str)
            self.current_widget.line_edit_org_name.setReadOnly(True)
            self.label_instructions.setText(
                _("TEXT_BOOTSTRAP_ORGANIZATION_INSTRUCTIONS_organization").format(
                    organization=self.start_addr.organization_id.str
                )
            )
            # Not creating on the default server
            if (
                self.start_addr.hostname != config.preferred_org_creation_backend_addr.hostname
                or self.start_addr.port != config.preferred_org_creation_backend_addr.port
            ):
                self.current_widget.radio_use_custom.setChecked(True)
                self.current_widget.radio_use_commercial.setDisabled(True)
                # Will not be used, it just makes the display prettier
                backend_addr = BackendAddr(
                    self.start_addr.hostname,
                    self.start_addr.port,
                    self.start_addr.use_ssl,
                )
                self.current_widget.line_edit_backend_addr.setText(backend_addr.to_url())
                self.current_widget.line_edit_backend_addr.setDisabled(True)
                self.current_widget.line_edit_backend_addr.setCursorPosition(0)
            else:
                self.current_widget.radio_use_commercial.setChecked(True)
                self.current_widget.radio_use_custom.setDisabled(True)

    def _on_info_filled(self, valid: bool) -> None:
        self.button_validate.setEnabled(valid)

    def on_close(self) -> None:
        self.status = None
        if self.create_job:
            self.create_job.cancel()

    async def _on_next_clicked(self) -> None:
        if isinstance(self.current_widget, CreateOrgUserInfoWidget):
            backend_addr = None

            if self.start_addr:
                backend_addr = self.start_addr
            else:
                org_id = OrganizationID(self.current_widget.line_edit_org_name.text())
                try:
                    if self.current_widget.radio_use_custom.isChecked():
                        assert self.current_widget.backend_addr is not None
                        addr = self.current_widget.backend_addr
                    else:
                        addr = self.config.preferred_org_creation_backend_addr
                    backend_addr = BackendOrganizationBootstrapAddr.build(
                        backend_addr=addr,
                        organization_id=org_id,
                        token=None,
                    )
                except ValueError as exc:
                    show_error(self, _("TEXT_ORG_WIZARD_INVALID_BACKEND_ADDR"), exception=exc)
                    return
            # Inputs have been validated with validators
            human_handle = HumanHandle(
                email=self.current_widget.line_edit_user_email.text(),
                label=self.current_widget.line_edit_user_full_name.clean_text(),
            )
            device_label = DeviceLabel(self.current_widget.line_edit_device.clean_text())

            assert self.dialog is not None
            self.dialog.button_close.setVisible(False)
            self.current_widget.setEnabled(False)
            self.button_validate.setEnabled(False)

            err_msg = None
            exception_value: Exception | None = None
            try:
                self.new_device = await bootstrap_organization(
                    backend_addr, human_handle=human_handle, device_label=device_label
                )
                # The organization is brand new, of course there is no existing
                # remote user manifest, hence our placeholder is non-speculative.
                await user_storage_non_speculative_init(
                    data_base_dir=self.config.data_base_dir, device=self.new_device
                )
            except InviteNotFoundError as exc:
                err_msg = _("TEXT_ORG_WIZARD_INVITE_NOT_FOUND")
                exception_value = exc
            except InviteAlreadyUsedError as exc:
                if self.start_addr:
                    err_msg = _("TEXT_ORG_WIZARD_INVITE_ALREADY_USED")
                else:
                    err_msg = _("TEXT_ORG_WIZARD_ORGANIZATION_ALREADY_EXISTS")
                exception_value = exc
            except BackendConnectionRefused as exc:
                err_msg = _("TEXT_ORG_WIZARD_CONNECTION_REFUSED")
                exception_value = exc
            except BackendNotAvailable as exc:
                err_msg = _("TEXT_ORG_WIZARD_CONNECTION_ERROR")
                exception_value = exc
            except BackendOutOfBallparkError as exc:
                err_msg = _("TEXT_BACKEND_STATE_DESYNC")
                exception_value = exc
            except Exception as exc:
                err_msg = _("TEXT_ORG_WIZARD_UNKNOWN_FAILURE")
                exception_value = exc

            if exception_value and err_msg:
                # Alert anyone listening (most likely a test)
                # that an error was encountered
                self.req_error.emit()

                show_error(self, err_msg, exception=exception_value)
                self.button_validate.setEnabled(True)
                self.current_widget.setEnabled(True)
                if self.dialog:
                    self.dialog.button_close.setVisible(True)

            else:
                # Alert anyone listening (most likely a test)
                # that we successfully got through Organization
                # creation.
                self.req_success.emit()

                assert isinstance(self.current_widget, CreateOrgUserInfoWidget)
                excl_strings = [
                    self.current_widget.line_edit_org_name.text(),
                    self.current_widget.line_edit_user_full_name.text(),
                    self.current_widget.line_edit_user_email.text(),
                ]
                self.main_layout.takeAt(0).widget().setParent(None)
                self.current_widget = AuthenticationChoiceWidget()
                self.main_layout.addWidget(self.current_widget)
                self.current_widget.exclude_strings(excl_strings)
                self.current_widget.authentication_state_changed.connect(
                    self._on_authentication_changed
                )
                self.button_validate.setText(_("ACTION_CREATE_DEVICE"))
                self.button_validate.setEnabled(self.current_widget.is_auth_valid())

        else:
            auth_method = self.current_widget.get_auth_method()
            try:
                assert self.new_device is not None
                if auth_method == DeviceFileType.PASSWORD:
                    save_device_with_password_in_config(
                        self.config.config_dir,
                        self.new_device,
                        self.current_widget.get_auth(),
                    )
                elif auth_method == DeviceFileType.SMARTCARD:
                    await save_device_with_smartcard_in_config(
                        self.config.config_dir, self.new_device
                    )
                self.status = (
                    self.new_device,
                    auth_method,
                    self.current_widget.get_auth(),
                )

                if self.dialog:
                    self.dialog.accept()
                elif QApplication.activeModalWidget():
                    # Mypy: the current modal should have an accept method, right ?
                    QApplication.activeModalWidget().accept()  # type: ignore[attr-defined]
                else:
                    logger.warning("Cannot close dialog when org wizard")
            except LocalDeviceCryptoError as exc:
                if auth_method == DeviceFileType.SMARTCARD:
                    show_error(self, _("TEXT_INVALID_SMARTCARD"), exception=exc)
            except LocalDeviceNotFoundError as exc:
                if auth_method == DeviceFileType.PASSWORD:
                    show_error(self, _("TEXT_CANNOT_SAVE_DEVICE"), exception=exc)
            except LocalDeviceError as exc:
                show_error(self, _("TEXT_CANNOT_SAVE_DEVICE"), exception=exc)

    def _on_authentication_changed(self, auth_method: Any, valid: bool) -> None:
        self.button_validate.setEnabled(valid)

    @classmethod
    def show_modal(
        cls,
        jobs_ctx: QtToTrioJobScheduler,
        config: CoreConfig,
        parent: QWidget,
        on_finished: Callable[[], Awaitable[None]],
        start_addr: BackendOrganizationBootstrapAddr | None = None,
    ) -> CreateOrgWidget:
        widget = cls(jobs_ctx, config, start_addr)
        dialog = GreyedDialog(widget, _("TEXT_ORG_WIZARD_TITLE"), parent=parent, width=1000)
        widget.dialog = dialog

        dialog.finished.connect(on_finished)
        # Unlike exec_, show is asynchronous and works within the main Qt loop
        dialog.show()
        return widget
