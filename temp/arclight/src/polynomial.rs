use std::cmp::Ordering;
use std::fmt;
use std::io;

use crate::report::{CaseReport, ReportItem};

const ROOT_TOLERANCE: f64 = 1e-10;
const COEFFICIENT_TOLERANCE: f64 = 1e-8;
const MAX_ITERATIONS: usize = 200;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
struct ExactComplex {
    re: i32,
    im: i32,
}

impl ExactComplex {
    const fn new(re: i32, im: i32) -> Self {
        Self { re, im }
    }

    fn to_approx(self) -> ApproxComplex {
        ApproxComplex::new(self.re as f64, self.im as f64)
    }
}

#[derive(Clone, Copy, Debug, PartialEq)]
struct ApproxComplex {
    re: f64,
    im: f64,
}

impl ApproxComplex {
    const fn new(re: f64, im: f64) -> Self {
        Self { re, im }
    }

    const fn zero() -> Self {
        Self::new(0.0, 0.0)
    }

    const fn one() -> Self {
        Self::new(1.0, 0.0)
    }

    fn add(self, other: Self) -> Self {
        Self::new(self.re + other.re, self.im + other.im)
    }

    fn sub(self, other: Self) -> Self {
        Self::new(self.re - other.re, self.im - other.im)
    }

    fn mul(self, other: Self) -> Self {
        Self::new(
            self.re * other.re - self.im * other.im,
            self.re * other.im + self.im * other.re,
        )
    }

    fn div(self, other: Self) -> Self {
        let scale = other.re * other.re + other.im * other.im;
        Self::new(
            (self.re * other.re + self.im * other.im) / scale,
            (self.im * other.re - self.re * other.im) / scale,
        )
    }

    fn abs(self) -> f64 {
        self.re.hypot(self.im)
    }

    fn powu(self, exponent: usize) -> Self {
        let mut out = Self::one();
        for _ in 0..exponent {
            out = out.mul(self);
        }
        out
    }

    fn distance(self, other: Self) -> f64 {
        self.sub(other).abs()
    }

    fn almost_zero(self, tolerance: f64) -> bool {
        self.abs() <= tolerance
    }

    fn rounded_if_close(self, tolerance: f64) -> Self {
        Self::new(round_if_close(self.re, tolerance), round_if_close(self.im, tolerance))
    }
}

impl fmt::Display for ApproxComplex {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let value = self.rounded_if_close(1e-8);
        match (value.re, value.im) {
            (re, im) if re.abs() < 1e-8 && im.abs() < 1e-8 => write!(f, "0"),
            (re, im) if im.abs() < 1e-8 => write!(f, "{}", format_scalar(re)),
            (re, im) if re.abs() < 1e-8 && (im - 1.0).abs() < 1e-8 => write!(f, "i"),
            (re, im) if re.abs() < 1e-8 && (im + 1.0).abs() < 1e-8 => write!(f, "-i"),
            (re, im) if re.abs() < 1e-8 => write!(f, "{}i", format_scalar(im)),
            (re, im) if (im - 1.0).abs() < 1e-8 => write!(f, "{} + i", format_scalar(re)),
            (re, im) if (im + 1.0).abs() < 1e-8 => write!(f, "{} - i", format_scalar(re)),
            (re, im) if im > 0.0 => write!(f, "{} + {}i", format_scalar(re), format_scalar(im)),
            (re, im) => write!(f, "{} - {}i", format_scalar(re), format_scalar(-im)),
        }
    }
}

#[derive(Debug, Clone)]
struct PolynomialCase {
    label: &'static str,
    coefficients: Vec<ExactComplex>,
}

#[derive(Debug, Clone)]
struct PolynomialCaseReport {
    case: PolynomialCase,
    calculated_roots: Vec<ApproxComplex>,
    reconstructed_coefficients: Vec<ApproxComplex>,
    residuals: Vec<ApproxComplex>,
    roots_are_valid: bool,
    reconstruction_matches: bool,
    degree_matches_root_count: bool,
    vieta_sum_matches: bool,
    vieta_constant_matches: bool,
}

#[derive(Debug, Clone)]
struct PolynomialReport {
    cases: Vec<PolynomialCaseReport>,
    all_examples_valid: bool,
}

