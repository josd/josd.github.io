use std::collections::HashMap;
use std::io;

use crate::report::{CaseReport, ReportItem};

const MAX_START: u64 = 10000;
const SAMPLE_START: u64 = 27;

#[derive(Debug, Clone)]
struct ProofReport {
    starts_checked: usize,
    all_reach_one: bool,
    max_steps: usize,
    max_steps_start: u64,
    highest_peak: u64,
    peak_start: u64,
    sample_trace_steps: usize,
    sample_trace_peak: u64,
    sample_trace_rule_valid: bool,
    max_steps_witness_verified: bool,
    peak_witness_verified: bool,
}

pub fn report() -> io::Result<CaseReport> {
    let report = prove_collatz_up_to(MAX_START);

    if !report.all_reach_one
        || !report.sample_trace_rule_valid
        || !report.max_steps_witness_verified
        || !report.peak_witness_verified
    {
        return Err(io::Error::new(
            io::ErrorKind::InvalidData,
            "Collatz check failed: an invariant or witness validation did not hold",
        ));
    }

    Ok(CaseReport::new("collatz-1000")
        .with_answer(vec![
            ReportItem::text(format!(
                "For starts 1..={MAX_START}, every tested value reaches 1 under the Collatz map."
            )),
            ReportItem::field("case", "collatz-1000"),
            ReportItem::field("range checked", format!("1..={MAX_START}")),
            ReportItem::field("method", "exhaustive verification"),
        ])
        .with_reason_why(vec![
            ReportItem::text(
                "We apply the standard Collatz rule step by step, memoize stopping times, and summarize the hardest witness in the tested range.",
            ),
            ReportItem::field("starts checked", report.starts_checked.to_string()),
            ReportItem::field("max steps", report.max_steps.to_string()),
            ReportItem::field("max-steps start", report.max_steps_start.to_string()),
            ReportItem::field("highest peak", report.highest_peak.to_string()),
            ReportItem::field("peak start", report.peak_start.to_string()),
            ReportItem::field(
                format!("trace({SAMPLE_START}) steps"),
                report.sample_trace_steps.to_string(),
            ),
            ReportItem::field(
                format!("trace({SAMPLE_START}) peak"),
                report.sample_trace_peak.to_string(),
            ),
        ])
        .with_check(vec![
            ReportItem::field("all reach 1", yes_no(report.all_reach_one)),
            ReportItem::field(
                format!("trace({SAMPLE_START}) follows rule"),
                yes_no(report.sample_trace_rule_valid),
            ),
            ReportItem::field(
                "max-steps witness ok",
                yes_no(report.max_steps_witness_verified),
            ),
            ReportItem::field("peak witness ok", yes_no(report.peak_witness_verified)),
        ]))
}

pub fn run_and_print() -> io::Result<()> {
    let report = prove_collatz_up_to(MAX_START);

    println!("=== Answer ===");
    println!(
        "For starts 1..={MAX_START}, every tested value reaches 1 under the Collatz map."
    );
    println!("case                : collatz-1000");
    println!("range checked       : 1..={MAX_START}");
    println!("method              : exhaustive verification");
    println!();
    println!("=== Reason Why ===");
    println!(
        "We apply the standard Collatz rule step by step, memoize stopping times, and summarize the hardest witness in the tested range."
    );
    println!("starts checked      : {}", report.starts_checked);
    println!("max steps           : {}", report.max_steps);
    println!("max-steps start     : {}", report.max_steps_start);
    println!("highest peak        : {}", report.highest_peak);
    println!("peak start          : {}", report.peak_start);
    println!("trace({SAMPLE_START}) steps    : {}", report.sample_trace_steps);
    println!("trace({SAMPLE_START}) peak     : {}", report.sample_trace_peak);
    println!();
    println!("=== Check ===");
    println!("all reach 1         : {}", yes_no(report.all_reach_one));
    println!(
        "trace({SAMPLE_START}) follows rule : {}",
        yes_no(report.sample_trace_rule_valid)
    );
    println!(
        "max-steps witness ok: {}",
        yes_no(report.max_steps_witness_verified)
    );
    println!(
        "peak witness ok     : {}",
        yes_no(report.peak_witness_verified)
    );

    if !report.all_reach_one
        || !report.sample_trace_rule_valid
        || !report.max_steps_witness_verified
        || !report.peak_witness_verified
    {
        return Err(io::Error::new(
            io::ErrorKind::InvalidData,
            "Collatz check failed: an invariant or witness validation did not hold",
        ));
    }

    Ok(())
}

