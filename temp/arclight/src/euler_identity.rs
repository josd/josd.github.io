use std::io;

use crate::report::{CaseReport, ReportItem};

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
struct ExactComplex {
    re: i32,
    im: i32,
}

impl ExactComplex {
    const fn new(re: i32, im: i32) -> Self {
        Self { re, im }
    }

    const fn add(self, other: Self) -> Self {
        Self::new(self.re + other.re, self.im + other.im)
    }

    const fn modulus_squared(self) -> i32 {
        self.re * self.re + self.im * self.im
    }
}

struct EulerIdentityReport {
    phase: ExactComplex,
    lhs_plus_one: ExactComplex,
    rhs_zero: ExactComplex,
    phase_mod_sq: i32,
    phase_mod_sq_is_one: bool,
    phase_is_minus_one: bool,
    lhs_real_is_zero: bool,
    lhs_imag_is_zero: bool,
    identity_holds: bool,
}

pub fn report() -> io::Result<CaseReport> {
    let report = evaluate();

    if !report.identity_holds
        || !report.phase_is_minus_one
        || !report.lhs_real_is_zero
        || !report.lhs_imag_is_zero
        || !report.phase_mod_sq_is_one
    {
        return Err(io::Error::new(
            io::ErrorKind::InvalidData,
            "euler-identity check failed: exact equality or a component-wise witness did not hold",
        ));
    }

    Ok(CaseReport::new("euler-identity")
        .with_answer(vec![
            ReportItem::text("Euler's identity holds exactly in this model: exp(i*pi) + 1 = 0."),
            ReportItem::field("case", "euler-identity"),
            ReportItem::field("formula", "exp(i*pi) + 1 = 0"),
            ReportItem::field("identity holds", yes_no(report.identity_holds)),
        ])
        .with_reason_why(vec![
            ReportItem::text(
                "We represent exp(i*pi) exactly as (-1, 0), add (1, 0), and compare the result with exact zero in integer complex arithmetic.",
            ),
            ReportItem::field("exp(i*pi) exact", format!("({}, {})", report.phase.re, report.phase.im)),
            ReportItem::field(
                "lhs + 1 exact",
                format!("({}, {})", report.lhs_plus_one.re, report.lhs_plus_one.im),
            ),
            ReportItem::field(
                "rhs zero exact",
                format!("({}, {})", report.rhs_zero.re, report.rhs_zero.im),
            ),
        ])
        .with_check(vec![
            ReportItem::field("phase = -1", yes_no(report.phase_is_minus_one)),
            ReportItem::field("phase modulus^2", report.phase_mod_sq.to_string()),
            ReportItem::field("sum real part = 0", yes_no(report.lhs_real_is_zero)),
            ReportItem::field("sum imag part = 0", yes_no(report.lhs_imag_is_zero)),
            ReportItem::field("phase modulus ok", yes_no(report.phase_mod_sq_is_one)),
        ]))
}

pub fn run_and_print() -> io::Result<()> {
    let report = evaluate();

    println!("=== Answer ===");
    println!("Euler's identity holds exactly in this model: exp(i*pi) + 1 = 0.");
    println!("case              : euler-identity");
    println!("formula           : exp(i*pi) + 1 = 0");
    println!("identity holds    : {}", yes_no(report.identity_holds));
    println!();
    println!("=== Reason Why ===");
    println!(
        "We represent exp(i*pi) exactly as (-1, 0), add (1, 0), and compare the result with exact zero in integer complex arithmetic."
    );
    println!(
        "exp(i*pi) exact   : ({}, {})",
        report.phase.re, report.phase.im
    );
    println!(
        "lhs + 1 exact     : ({}, {})",
        report.lhs_plus_one.re, report.lhs_plus_one.im
    );
    println!(
        "rhs zero exact    : ({}, {})",
        report.rhs_zero.re, report.rhs_zero.im
    );
    println!();
    println!("=== Check ===");
    println!("phase = -1        : {}", yes_no(report.phase_is_minus_one));
    println!("phase modulus^2    : {}", report.phase_mod_sq);
    println!("sum real part = 0 : {}", yes_no(report.lhs_real_is_zero));
    println!("sum imag part = 0 : {}", yes_no(report.lhs_imag_is_zero));
    println!("phase modulus ok  : {}", yes_no(report.phase_mod_sq_is_one));

    if !report.identity_holds
        || !report.phase_is_minus_one
        || !report.lhs_real_is_zero
        || !report.lhs_imag_is_zero
        || !report.phase_mod_sq_is_one
    {
        return Err(io::Error::new(
            io::ErrorKind::InvalidData,
            "euler-identity check failed: exact equality or a component-wise witness did not hold",
        ));
    }

    Ok(())
}

fn evaluate() -> EulerIdentityReport {
    let zero = ExactComplex::new(0, 0);
    let one = ExactComplex::new(1, 0);

    let minus_one = 0 - 1;
    let phase = ExactComplex::new(minus_one, 0);
    let lhs_plus_one = phase.add(one);
    let rhs_zero = zero;
    let phase_mod_sq = phase.modulus_squared();
    let phase_mod_sq_is_one = phase_mod_sq == 1;
    let identity_holds = lhs_plus_one == rhs_zero;

    EulerIdentityReport {
        phase,
        lhs_plus_one,
        rhs_zero,
        phase_mod_sq,
        phase_mod_sq_is_one,
        phase_is_minus_one: phase == ExactComplex::new(-1, 0),
        lhs_real_is_zero: lhs_plus_one.re == 0,
        lhs_imag_is_zero: lhs_plus_one.im == 0,
        identity_holds,
    }
}

fn yes_no(value: bool) -> &'static str {
    if value { "yes" } else { "no" }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn euler_identity_report_is_consistent() {
        let report = evaluate();

        assert_eq!(report.phase, ExactComplex::new(-1, 0));
        assert_eq!(report.lhs_plus_one, ExactComplex::new(0, 0));
        assert_eq!(report.rhs_zero, ExactComplex::new(0, 0));
        assert_eq!(report.phase_mod_sq, 1);
        assert!(report.phase_mod_sq_is_one);
        assert!(report.phase_is_minus_one);
        assert!(report.lhs_real_is_zero);
        assert!(report.lhs_imag_is_zero);
        assert!(report.identity_holds);
    }
}
