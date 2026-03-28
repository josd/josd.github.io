use std::collections::{HashSet, VecDeque};
use std::fmt;
use std::io;

use crate::report::{CaseReport, ReportItem};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, PartialOrd, Ord)]
enum City {
    Gent,
    Brugge,
    Kortrijk,
    Oostende,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, PartialOrd, Ord)]
enum Stage {
    Drive,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, PartialOrd, Ord)]
enum Action {
    DriveGentBrugge,
    DriveGentKortrijk,
    DriveKortrijkBrugge,
    DriveBruggeOostende,
}

impl Action {
    fn stage(self) -> Stage {
        match self {
            Action::DriveGentBrugge
            | Action::DriveGentKortrijk
            | Action::DriveKortrijkBrugge
            | Action::DriveBruggeOostende => Stage::Drive,
        }
    }
}

impl fmt::Display for Action {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let name = match self {
            Action::DriveGentBrugge => "drive_gent_brugge",
            Action::DriveGentKortrijk => "drive_gent_kortrijk",
            Action::DriveKortrijkBrugge => "drive_kortrijk_brugge",
            Action::DriveBruggeOostende => "drive_brugge_oostende",
        };
        write!(f, "{name}")
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
struct Description {
    from: City,
    to: City,
    action: Action,
    duration_seconds: u32,
    cost_milli: u32,
    belief_ppm: u32,
    comfort_ppm: u32,
}

#[derive(Debug, Clone, Copy)]
struct Constraints {
    max_duration_seconds: u32,
    max_cost_milli: u32,
    min_belief_ppm: u32,
    min_comfort_ppm: u32,
    max_stages: usize,
}

#[derive(Debug, Clone)]
struct Problem {
    descriptions: Vec<Description>,
    start: City,
    goal: City,
    constraints: Constraints,
}

#[derive(Debug, Clone, PartialEq, Eq, Hash)]
struct Route {
    from: City,
    to: City,
    actions: Vec<Action>,
    duration_seconds: u32,
    cost_milli: u32,
    belief_ppm: u32,
    comfort_ppm: u32,
}

impl Route {
    fn stage_count(&self) -> usize {
        let mut previous = None;
        let mut count = 0;

        for action in &self.actions {
            let stage = action.stage();
            if previous != Some(stage) {
                count += 1;
                previous = Some(stage);
            }
        }

        count
    }

