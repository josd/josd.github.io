use std::process::Command;

fn run_args(args: &[&str]) -> std::process::Output {
    Command::new(env!("CARGO_BIN_EXE_arclight"))
        .args(args)
        .output()
        .expect("failed to run arclight binary")
}

fn run_case(arg: &str) -> std::process::Output {
    run_args(&[arg])
}


#[test]
fn delfour_cli_reports_the_phone_and_scanner_flow() {
    let output = run_case("delfour");
    assert!(output.status.success());

    let stdout = String::from_utf8(output.stdout).expect("stdout should be valid utf-8");
    assert!(stdout.contains("case                 : delfour"));
    assert!(stdout.contains("decision             : Allowed"));
    assert!(stdout.contains("scanned product      : Classic Tea Biscuits"));
    assert!(stdout.contains("suggested alternative: Low-Sugar Tea Biscuits"));
    assert!(stdout.contains("threshold            : 10.0"));
    assert!(stdout.contains("retailer             : Delfour"));
    assert!(stdout.contains("signature verifies              : yes"));
    assert!(stdout.contains("payload hash matches            : yes"));
    assert!(stdout.contains("authorization allowed           : yes"));
    assert!(stdout.contains("alternative lowers sugar        : yes"));
    assert!(stdout.contains("duty timing consistent          : yes"));
    assert!(stdout.contains("marketing prohibited            : yes"));
}

#[test]
fn euler_identity_cli_reports_component_checks() {
    let output = run_case("euler-identity");
    assert!(output.status.success());

    let stdout = String::from_utf8(output.stdout).expect("stdout should be valid utf-8");
    assert!(stdout.contains("case              : euler-identity"));
    assert!(stdout.contains("identity holds    : yes"));
    assert!(stdout.contains("phase = -1        : yes"));
    assert!(stdout.contains("sum real part = 0 : yes"));
    assert!(stdout.contains("sum imag part = 0 : yes"));
    assert!(stdout.contains("phase modulus ok  : yes"));
}

#[test]
fn fibonacci_cli_reports_independent_checks() {
    let output = run_case("fibonacci");
    assert!(output.status.success());

    let stdout = String::from_utf8(output.stdout).expect("stdout should be valid utf-8");
    assert!(stdout.contains("case          : fibonacci"));
    assert!(stdout.contains("F(10) = 55          : yes"));
    assert!(stdout.contains("digits in F(1000)   : 209"));
    assert!(stdout.contains("fast-doubling agrees: yes"));
    assert!(stdout.contains("Cassini at n=100    : yes"));
}

#[test]
fn deep_taxonomy_cli_reports_boundary_and_count_checks() {
    let output = run_case("deep-taxonomy-100000");
    assert!(output.status.success());

    let stdout = String::from_utf8(output.stdout).expect("stdout should be valid utf-8");
    assert!(stdout.contains("case          : deep-taxonomy-100000"));
    assert!(stdout.contains("goal reached  : yes"));
    assert!(stdout.contains("rule count ok : yes"));
    assert!(stdout.contains("N(100000) seen: yes"));
    assert!(stdout.contains("A2 derived    : yes"));
    assert!(stdout.contains("count formula ok: yes"));
}

#[test]
fn list_shows_all_available_cases() {
    let output = run_case("--list");
    assert!(output.status.success());

    let stdout = String::from_utf8(output.stdout).expect("stdout should be valid utf-8");
    assert!(stdout.contains("collatz-1000"));
    assert!(stdout.contains("control-system"));
    assert!(stdout.contains("deep-taxonomy-100000"));
    assert!(stdout.contains("delfour"));
    assert!(stdout.contains("euler-identity"));
    assert!(stdout.contains("fibonacci"));
    assert!(stdout.contains("goldbach-1000"));
    assert!(stdout.contains("gps"));
    assert!(stdout.contains("kaprekar-6174"));
    assert!(stdout.contains("path-discovery"));
    assert!(stdout.contains("polynomial"));
}

