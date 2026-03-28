use std::io;

use crate::report::{CaseReport, ReportItem};

const MAX_TARGET: usize = 1000;
const SAMPLE_TARGET: usize = 1000;
const KNOWN_PRIME_COUNT_UP_TO_1000: usize = 168;

#[derive(Debug, Clone)]
struct ProofReport {
    even_targets_checked: usize,
    all_even_targets_representable: bool,
    total_decompositions: usize,
    fewest_decompositions: usize,
    hardest_targets: Vec<usize>,
    most_decompositions: usize,
    richest_target: usize,
    sample_pair: (usize, usize),
    prime_count: usize,
    prime_count_matches_known: bool,
    sample_pair_valid: bool,
    richest_target_verified: bool,
    hardest_targets_verified: bool,
}

pub fn report() -> io::Result<CaseReport> {
    let report = prove_goldbach_up_to(MAX_TARGET);

    if !report.all_even_targets_representable
        || !report.prime_count_matches_known
        || !report.sample_pair_valid
        || !report.richest_target_verified
        || !report.hardest_targets_verified
    {
        return Err(io::Error::new(
            io::ErrorKind::InvalidData,
            "goldbach-1000 check failed: a decomposition or prime-table cross-check did not hold",
        ));
    }

    Ok(CaseReport::new("goldbach-1000")
        .with_answer(vec![
            ReportItem::text(format!(
                "Every even integer from 4 through {MAX_TARGET} has at least one Goldbach decomposition in the tested range."
            )),
            ReportItem::field("case", "goldbach-1000"),
            ReportItem::field("range checked", format!("even integers 4..={MAX_TARGET}")),
            ReportItem::field("method", "exhaustive verification"),
        ])
        .with_reason_why(vec![
            ReportItem::text(
                "We generate all primes up to the range limit, enumerate unordered prime pairs p + q = n for each even target, and summarize the sparsest and richest cases.",
            ),
            ReportItem::field("even targets checked", report.even_targets_checked.to_string()),
            ReportItem::field("total decompositions", report.total_decompositions.to_string()),
            ReportItem::field("fewest decompositions", report.fewest_decompositions.to_string()),
            ReportItem::field("hardest targets", format_targets(&report.hardest_targets)),
            ReportItem::field("most decompositions", report.most_decompositions.to_string()),
            ReportItem::field("richest target", report.richest_target.to_string()),
            ReportItem::field(format!("primes ≤ {MAX_TARGET}"), report.prime_count.to_string()),
            ReportItem::field(
                format!("balanced pair({SAMPLE_TARGET})"),
                format!("{} + {}", report.sample_pair.0, report.sample_pair.1),
            ),
        ])
        .with_check(vec![
            ReportItem::field("all represented", yes_no(report.all_even_targets_representable)),
            ReportItem::field("prime count known", yes_no(report.prime_count_matches_known)),
            ReportItem::field("balanced pair valid", yes_no(report.sample_pair_valid)),
            ReportItem::field("richest target ok", yes_no(report.richest_target_verified)),
            ReportItem::field("hardest targets ok", yes_no(report.hardest_targets_verified)),
        ]))
}

pub fn run_and_print() -> io::Result<()> {
    let report = prove_goldbach_up_to(MAX_TARGET);

    println!("=== Answer ===");
    println!(
        "Every even integer from 4 through {MAX_TARGET} has at least one Goldbach decomposition in the tested range."
    );
    println!("case                 : goldbach-1000");
    println!("range checked        : even integers 4..={MAX_TARGET}");
    println!("method               : exhaustive verification");
    println!();
    println!("=== Reason Why ===");
    println!(
        "We generate all primes up to the range limit, enumerate unordered prime pairs p + q = n for each even target, and summarize the sparsest and richest cases."
    );
    println!("even targets checked : {}", report.even_targets_checked);
    println!("total decompositions : {}", report.total_decompositions);
    println!("fewest decompositions: {}", report.fewest_decompositions);
    println!("hardest targets      : {}", format_targets(&report.hardest_targets));
    println!("most decompositions  : {}", report.most_decompositions);
    println!("richest target       : {}", report.richest_target);
    println!("primes ≤ {MAX_TARGET}       : {}", report.prime_count);
    println!(
        "balanced pair({SAMPLE_TARGET}) : {} + {}",
        report.sample_pair.0,
        report.sample_pair.1
    );
    println!();
    println!("=== Check ===");
    println!("all represented      : {}", yes_no(report.all_even_targets_representable));
    println!("prime count known    : {}", yes_no(report.prime_count_matches_known));
    println!("balanced pair valid  : {}", yes_no(report.sample_pair_valid));
    println!("richest target ok    : {}", yes_no(report.richest_target_verified));
    println!("hardest targets ok   : {}", yes_no(report.hardest_targets_verified));

    if !report.all_even_targets_representable
        || !report.prime_count_matches_known
        || !report.sample_pair_valid
        || !report.richest_target_verified
        || !report.hardest_targets_verified
    {
        return Err(io::Error::new(
            io::ErrorKind::InvalidData,
            "goldbach-1000 check failed: a decomposition or prime-table cross-check did not hold",
        ));
    }

    Ok(())
}

