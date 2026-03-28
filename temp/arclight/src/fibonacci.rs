use std::io;

use crate::report::{CaseReport, ReportItem};

use num_bigint::BigUint;
use num_traits::{One, Zero};

const TARGETS: [usize; 5] = [0, 1, 10, 100, 1000];

pub fn report() -> io::Result<CaseReport> {
    let values = TARGETS.map(|n| (n, fibonacci(n)));
    let f10_ok = values
        .iter()
        .find(|(n, _)| *n == 10)
        .map(|(_, value)| value == &num_bigint::BigUint::from(55u8))
        .unwrap_or(false);
    let f1000_digits = values
        .iter()
        .find(|(n, _)| *n == 1000)
        .map(|(_, value)| value.to_string().len())
        .unwrap_or(0);
    let fast_doubling_agrees = TARGETS
        .iter()
        .copied()
        .all(|n| fibonacci(n) == fast_doubling(n).0);
    let cassini_100_holds = {
        let f99 = fibonacci(99);
        let f100 = fibonacci(100);
        let f101 = fibonacci(101);
        &f101 * &f99 == &f100 * &f100 + BigUint::one()
    };

    if !f10_ok || f1000_digits != 209 || !fast_doubling_agrees || !cassini_100_holds {
        return Err(io::Error::new(
            io::ErrorKind::InvalidData,
            "fibonacci check failed: a direct value, fast-doubling cross-check, or Cassini identity failed",
        ));
    }

    let mut reason = vec![
        ReportItem::text(
            "The program uses the defining recurrence F(n+1) = F(n) + F(n-1) with arbitrary-precision integers, so each reported value is exact.",
        ),
    ];
    for (n, value) in &values {
        reason.push(ReportItem::field(format!("F({n})"), value.to_string()));
    }

    Ok(CaseReport::new("fibonacci")
        .with_answer(vec![
            ReportItem::text("The requested Fibonacci values are computed exactly, up to F(1000)."),
            ReportItem::field("case", "fibonacci"),
            ReportItem::field("targets", "0, 1, 10, 100, 1000"),
        ])
        .with_reason_why(reason)
        .with_check(vec![
            ReportItem::field("F(10) = 55", if f10_ok { "yes" } else { "no" }),
            ReportItem::field("digits in F(1000)", f1000_digits.to_string()),
            ReportItem::field(
                "fast-doubling agrees",
                if fast_doubling_agrees { "yes" } else { "no" },
            ),
            ReportItem::field(
                "Cassini at n=100",
                if cassini_100_holds { "yes" } else { "no" },
            ),
        ]))
}

pub fn run_and_print() -> io::Result<()> {
    let values = TARGETS.map(|n| (n, fibonacci(n)));
    let f10_ok = values
        .iter()
        .find(|(n, _)| *n == 10)
        .map(|(_, value)| value == &BigUint::from(55u8))
        .unwrap_or(false);
    let f1000_digits = values
        .iter()
        .find(|(n, _)| *n == 1000)
        .map(|(_, value)| value.to_string().len())
        .unwrap_or(0);
    let fast_doubling_agrees = TARGETS
        .iter()
        .copied()
        .all(|n| fibonacci(n) == fast_doubling(n).0);
    let cassini_100_holds = {
        let f99 = fibonacci(99);
        let f100 = fibonacci(100);
        let f101 = fibonacci(101);
        &f101 * &f99 == &f100 * &f100 + BigUint::one()
    };

    println!("=== Answer ===");
    println!("The requested Fibonacci values are computed exactly, up to F(1000).");
    println!("case          : fibonacci");
    println!("targets       : 0, 1, 10, 100, 1000");
    println!();
    println!("=== Reason Why ===");
    println!(
        "The program uses the defining recurrence F(n+1) = F(n) + F(n-1) with arbitrary-precision integers, so each reported value is exact."
    );
    for (n, value) in &values {
        println!("F({n:<4}) = {value}");
    }
    println!();
    println!("=== Check ===");
    println!("F(10) = 55          : {}", if f10_ok { "yes" } else { "no" });
    println!("digits in F(1000)   : {}", f1000_digits);
    println!(
        "fast-doubling agrees: {}",
        if fast_doubling_agrees { "yes" } else { "no" }
    );
    println!(
        "Cassini at n=100    : {}",
        if cassini_100_holds { "yes" } else { "no" }
    );

    if !f10_ok || f1000_digits != 209 || !fast_doubling_agrees || !cassini_100_holds {
        return Err(io::Error::new(
            io::ErrorKind::InvalidData,
            "fibonacci check failed: a direct value, fast-doubling cross-check, or Cassini identity failed",
        ));
    }

    Ok(())
}

fn fibonacci(n: usize) -> BigUint {
    match n {
        0 => BigUint::zero(),
        1 => BigUint::one(),
        _ => {
            let mut previous = BigUint::zero();
            let mut current = BigUint::one();

            for _ in 1..n {
                let next = &previous + &current;
                previous = current;
                current = next;
            }

            current
        }
    }
}

fn fast_doubling(n: usize) -> (BigUint, BigUint) {
    if n == 0 {
        return (BigUint::zero(), BigUint::one());
    }

    let (a, b) = fast_doubling(n / 2);
    let two_b_minus_a = (&b << 1usize) - &a;
    let c = &a * &two_b_minus_a;
    let d = &a * &a + &b * &b;

    if n % 2 == 0 {
        (c, d)
    } else {
        (d.clone(), c + d)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn computes_small_values() {
        assert_eq!(fibonacci(0), BigUint::from(0u8));
        assert_eq!(fibonacci(1), BigUint::from(1u8));
        assert_eq!(fibonacci(10), BigUint::from(55u8));
    }

    #[test]
    fn fast_doubling_matches_iterative_values() {
        for n in [0, 1, 2, 10, 100, 1000] {
            assert_eq!(fibonacci(n), fast_doubling(n).0);
        }
    }

    #[test]
    fn computes_large_value_used_in_the_cli_example() {
        assert_eq!(fibonacci(1000).to_string(), "43466557686937456435688527675040625802564660517371780402481729089536555417949051890403879840079255169295922593080322634775209689623239873322471161642996440906533187938298969649928516003704476137795166849228875");
    }
}
