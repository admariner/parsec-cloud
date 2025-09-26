#[test]
fn version() {
    crate::assert_cmd_success!("--version").stdout(
        // Using `concat!` simplify updating the version using `version-updater`
        concat!("parsec-cli 3.5.0-a.6.dev.20357+d35f1c7", "\n"),
    );
}