fn prove_goldbach_up_to(max_target: usize) -> ProofReport {
    let prime_table = sieve(max_target);
    let primes = primes_from_table(&prime_table);

    let mut even_targets_checked = 0;
    let mut all_even_targets_representable = true;
    let mut total_decompositions = 0;
    let mut fewest_decompositions = usize::MAX;
    let mut hardest_targets = Vec::new();
    let mut most_decompositions = 0;
    let mut richest_target = 4;

    for target in (4..=max_target).step_by(2) {
        even_targets_checked += 1;
        let decompositions = goldbach_pairs(target, &primes, &prime_table);
        let count = decompositions.len();

        all_even_targets_representable &= count > 0;
        total_decompositions += count;

        if count < fewest_decompositions {
            fewest_decompositions = count;
            hardest_targets.clear();
            hardest_targets.push(target);
        } else if count == fewest_decompositions {
            hardest_targets.push(target);
        }

        if count > most_decompositions {
            most_decompositions = count;
            richest_target = target;
        }
    }

    let sample_pairs = goldbach_pairs(SAMPLE_TARGET, &primes, &prime_table);
    let sample_pair = balanced_pair(&sample_pairs).unwrap_or((0, 0));

    ProofReport {
        even_targets_checked,
        all_even_targets_representable,
        total_decompositions,
        fewest_decompositions,
        hardest_targets: hardest_targets.clone(),
        most_decompositions,
        richest_target,
        sample_pair,
        prime_count: primes.len(),
        prime_count_matches_known: primes.len() == KNOWN_PRIME_COUNT_UP_TO_1000,
        sample_pair_valid: sample_pair.0 + sample_pair.1 == SAMPLE_TARGET
            && prime_table[sample_pair.0]
            && prime_table[sample_pair.1],
        richest_target_verified: goldbach_pairs(richest_target, &primes, &prime_table).len()
            == most_decompositions,
        hardest_targets_verified: hardest_targets.iter().all(|&target| {
            goldbach_pairs(target, &primes, &prime_table).len() == fewest_decompositions
        }),
    }
}

fn sieve(limit: usize) -> Vec<bool> {
    let mut is_prime = vec![true; limit + 1];
    if !is_prime.is_empty() {
        is_prime[0] = false;
    }
    if limit >= 1 {
        is_prime[1] = false;
    }

    let mut p = 2;
    while p * p <= limit {
        if is_prime[p] {
            let mut multiple = p * p;
            while multiple <= limit {
                is_prime[multiple] = false;
                multiple += p;
            }
        }
        p += 1;
    }

    is_prime
}

fn primes_from_table(prime_table: &[bool]) -> Vec<usize> {
    prime_table
        .iter()
        .enumerate()
        .filter_map(|(value, &is_prime)| is_prime.then_some(value))
        .collect()
}

fn goldbach_pairs(
    target: usize,
    primes: &[usize],
    prime_table: &[bool],
) -> Vec<(usize, usize)> {
    let mut pairs = Vec::new();

    for &left in primes {
        if left > target / 2 {
            break;
        }

        let right = target - left;
        if prime_table[right] {
            pairs.push((left, right));
        }
    }

    pairs
}

fn balanced_pair(pairs: &[(usize, usize)]) -> Option<(usize, usize)> {
    pairs
        .iter()
        .copied()
        .min_by_key(|(left, right)| right - left)
}

fn format_targets(targets: &[usize]) -> String {
    targets
        .iter()
        .map(|target| target.to_string())
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
    fn sieve_marks_small_primes_correctly() {
        let is_prime = sieve(20);

        assert!(is_prime[2]);
        assert!(is_prime[3]);
        assert!(is_prime[5]);
        assert!(is_prime[19]);
        assert!(!is_prime[0]);
        assert!(!is_prime[1]);
        assert!(!is_prime[4]);
        assert!(!is_prime[15]);
    }

    #[test]
    fn goldbach_pairs_for_100_match_the_known_decompositions() {
        let is_prime = sieve(100);
        let primes = primes_from_table(&is_prime);
        let pairs = goldbach_pairs(100, &primes, &is_prime);

        assert_eq!(pairs.len(), 6);
        assert_eq!(balanced_pair(&pairs), Some((47, 53)));
    }

    #[test]
    fn exhaustive_check_matches_the_known_results_for_first_1000_integers() {
        let report = prove_goldbach_up_to(MAX_TARGET);

        assert_eq!(report.even_targets_checked, 499);
        assert!(report.all_even_targets_representable);
        assert_eq!(report.total_decompositions, 8222);
        assert_eq!(report.fewest_decompositions, 1);
        assert_eq!(report.hardest_targets, vec![4, 6, 8, 12]);
        assert_eq!(report.most_decompositions, 52);
        assert_eq!(report.richest_target, 990);
        assert_eq!(report.sample_pair, (491, 509));
        assert_eq!(report.prime_count, 168);
        assert!(report.prime_count_matches_known);
        assert!(report.sample_pair_valid);
        assert!(report.richest_target_verified);
        assert!(report.hardest_targets_verified);
    }
}