pub fn report() -> io::Result<CaseReport> {
    let report = evaluate();

    if !report.all_examples_valid {
        return Err(io::Error::new(
            io::ErrorKind::InvalidData,
            "polynomial check failed: at least one example had invalid roots or reconstruction",
        ));
    }

    let mut reason = vec![ReportItem::text(
        "For each source polynomial, we solve for the roots numerically, substitute them back to measure the residuals, and rebuild the polynomial from those roots.",
    )];
    for (index, example) in report.cases.iter().enumerate() {
        reason.extend(example_report_items(index + 1, example));
    }

    Ok(CaseReport::new("polynomial")
        .with_answer(vec![
            ReportItem::text(
                "Both polynomial examples are solved consistently: the computed roots satisfy the source polynomials and reconstruct the original coefficients.",
            ),
            ReportItem::field("case", "polynomial"),
            ReportItem::field("examples solved", report.cases.len().to_string()),
            ReportItem::field("all examples valid", yes_no(report.all_examples_valid)),
        ])
        .with_reason_why(reason)
        .with_check(vec![ReportItem::field(
            "all examples valid",
            yes_no(report.all_examples_valid),
        )]))
}

pub fn run_and_print() -> io::Result<()> {
    let report = evaluate();

    println!("=== Answer ===");
    println!(
        "Both polynomial examples are solved consistently: the computed roots satisfy the source polynomials and reconstruct the original coefficients."
    );
    println!("case                 : polynomial");
    println!("examples solved      : {}", report.cases.len());
    println!("all examples valid   : {}", yes_no(report.all_examples_valid));
    println!();
    println!("=== Reason Why ===");
    println!(
        "For each source polynomial, we solve for the roots numerically, substitute them back to measure the residuals, and rebuild the polynomial from those roots."
    );

    for (index, example) in report.cases.iter().enumerate() {
        println!();
        println!("Example #{}", index + 1);
        println!("label                : {}", example.case.label);
        println!("degree               : {}", example.case.coefficients.len() - 1);
        println!(
            "coefficients         : {}",
            format_exact_complex_list(&example.case.coefficients)
        );
        println!("roots found          : {}", example.calculated_roots.len());
        println!(
            "roots calculated     : {}",
            format_root_list(&example.calculated_roots)
        );
        println!(
            "residuals            : {}",
            format_approx_complex_list(&example.residuals)
        );
        println!(
            "reconstructed        : {}",
            format_approx_complex_list(&example.reconstructed_coefficients)
        );
        println!(
            "reconstruction ok    : {}",
            yes_no(example.reconstruction_matches)
        );
        println!(
            "roots valid          : {}",
            yes_no(example.roots_are_valid)
        );
        println!(
            "degree/root count ok : {}",
            yes_no(example.degree_matches_root_count)
        );
        println!(
            "Vieta sum ok         : {}",
            yes_no(example.vieta_sum_matches)
        );
        println!(
            "Vieta product ok     : {}",
            yes_no(example.vieta_constant_matches)
        );
    }

    println!();
    println!("=== Check ===");
    println!("all examples valid   : {}", yes_no(report.all_examples_valid));

    if !report.all_examples_valid {
        return Err(io::Error::new(
            io::ErrorKind::InvalidData,
            "polynomial check failed: at least one example had invalid roots or reconstruction",
        ));
    }

    Ok(())
}

fn example_report_items(index: usize, example: &PolynomialCaseReport) -> Vec<ReportItem> {
    vec![
        ReportItem::text(format!("Example #{index}")),
        ReportItem::field("label", example.case.label),
        ReportItem::field("degree", (example.case.coefficients.len() - 1).to_string()),
        ReportItem::field(
            "coefficients",
            format_exact_complex_list(&example.case.coefficients),
        ),
        ReportItem::field("roots found", example.calculated_roots.len().to_string()),
        ReportItem::field(
            "roots calculated",
            format_root_list(&example.calculated_roots),
        ),
        ReportItem::field(
            "residuals",
            format_approx_complex_list(&example.residuals),
        ),
        ReportItem::field(
            "reconstructed",
            format_approx_complex_list(&example.reconstructed_coefficients),
        ),
        ReportItem::field("reconstruction ok", yes_no(example.reconstruction_matches)),
        ReportItem::field("roots valid", yes_no(example.roots_are_valid)),
        ReportItem::field(
            "degree/root count ok",
            yes_no(example.degree_matches_root_count),
        ),
        ReportItem::field("Vieta sum ok", yes_no(example.vieta_sum_matches)),
        ReportItem::field("Vieta product ok", yes_no(example.vieta_constant_matches)),
    ]
}

