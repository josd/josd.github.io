use std::collections::BTreeMap;
use std::io;

use crate::report::{CaseReport, ReportItem};

const KAPREKAR_CONSTANT: u16 = 6174;
const MAX_EXPECTED_ITERATIONS: usize = 7;
const LEADING_ZERO_WITNESS: u16 = 2111;

#[derive(Debug, Clone)]
struct ProofReport {
    valid_starts_checked: usize,
    repdigits_excluded: usize,
    fixed_point_verified: bool,
    all_starts_reach_constant: bool,
    bound_verified: bool,
    histogram_total_verified: bool,
    worst_case_trace_verified: bool,
    leading_zero_trace_verified: bool,
    max_iterations: usize,
    worst_case_starts: usize,
    step_histogram: BTreeMap<usize, usize>,
    worst_case_trace: Vec<u16>,
    leading_zero_trace: Vec<u16>,
}

pub fn report() -> io::Result<CaseReport> {
    let report = prove_kaprekar_6174();

    if !report.fixed_point_verified
        || !report.all_starts_reach_constant
        || !report.bound_verified
        || !report.histogram_total_verified
        || !report.worst_case_trace_verified
        || !report.leading_zero_trace_verified
    {
        return Err(io::Error::new(
            io::ErrorKind::InvalidData,
            "kaprekar-6174 check failed: a fixed-point, histogram, or witness validation failed",
        ));
    }

    Ok(CaseReport::new("kaprekar-6174")
        .with_answer(vec![
            ReportItem::text(
                "Every valid four-digit start tested reaches 6174, and all of them do so within seven iterations.",
            ),
            ReportItem::field("case", "kaprekar-6174"),
            ReportItem::field("constant", KAPREKAR_CONSTANT.to_string()),
            ReportItem::field("method", "exhaustive verification"),
        ])
        .with_reason_why(vec![
            ReportItem::text(
                "We apply Kaprekar's routine to every non-repdigit four-digit start, record the full iteration counts, and keep concrete witness traces for the worst and leading-zero cases.",
            ),
            ReportItem::field("valid starts checked", report.valid_starts_checked.to_string()),
            ReportItem::field("repdigits excluded", report.repdigits_excluded.to_string()),
            ReportItem::field("max iterations", report.max_iterations.to_string()),
            ReportItem::field("worst-case starts", report.worst_case_starts.to_string()),
            ReportItem::field("step histogram", format_histogram(&report.step_histogram)),
            ReportItem::field("worst-case trace", format_trace(&report.worst_case_trace)),
            ReportItem::field("leading-zero trace", format_trace(&report.leading_zero_trace)),
        ])
        .with_check(vec![
            ReportItem::field("6174 fixed point", yes_no(report.fixed_point_verified)),
            ReportItem::field("all starts reach it", yes_no(report.all_starts_reach_constant)),
            ReportItem::field("bound <= 7 verified", yes_no(report.bound_verified)),
            ReportItem::field("histogram total ok", yes_no(report.histogram_total_verified)),
            ReportItem::field("worst trace valid", yes_no(report.worst_case_trace_verified)),
            ReportItem::field("leading-zero valid", yes_no(report.leading_zero_trace_verified)),
        ]))
}

pub fn run_and_print() -> io::Result<()> {
    let report = prove_kaprekar_6174();

    println!("=== Answer ===");
    println!(
        "Every valid four-digit start tested reaches 6174, and all of them do so within seven iterations."
    );
    println!("case                : kaprekar-6174");
    println!("constant            : {KAPREKAR_CONSTANT}");
    println!("method              : exhaustive verification");
    println!();
    println!("=== Reason Why ===");
    println!(
        "We apply Kaprekar's routine to every non-repdigit four-digit start, record the full iteration counts, and keep concrete witness traces for the worst and leading-zero cases."
    );
    println!("valid starts checked: {}", report.valid_starts_checked);
    println!("repdigits excluded  : {}", report.repdigits_excluded);
    println!("max iterations      : {}", report.max_iterations);
    println!("worst-case starts   : {}", report.worst_case_starts);
    println!("step histogram      : {}", format_histogram(&report.step_histogram));
    println!("worst-case trace    : {}", format_trace(&report.worst_case_trace));
    println!("leading-zero trace  : {}", format_trace(&report.leading_zero_trace));
    println!();
    println!("=== Check ===");
    println!("6174 fixed point    : {}", yes_no(report.fixed_point_verified));
    println!("all starts reach it : {}", yes_no(report.all_starts_reach_constant));
    println!("bound <= 7 verified : {}", yes_no(report.bound_verified));
    println!("histogram total ok  : {}", yes_no(report.histogram_total_verified));
    println!("worst trace valid   : {}", yes_no(report.worst_case_trace_verified));
    println!("leading-zero valid  : {}", yes_no(report.leading_zero_trace_verified));

    if !report.fixed_point_verified
        || !report.all_starts_reach_constant
        || !report.bound_verified
        || !report.histogram_total_verified
        || !report.worst_case_trace_verified
        || !report.leading_zero_trace_verified
    {
        return Err(io::Error::new(
            io::ErrorKind::InvalidData,
            "kaprekar-6174 check failed: a fixed-point, histogram, or witness validation failed",
        ));
    }

    Ok(())
}