fn prove_collatz_up_to(max_start: u64) -> ProofReport {
    let mut memo = HashMap::from([(1_u64, 0_usize)]);
    let mut starts_checked = 0;
    let mut all_reach_one = true;
    let mut max_steps = 0;
    let mut max_steps_start = 1;
    let mut highest_peak = 1;
    let mut peak_start = 1;

    for start in 1..=max_start {
        starts_checked += 1;
        let trace = collatz_trace(start);
        let reaches_one = trace.last().copied() == Some(1);
        let steps = stopping_time(start, &mut memo);
        let peak = trace.iter().copied().max().unwrap_or(start);

        all_reach_one &= reaches_one;

        if steps > max_steps {
            max_steps = steps;
            max_steps_start = start;
        }

        if peak > highest_peak {
            highest_peak = peak;
            peak_start = start;
        }
    }

    let sample_trace = collatz_trace(SAMPLE_START);
    let max_steps_trace = collatz_trace(max_steps_start);
    let peak_trace = collatz_trace(peak_start);

    ProofReport {
        starts_checked,
        all_reach_one,
        max_steps,
        max_steps_start,
        highest_peak,
        peak_start,
        sample_trace_steps: sample_trace.len().saturating_sub(1),
        sample_trace_peak: sample_trace.iter().copied().max().unwrap_or(SAMPLE_START),
        sample_trace_rule_valid: trace_follows_rule(&sample_trace),
        max_steps_witness_verified: max_steps_trace.len().saturating_sub(1) == max_steps,
        peak_witness_verified: peak_trace.iter().copied().max().unwrap_or(peak_start) == highest_peak,
    }
}

fn stopping_time(start: u64, memo: &mut HashMap<u64, usize>) -> usize {
    if let Some(&steps) = memo.get(&start) {
        return steps;
    }

    let mut path = Vec::new();
    let mut current = start;

    while !memo.contains_key(&current) {
        path.push(current);
        current = collatz_step(current);
    }

    let mut known_steps = memo[&current];

    while let Some(value) = path.pop() {
        known_steps += 1;
        memo.insert(value, known_steps);
    }

    memo[&start]
}

fn collatz_trace(start: u64) -> Vec<u64> {
    let mut trace = vec![start];
    let mut current = start;

    while current != 1 {
        current = collatz_step(current);
        trace.push(current);
    }

    trace
}

fn trace_follows_rule(trace: &[u64]) -> bool {
    trace.windows(2)
        .all(|pair| collatz_step(pair[0]) == pair[1])
        && trace.last().copied() == Some(1)
}

fn collatz_step(value: u64) -> u64 {
    if value % 2 == 0 {
        value / 2
    } else {
        value * 3 + 1
    }
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
    fn collatz_step_matches_standard_examples() {
        assert_eq!(collatz_step(1), 4);
        assert_eq!(collatz_step(2), 1);
        assert_eq!(collatz_step(3), 10);
        assert_eq!(collatz_step(27), 82);
    }

    #[test]
    fn trace_for_27_has_the_expected_length_and_peak() {
        let trace = collatz_trace(27);

        assert_eq!(trace.first().copied(), Some(27));
        assert_eq!(trace.last().copied(), Some(1));
        assert!(trace_follows_rule(&trace));
        assert_eq!(trace.len() - 1, 111);
        assert_eq!(trace.iter().copied().max(), Some(9232));
    }

    #[test]
    fn exhaustive_check_matches_the_known_results_for_first_10000_starts() {
        let report = prove_collatz_up_to(MAX_START);

        assert_eq!(report.starts_checked, 10000);
        assert!(report.all_reach_one);
        assert_eq!(report.max_steps, 261);
        assert_eq!(report.max_steps_start, 6171);
        assert_eq!(report.highest_peak, 27114424);
        assert_eq!(report.peak_start, 9663);
        assert_eq!(report.sample_trace_steps, 111);
        assert_eq!(report.sample_trace_peak, 9232);
        assert!(report.sample_trace_rule_valid);
        assert!(report.max_steps_witness_verified);
        assert!(report.peak_witness_verified);
    }
}
