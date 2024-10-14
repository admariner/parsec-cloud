// Parsec Cloud (https://parsec.cloud) Copyright (c) BUSL-1.1 2016-present Scille SAS

export enum PageToWindowChannel {
  ConfigUpdate = 'parsec-config-update',
  CloseApp = 'parsec-close-app',
  OpenFile = 'parsec-open-file',
  MountpointUpdate = 'parsec-mountpoint-update',
  UpdateAvailabilityRequest = 'parsec-update-availability-request',
  UpdateApp = 'parsec-update-app',
  PrepareUpdate = 'parsec-prepare-update',
  Log = 'parsec-log',
  PageIsInitialized = 'parsec-page-is-initialized',
  OpenConfigDir = 'parsec-open-config-dir',
  AuthorizeURL = 'parsec-authorized-url',
}

export enum WindowToPageChannel {
  OpenPathFailed = 'parsec-open-path-failed',
  UpdateAvailability = 'parsec-update-availability',
  OpenLink = 'parsec-open-link',
  CloseRequest = 'parsec-close-request',
  CleanUpBeforeUpdate = 'parsec-clean-up-before-update',
  IsDevMode = 'parsec-is-dev-mode',
  PrintToConsole = 'parsec-print-to-console',
}
