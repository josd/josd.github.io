use std::fmt;
use std::io;

use crate::report::{CaseReport, ReportItem};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, PartialOrd, Ord)]
enum PairMeasurement {
    Input1,
    #[cfg(test)]
    Disturbance2,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, PartialOrd, Ord)]
enum BoolMeasurement {
    Input2,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, PartialOrd, Ord)]
enum ScalarMeasurement {
    #[cfg(test)]
    Input3,
    Disturbance1,
    Output2,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, PartialOrd, Ord)]
enum Observation {
    #[cfg(test)]
    State1,
    #[cfg(test)]
    State2,
    State3,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, PartialOrd, Ord)]
enum Target {
    Output2,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, PartialOrd, Ord)]
enum Actuator {
    Actuator1,
    Actuator2,
}

impl fmt::Display for Actuator {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let name = match self {
            Actuator::Actuator1 => "actuator1",
            Actuator::Actuator2 => "actuator2",
        };
        write!(f, "{name}")
    }
}

#[derive(Debug, Clone, Copy, PartialEq)]
struct ControlOutput {
    actuator: Actuator,
    value: f64,
}

#[derive(Debug, Clone)]
struct ControlSystemReport {
    measurement10_input1: f64,
    outputs: Vec<ControlOutput>,
    query_satisfied: bool,
    has_unique_actuators: bool,
    actuator1_matches_direct_formula: bool,
    actuator2_matches_direct_formula: bool,
}

pub fn report() -> io::Result<CaseReport> {
    let report = evaluate();

    if !report.query_satisfied
        || report.outputs.len() != 2
        || !report.has_unique_actuators
        || !report.actuator1_matches_direct_formula
        || !report.actuator2_matches_direct_formula
    {
        return Err(io::Error::new(
            io::ErrorKind::InvalidData,
            "control-system check failed: an independent actuator validation did not hold",
        ));
    }

    let mut reason = vec![
        ReportItem::text(
            "The helper rule measurement10(input1) is derived first, then both control rules are evaluated from the available measurements, observations, and target.",
        ),
        ReportItem::field("measurement10(input1)", format!("{:.6}", report.measurement10_input1)),
    ];
    for output in &report.outputs {
        reason.push(ReportItem::field(output.actuator.to_string(), format!("{:.6}", output.value)));
    }

    Ok(CaseReport::new("control-system")
        .with_answer(vec![
            ReportItem::text(
                "The control query is satisfied: the source facts derive concrete outputs for actuator1 and actuator2.",
            ),
            ReportItem::field("case", "control-system"),
            ReportItem::field("controls found", report.outputs.len().to_string()),
            ReportItem::field("query satisfied", yes_no(report.query_satisfied)),
        ])
        .with_reason_why(reason)
        .with_check(vec![
            ReportItem::field("derived both controls", yes_no(report.outputs.len() == 2)),
            ReportItem::field("unique actuators", yes_no(report.has_unique_actuators)),
            ReportItem::field(
                "actuator1 formula ok",
                yes_no(report.actuator1_matches_direct_formula),
            ),
            ReportItem::field(
                "actuator2 formula ok",
                yes_no(report.actuator2_matches_direct_formula),
            ),
        ]))
}

pub fn run_and_print() -> io::Result<()> {
    let report = evaluate();

    println!("=== Answer ===");
    println!(
        "The control query is satisfied: the source facts derive concrete outputs for actuator1 and actuator2."
    );
    println!("case                 : control-system");
    println!("controls found       : {}", report.outputs.len());
    println!("query satisfied      : {}", yes_no(report.query_satisfied));
    println!();
    println!("=== Reason Why ===");
    println!(
        "The helper rule measurement10(input1) is derived first, then both control rules are evaluated from the available measurements, observations, and target."
    );
    println!("measurement10(input1): {:.6}", report.measurement10_input1);
    for output in &report.outputs {
        println!("{}            : {:.6}", output.actuator, output.value);
    }
    println!();
    println!("=== Check ===");
    println!("derived both controls: {}", yes_no(report.outputs.len() == 2));
    println!("unique actuators     : {}", yes_no(report.has_unique_actuators));
    println!(
        "actuator1 formula ok : {}",
        yes_no(report.actuator1_matches_direct_formula)
    );
    println!(
        "actuator2 formula ok : {}",
        yes_no(report.actuator2_matches_direct_formula)
    );

    if !report.query_satisfied
        || report.outputs.len() != 2
        || !report.has_unique_actuators
        || !report.actuator1_matches_direct_formula
        || !report.actuator2_matches_direct_formula
    {
        return Err(io::Error::new(
            io::ErrorKind::InvalidData,
            "control-system check failed: an independent actuator validation did not hold",
        ));
    }

    Ok(())
}

