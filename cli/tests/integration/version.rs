#[test]
fn version() {
    crate::assert_cmd_success!("--version").stdout(
        // Using `concat!` simplify updating the version using `version-updater`
        concat!("parsec-cli 3.9.3-a.0.dev.20656+8c2020e", "\n"),
    );
}