    fn satisfies(&self, constraints: &Constraints) -> bool {
        self.duration_seconds <= constraints.max_duration_seconds
            && self.cost_milli <= constraints.max_cost_milli
            && self.belief_ppm >= constraints.min_belief_ppm
            && self.comfort_ppm >= constraints.min_comfort_ppm
            && self.stage_count() <= constraints.max_stages
    }
}

pub fn report() -> io::Result<CaseReport> {
    let problem = problem();
    let goal_routes = infer_goal_routes(&problem);
    let total_routes = goal_routes.len();
    let all_routes_satisfy_constraints = goal_routes
        .iter()
        .all(|route| route.satisfies(&problem.constraints));
    let routes_have_correct_endpoints = goal_routes
        .iter()
        .all(|route| route.from == problem.start && route.to == problem.goal);
    let route_metrics_recomputed = goal_routes
        .iter()
        .all(|route| route_matches_descriptions(route, &problem.descriptions));
    let expected_route_count = total_routes == 2;

    if goal_routes.is_empty()
        || !all_routes_satisfy_constraints
        || !routes_have_correct_endpoints
        || !route_metrics_recomputed
        || !expected_route_count
    {
        return Err(io::Error::new(
            io::ErrorKind::InvalidData,
            "gps check failed: a route constraint, endpoint, metric, or count check failed",
        ));
    }

    let mut reason = vec![
        ReportItem::text(
            "Routes are built compositionally from direct descriptions, with duration and cost added and belief and comfort combined multiplicatively.",
        ),
    ];
    for (index, route) in goal_routes.iter().enumerate() {
        reason.extend(route_report_items(index + 1, route, &problem.constraints));
    }

    Ok(CaseReport::new("gps")
        .with_answer(vec![
            ReportItem::text(
                "The GPS case finds all goal routes from Gent to Oostende that satisfy the route constraints.",
            ),
            ReportItem::field("case", "gps"),
            ReportItem::field("routes", total_routes.to_string()),
        ])
        .with_reason_why(reason)
        .with_check(vec![
            ReportItem::field(
                "all routes satisfy constraints",
                if all_routes_satisfy_constraints { "yes" } else { "no" },
            ),
            ReportItem::field(
                "all routes hit goal endpoints",
                if routes_have_correct_endpoints { "yes" } else { "no" },
            ),
            ReportItem::field(
                "metrics recompute from steps",
                if route_metrics_recomputed { "yes" } else { "no" },
            ),
            ReportItem::field(
                "expected route count (= 2)",
                if expected_route_count { "yes" } else { "no" },
            ),
        ]))
}

pub fn run_and_print() -> io::Result<()> {
    let problem = problem();
    let goal_routes = infer_goal_routes(&problem);
    let total_routes = goal_routes.len();
    let all_routes_satisfy_constraints = goal_routes
        .iter()
        .all(|route| route.satisfies(&problem.constraints));
    let routes_have_correct_endpoints = goal_routes
        .iter()
        .all(|route| route.from == problem.start && route.to == problem.goal);
    let route_metrics_recomputed = goal_routes
        .iter()
        .all(|route| route_matches_descriptions(route, &problem.descriptions));
    let expected_route_count = total_routes == 2;

    println!("=== Answer ===");
    println!(
        "The GPS case finds all goal routes from Gent to Oostende that satisfy the route constraints."
    );
    println!("case      : gps");
    println!("routes    : {}", total_routes);
    println!();
    println!("=== Reason Why ===");
    println!(
        "Routes are built compositionally from direct descriptions, with duration and cost added and belief and comfort combined multiplicatively."
    );

    for (index, route) in goal_routes.iter().enumerate() {
        print_route(index + 1, route, &problem.constraints);
        if index + 1 != total_routes {
            println!();
        }
    }

    println!();
    println!("=== Check ===");
    println!(
        "all routes satisfy constraints : {}",
        if all_routes_satisfy_constraints { "yes" } else { "no" }
    );
    println!(
        "all routes hit goal endpoints  : {}",
        if routes_have_correct_endpoints { "yes" } else { "no" }
    );
    println!(
        "metrics recompute from steps   : {}",
        if route_metrics_recomputed { "yes" } else { "no" }
    );
    println!(
        "expected route count (= 2)     : {}",
        if expected_route_count { "yes" } else { "no" }
    );

    if goal_routes.is_empty()
        || !all_routes_satisfy_constraints
        || !routes_have_correct_endpoints
        || !route_metrics_recomputed
        || !expected_route_count
    {
        return Err(io::Error::new(
            io::ErrorKind::InvalidData,
            "gps check failed: a route constraint, endpoint, metric, or count check failed",
        ));
    }

    Ok(())
}

fn problem() -> Problem {
    Problem {
        descriptions: vec![
            Description {
                from: City::Gent,
                to: City::Brugge,
                action: Action::DriveGentBrugge,
                duration_seconds: 1500,
                cost_milli: 6,
                belief_ppm: 960_000,
                comfort_ppm: 990_000,
            },
            Description {
                from: City::Gent,
                to: City::Kortrijk,
                action: Action::DriveGentKortrijk,
                duration_seconds: 1600,
                cost_milli: 7,
                belief_ppm: 960_000,
                comfort_ppm: 990_000,
            },
            Description {
                from: City::Kortrijk,
                to: City::Brugge,
                action: Action::DriveKortrijkBrugge,
                duration_seconds: 1600,
                cost_milli: 7,
                belief_ppm: 960_000,
                comfort_ppm: 990_000,
            },
            Description {
                from: City::Brugge,
                to: City::Oostende,
                action: Action::DriveBruggeOostende,
                duration_seconds: 900,
                cost_milli: 4,
                belief_ppm: 980_000,
                comfort_ppm: 1_000_000,
            },
        ],
        start: City::Gent,
        goal: City::Oostende,
        constraints: Constraints {
            max_duration_seconds: 5_000,
            max_cost_milli: 5_000,
            min_belief_ppm: 200_000,
            min_comfort_ppm: 400_000,
            max_stages: 1,
        },
    }
}

fn infer_goal_routes(problem: &Problem) -> Vec<Route> {
    let mut known = HashSet::new();
    let mut agenda = VecDeque::new();

    for description in &problem.descriptions {
        let route = Route {
            from: description.from,
            to: description.to,
            actions: vec![description.action],
            duration_seconds: description.duration_seconds,
            cost_milli: description.cost_milli,
            belief_ppm: description.belief_ppm,
            comfort_ppm: description.comfort_ppm,
        };

        if known.insert(route.clone()) {
            agenda.push_back(route);
        }
    }

    while let Some(rest) = agenda.pop_front() {
        for description in &problem.descriptions {
            if description.to == rest.from {
                let mut actions = Vec::with_capacity(rest.actions.len() + 1);
                actions.push(description.action);
                actions.extend(rest.actions.iter().copied());

                let route = Route {
                    from: description.from,
                    to: rest.to,
                    actions,
                    duration_seconds: description.duration_seconds + rest.duration_seconds,
                    cost_milli: description.cost_milli + rest.cost_milli,
                    belief_ppm: multiply_ppm(description.belief_ppm, rest.belief_ppm),
                    comfort_ppm: multiply_ppm(description.comfort_ppm, rest.comfort_ppm),
                };

                if known.insert(route.clone()) {
                    agenda.push_back(route);
                }
            }
        }
    }

    let mut routes: Vec<Route> = known
        .into_iter()
        .filter(|route| route.from == problem.start && route.to == problem.goal)
        .filter(|route| route.satisfies(&problem.constraints))
        .collect();

    routes.sort_by(|left, right| {
        left.actions
            .len()
            .cmp(&right.actions.len())
            .then_with(|| left.actions.cmp(&right.actions))
    });

    routes
}

fn route_matches_descriptions(route: &Route, descriptions: &[Description]) -> bool {
    let mut current = route.from;
    let mut duration_seconds = 0_u32;
    let mut cost_milli = 0_u32;
    let mut belief_ppm = 1_000_000_u32;
    let mut comfort_ppm = 1_000_000_u32;

    for action in &route.actions {
        let Some(description) = descriptions.iter().find(|description| {
            description.from == current && description.action == *action
        }) else {
            return false;
        };

        current = description.to;
        duration_seconds += description.duration_seconds;
        cost_milli += description.cost_milli;
        belief_ppm = multiply_ppm(belief_ppm, description.belief_ppm);
        comfort_ppm = multiply_ppm(comfort_ppm, description.comfort_ppm);
    }

    current == route.to
        && duration_seconds == route.duration_seconds
        && cost_milli == route.cost_milli
        && belief_ppm == route.belief_ppm
        && comfort_ppm == route.comfort_ppm
}

fn multiply_ppm(left: u32, right: u32) -> u32 {
    ((left as u64 * right as u64) / 1_000_000_u64) as u32
}

fn route_report_items(index: usize, route: &Route, constraints: &Constraints) -> Vec<ReportItem> {
    let mut items = vec![
        ReportItem::text(format!("Route #{index}")),
        ReportItem::field("Steps", route.actions.len().to_string()),
        ReportItem::field(
            "Duration",
            format!("{} s (≤ {})", route.duration_seconds, constraints.max_duration_seconds),
        ),
        ReportItem::field(
            "Cost",
            format!(
                "{} (≤ {})",
                format_decimal(route.cost_milli as u64, 1_000, 3),
                format_decimal(constraints.max_cost_milli as u64, 1_000, 1)
            ),
        ),
        ReportItem::field(
            "Belief",
            format!(
                "{} (≥ {})",
                format_decimal(route.belief_ppm as u64, 1_000_000, 3),
                format_decimal(constraints.min_belief_ppm as u64, 1_000_000, 1)
            ),
        ),
        ReportItem::field(
            "Comfort",
            format!(
                "{} (≥ {})",
                format_decimal(route.comfort_ppm as u64, 1_000_000, 3),
                format_decimal(constraints.min_comfort_ppm as u64, 1_000_000, 1)
            ),
        ),
        ReportItem::field("Stages", format!("{} (≤ {})", route.stage_count(), constraints.max_stages)),
    ];
    for (step_index, action) in route.actions.iter().enumerate() {
        items.push(ReportItem::text(format!("  {}. {}", step_index + 1, action)));
    }
    items
}

fn print_route(index: usize, route: &Route, constraints: &Constraints) {
    println!("Route #{index}");
    println!(" Steps    : {}", route.actions.len());
    println!(
        " Duration : {} s (≤ {})",
        route.duration_seconds,
        constraints.max_duration_seconds
    );
    println!(
        " Cost     : {} (≤ {})",
        format_decimal(route.cost_milli as u64, 1_000, 3),
        format_decimal(constraints.max_cost_milli as u64, 1_000, 1)
    );
    println!(
        " Belief   : {} (≥ {})",
        format_decimal(route.belief_ppm as u64, 1_000_000, 3),
        format_decimal(constraints.min_belief_ppm as u64, 1_000_000, 1)
    );
    println!(
        " Comfort  : {} (≥ {})",
        format_decimal(route.comfort_ppm as u64, 1_000_000, 3),
        format_decimal(constraints.min_comfort_ppm as u64, 1_000_000, 1)
    );
    println!(
        " Stages   : {} (≤ {})",
        route.stage_count(),
        constraints.max_stages
    );

    for (step_index, action) in route.actions.iter().enumerate() {
        println!("   {}. {}", step_index + 1, action);
    }
}

fn format_decimal(value: u64, scale: u64, digits: usize) -> String {
    let fractional_scale = 10_u64.pow(digits as u32);
    let scaled = value * fractional_scale;
    let rounded = (scaled + (scale / 2)) / scale;
    let mut whole = rounded / fractional_scale;
    let mut fractional = rounded % fractional_scale;

    if fractional == fractional_scale {
        whole += 1;
        fractional = 0;
    }

    format!("{whole}.{:0digits$}", fractional, digits = digits)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn finds_the_two_goal_routes() {
        let routes = infer_goal_routes(&problem());

        assert_eq!(routes.len(), 2);
        assert_eq!(routes[0].actions, vec![Action::DriveGentBrugge, Action::DriveBruggeOostende]);
        assert_eq!(routes[1].actions, vec![Action::DriveGentKortrijk, Action::DriveKortrijkBrugge, Action::DriveBruggeOostende]);
    }

    #[test]
    fn route_metrics_can_be_recomputed_from_the_selected_steps() {
        let problem = problem();
        for route in infer_goal_routes(&problem) {
            assert!(route_matches_descriptions(&route, &problem.descriptions));
        }
    }

    #[test]
    fn ppm_multiplication_matches_the_route_probability_model() {
        assert_eq!(multiply_ppm(960_000, 980_000), 940_800);
        assert_eq!(multiply_ppm(960_000, 960_000), 921_600);
    }
}