fn evaluate() -> PolynomialReport {
    let cases = source_cases()
        .into_iter()
        .map(|case| {
            let mut calculated_roots = solve_roots(&case.coefficients);
            sort_roots_for_display(&mut calculated_roots);

            let reconstructed_coefficients = polynomial_from_roots(&calculated_roots);
            let residuals = calculated_roots
                .iter()
                .copied()
                .map(|root| evaluate_polynomial(&case.coefficients, root))
                .collect::<Vec<_>>();
            let roots_are_valid = residuals
                .iter()
                .copied()
                .all(|residual| residual.almost_zero(ROOT_TOLERANCE));
            let source_coefficients = case
                .coefficients
                .iter()
                .copied()
                .map(ExactComplex::to_approx)
                .collect::<Vec<_>>();
            let reconstruction_matches = approx_lists_match(
                &reconstructed_coefficients,
                &source_coefficients,
                COEFFICIENT_TOLERANCE,
            );
            let degree = case.coefficients.len().saturating_sub(1);
            let expected_root_sum = ApproxComplex::zero().sub(source_coefficients[1].div(source_coefficients[0]));
            let expected_root_product = {
                let sign = if degree % 2 == 0 { 1.0 } else { -1.0 };
                source_coefficients[degree]
                    .div(source_coefficients[0])
                    .mul(ApproxComplex::new(sign, 0.0))
            };
            let actual_root_sum = sum_complex(&calculated_roots);
            let actual_root_product = product_complex(&calculated_roots);
            let degree_matches_root_count = calculated_roots.len() == degree;
            let vieta_sum_matches = actual_root_sum.distance(expected_root_sum) <= COEFFICIENT_TOLERANCE;
            let vieta_constant_matches = actual_root_product.distance(expected_root_product) <= COEFFICIENT_TOLERANCE;

            PolynomialCaseReport {
                case,
                calculated_roots,
                reconstructed_coefficients,
                residuals,
                roots_are_valid,
                reconstruction_matches,
                degree_matches_root_count,
                vieta_sum_matches,
                vieta_constant_matches,
            }
        })
        .collect::<Vec<_>>();

    let all_examples_valid = cases
        .iter()
        .all(|example| {
            example.roots_are_valid
                && example.reconstruction_matches
                && example.degree_matches_root_count
                && example.vieta_sum_matches
                && example.vieta_constant_matches
        });

    PolynomialReport {
        cases,
        all_examples_valid,
    }
}

fn source_cases() -> Vec<PolynomialCase> {
    vec![
        PolynomialCase {
            label: "real quartic",
            coefficients: vec![
                ExactComplex::new(1, 0),
                ExactComplex::new(-10, 0),
                ExactComplex::new(35, 0),
                ExactComplex::new(-50, 0),
                ExactComplex::new(24, 0),
            ],
        },
        PolynomialCase {
            label: "complex quartic",
            coefficients: vec![
                ExactComplex::new(1, 0),
                ExactComplex::new(-9, -5),
                ExactComplex::new(14, 33),
                ExactComplex::new(24, -44),
                ExactComplex::new(-26, 0),
            ],
        },
    ]
}

fn solve_roots(coefficients: &[ExactComplex]) -> Vec<ApproxComplex> {
    let degree = coefficients.len().saturating_sub(1);
    if degree == 0 {
        return Vec::new();
    }

    let lead = coefficients[0].to_approx();
    let monic = coefficients
        .iter()
        .copied()
        .map(ExactComplex::to_approx)
        .map(|coefficient| coefficient.div(lead))
        .collect::<Vec<_>>();

    let radius = 1.0
        + monic
            .iter()
            .skip(1)
            .map(|coefficient| coefficient.abs())
            .fold(0.0_f64, f64::max);
    let seed = ApproxComplex::new(0.4, 0.9);
    let mut roots = (0..degree)
        .map(|index| seed.powu(index).mul(ApproxComplex::new(radius, 0.0)))
        .collect::<Vec<_>>();

    for _ in 0..MAX_ITERATIONS {
        let mut max_delta: f64 = 0.0;

        for index in 0..degree {
            let root = roots[index];
            let mut denominator = ApproxComplex::one();
            for (other_index, other_root) in roots.iter().copied().enumerate() {
                if other_index != index {
                    denominator = denominator.mul(root.sub(other_root));
                }
            }

            if denominator.almost_zero(1e-18) {
                denominator = denominator.add(ApproxComplex::new(1e-12, 1e-12));
            }

            let delta = evaluate_monic_polynomial(&monic, root).div(denominator);
            roots[index] = root.sub(delta);
            max_delta = max_delta.max(delta.abs());
        }

        if max_delta < ROOT_TOLERANCE {
            break;
        }
    }

    roots
}

