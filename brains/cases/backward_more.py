#!/usr/bin/env python3
"""
backward_more.py
================

What this file is
-----------------
A small, self-contained demo of a “more interesting than” relation, built from:

  • numerical scores (via a builtin math:greaterThan),
  • awards/boringness context,
  • and a transitivity rule.

All inference is implemented in Python using:

  - a tiny triple-based KB (S, P, O),
  - a simple rule compilation to compute the extension of :moreInterestingThan,
  - proof trees stored alongside each derived triple.

Higher-order look, first-order core
-----------------------------------
Predicate symbols like ":moreInterestingThan" and "math:greaterThan" are just
strings (names / intensions). Application is mediated by a fixed binary
predicate over triples:

    Holds₂(P, S, O)  ≈  (S, P, O) ∈ ext(P)

We compute ext(:moreInterestingThan) by specialized rules over the base
extensions of:

    :score, :hasAward, :boring, and the builtin math:greaterThan

which keeps the **higher-order look** but a small, **first-order core**
implementation.

Knowledge base
--------------
Rules:

  R1_score:
    (?X, ":moreInterestingThan", ?Y)
      <=
    (?X, ":score", ?SX),
    (?Y, ":score", ?SY),
    (?SX, "math:greaterThan", ?SY).

  R2_award_boring:
    (?X, ":moreInterestingThan", ?Y)
      <=
    (?X, ":hasAward", True),
    (?Y, ":boring", True).

  R3_transitive:
    (?X, ":moreInterestingThan", ?Z)
      <=
    (?X, ":moreInterestingThan", ?Y),
    (?Y, ":moreInterestingThan", ?Z).

Facts:

  ("A", ":score", 8)
  ("B", ":score", 5)
  ("B", ":moreInterestingThan", "C")
  ("D", ":hasAward", True)
  ("B", ":boring", True)

Intuitively:

  - A is more interesting than B because 8 > 5 (R1 + builtin).
  - B is more interesting than C (fact).
  - D is more interesting than B because D has an award and B is boring (R2).
  - By transitivity (R3), A>C and D>C also hold.

What the script does
--------------------
When you run:

  python backward_more.py

it executes:

  1) ("A", ":moreInterestingThan", "B")
  2) ("A", ":moreInterestingThan", "C")
  3) ("D", ":moreInterestingThan", "B")
  4) ("C", ":moreInterestingThan", "A")
  5) ("?Who", ":moreInterestingThan", "C")
  6) ("?X", ":moreInterestingThan", "?Y")

For each query it prints:

  - Answer: YES/NO and instance(s)
  - Reason why: proof tree (success) or short explanation (failure)
  - Check: a per-query sanity check

At the end it runs a global `run_checks()` harness with several PASS tests.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Tuple, Set

Triple = Tuple[Any, str, Any]
Subst = Dict[str, Any]


# ---------------------------------------------------------------------------
# Base facts
# ---------------------------------------------------------------------------

# Fact predicates:
#   :score        (entity, score-int)
#   :moreInterestingThan  (entity, entity)  [base edge]
#   :hasAward     (entity, True)
#   :boring       (entity, True)

SCORE_FACTS: Dict[str, int] = {
    "A": 8,
    "B": 5,
}

MORE_BASE: Set[Tuple[str, str]] = {
    ("B", "C"),  # given base edge
}

HAS_AWARD: Set[str] = {"D"}
BORING: Set[str] = {"B"}

P_MORE = ":moreInterestingThan"
P_SCORE = ":score"
P_HASAWARD = ":hasAward"
P_BORING = ":boring"
P_GT = "math:greaterThan"


# ---------------------------------------------------------------------------
# Builtin
# ---------------------------------------------------------------------------

def is_builtin(pred: str) -> bool:
    return pred == P_GT


def eval_builtin(goal: Triple) -> Tuple[bool, str]:
    """Evaluate math:greaterThan on ground integers."""
    s, p, o = goal
    if p != P_GT:
        return False, f"unknown builtin {p}"
    if isinstance(s, int) and isinstance(o, int):
        return (s > o), f"{s} > {o}"
    return False, "not ground or not integers"


# ---------------------------------------------------------------------------
# Proof tree representation
# ---------------------------------------------------------------------------

@dataclass
class ProofNode:
    # kind ∈ {"fact", "rule", "builtin"}
    goal: Triple
    kind: str
    rule_id: Optional[str] = None
    detail: Optional[str] = None
    children: List["ProofNode"] = field(default_factory=list)


def pp_proof(node: ProofNode, indent: int = 0) -> None:
    pad = " " * indent
    if node.kind == "fact":
        print(f"{pad}✓ fact {node.goal}")
    elif node.kind == "builtin":
        print(f"{pad}✓ builtin {node.goal} ({node.detail})")
    elif node.kind == "rule":
        print(f"{pad}Goal: {node.goal} via {node.rule_id}")
        for ch in node.children:
            pp_proof(ch, indent + 1)
        print(f"{pad}✓ Proven: {node.goal}")


@dataclass
class Failure:
    goal: Triple
    reason: str


def pp_failure(f: Failure) -> None:
    print(f"✗ {f.goal} — {f.reason}")


# ---------------------------------------------------------------------------
# Precomputed model for :moreInterestingThan
# ---------------------------------------------------------------------------

# edges[(x,y)] = ProofNode for x :moreInterestingThan y
EDGES: Dict[Tuple[str, str], ProofNode] = {}


def _mk_fact(goal: Triple) -> ProofNode:
    return ProofNode(goal=goal, kind="fact", detail="base fact")


def _mk_builtin(goal: Triple, reason: str) -> ProofNode:
    return ProofNode(goal=goal, kind="builtin", detail=reason)


def _mk_rule(rule_id: str, goal: Triple, children: List[ProofNode]) -> ProofNode:
    return ProofNode(goal=goal, kind="rule", rule_id=rule_id, children=children)


def compute_edges() -> Dict[Tuple[str, str], ProofNode]:
    """
    Compute all :moreInterestingThan edges and attach a proof to each.

    Rules implemented:
      - R1_score       (via SCORE_FACTS and builtin math:greaterThan)
      - R2_award_boring (via HAS_AWARD and BORING)
      - R3_transitive   (transitive closure on the above)
    """
    edges: Dict[Tuple[str, str], ProofNode] = {}

    # Base fact
    for (x, y) in MORE_BASE:
        goal = (x, P_MORE, y)
        edges[(x, y)] = _mk_fact(goal)

    # R1_score: X>Y if score(X) > score(Y)
    for x, sx in SCORE_FACTS.items():
        for y, sy in SCORE_FACTS.items():
            if sx <= sy:
                continue
            goal = (x, P_MORE, y)
            if (x, y) in edges:
                continue
            # children: score facts + builtin
            c1 = _mk_fact((x, P_SCORE, sx))
            c2 = _mk_fact((y, P_SCORE, sy))
            ok, reason = eval_builtin((sx, P_GT, sy))
            c3 = _mk_builtin((sx, P_GT, sy), reason)
            edges[(x, y)] = _mk_rule("R1_score", goal, [c1, c2, c3])

    # R2_award_boring: X>Y if award(X) & boring(Y)
    for x in HAS_AWARD:
        for y in BORING:
            goal = (x, P_MORE, y)
            if (x, y) in edges:
                continue
            c1 = _mk_fact((x, P_HASAWARD, True))
            c2 = _mk_fact((y, P_BORING, True))
            edges[(x, y)] = _mk_rule("R2_award_boring", goal, [c1, c2])

    # R3_transitive: transitive closure
    changed = True
    while changed:
        changed = False
        pairs = list(edges.keys())
        for (x, y1) in pairs:
            for (y2, z) in pairs:
                if y1 != y2:
                    continue
                if (x, z) in edges:
                    continue
                goal = (x, P_MORE, z)
                # children: proof for x>y, proof for y>z
                c1 = edges[(x, y1)]
                c2 = edges[(y2, z)]
                edges[(x, z)] = _mk_rule("R3_transitive", goal, [c1, c2])
                changed = True

    return edges


# Precompute on import
EDGES = compute_edges()


# ---------------------------------------------------------------------------
# Query engine (pattern matching over EDGES)
# ---------------------------------------------------------------------------

def is_var(t: Any) -> bool:
    return isinstance(t, str) and t.startswith("?")


def match_goal(goal: Triple) -> List[Tuple[Subst, ProofNode]]:
    """
    Match a goal (S, :moreInterestingThan, O) against the precomputed edges.

    S and O may be constants or variables (?X). Returns all substitutions θ
    and their associated proof trees.
    """
    s_pat, p, o_pat = goal
    if p != P_MORE:
        raise ValueError("This demo only supports :moreInterestingThan as query predicate.")

    results: List[Tuple[Subst, ProofNode]] = []

    for (x, y), proof in EDGES.items():
        theta: Subst = {}
        # match subject
        if is_var(s_pat):
            theta[s_pat] = x
        elif s_pat != x:
            continue
        # match object
        if is_var(o_pat):
            # if same variable as subject, enforce equality
            if o_pat == s_pat:
                if theta[s_pat] != y:
                    continue
            theta[o_pat] = y
        elif o_pat != y:
            continue
        results.append((theta, proof))

    return results


# ---------------------------------------------------------------------------
# ARC-style per-query sections
# ---------------------------------------------------------------------------

def arc_answer(goal: Triple, answers: List[Tuple[Subst, ProofNode]], show_all: bool = False) -> None:
    print("Answer")
    print("------")
    if not answers:
        print("NO — not derivable from the KB.")
        print()
        return

    if show_all:
        for i, (theta, _) in enumerate(answers, start=1):
            inst = (theta.get(goal[0], goal[0]), goal[1], theta.get(goal[2], goal[2]))
            bindings = {v: x for v, x in theta.items() if is_var(v)}
            extra = f" bindings={bindings}" if bindings else ""
            print(f"{i}. YES — instance: {inst}{extra}")
    else:
        theta, _ = answers[0]
        inst = (theta.get(goal[0], goal[0]), goal[1], theta.get(goal[2], goal[2]))
        bindings = {v: x for v, x in theta.items() if is_var(v)}
        extra = f" bindings={bindings}" if bindings else ""
        print(f"YES — instance: {inst}{extra}")
    print()


def arc_reason(goal: Triple, answers: List[Tuple[Subst, ProofNode]]) -> None:
    print("Reason why")
    print("----------")
    if answers:
        print("Proof tree:")
        pp_proof(answers[0][1])
        if len(answers) > 1:
            print(f"(+ {len(answers)-1} more proof(s) omitted)")
    else:
        # simple failure explanation
        f = Failure(goal=goal, reason="no path for :moreInterestingThan with given KB")
        pp_failure(f)
    print()


def arc_check(goal: Triple, answers: List[Tuple[Subst, ProofNode]], expect_subset: Set[Triple] | None = None) -> None:
    print("Check (harness)")
    print("---------------")

    # 1) If there is an answer, verify proof tree structure (quick sanity).
    if answers:
        node = answers[0][1]

        def verify(node: ProofNode) -> bool:
            if node.kind == "fact":
                # facts are always accepted here; they are either base :moreInterestingThan,
                # :score, :hasAward, or :boring
                return True
            if node.kind == "builtin":
                ok, _ = eval_builtin(node.goal)
                return ok
            if node.kind == "rule":
                return all(verify(ch) for ch in node.children)
            return False

        assert verify(node), "Proof tree verification failed."
    else:
        # For a failing query with ground constants, ensure it's really absent
        s_pat, p, o_pat = goal
        if not is_var(s_pat) and not is_var(o_pat) and p == P_MORE:
            assert (s_pat, o_pat) not in EDGES, "Goal unexpectedly present in EDGES."

    # 2) If an expected subset is given, check that it's included in instances
    if expect_subset is not None:
        insts = set()
        for theta, _ in answers:
            s = theta.get(goal[0], goal[0])
            o = theta.get(goal[2], goal[2])
            insts.add((s, goal[1], o))
        missing = {t for t in expect_subset if t not in insts}
        assert not missing, f"Missing expected instances: {missing}"

    print("OK.\n")


def run_arc(goal: Triple, show_all: bool = False, expect_subset: Set[Triple] | None = None) -> None:
    answers = match_goal(goal)
    arc_answer(goal, answers, show_all=show_all)
    arc_reason(goal, answers)
    arc_check(goal, answers, expect_subset=expect_subset)


# ---------------------------------------------------------------------------
# Global Check (multi-test harness)
# ---------------------------------------------------------------------------

class CheckFailure(AssertionError):
    pass


def check(cond: bool, msg: str) -> None:
    if not cond:
        raise CheckFailure(msg)


def run_checks() -> List[str]:
    notes: List[str] = []

    expected_edges = {
        ("B", "C"),  # base
        ("A", "B"),  # scores: 8 > 5
        ("D", "B"),  # award/boring
        ("A", "C"),  # A>B, B>C
        ("D", "C"),  # D>B, B>C
    }
    got_edges = set(EDGES.keys())
    check(expected_edges == got_edges, f"Edges mismatch: expected {expected_edges}, got {got_edges}")
    notes.append("PASS 1: ext(:moreInterestingThan) matches expected closure.")

    # 2) A > B provable
    ans1 = match_goal(("A", P_MORE, "B"))
    check(ans1, "A :moreInterestingThan B should be provable.")
    notes.append("PASS 2: A :moreInterestingThan B provable.")

    # 3) C > A not provable
    ans2 = match_goal(("C", P_MORE, "A"))
    check(not ans2, "C :moreInterestingThan A should not be provable.")
    notes.append("PASS 3: C :moreInterestingThan A not provable.")

    # 4) ?Who > C includes {B, A, D}
    ans3 = match_goal(("?Who", P_MORE, "C"))
    who_set = {theta["?Who"] for theta, _ in ans3}
    check({"B", "A", "D"}.issubset(who_set), f"?Who > C missing some expected names: got {who_set}")
    notes.append("PASS 4: ?Who :moreInterestingThan C includes {A,B,D}.")

    # 5) ?X > ?Y has exactly the expected pairs
    ans4 = match_goal(("?X", P_MORE, "?Y"))
    pairs = {(theta["?X"], theta["?Y"]) for theta, _ in ans4}
    check(pairs == expected_edges, f"?X :moreInterestingThan ?Y pairs mismatch: {pairs}")
    notes.append("PASS 5: ?X :moreInterestingThan ?Y returns the correct closure pairs.")

    # 6) Builtin math:greaterThan sanity checks
    ok1, _ = eval_builtin((8, P_GT, 5))
    ok2, _ = eval_builtin((3, P_GT, 5))
    ok3, reason3 = eval_builtin(("?X", P_GT, 1))
    check(ok1, "math:greaterThan(8,5) should be true.")
    check(not ok2, "math:greaterThan(3,5) should be false.")
    check(not ok3 and "not ground" in reason3, "Non-ground builtin should fail with 'not ground'.")
    notes.append("PASS 6: builtin math:greaterThan behaves correctly (true/false/groundness).")

    return notes


# ---------------------------------------------------------------------------
# Main: demo + checks
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # 1) Score rule: A > B (8 > 5)
    print("=== Query 1 ===")
    run_arc(("A", P_MORE, "B"))

    # 2) Transitivity: A > B and B > C ⇒ A > C
    print("=== Query 2 ===")
    run_arc(("A", P_MORE, "C"))

    # 3) Context rule: D > B (award/boring)
    print("=== Query 3 ===")
    run_arc(("D", P_MORE, "B"))

    # 4) Failure: C > A
    print("=== Query 4 ===")
    run_arc(("C", P_MORE, "A"))

    # 5) Open variable: Who > C?
    print("=== Query 5 ===")
    expect_who_c = {
        ("B", P_MORE, "C"),
        ("A", P_MORE, "C"),
        ("D", P_MORE, "C"),
    }
    run_arc(("?Who", P_MORE, "C"), show_all=True, expect_subset=expect_who_c)

    # 6) Both ends open: X > Y
    print("=== Query 6 ===")
    expect_pairs = {
        ("B", P_MORE, "C"),
        ("D", P_MORE, "B"),
        ("A", P_MORE, "B"),
        ("D", P_MORE, "C"),
        ("A", P_MORE, "C"),
    }
    run_arc(("?X", P_MORE, "?Y"), show_all=True, expect_subset=expect_pairs)

    # Global harness
    print("Global Check (harness)")
    print("======================")
    try:
        for note in run_checks():
            print(note)
    except CheckFailure as e:
        print("FAIL:", e)
        raise

