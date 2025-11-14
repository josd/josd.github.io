# -*- coding: utf-8 -*-
"""
wstLogic-style State Transition Planning (Travel)
with COST *and* TIME using specialized Python code
--------------------------------------------------

We keep the *same modeling story* as the original file:

• States: a tiny 4-step timeline S0 → S1 → S2 → S3.
• Cities as *class names*: ex:At_Brussels, ex:At_Paris, etc.
  - holds1(C, S)  means “state S satisfies class-name C”.

• Actions as *names* (intensions):
    ex:Fly_Brussels_Paris, ex:Train_Brussels_Paris,
    ex:Fly_Paris_London, ex:Fly_Paris_Berlin, ex:Train_London_Berlin

  - holds2(A, S, S1) means “doing action-name A at S leads to S1”.

• Meta over action names:
    Pre(A, Cpre)   -- precondition class (must hold in FROM state)
    Add(A, Cadd)   -- effect class to add in TO state
    Cost(A, c)     -- cost of A, where c is a tiny natural "0".."9"
    Time(A, t)     -- time of A, likewise
    Forbidden(A)   -- policy tag, action is forbidden

We now implement everything with **specialized Python closures**:

    - A single pass to compute holds1 / holds2 along the S0..S3 chain
    - A small DP to compute PathCost(S0,S, c) and PathTime(S0,S, t)
      *ignoring Forbidden actions when building paths*
    - BestCost(S, c) and BestTime(S, t) as true minima per state

Questions
---------
Q1) Enumerate all plan edges holds2(A,S,S1).
Q2) Minimal COST to each state where At_Berlin holds.
Q3) Minimal TIME to each state where At_Berlin holds.
Q4) Example COST and TIME sets to S2.
Q5) Policy: does any transition use Fly_Paris_London (Forbidden)?

How to run
----------
    python wst_travel_planning.py

Printed sections
----------------
Model → Question → Answer → Reason why → Check (12 tests)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Set, Tuple


# ─────────────────────────────────────────────────────────────────────
# Names, states, cities, actions
# ─────────────────────────────────────────────────────────────────────

EX = "ex:"


def local(name: str) -> str:
    """Strip 'ex:' prefix for nicer printing."""
    return name.split(":", 1)[1] if ":" in name else name


# States (time steps)
S0, S1, S2, S3 = "S0", "S1", "S2", "S3"
STATES: Tuple[str, ...] = (S0, S1, S2, S3)

# Cities → each becomes a class name ex:At_City
CITIES: Tuple[str, ...] = ("Brussels", "Paris", "London", "Berlin")
At: Dict[str, str] = {city: EX + f"At_{city}" for city in CITIES}

# Action names (intensions)
Fly_BP = EX + "Fly_Brussels_Paris"
Train_BP = EX + "Train_Brussels_Paris"
Fly_PL = EX + "Fly_Paris_London"
Fly_PB = EX + "Fly_Paris_Berlin"
Train_LB = EX + "Train_London_Berlin"

# Policy tag
ForbiddenName = EX + "Forbidden"  # we keep only the concept; actual tag is a set

# Helper: tiny naturals as ints 0..9, but when printing we use strings "0".."9".
def sat_add(a: int, b: int) -> int:
    """Saturating addition on tiny naturals (0..9)."""
    s = a + b
    return s if s <= 9 else 9


# ─────────────────────────────────────────────────────────────────────
# Internal structures
# ─────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Action:
    name: str
    pre: str   # class name ex:At_Paris
    add: str   # class name ex:At_London
    cost: int  # 0..9
    time: int  # 0..9


@dataclass
class TravelModel:
    states: Tuple[str, ...]
    cities: Tuple[str, ...]
    at: Dict[str, str]

    actions: Dict[str, Action]
    forbidden: Set[str]
    next_map: Dict[str, str]

    # holds1(C,S) represented as: holds1[state] = {class_names}
    holds1: Dict[str, Set[str]]

    # holds2(A,S,S1) as a set of triples
    holds2: Set[Tuple[str, str, str]]

    # Path measures from S0:
    #   PathCost(S0,S,c) where c is an int in path_cost[S]
    #   PathTime(S0,S,t) where t is an int in path_time[S]
    path_cost: Dict[str, Set[int]]
    path_time: Dict[str, Set[int]]

    # Best minima per state (if reachable)
    best_cost: Dict[str, int]
    best_time: Dict[str, int]


# ─────────────────────────────────────────────────────────────────────
# Model construction
# ─────────────────────────────────────────────────────────────────────

def build_model() -> TravelModel:
    # Action schema
    actions: Dict[str, Action] = {
        Fly_BP: Action(Fly_BP, pre=At["Brussels"], add=At["Paris"], cost=1, time=1),
        Train_BP: Action(Train_BP, pre=At["Brussels"], add=At["Paris"], cost=2, time=2),
        Fly_PL: Action(Fly_PL, pre=At["Paris"], add=At["London"], cost=1, time=2),
        Fly_PB: Action(Fly_PB, pre=At["Paris"], add=At["Berlin"], cost=2, time=2),
        Train_LB: Action(Train_LB, pre=At["London"], add=At["Berlin"], cost=2, time=3),
    }

    # Policy: flying into London is forbidden
    forbidden: Set[str] = {Fly_PL}

    # Explicit successor chain
    next_map: Dict[str, str] = {S0: S1, S1: S2, S2: S3}

    # --- Step 1: compute holds1 and holds2 along the chain ---

    holds1: Dict[str, Set[str]] = {s: set() for s in STATES}
    holds2: Set[Tuple[str, str, str]] = set()

    # Initial condition: At_Brussels holds in S0
    holds1[S0].add(At["Brussels"])

    # We can process the chain topologically: S0→S1→S2→S3
    order = [S0, S1, S2]
    for s in order:
        s1 = next_map.get(s)
        if s1 is None:
            continue
        for act in actions.values():
            # Enabled if precondition holds in FROM state
            if act.pre in holds1[s]:
                # Transition holds2(A,S,S1)
                holds2.add((act.name, s, s1))
                # Effect: add-class holds in TO state
                holds1[s1].add(act.add)

    # --- Step 2: compute path costs and times (respecting policy) ---

    path_cost: Dict[str, Set[int]] = {s: set() for s in STATES}
    path_time: Dict[str, Set[int]] = {s: set() for s in STATES}

    path_cost[S0].add(0)
    path_time[S0].add(0)

    # For planning, we ignore forbidden actions when walking edges
    for s in order:
        s1 = next_map.get(s)
        if s1 is None:
            continue

        # All non-forbidden edges leaving s
        outgoing = [
            (a_name, s, s1)
            for (a_name, fr, to) in holds2
            if fr == s and to == s1 and a_name not in forbidden
        ]

        # Costs
        for c0 in path_cost[s]:
            for a_name, _, _ in outgoing:
                act = actions[a_name]
                c1 = sat_add(c0, act.cost)
                path_cost[s1].add(c1)

        # Times
        for t0 in path_time[s]:
            for a_name, _, _ in outgoing:
                act = actions[a_name]
                t1 = sat_add(t0, act.time)
                path_time[s1].add(t1)

    # --- Step 3: minima per state ---

    best_cost: Dict[str, int] = {}
    best_time: Dict[str, int] = {}

    for s in STATES:
        if path_cost[s]:
            best_cost[s] = min(path_cost[s])
        if path_time[s]:
            best_time[s] = min(path_time[s])

    return TravelModel(
        states=STATES,
        cities=CITIES,
        at=At,
        actions=actions,
        forbidden=forbidden,
        next_map=next_map,
        holds1=holds1,
        holds2=holds2,
        path_cost=path_cost,
        path_time=path_time,
        best_cost=best_cost,
        best_time=best_time,
    )


# ─────────────────────────────────────────────────────────────────────
# Query helpers (Q1–Q5)
# ─────────────────────────────────────────────────────────────────────

def q1_edges(m: TravelModel) -> List[Tuple[str, str, str]]:
    """Enumerate all plan edges holds2(A,S,S1)."""
    return sorted(m.holds2)


def q2_best_cost_berlin(m: TravelModel) -> List[Tuple[str, str]]:
    """Minimal COST to each state where At_Berlin holds."""
    berlin = m.at["Berlin"]
    res: List[Tuple[str, str]] = []
    for s in m.states:
        if berlin in m.holds1[s] and s in m.best_cost:
            res.append((s, str(m.best_cost[s])))
    return sorted(res)


def q3_best_time_berlin(m: TravelModel) -> List[Tuple[str, str]]:
    """Minimal TIME to each state where At_Berlin holds."""
    berlin = m.at["Berlin"]
    res: List[Tuple[str, str]] = []
    for s in m.states:
        if berlin in m.holds1[s] and s in m.best_time:
            res.append((s, str(m.best_time[s])))
    return sorted(res)


def q4_cost_time_S2(m: TravelModel) -> Tuple[List[str], List[str]]:
    """
    Example (COST, TIME) sets to S2.

    Note: as in the original logic encoding, PathCost and PathTime are computed
    independently; we just show the sets of values reachable at S2.
    """
    costs = sorted(str(c) for c in m.path_cost[S2])
    times = sorted(str(t) for t in m.path_time[S2])
    return costs, times


def q5_forbidden_transition_present(m: TravelModel) -> bool:
    """Check if the forbidden action Fly_Paris_London appears among transitions."""
    for a, s, t in m.holds2:
        if a == Fly_PL:
            return True
    return False


# ─────────────────────────────────────────────────────────────────────
# Presentation
# ─────────────────────────────────────────────────────────────────────

def print_model(m: TravelModel) -> None:
    print("Model")
    print("=====")
    print(f"States (time steps) = {list(m.states)}")
    print("Locations as classes: " + ", ".join(local(m.at[c]) for c in m.cities))
    print("\nFixed predicates (informal)")
    print("----------------------------")
    print("• holds1(C,S)  — class-name C holds in state S (implemented as a map state→classes)")
    print("• holds2(A,S,S1) — do action-name A from S to S1 (implemented as a set of triples)")
    print("• Pre/Add/Cost/Time are compiled into a small Action schema (no runtime rules).")
    print("\nInitial & step graph")
    print("--------------------")
    print(f"Initial: {local(m.at['Brussels'])} holds in S0; step chain S0→S1→S2→S3.")
    print("\nActions (cost, time)")
    print("--------------------")
    print("• Fly Brussels→Paris (cost 1, time 1) | Train Brussels→Paris (2, 2)")
    print("• Fly Paris→London (1, 2) [Forbidden for planning] | Fly Paris→Berlin (2, 2)")
    print("• Train London→Berlin (2, 3)")
    print("\nPlanning policy")
    print("----------------")
    print("• Forbidden actions (here: Fly_Paris_London) are still present as transitions,")
    print("  but they are NOT used when computing PathCost/PathTime/BestCost/BestTime.\n")


def print_question() -> None:
    print("Question")
    print("========")
    print("Q1) Enumerate all plan edges holds2(A,S,S1).")
    print("Q2) Minimal COST to reach any state where At_Berlin holds.")
    print("Q3) Minimal TIME to reach any state where At_Berlin holds.")
    print("Q4) Example (COST, TIME) value sets to S2.")
    print("Q5) Policy: does a transition using Fly_Paris_London appear (Forbidden)?")
    print()


def run_queries(m: TravelModel):
    edges = q1_edges(m)
    best_costs_berlin = q2_best_cost_berlin(m)
    best_times_berlin = q3_best_time_berlin(m)
    costs_S2, times_S2 = q4_cost_time_S2(m)
    forb_present = q5_forbidden_transition_present(m)

    return (
        ("Q1", edges),
        ("Q2", best_costs_berlin),
        ("Q3", best_times_berlin),
        ("Q4", costs_S2, times_S2),
        ("Q5", forb_present),
    )


def print_answer(res1, res2, res3, res4, res5) -> None:
    print("Answer")
    print("======")

    tag1, edges = res1
    tag2, best_costs_berlin = res2
    tag3, best_times_berlin = res3
    tag4, costs_S2, times_S2 = res4
    tag5, forb_present = res5

    if edges:
        triples = ", ".join(f"{local(a)}:{s}->{t}" for (a, s, t) in edges)
        print(f"{tag1}) {triples}")
    else:
        print(f"{tag1}) ∅")

    if best_costs_berlin:
        show = ", ".join(f"{sg}@cost={c}" for (sg, c) in best_costs_berlin)
        print(f"{tag2}) minimal costs to Berlin states: {show}")
    else:
        print(f"{tag2}) no Berlin-reachable states (cost)")

    if best_times_berlin:
        show = ", ".join(f"{sg}@time={t}" for (sg, t) in best_times_berlin)
        print(f"{tag3}) minimal times to Berlin states: {show}")
    else:
        print(f"{tag3}) no Berlin-reachable states (time)")

    print(f"{tag4}) for S2: PathCost in {costs_S2 or '∅'}, PathTime in {times_S2 or '∅'}")
    print(f"{tag5}) Forbidden action Fly_Paris_London among transitions: "
          f"{'Yes' if forb_present else 'No'}\n")


def print_reason() -> None:
    print("Reason why")
    print("==========")
    print("• We keep names as intensions (URIs) and use holds₁/holds₂-style relations, but")
    print("  all reasoning is implemented with small, explicit Python closures.")
    print("• Enabling is handled by checking preconditions (At_city) in the FROM state and")
    print("  following the small Next-chain S0→S1→S2→S3.")
    print("• Cost and time are tiny naturals (0..9) with a saturating addition sat_add.")
    print("• PathCost/PathTime accumulate measures from S0 to each state using only actions")
    print("  that are NOT Forbidden, modeling a simple policy-aware planner.")
    print("• BestCost/BestTime are true minima per state, computed directly from the sets.")
    print("• Forbidden actions remain visible in holds2, so policies can be inspected in")
    print("  queries while still being excluded from preferred plans.\n")


# ─────────────────────────────────────────────────────────────────────
# Check (12 tests)
# ─────────────────────────────────────────────────────────────────────

class CheckFailure(AssertionError):
    pass


def check(c: bool, msg: str):
    if not c:
        raise CheckFailure(msg)


def run_checks(m: TravelModel) -> List[str]:
    notes: List[str] = []

    # 1) Core edges appear (S0→S1 by Fly_BP; S1→S2 by Fly_PB)
    edges = set(m.holds2)
    check((Fly_BP, S0, S1) in edges and (Fly_PB, S1, S2) in edges, "Core edges missing.")
    notes.append("PASS 1: Core transitions generated (S0→S1 via Fly_BP; S1→S2 via Fly_PB).")

    # 2) Berlin is reachable at S2
    check(At["Berlin"] in m.holds1[S2], "Berlin not reachable at S2.")
    notes.append("PASS 2: Berlin reachable at S2.")

    # 3) PathCost exists for S2
    check(bool(m.path_cost[S2]), "PathCost to S2 missing.")
    notes.append("PASS 3: PathCost to S2 exists.")

    # 4) A cost 3 plan to S2 exists (Fly_BP=1 + Fly_PB=2, or Train_BP+Fly_PB)
    cvals_S2 = {str(c) for c in m.path_cost[S2]}
    check("3" in cvals_S2, "Expected cost 3 among costs to S2.")
    notes.append("PASS 4: A cost 3 plan to S2 exists.")

    # 5) BestCost(S2) is 3 under the policy (no Fly_PL used)
    check(m.best_cost.get(S2) == 3, "BestCost for S2 should be 3 under policy.")
    notes.append("PASS 5: BestCost(S2)=3 under policy-aware planning.")

    # 6) PathTime exists for S2 and includes 3 (1 + 2 via Fly_BP + Fly_PB)
    tvals_S2 = {str(t) for t in m.path_time[S2]}
    check(bool(tvals_S2), "PathTime to S2 missing.")
    check("3" in tvals_S2, "Expected time 3 among times to S2.")
    notes.append("PASS 6: PathTime to S2 includes 3.")

    # 7) BestTime(S2) is 3
    check(m.best_time.get(S2) == 3, "BestTime for S2 should be 3 under policy.")
    notes.append("PASS 7: BestTime(S2)=3 under policy-aware planning.")

    # 8) Forbidden action is detectable among transitions
    check(q5_forbidden_transition_present(m), "Forbidden action not detectable.")
    notes.append("PASS 8: Forbidden action detectable among transitions.")

    # 9) No transitions from the last state S3
    check(all(fr != S3 for (_, fr, _) in m.holds2), "Unexpected transitions from final state S3.")
    notes.append("PASS 9: No transitions from S3.")

    # 10) London is reachable at S2 (via forbidden Fly_PL) at the world level
    check(At["London"] in m.holds1[S2], "London should be reachable at S2 (world level).")
    notes.append("PASS 10: London reachable at S2 despite policy (world semantics).")

    # 11) Building the model twice yields the same closure
    m2 = build_model()
    check(
        m.holds1 == m2.holds1
        and m.holds2 == m2.holds2
        and m.path_cost == m2.path_cost
        and m.path_time == m2.path_time
        and m.best_cost == m2.best_cost
        and m.best_time == m2.best_time,
        "Model closure not stable across rebuilds.",
    )
    notes.append("PASS 11: Model rebuilding is stable (same holds1, holds2, paths, minima).")

    # 12) Policy respected in planning: cost 2 path to S2 (via Fly_PL) is excluded
    check("2" not in cvals_S2, "Policy violation: cost 2 path to S2 should be excluded.")
    notes.append("PASS 12: Policy respected in PathCost/BestCost (no cost-2 plan to S2).")

    return notes


# ─────────────────────────────────────────────────────────────────────
# Standalone runner
# ─────────────────────────────────────────────────────────────────────

def main():
    m = build_model()

    print_model(m)
    print_question()
    res1, res2, res3, res4, res5 = run_queries(m)
    print_answer(res1, res2, res3, res4, res5)
    print_reason()

    print("Check (harness)")
    print("===============")
    try:
        for note in run_checks(m):
            print(note)
    except CheckFailure as e:
        print("FAIL:", e)
        raise


if __name__ == "__main__":
    main()

