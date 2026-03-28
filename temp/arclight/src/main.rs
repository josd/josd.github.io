use std::env;
use std::io::{self, Write};

mod collatz_1000;
mod control_system;
mod deep_taxonomy_100000;
mod delfour;
mod euler_identity;
mod fibonacci;
mod goldbach_1000;
mod gps;
mod kaprekar_6174;
mod path_discovery;
mod polynomial;
mod report;

use report::CaseReport;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum CaseName {
    Collatz1000,
    ControlSystem,
    DeepTaxonomy100000,
    Delfour,
    EulerIdentity,
    Fibonacci,
    Goldbach1000,
    Gps,
    Kaprekar6174,
    PathDiscovery,
    Polynomial,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum OutputFormat {
    Text,
    Json,
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct CliOptions {
    command: Command,
    format: OutputFormat,
}

#[derive(Debug, Clone, PartialEq, Eq)]
enum Command {
    List,
    All,
    Case(CaseName),
}

fn parse_case_name(raw: &str) -> io::Result<CaseName> {
    match raw {
        "collatz-1000" | "collatz_1000" | "collatz-10000" | "collatz_10000" | "collatz" => Ok(CaseName::Collatz1000),
        "control-system" | "control_system" => Ok(CaseName::ControlSystem),
        "deep-taxonomy-100000" | "deep_taxonomy_100000" => Ok(CaseName::DeepTaxonomy100000),
        "delfour" => Ok(CaseName::Delfour),
        "euler-identity" | "euler_identity" => Ok(CaseName::EulerIdentity),
        "fibonacci" => Ok(CaseName::Fibonacci),
        "goldbach-1000" | "goldbach_1000" | "goldbach" => Ok(CaseName::Goldbach1000),
        "gps" => Ok(CaseName::Gps),
        "kaprekar-6174" | "kaprekar_6174" => Ok(CaseName::Kaprekar6174),
        "path-discovery" | "path_discovery" => Ok(CaseName::PathDiscovery),
        "polynomial" => Ok(CaseName::Polynomial),
        other => Err(io::Error::new(
            io::ErrorKind::InvalidInput,
            format!(
                "unknown case '{other}'. available cases:\n  collatz-1000\n  control-system\n  deep-taxonomy-100000\n  delfour\n  euler-identity\n  fibonacci\n  goldbach-1000\n  gps\n  kaprekar-6174\n  path-discovery\n  polynomial\n\nextra commands:\n  --list\n  --all\n\nextra options:\n  --format text\n  --format json"
            ),
        )),
    }
}

fn parse_args(args: impl IntoIterator<Item = String>) -> io::Result<CliOptions> {
    let mut format = OutputFormat::Text;
    let mut command = Command::All;
    let mut saw_command = false;

    let mut iter = args.into_iter();
    while let Some(arg) = iter.next() {
        match arg.as_str() {
            "--format" => {
                let value = iter.next().ok_or_else(|| {
                    io::Error::new(io::ErrorKind::InvalidInput, "missing value after --format")
                })?;
                format = match value.as_str() {
                    "text" => OutputFormat::Text,
                    "json" => OutputFormat::Json,
                    other => {
                        return Err(io::Error::new(
                            io::ErrorKind::InvalidInput,
                            format!("unknown format '{other}'. use 'text' or 'json'"),
                        ))
                    }
                };
            }
            "--json" => format = OutputFormat::Json,
            "--text" => format = OutputFormat::Text,
            "--list" | "list" => {
                if saw_command {
                    return Err(io::Error::new(
                        io::ErrorKind::InvalidInput,
                        "multiple commands provided; use one case name, --all, or --list",
                    ));
                }
                command = Command::List;
                saw_command = true;
            }
            "--all" | "all" => {
                if saw_command {
                    return Err(io::Error::new(
                        io::ErrorKind::InvalidInput,
                        "multiple commands provided; use one case name, --all, or --list",
                    ));
                }
                command = Command::All;
                saw_command = true;
            }
            raw_case => {
                if saw_command {
                    return Err(io::Error::new(
                        io::ErrorKind::InvalidInput,
                        "multiple commands provided; use one case name, --all, or --list",
                    ));
                }
                command = Command::Case(parse_case_name(raw_case)?);
                saw_command = true;
            }
        }
    }

    Ok(CliOptions { command, format })
}

fn case_names() -> &'static [&'static str] {
    &[
        "collatz-1000",
        "control-system",
        "deep-taxonomy-100000",
        "delfour",
        "euler-identity",
        "fibonacci",
        "goldbach-1000",
        "gps",
        "kaprekar-6174",
        "path-discovery",
        "polynomial",
    ]
}

fn print_case_list() {
    for case in case_names() {
        println!("{case}");
    }
}

fn case_report(case_name: CaseName) -> io::Result<CaseReport> {
    match case_name {
        CaseName::Collatz1000 => collatz_1000::report(),
        CaseName::ControlSystem => control_system::report(),
        CaseName::DeepTaxonomy100000 => deep_taxonomy_100000::report(),
        CaseName::Delfour => delfour::report(),
        CaseName::EulerIdentity => euler_identity::report(),
        CaseName::Fibonacci => fibonacci::report(),
        CaseName::Goldbach1000 => goldbach_1000::report(),
        CaseName::Gps => gps::report(),
        CaseName::Kaprekar6174 => kaprekar_6174::report(),
        CaseName::PathDiscovery => path_discovery::report(),
        CaseName::Polynomial => polynomial::report(),
    }
}

fn emit_json_report(report: &CaseReport, mut writer: impl Write) -> io::Result<()> {
    serde_json::to_writer_pretty(&mut writer, report)
        .map_err(|error| io::Error::new(io::ErrorKind::Other, error))?;
    writer.write_all(b"\n")
}

fn run_case_text(case_name: CaseName) -> io::Result<()> {
    match case_name {
        CaseName::Collatz1000 => collatz_1000::run_and_print(),
        CaseName::ControlSystem => control_system::run_and_print(),
        CaseName::DeepTaxonomy100000 => deep_taxonomy_100000::run_and_print(),
        CaseName::Delfour => delfour::run_and_print(),
        CaseName::EulerIdentity => euler_identity::run_and_print(),
        CaseName::Fibonacci => fibonacci::run_and_print(),
        CaseName::Goldbach1000 => goldbach_1000::run_and_print(),
        CaseName::Gps => gps::run_and_print(),
        CaseName::Kaprekar6174 => kaprekar_6174::run_and_print(),
        CaseName::PathDiscovery => path_discovery::run_and_print(),
        CaseName::Polynomial => polynomial::run_and_print(),
    }
}

fn all_case_names() -> [CaseName; 11] {
    [
        CaseName::Collatz1000,
        CaseName::ControlSystem,
        CaseName::DeepTaxonomy100000,
        CaseName::Delfour,
        CaseName::EulerIdentity,
        CaseName::Fibonacci,
        CaseName::Goldbach1000,
        CaseName::Gps,
        CaseName::Kaprekar6174,
        CaseName::PathDiscovery,
        CaseName::Polynomial,
    ]
}

fn run_all_cases(format: OutputFormat) -> io::Result<()> {
    match format {
        OutputFormat::Text => {
            let runners: [fn() -> io::Result<()>; 11] = [
                collatz_1000::run_and_print,
                control_system::run_and_print,
                deep_taxonomy_100000::run_and_print,
                delfour::run_and_print,
                euler_identity::run_and_print,
                fibonacci::run_and_print,
                goldbach_1000::run_and_print,
                gps::run_and_print,
                kaprekar_6174::run_and_print,
                path_discovery::run_and_print,
                polynomial::run_and_print,
            ];

            for (index, run) in runners.into_iter().enumerate() {
                if index > 0 {
                    println!();
                    println!("------------------------------------------------------------------------");
                    println!();
                }
                run()?;
            }
            Ok(())
        }
        OutputFormat::Json => {
            let reports = all_case_names()
                .into_iter()
                .map(case_report)
                .collect::<io::Result<Vec<_>>>()?;
            let mut stdout = io::stdout();
            serde_json::to_writer_pretty(&mut stdout, &reports)
                .map_err(|error| io::Error::new(io::ErrorKind::Other, error))?;
            stdout.write_all(b"\n")
        }
    }
}

fn main() -> io::Result<()> {
    let options = parse_args(env::args().skip(1))?;

    match options.command {
        Command::List => {
            print_case_list();
            Ok(())
        }
        Command::All => run_all_cases(options.format),
        Command::Case(case_name) => match options.format {
            OutputFormat::Text => run_case_text(case_name),
            OutputFormat::Json => {
                let report = case_report(case_name)?;
                emit_json_report(&report, io::stdout())
            }
        },
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn accepts_hyphenated_and_snake_case_aliases() {
        assert!(matches!(parse_case_name("collatz-1000").unwrap(), CaseName::Collatz1000));
        assert!(matches!(parse_case_name("collatz_1000").unwrap(), CaseName::Collatz1000));
        assert!(matches!(parse_case_name("collatz-10000").unwrap(), CaseName::Collatz1000));
        assert!(matches!(parse_case_name("collatz_10000").unwrap(), CaseName::Collatz1000));
        assert!(matches!(parse_case_name("collatz").unwrap(), CaseName::Collatz1000));
        assert!(matches!(parse_case_name("control-system").unwrap(), CaseName::ControlSystem));
        assert!(matches!(parse_case_name("control_system").unwrap(), CaseName::ControlSystem));
        assert!(matches!(parse_case_name("deep-taxonomy-100000").unwrap(), CaseName::DeepTaxonomy100000));
        assert!(matches!(parse_case_name("deep_taxonomy_100000").unwrap(), CaseName::DeepTaxonomy100000));
        assert!(matches!(parse_case_name("euler-identity").unwrap(), CaseName::EulerIdentity));
        assert!(matches!(parse_case_name("euler_identity").unwrap(), CaseName::EulerIdentity));
        assert!(matches!(parse_case_name("goldbach-1000").unwrap(), CaseName::Goldbach1000));
        assert!(matches!(parse_case_name("goldbach_1000").unwrap(), CaseName::Goldbach1000));
        assert!(matches!(parse_case_name("goldbach").unwrap(), CaseName::Goldbach1000));
        assert!(matches!(parse_case_name("kaprekar-6174").unwrap(), CaseName::Kaprekar6174));
        assert!(matches!(parse_case_name("kaprekar_6174").unwrap(), CaseName::Kaprekar6174));
        assert!(matches!(parse_case_name("path-discovery").unwrap(), CaseName::PathDiscovery));
        assert!(matches!(parse_case_name("path_discovery").unwrap(), CaseName::PathDiscovery));
        assert!(matches!(parse_case_name("polynomial").unwrap(), CaseName::Polynomial));
    }

    #[test]
    fn unknown_case_lists_available_options() {
        let error = parse_case_name("nope").unwrap_err();
        let message = error.to_string();

        assert!(message.contains("unknown case 'nope'"));
        assert!(message.contains("collatz-1000"));
        assert!(message.contains("goldbach-1000"));
        assert!(message.contains("path-discovery"));
        assert!(message.contains("--list"));
        assert!(message.contains("--format json"));
    }

    #[test]
    fn parses_format_before_or_after_command() {
        assert_eq!(
            parse_args(["--format".into(), "json".into(), "goldbach-1000".into()]).unwrap(),
            CliOptions {
                command: Command::Case(CaseName::Goldbach1000),
                format: OutputFormat::Json,
            }
        );
        assert_eq!(
            parse_args(["goldbach-1000".into(), "--format".into(), "json".into()]).unwrap(),
            CliOptions {
                command: Command::Case(CaseName::Goldbach1000),
                format: OutputFormat::Json,
            }
        );
    }
}