fn evaluate() -> ControlSystemReport {
    let measurement10_input1 = measurement10(PairMeasurement::Input1)
        .expect("measurement10(input1) should be derivable from measurement1(input1, [6, 11])");

    let mut outputs = Vec::with_capacity(2);

    if let (Some(true), Some(disturbance1)) = (
        measurement2(BoolMeasurement::Input2),
        measurement3(ScalarMeasurement::Disturbance1),
    ) {
        let c1 = measurement10_input1 * 19.6;
        let c2 = disturbance1.log10();
        let c = c1 - c2;
        outputs.push(ControlOutput {
            actuator: Actuator::Actuator1,
            value: c,
        });
    }

    if let (Some(state3), Some(output2), Some(target2)) = (
        observation3(Observation::State3),
        measurement4(ScalarMeasurement::Output2),
        target2(Target::Output2),
    ) {
        let error = target2 - output2;
        let differential_error = state3 - output2;
        let c1 = 5.8 * error;
        let nonlinear_factor = 7.3 / error;
        let c2 = nonlinear_factor * differential_error;
        let c = c1 + c2;
        outputs.push(ControlOutput {
            actuator: Actuator::Actuator2,
            value: c,
        });
    }

    let actuator1_expected = expected_actuator1_output();
    let actuator2_expected = expected_actuator2_output();

    ControlSystemReport {
        measurement10_input1,
        query_satisfied: !outputs.is_empty(),
        has_unique_actuators: output_for(&outputs, Actuator::Actuator1).is_some()
            && output_for(&outputs, Actuator::Actuator2).is_some()
            && outputs.iter().filter(|output| output.actuator == Actuator::Actuator1).count() == 1
            && outputs.iter().filter(|output| output.actuator == Actuator::Actuator2).count() == 1,
        actuator1_matches_direct_formula: output_for(&outputs, Actuator::Actuator1)
            .map(|output| approx_eq(output.value, actuator1_expected, 1e-9))
            .unwrap_or(false),
        actuator2_matches_direct_formula: output_for(&outputs, Actuator::Actuator2)
            .map(|output| approx_eq(output.value, actuator2_expected, 1e-9))
            .unwrap_or(false),
        outputs,
    }
}

fn output_for(outputs: &[ControlOutput], actuator: Actuator) -> Option<ControlOutput> {
    outputs.iter().copied().find(|output| output.actuator == actuator)
}

fn expected_actuator1_output() -> f64 {
    let helper = measurement10(PairMeasurement::Input1)
        .expect("measurement10(input1) should be available for actuator1 validation");
    let disturbance1 = measurement3(ScalarMeasurement::Disturbance1)
        .expect("disturbance1 should be available for actuator1 validation");

    helper * 19.6 - disturbance1.log10()
}

fn expected_actuator2_output() -> f64 {
    let state3 = observation3(Observation::State3)
        .expect("state3 should be available for actuator2 validation");
    let output2 = measurement4(ScalarMeasurement::Output2)
        .expect("output2 should be available for actuator2 validation");
    let target2 = target2(Target::Output2)
        .expect("target2 should be available for actuator2 validation");

    let error = target2 - output2;
    let differential_error = state3 - output2;
    5.8 * error + (7.3 / error) * differential_error
}

fn approx_eq(left: f64, right: f64, tolerance: f64) -> bool {
    (left - right).abs() <= tolerance
}