fn prove_kaprekar_6174() -> ProofReport {
    let mut valid_starts_checked = 0;
    let mut repdigits_excluded = 0;
    let mut all_starts_reach_constant = true;
    let mut bound_verified = true;
    let mut max_iterations = 0;
    let mut worst_case_starts = 0;
    let mut step_histogram = BTreeMap::new();
    let mut worst_case_trace = Vec::new();

    for start in 0..=9999_u16 {
        if !has_at_least_two_distinct_digits(start) {
            repdigits_excluded += 1;
            continue;
        }

        valid_starts_checked += 1;
        let trace = kaprekar_trace(start);
        let reaches_constant = trace.last().copied() == Some(KAPREKAR_CONSTANT);
        let iterations = trace.len().saturating_sub(1);

        all_starts_reach_constant &= reaches_constant;
        bound_verified &= reaches_constant && iterations <= MAX_EXPECTED_ITERATIONS;
        *step_histogram.entry(iterations).or_insert(0) += 1;

        if iterations > max_iterations {
            max_iterations = iterations;
            worst_case_starts = 1;
            worst_case_trace = trace;
        } else if iterations == max_iterations {
            worst_case_starts += 1;
        }
    }

    let leading_zero_trace = kaprekar_trace(LEADING_ZERO_WITNESS);

    ProofReport {
        valid_starts_checked,
        repdigits_excluded,
        fixed_point_verified: kaprekar_step(KAPREKAR_CONSTANT) == KAPREKAR_CONSTANT,
        all_starts_reach_constant,
        bound_verified,
        histogram_total_verified: step_histogram.values().sum::<usize>() == valid_starts_checked,
        worst_case_trace_verified: trace_follows_rule(&worst_case_trace)
            && worst_case_trace.last().copied() == Some(KAPREKAR_CONSTANT)
            && worst_case_trace.len().saturating_sub(1) == max_iterations,
        leading_zero_trace_verified: trace_follows_rule(&leading_zero_trace)
            && leading_zero_trace.first().copied() == Some(LEADING_ZERO_WITNESS)
            && leading_zero_trace.last().copied() == Some(KAPREKAR_CONSTANT),
        max_iterations,
        worst_case_starts,
        step_histogram,
        worst_case_trace,
        leading_zero_trace,
    }
}

fn kaprekar_trace(start: u16) -> Vec<u16> {
    let mut trace = vec![start];
    let mut current = start;

    for _ in 0..=MAX_EXPECTED_ITERATIONS {
        if current == KAPREKAR_CONSTANT {
            break;
        }

        current = kaprekar_step(current);
        trace.push(current);
    }

    trace
}

fn kaprekar_step(value: u16) -> u16 {
    let mut digits = digits_of(value);
    digits.sort_unstable();

    let ascending = number_from_digits(digits);
    digits.reverse();
    let descending = number_from_digits(digits);

    descending - ascending
}

fn trace_follows_rule(trace: &[u16]) -> bool {
    trace.windows(2)
        .all(|pair| kaprekar_step(pair[0]) == pair[1])
}

fn has_at_least_two_distinct_digits(value: u16) -> bool {
    let digits = digits_of(value);
    digits.windows(2).any(|pair| pair[0] != pair[1])
        || (digits[0] != digits[3])
}

fn digits_of(value: u16) -> [u8; 4] {
    [
        ((value / 1000) % 10) as u8,
        ((value / 100) % 10) as u8,
        ((value / 10) % 10) as u8,
        (value % 10) as u8,
    ]
}

fn number_from_digits(digits: [u8; 4]) -> u16 {
    digits.into_iter().fold(0_u16, |acc, digit| acc * 10 + digit as u16)
}

fn format_trace(trace: &[u16]) -> String {
    trace
        .iter()
        .map(|value| format!("{value:04}"))
        .collect::<Vec<_>>()
        .join(" -> ")
}

fn format_histogram(histogram: &BTreeMap<usize, usize>) -> String {
    histogram
        .iter()
        .map(|(iterations, count)| format!("{iterations}->{count}"))
        .collect::<Vec<_>>()
        .join(", ")
}

fn yes_no(value: bool) -> &'static str {
    if value {
        "yes"
    } else {
        "no"
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn kaprekar_step_matches_the_standard_examples() {
        assert_eq!(kaprekar_step(3524), 3087);
        assert_eq!(kaprekar_step(2111), 999);
        assert_eq!(kaprekar_step(6174), 6174);
    }

    #[test]
    fn exhaustive_proof_matches_the_known_bound() {
        let report = prove_kaprekar_6174();

        assert_eq!(report.valid_starts_checked, 9990);
        assert_eq!(report.repdigits_excluded, 10);
        assert!(report.fixed_point_verified);
        assert!(report.all_starts_reach_constant);
        assert!(report.bound_verified);
        assert!(report.histogram_total_verified);
        assert!(report.worst_case_trace_verified);
        assert!(report.leading_zero_trace_verified);
        assert_eq!(report.max_iterations, 7);
        assert_eq!(report.worst_case_starts, 2184);
        assert_eq!(format_trace(&report.worst_case_trace), "0014 -> 4086 -> 8172 -> 7443 -> 3996 -> 6264 -> 4176 -> 6174");
        assert_eq!(format_trace(&report.leading_zero_trace), "2111 -> 0999 -> 8991 -> 8082 -> 8532 -> 6174");
    }
}