#[test]
fn collatz_1000_cli_reports_the_exhaustive_proof_summary() {
    let output = run_case("collatz-1000");
    assert!(output.status.success());

    let stdout = String::from_utf8(output.stdout).expect("stdout should be valid utf-8");
    assert!(stdout.contains("case                : collatz-1000"));
    assert!(stdout.contains("range checked       : 1..=10000"));
    assert!(stdout.contains("method              : exhaustive verification"));
    assert!(stdout.contains("starts checked      : 10000"));
    assert!(stdout.contains("all reach 1         : yes"));
    assert!(stdout.contains("max steps           : 261"));
    assert!(stdout.contains("max-steps start     : 6171"));
    assert!(stdout.contains("highest peak        : 27114424"));
    assert!(stdout.contains("peak start          : 9663"));
    assert!(stdout.contains("trace(27) steps    : 111"));
    assert!(stdout.contains("trace(27) peak     : 9232"));
    assert!(stdout.contains("trace(27) follows rule : yes"));
    assert!(stdout.contains("max-steps witness ok: yes"));
    assert!(stdout.contains("peak witness ok     : yes"));
}

#[test]
fn goldbach_1000_cli_reports_the_exhaustive_proof_summary() {
    let output = run_case("goldbach-1000");
    assert!(output.status.success());

    let stdout = String::from_utf8(output.stdout).expect("stdout should be valid utf-8");
    assert!(stdout.contains("case                 : goldbach-1000"));
    assert!(stdout.contains("range checked        : even integers 4..=1000"));
    assert!(stdout.contains("method               : exhaustive verification"));
    assert!(stdout.contains("even targets checked : 499"));
    assert!(stdout.contains("all represented      : yes"));
    assert!(stdout.contains("total decompositions : 8222"));
    assert!(stdout.contains("fewest decompositions: 1"));
    assert!(stdout.contains("hardest targets      : 4, 6, 8, 12"));
    assert!(stdout.contains("most decompositions  : 52"));
    assert!(stdout.contains("richest target       : 990"));
    assert!(stdout.contains("primes ≤ 1000       : 168"));
    assert!(stdout.contains("balanced pair(1000) : 491 + 509"));
    assert!(stdout.contains("prime count known    : yes"));
    assert!(stdout.contains("balanced pair valid  : yes"));
}

#[test]
fn gps_cli_reports_the_expected_routes() {
    let output = run_case("gps");
    assert!(output.status.success());

    let stdout = String::from_utf8(output.stdout).expect("stdout should be valid utf-8");
    assert!(stdout.contains("case      : gps"));
    assert!(stdout.contains("Route #1"));
    assert!(stdout.contains("drive_gent_brugge"));
    assert!(stdout.contains("Route #2"));
    assert!(stdout.contains("drive_gent_kortrijk"));
    assert!(stdout.contains("metrics recompute from steps   : yes"));
    assert!(stdout.contains("expected route count (= 2)     : yes"));
}

#[test]
fn kaprekar_6174_cli_reports_the_exhaustive_proof_summary() {
    let output = run_case("kaprekar-6174");
    assert!(output.status.success());

    let stdout = String::from_utf8(output.stdout).expect("stdout should be valid utf-8");
    assert!(stdout.contains("case                : kaprekar-6174"));
    assert!(stdout.contains("method              : exhaustive verification"));
    assert!(stdout.contains("valid starts checked: 9990"));
    assert!(stdout.contains("repdigits excluded  : 10"));
    assert!(stdout.contains("6174 fixed point    : yes"));
    assert!(stdout.contains("all starts reach it : yes"));
    assert!(stdout.contains("bound <= 7 verified : yes"));
    assert!(stdout.contains("histogram total ok  : yes"));
    assert!(stdout.contains("worst trace valid   : yes"));
    assert!(stdout.contains("leading-zero valid  : yes"));
    assert!(stdout.contains("max iterations      : 7"));
    assert!(stdout.contains("worst-case starts   : 2184"));
    assert!(stdout.contains("worst-case trace    : 0014 -> 4086 -> 8172 -> 7443 -> 3996 -> 6264 -> 4176 -> 6174"));
    assert!(stdout.contains("leading-zero trace  : 2111 -> 0999 -> 8991 -> 8082 -> 8532 -> 6174"));
}

