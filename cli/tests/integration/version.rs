#[test]
fn version() {
    crate::assert_cmd_success!("--version").stdout(
        // Using `concat!` simplify updating the version using `version-updater`
        concat!("parsec-cli 3.9.1-a.0.dev.20634+1a4f1bf", "\n"),
    );
}
