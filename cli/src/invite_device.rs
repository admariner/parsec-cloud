// Parsec Cloud (https://parsec.cloud) Copyright (c) BUSL-1.1 2016-present Scille SAS

use clap::Args;
use std::path::PathBuf;
use terminal_spinners::{SpinnerBuilder, DOTS};

use libparsec::{
    authenticated_cmds::latest::invite_new::{self, InviteNewRep, UserOrDevice},
    get_default_config_dir, BackendInvitationAddr, InvitationType,
};

use crate::utils::*;

#[derive(Args)]
pub struct InviteDevice {
    /// Parsec config directory
    #[arg(short, long, default_value_os_t = get_default_config_dir())]
    config_dir: PathBuf,
    /// Device slughash
    #[arg(short, long)]
    device: Option<String>,
}

pub async fn invite_device(invite_device: InviteDevice) -> anyhow::Result<()> {
    load_device_and_run(
        invite_device.config_dir,
        invite_device.device,
        |cmds, device| async move {
            let handle = SpinnerBuilder::new()
                .spinner(&DOTS)
                .text("Creating device invitation")
                .start();

            let rep = cmds
                .send(invite_new::Req(UserOrDevice::Device { send_email: false }))
                .await?;

            let url = match rep {
                InviteNewRep::Ok { token, .. } => BackendInvitationAddr::new(
                    device.organization_addr.clone(),
                    device.organization_id().clone(),
                    InvitationType::Device,
                    token,
                )
                .to_url(),
                rep => {
                    return Err(anyhow::anyhow!(
                        "Server refused to create device invitation: {rep:?}"
                    ));
                }
            };

            handle.done();

            println!("Invitation URL: {YELLOW}{url}{RESET}");

            Ok(())
        },
    )
    .await
}