#[test]
fn path_discovery_cli_reports_the_expected_route_count() {
    let output = run_case("path-discovery");
    assert!(output.status.success());

    let stdout = String::from_utf8(output.stdout).expect("stdout should be valid utf-8");
    assert!(stdout.contains("case          : path-discovery"));
    assert!(stdout.contains("airports      : 7698"));
    assert!(stdout.contains("flights       : 37274"));
    assert!(stdout.contains("routes found  : 3"));
    assert!(stdout.contains("Ostend-Bruges International Airport"));
    assert!(stdout.contains("Václav Havel Airport Prague"));
    assert!(stdout.contains("Route #1"));
    assert!(stdout.contains("all routes are simple paths      : yes"));
    assert!(stdout.contains("route set matches known answer   : yes"));
}

#[test]
fn control_system_cli_reports_both_actuator_outputs() {
    let output = run_case("control-system");
    assert!(output.status.success());

    let stdout = String::from_utf8(output.stdout).expect("stdout should be valid utf-8");
    assert!(stdout.contains("case                 : control-system"));
    assert!(stdout.contains("controls found       : 2"));
    assert!(stdout.contains("query satisfied      : yes"));
    assert!(stdout.contains("actuator1"));
    assert!(stdout.contains("actuator2"));
    assert!(stdout.contains("unique actuators     : yes"));
    assert!(stdout.contains("actuator1 formula ok : yes"));
    assert!(stdout.contains("actuator2 formula ok : yes"));
}

#[test]
fn polynomial_cli_reports_both_expected_examples() {
    let output = run_case("polynomial");
    assert!(output.status.success());

    let stdout = String::from_utf8(output.stdout).expect("stdout should be valid utf-8");
    assert!(stdout.contains("case                 : polynomial"));
    assert!(stdout.contains("examples solved      : 2"));
    assert!(stdout.contains("all examples valid   : yes"));
    assert!(stdout.contains("Example #1"));
    assert!(stdout.contains("label                : real quartic"));
    assert!(stdout.contains("roots calculated     : 4, 3, 2, 1"));
    assert!(stdout.contains("residuals            : [[0, 0], [0, 0], [0, 0], [0, 0]]"));
    assert!(stdout.contains("Example #2"));
    assert!(stdout.contains("label                : complex quartic"));
    assert!(stdout.contains("roots calculated     :"));
    assert!(stdout.contains("3 + 2i"));
    assert!(stdout.contains("5 + i"));
    assert!(stdout.contains("i"));
    assert!(stdout.contains("1 + i"));
    assert!(stdout.contains("reconstruction ok    : yes"));
    assert!(stdout.contains("roots valid          : yes"));
    assert!(stdout.contains("degree/root count ok : yes"));
    assert!(stdout.contains("Vieta sum ok         : yes"));
    assert!(stdout.contains("Vieta product ok     : yes"));
}

#[test]
fn bare_invocation_runs_the_same_cases_as_all() {
    let bare = Command::new(env!("CARGO_BIN_EXE_arclight"))
        .output()
        .expect("failed to run bare arclight binary");
    assert!(bare.status.success());

    let all = run_case("--all");
    assert!(all.status.success());

    let bare_stdout = String::from_utf8(bare.stdout).expect("stdout should be valid utf-8");
    let all_stdout = String::from_utf8(all.stdout).expect("stdout should be valid utf-8");

    assert_eq!(bare_stdout, all_stdout);
}

#[test]
fn json_output_for_single_case_is_structured() {
    let output = run_args(&["collatz-1000", "--format", "json"]);
    assert!(output.status.success());

    let stdout = String::from_utf8(output.stdout).expect("stdout should be valid utf-8");
    let value: serde_json::Value = serde_json::from_str(&stdout).expect("valid json output");

    assert_eq!(value["case"], "collatz-1000");
    assert!(value["answer"].is_array());
    assert!(value["reason_why"].is_array());
    assert!(value["check"].is_array());
}

#[test]
fn json_output_for_all_cases_is_an_array_of_eleven_reports() {
    let output = run_args(&["--all", "--format", "json"]);
    assert!(output.status.success());

    let stdout = String::from_utf8(output.stdout).expect("stdout should be valid utf-8");
    let value: serde_json::Value = serde_json::from_str(&stdout).expect("valid json output");

    let reports = value.as_array().expect("top-level json array");
    assert_eq!(reports.len(), 11);
    assert_eq!(reports[0]["case"], "collatz-1000");
    assert_eq!(reports[9]["case"], "polynomial");
}
