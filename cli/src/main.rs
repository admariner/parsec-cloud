// Parsec Cloud (https://parsec.cloud) Copyright (c) BUSL-1.1 2016-present Scille SAS

mod create_organization;
mod list_devices;
mod utils;

use clap::{Parser, Subcommand};

/// Parsec cli
#[derive(Parser)]
struct Arg {
    #[command(subcommand)]
    command: Command,
}

#[derive(Subcommand)]
enum Command {
    /// Create new organization
    CreateOrganization(create_organization::CreateOrganization),
    /// List all devices
    ListDevices(list_devices::ListDevices),
}

#[tokio::main]
async fn main() {
    let arg = Arg::parse();

    match arg.command {
        Command::CreateOrganization(create_organization) => {
            create_organization::create_organization(create_organization).await
        }
        Command::ListDevices(list_devices) => list_devices::list_devices(list_devices).await,
    }
}