fn sum_complex(values: &[ApproxComplex]) -> ApproxComplex {
    values
        .iter()
        .copied()
        .fold(ApproxComplex::zero(), |acc, value| acc.add(value))
}

fn product_complex(values: &[ApproxComplex]) -> ApproxComplex {
    values
        .iter()
        .copied()
        .fold(ApproxComplex::one(), |acc, value| acc.mul(value))
}

fn polynomial_from_roots(roots: &[ApproxComplex]) -> Vec<ApproxComplex> {
    let mut coefficients = vec![ApproxComplex::one()];

    for root in roots {
        let factor = [ApproxComplex::one(), ApproxComplex::zero().sub(*root)];
        coefficients = multiply_polynomials(&coefficients, &factor);
    }

    coefficients
}

fn multiply_polynomials(left: &[ApproxComplex], right: &[ApproxComplex]) -> Vec<ApproxComplex> {
    let mut out = vec![ApproxComplex::zero(); left.len() + right.len() - 1];

    for (left_index, left_value) in left.iter().copied().enumerate() {
        for (right_index, right_value) in right.iter().copied().enumerate() {
            let index = left_index + right_index;
            out[index] = out[index].add(left_value.mul(right_value));
        }
    }

    out
}

fn evaluate_polynomial(coefficients: &[ExactComplex], x: ApproxComplex) -> ApproxComplex {
    coefficients
        .iter()
        .copied()
        .map(ExactComplex::to_approx)
        .fold(ApproxComplex::zero(), |acc, coefficient| acc.mul(x).add(coefficient))
}

fn evaluate_monic_polynomial(coefficients: &[ApproxComplex], x: ApproxComplex) -> ApproxComplex {
    coefficients
        .iter()
        .copied()
        .fold(ApproxComplex::zero(), |acc, coefficient| acc.mul(x).add(coefficient))
}

fn approx_lists_match(left: &[ApproxComplex], right: &[ApproxComplex], tolerance: f64) -> bool {
    left.len() == right.len()
        && left
            .iter()
            .copied()
            .zip(right.iter().copied())
            .all(|(lhs, rhs)| lhs.distance(rhs) <= tolerance)
}

fn sort_roots_for_display(roots: &mut [ApproxComplex]) {
    roots.sort_by(|left, right| compare_roots(*left, *right));
}

fn compare_roots(left: ApproxComplex, right: ApproxComplex) -> Ordering {
    let left = left.rounded_if_close(1e-8);
    let right = right.rounded_if_close(1e-8);
    let left_real = left.im.abs() < 1e-8;
    let right_real = right.im.abs() < 1e-8;

    match (left_real, right_real) {
        (true, true) => right.re.partial_cmp(&left.re).unwrap_or(Ordering::Equal),
        (true, false) => Ordering::Less,
        (false, true) => Ordering::Greater,
        (false, false) => right
            .im
            .partial_cmp(&left.im)
            .unwrap_or(Ordering::Equal)
            .then_with(|| right.re.partial_cmp(&left.re).unwrap_or(Ordering::Equal)),
    }
}

fn format_exact_complex_list(values: &[ExactComplex]) -> String {
    let body = values
        .iter()
        .map(|value| format!("[{}, {}]", value.re, value.im))
        .collect::<Vec<_>>()
        .join(", ");
    format!("[{body}]")
}

fn format_approx_complex_list(values: &[ApproxComplex]) -> String {
    let body = values
        .iter()
        .map(|value| {
            let snapped = value.rounded_if_close(1e-8);
            format!("[{}, {}]", format_scalar(snapped.re), format_scalar(snapped.im))
        })
        .collect::<Vec<_>>()
        .join(", ");
    format!("[{body}]")
}

fn format_root_list(values: &[ApproxComplex]) -> String {
    values
        .iter()
        .map(ToString::to_string)
        .collect::<Vec<_>>()
        .join(", ")
}

