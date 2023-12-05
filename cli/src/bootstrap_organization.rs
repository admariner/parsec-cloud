// Parsec Cloud (https://parsec.cloud) Copyright (c) BUSL-1.1 2016-present Scille SAS

use clap::Args;
use std::{path::PathBuf, sync::Arc};
use terminal_spinners::{SpinnerBuilder, DOTS};

use libparsec::{
    AvailableDevice, BackendOrganizationBootstrapAddr, ClientConfig, DeviceLabel,
    DeviceSaveStrategy, HumanHandle, Password,
};

#[derive(Args)]
pub struct BootstrapOrganization {
    /// Parsec config directory
    #[arg(short, long)]
    config_dir: Option<PathBuf>,
    /// Bootstrap address
    /// (e.g: parsec://127.0.0.1:6770/Org?no_ssl=true&action=bootstrap_organization&token=59961ba6dcc9b018d2fdc9da1c0c762b716a27cff30594562dc813e4b765871a)
    #[arg(short, long)]
    addr: BackendOrganizationBootstrapAddr,
    /// Device label
    #[arg(short, long)]
    device_label: DeviceLabel,
    /// User fullname
    #[arg(short, long)]
    label: String,
    /// User email
    #[arg(short, long)]
    email: String,
}

pub async fn bootstrap_organization_req(
    client_config: ClientConfig,
    addr: BackendOrganizationBootstrapAddr,
    device_label: DeviceLabel,
    human_handle: HumanHandle,
    password: Password,
) -> anyhow::Result<AvailableDevice> {
    let on_event_callback = Arc::new(|_| ());

    Ok(libparsec::bootstrap_organization(
        client_config,
        on_event_callback,
        addr,
        DeviceSaveStrategy::Password { password },
        human_handle,
        device_label,
        // TODO: handle sequestered organization
        None,
    )
    .await?)
}

pub async fn bootstrap_organization(
    bootstrap_organization: BootstrapOrganization,
) -> anyhow::Result<()> {
    let human_handle =
        HumanHandle::new(&bootstrap_organization.email, &bootstrap_organization.label)
            .map_err(|e| anyhow::anyhow!("Cannot create human handle: {e}"))?;

    let password = rpassword::prompt_password("password:")?.into();

    let handle = SpinnerBuilder::new()
        .spinner(&DOTS)
        .text("Bootstrapping organization in the server")
        .start();

    bootstrap_organization_req(
        ClientConfig::default(),
        bootstrap_organization.addr,
        bootstrap_organization.device_label,
        human_handle,
        password,
    )
    .await?;

    handle.done();

    Ok(())
}
