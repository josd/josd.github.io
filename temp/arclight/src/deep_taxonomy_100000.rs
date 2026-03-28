use std::collections::VecDeque;
use std::io;

use crate::report::{CaseReport, ReportItem};

const MAX_N: usize = 100_000;
const RULE_COUNT: usize = 100_002;
const EXPECTED_TYPE_FACTS: usize = 3 * MAX_N + 2;
const EXPECTED_DERIVED_FACTS: usize = EXPECTED_TYPE_FACTS + 1;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum Entity {
    Ind,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum Class {
    N(usize),
    I(usize),
    J(usize),
    A2,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum DerivedFact {
    HasClass(Entity, Class),
}

#[derive(Debug, Clone, Copy)]
struct RunResult {
    seed_facts: usize,
    rules: usize,
    derived_facts: usize,
    type_facts: usize,
    goal_reached: bool,
    n_max_seen: bool,
    a2_seen: bool,
    counts_match_closed_form: bool,
}

pub fn report() -> io::Result<CaseReport> {
    let result = run();

    if !result.goal_reached
        || result.rules != RULE_COUNT
        || !result.n_max_seen
        || !result.a2_seen
        || !result.counts_match_closed_form
    {
        return Err(io::Error::new(
            io::ErrorKind::InvalidData,
            "deep-taxonomy-100000 check failed: goal, boundary, or closed-form counts did not match",
        ));
    }

    Ok(CaseReport::new("deep-taxonomy-100000")
        .with_answer(vec![
            ReportItem::text(
                "The deep taxonomy chain reaches the goal from the seed fact after deriving the full class ladder up to N(100000).",
            ),
            ReportItem::field("case", "deep-taxonomy-100000"),
            ReportItem::field("goal reached", if result.goal_reached { "yes" } else { "no" }),
        ])
        .with_reason_why(vec![
            ReportItem::text(
                "Starting from Ind : N(0), each N(i) derives N(i+1), I(i+1), and J(i+1); N(100000) then derives A2, which derives the goal.",
            ),
            ReportItem::field("seed facts", result.seed_facts.to_string()),
            ReportItem::field("rules", result.rules.to_string()),
            ReportItem::field("derived facts", result.derived_facts.to_string()),
            ReportItem::field("type facts", result.type_facts.to_string()),
        ])
        .with_check(vec![
            ReportItem::field("rule count ok", if result.rules == RULE_COUNT { "yes" } else { "no" }),
            ReportItem::field("N(100000) seen", if result.n_max_seen { "yes" } else { "no" }),
            ReportItem::field("A2 derived", if result.a2_seen { "yes" } else { "no" }),
            ReportItem::field(
                "count formula ok",
                if result.counts_match_closed_form { "yes" } else { "no" },
            ),
        ]))
}

pub fn run_and_print() -> io::Result<()> {
    let result = run();

    println!("=== Answer ===");
    println!(
        "The deep taxonomy chain reaches the goal from the seed fact after deriving the full class ladder up to N(100000)."
    );
    println!("case          : deep-taxonomy-100000");
    println!("goal reached  : {}", if result.goal_reached { "yes" } else { "no" });
    println!();
    println!("=== Reason Why ===");
    println!(
        "Starting from Ind : N(0), each N(i) derives N(i+1), I(i+1), and J(i+1); N(100000) then derives A2, which derives the goal."
    );
    println!("seed facts    : {}", result.seed_facts);
    println!("rules         : {}", result.rules);
    println!("derived facts : {}", result.derived_facts);
    println!("type facts    : {}", result.type_facts);
    println!();
    println!("=== Check ===");
    println!("rule count ok : {}", if result.rules == RULE_COUNT { "yes" } else { "no" });
    println!("N(100000) seen: {}", if result.n_max_seen { "yes" } else { "no" });
    println!("A2 derived    : {}", if result.a2_seen { "yes" } else { "no" });
    println!(
        "count formula ok: {}",
        if result.counts_match_closed_form { "yes" } else { "no" }
    );

    if !result.goal_reached
        || result.rules != RULE_COUNT
        || !result.n_max_seen
        || !result.a2_seen
        || !result.counts_match_closed_form
    {
        return Err(io::Error::new(
            io::ErrorKind::InvalidData,
            "deep-taxonomy-100000 check failed: goal, boundary, or closed-form counts did not match",
        ));
    }

    Ok(())
}

fn run() -> RunResult {
    let mut agenda = VecDeque::with_capacity(MAX_N + 2);

    let mut n_seen = vec![false; MAX_N + 1];
    let mut i_seen = vec![false; MAX_N + 1];
    let mut j_seen = vec![false; MAX_N + 1];
    let mut a2_seen = false;
    let mut goal_seen = false;

    enqueue_class(Class::N(0), &mut agenda, &mut n_seen, &mut i_seen, &mut j_seen, &mut a2_seen);

    while let Some(fact) = agenda.pop_front() {
        match fact {
            DerivedFact::HasClass(Entity::Ind, Class::N(index)) if index < MAX_N => {
                let next = index + 1;
                enqueue_class(Class::N(next), &mut agenda, &mut n_seen, &mut i_seen, &mut j_seen, &mut a2_seen);
                enqueue_class(Class::I(next), &mut agenda, &mut n_seen, &mut i_seen, &mut j_seen, &mut a2_seen);
                enqueue_class(Class::J(next), &mut agenda, &mut n_seen, &mut i_seen, &mut j_seen, &mut a2_seen);
            }
            DerivedFact::HasClass(Entity::Ind, Class::N(index)) if index == MAX_N => {
                enqueue_class(Class::A2, &mut agenda, &mut n_seen, &mut i_seen, &mut j_seen, &mut a2_seen);
            }
            DerivedFact::HasClass(Entity::Ind, Class::A2) => {
                goal_seen = true;
            }
            DerivedFact::HasClass(Entity::Ind, Class::I(_))
            | DerivedFact::HasClass(Entity::Ind, Class::J(_)) => {}
            DerivedFact::HasClass(Entity::Ind, Class::N(_)) => {}
        }
    }

    let type_facts = n_seen.iter().filter(|seen| **seen).count()
        + i_seen.iter().skip(1).filter(|seen| **seen).count()
        + j_seen.iter().skip(1).filter(|seen| **seen).count()
        + usize::from(a2_seen);

    let derived_facts = type_facts + usize::from(goal_seen);

    RunResult {
        seed_facts: 1,
        rules: RULE_COUNT,
        derived_facts,
        type_facts,
        goal_reached: goal_seen,
        n_max_seen: n_seen[MAX_N],
        a2_seen,
        counts_match_closed_form: type_facts == EXPECTED_TYPE_FACTS
            && derived_facts == EXPECTED_DERIVED_FACTS,
    }
}

fn enqueue_class(
    class: Class,
    agenda: &mut VecDeque<DerivedFact>,
    n_seen: &mut [bool],
    i_seen: &mut [bool],
    j_seen: &mut [bool],
    a2_seen: &mut bool,
) {
    let inserted = match class {
        Class::N(index) => insert_flag(&mut n_seen[index]),
        Class::I(index) => insert_flag(&mut i_seen[index]),
        Class::J(index) => insert_flag(&mut j_seen[index]),
        Class::A2 => insert_flag(a2_seen),
    };

    if inserted {
        agenda.push_back(DerivedFact::HasClass(Entity::Ind, class));
    }
}

fn insert_flag(slot: &mut bool) -> bool {
    if *slot {
        false
    } else {
        *slot = true;
        true
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn reaches_goal_and_matches_closed_form_counts() {
        let result = run();

        assert!(result.goal_reached);
        assert!(result.n_max_seen);
        assert!(result.a2_seen);
        assert_eq!(result.rules, RULE_COUNT);
        assert_eq!(result.type_facts, EXPECTED_TYPE_FACTS);
        assert_eq!(result.derived_facts, EXPECTED_DERIVED_FACTS);
        assert!(result.counts_match_closed_form);
    }
}