fn measurement1(name: PairMeasurement) -> Option<[f64; 2]> {
    match name {
        PairMeasurement::Input1 => Some([6.0, 11.0]),
        #[cfg(test)]
        PairMeasurement::Disturbance2 => Some([45.0, 39.0]),
    }
}

fn measurement2(name: BoolMeasurement) -> Option<bool> {
    match name {
        BoolMeasurement::Input2 => Some(true),
    }
}

fn measurement3(name: ScalarMeasurement) -> Option<f64> {
    match name {
        #[cfg(test)]
        ScalarMeasurement::Input3 => Some(56_967.0),
        ScalarMeasurement::Disturbance1 => Some(35_766.0),
        ScalarMeasurement::Output2 => None,
    }
}

fn measurement4(name: ScalarMeasurement) -> Option<f64> {
    match name {
        ScalarMeasurement::Output2 => Some(24.0),
        #[cfg(test)]
        ScalarMeasurement::Input3 | ScalarMeasurement::Disturbance1 => None,
        #[cfg(not(test))]
        ScalarMeasurement::Disturbance1 => None,
    }
}

#[cfg(test)]
fn observation1(name: Observation) -> Option<f64> {
    match name {
        Observation::State1 => Some(80.0),
        Observation::State2 | Observation::State3 => None,
    }
}

#[cfg(test)]
fn observation2(name: Observation) -> Option<bool> {
    match name {
        Observation::State2 => Some(false),
        Observation::State1 | Observation::State3 => None,
    }
}

fn observation3(name: Observation) -> Option<f64> {
    match name {
        Observation::State3 => Some(22.0),
        #[cfg(test)]
        Observation::State1 | Observation::State2 => None,
    }
}

fn target2(name: Target) -> Option<f64> {
    match name {
        Target::Output2 => Some(29.0),
    }
}

fn measurement10(name: PairMeasurement) -> Option<f64> {
    let [m1, m2] = measurement1(name)?;

    if m1 < m2 {
        let difference = m2 - m1;
        Some(difference.sqrt())
    } else {
        Some(m1)
    }
}

fn yes_no(value: bool) -> &'static str {
    if value { "yes" } else { "no" }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn assert_approx_eq(left: f64, right: f64) {
        let delta = (left - right).abs();
        assert!(
            delta <= 1e-9,
            "expected {left} to be within 1e-9 of {right}, delta was {delta}"
        );
    }

    #[test]
    fn measurement10_uses_the_square_root_branch_for_input1() {
        assert_approx_eq(measurement10(PairMeasurement::Input1).unwrap(), 5.0_f64.sqrt());
    }

    #[test]
    fn measurement10_uses_the_passthrough_branch_when_the_first_value_is_not_smaller() {
        assert_approx_eq(measurement10(PairMeasurement::Disturbance2).unwrap(), 45.0);
    }

    #[test]
    fn evaluates_both_control_rules_from_the_source_program() {
        let report = evaluate();

        assert!(report.query_satisfied);
        assert_eq!(report.outputs.len(), 2);
        assert_eq!(report.outputs[0].actuator, Actuator::Actuator1);
        assert_eq!(report.outputs[1].actuator, Actuator::Actuator2);
        assert_approx_eq(report.outputs[0].value, 5.0_f64.sqrt() * 19.6 - 35_766.0_f64.log10());
        assert_approx_eq(report.outputs[1].value, 26.08);
        assert!(report.has_unique_actuators);
        assert!(report.actuator1_matches_direct_formula);
        assert!(report.actuator2_matches_direct_formula);
    }

    #[test]
    fn preserves_the_other_seed_facts_from_the_source_input() {
        assert_eq!(measurement2(BoolMeasurement::Input2), Some(true));
        assert_eq!(measurement3(ScalarMeasurement::Input3), Some(56_967.0));
        assert_eq!(measurement4(ScalarMeasurement::Output2), Some(24.0));
        assert_eq!(observation1(Observation::State1), Some(80.0));
        assert_eq!(observation2(Observation::State2), Some(false));
        assert_eq!(target2(Target::Output2), Some(29.0));
    }
}