fn format_scalar(value: f64) -> String {
    let snapped = round_if_close(value, 1e-8);
    if (snapped - snapped.round()).abs() < 1e-8 {
        format!("{:.0}", snapped)
    } else {
        let rendered = format!("{snapped:.12}");
        rendered.trim_end_matches('0').trim_end_matches('.').to_string()
    }
}

fn round_if_close(value: f64, tolerance: f64) -> f64 {
    if value.abs() < tolerance {
        0.0
    } else {
        let rounded = value.round();
        if (value - rounded).abs() < tolerance {
            rounded
        } else {
            value
        }
    }
}

fn yes_no(value: bool) -> &'static str {
    if value { "yes" } else { "no" }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn expected_roots() -> Vec<Vec<ApproxComplex>> {
        vec![
            vec![
                ApproxComplex::new(4.0, 0.0),
                ApproxComplex::new(3.0, 0.0),
                ApproxComplex::new(2.0, 0.0),
                ApproxComplex::new(1.0, 0.0),
            ],
            vec![
                ApproxComplex::new(3.0, 2.0),
                ApproxComplex::new(5.0, 1.0),
                ApproxComplex::new(0.0, 1.0),
                ApproxComplex::new(1.0, 1.0),
            ],
        ]
    }

    fn assert_same_root_set(actual: &[ApproxComplex], expected: &[ApproxComplex]) {
        assert_eq!(actual.len(), expected.len());

        let mut remaining = actual.to_vec();
        for want in expected {
            let position = remaining
                .iter()
                .position(|candidate| candidate.distance(*want) <= 1e-6)
                .expect("missing expected root");
            remaining.remove(position);
        }

        assert!(remaining.is_empty());
    }

    #[test]
    fn calculates_the_expected_roots_from_the_source_coefficients() {
        for (source_case, expected) in source_cases().into_iter().zip(expected_roots()) {
            let roots = solve_roots(&source_case.coefficients);
            assert_same_root_set(&roots, &expected);
        }
    }

    #[test]
    fn reconstructs_the_source_coefficients_from_the_calculated_roots() {
        for source_case in source_cases() {
            let roots = solve_roots(&source_case.coefficients);
            let reconstructed = polynomial_from_roots(&roots);
            let expected = source_case
                .coefficients
                .iter()
                .copied()
                .map(ExactComplex::to_approx)
                .collect::<Vec<_>>();
            assert!(approx_lists_match(
                &reconstructed,
                &expected,
                COEFFICIENT_TOLERANCE,
            ));
        }
    }

    #[test]
    fn every_calculated_root_satisfies_each_source_polynomial() {
        for source_case in source_cases() {
            for root in solve_roots(&source_case.coefficients) {
                assert!(evaluate_polynomial(&source_case.coefficients, root).almost_zero(ROOT_TOLERANCE));
            }
        }
    }

    #[test]
    fn polynomial_report_matches_the_expected_examples() {
        let report = evaluate();

        assert_eq!(report.cases.len(), 2);
        assert!(report.all_examples_valid);

        assert_eq!(report.cases[0].case.label, "real quartic");
        assert_same_root_set(
            &report.cases[0].calculated_roots,
            &expected_roots()[0],
        );
        assert!(report.cases[0].roots_are_valid);
        assert!(report.cases[0].reconstruction_matches);
        assert!(report.cases[0].degree_matches_root_count);
        assert!(report.cases[0].vieta_sum_matches);
        assert!(report.cases[0].vieta_constant_matches);

        assert_eq!(report.cases[1].case.label, "complex quartic");
        assert_same_root_set(
            &report.cases[1].calculated_roots,
            &expected_roots()[1],
        );
        assert!(report.cases[1].roots_are_valid);
        assert!(report.cases[1].reconstruction_matches);
        assert!(report.cases[1].degree_matches_root_count);
        assert!(report.cases[1].vieta_sum_matches);
        assert!(report.cases[1].vieta_constant_matches);
    }

    #[test]
    fn formats_readable_roots() {
        assert_eq!(format_root_list(&[ApproxComplex::new(4.0, 0.0)]), "4");
        assert_eq!(format_root_list(&[ApproxComplex::new(0.0, 1.0)]), "i");
        assert_eq!(format_root_list(&[ApproxComplex::new(1.0, 1.0)]), "1 + i");
        assert_eq!(format_root_list(&[ApproxComplex::new(3.0, 2.0)]), "3 + 2i");
    }
}
