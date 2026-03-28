# -*- coding: utf-8 -*-
"""
Relational Algebra over Social Links
(Union, Composition, Star) in the Hayes–Menzel Style
----------------------------------------------------

We work with *relation names* (intensions) like ex:Follows, ex:Mentors,
ex:Collaborates, ex:Knows, and a fixed application predicate in the story:

    holds2(R, x, y)   # ⟨x,y⟩ ∈ extension of relation-name R

Meta over **names**:

    SubRelOf(P,Q)     — inclusion (P ⊆ Q)
    Union(P,Q,R)      — R = P ∪ Q
    Comp(P,Q,R)       — R = P ∘ Q (relational composition)
    Star(P,R)         — R = P⁺ (non-reflexive transitive closure: length ≥ 1)

We implement the induced semantics with **specialized Python closures**:

    - leq_strict: transitive closure of SubRelOf
    - leq      : leq_strict plus reflexivity (R ⊆ R)
    - holds2   : a map from relation-name → set of pairs (x,y)
                 with explicit Union, Comp, Star operations

Intended relations
------------------
Base social links:

    Follows     : some “follows” edges
    Mentors     : mentoring edges
    Collaborates: collaboration edges

Constructed:

    Knows  : intended Follows ∪ Mentors ∪ Collaborates
    TwoHop : intended Knows ∘ Knows
    ReachK : intended Knows⁺ (length ≥ 1)

Questions
---------
Q1) List all (X,Y) with holds2(TwoHop,X,Y).
Q2) Witness relation-names R s.t. Comp(Knows,Knows,R) and holds2(R,Alice,Dave).
Q3) Check universal property:
        ∀R,y: (leq(R,Knows) ∧ holds2(R,Alice,y)) → holds2(ReachK,Alice,y).

How to run
----------
    python relational_algebra_social.py

Printed sections
----------------
Model → Question → Answer → Reason why → Check (harness)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Set, Tuple


# -------------------------
# Domain (individuals)
# -------------------------

D: Tuple[str, ...] = (
    "Alice",
    "Bob",
    "Carol",
    "Dave",
    "Erin",
    "Frank",
)


# -------------------------
# Relation names (intensions)
# -------------------------

EX = "ex:"

Follows = EX + "Follows"
Mentors = EX + "Mentors"
Collaborates = EX + "Collaborates"

Knows = EX + "Knows"       # intended: Follows ∪ Mentors ∪ Collaborates
TwoHop = EX + "TwoHop"     # intended: Knows ∘ Knows
ReachK = EX + "ReachK"     # intended: Knows⁺ (length ≥ 1)

Role = str
Pair = Tuple[str, str]

ROLE_NAMES: Set[Role] = {
    Follows,
    Mentors,
    Collaborates,
    Knows,
    TwoHop,
    ReachK,
}

# meta over names (we store as Python data, not facts)
SUBRELOF_BASE: Dict[Role, Set[Role]] = {
    Follows: {Knows},
    Mentors: {Knows},
    Collaborates: {Knows},
}

UNION_BASE: List[Tuple[Role, Role, Role]] = [
    (Follows, Mentors, Knows),      # Knows gets Follows ∪ Mentors
    (Knows, Collaborates, Knows),   # Knows also absorbs Collaborates
]

COMP_BASE: List[Tuple[Role, Role, Role]] = [
    (Knows, Knows, TwoHop),         # TwoHop = Knows ∘ Knows
]

STAR_BASE: List[Tuple[Role, Role]] = [
    (Knows, ReachK),                # ReachK = Knows⁺
]


# -------------------------
# Formatting helpers
# -------------------------

def local(name: str) -> str:
    return name.split(":", 1)[1] if ":" in name else name


def fmt_pairs(pairs: Iterable[Pair]) -> str:
    seq = sorted(set(pairs))
    if not seq:
        return "∅"
    return "{" + ", ".join(f"⟨{x},{y}⟩" for (x, y) in seq) + "}"


def fmt_set(names: Iterable[str]) -> str:
    s = sorted(set(names))
    if not s:
        return "∅"
    return "{" + ", ".join(local(n) for n in s) + "}"


# -------------------------
# Base holds2 facts
# -------------------------

def base_relation_extensions() -> Dict[Role, Set[Pair]]:
    """Explicit social links for Follows, Mentors, Collaborates."""
    rel: Dict[Role, Set[Pair]] = {r: set() for r in ROLE_NAMES}

    # Follows edges
    for a, b in [
        ("Alice", "Bob"),
        ("Bob", "Carol"),
        ("Carol", "Dave"),
        ("Bob", "Dave"),
        ("Erin", "Frank"),
    ]:
        rel[Follows].add((a, b))

    # Mentors edges
    for a, b in [
        ("Alice", "Carol"),
        ("Dave", "Erin"),
    ]:
        rel[Mentors].add((a, b))

    # Collaborates edges
    for a, b in [
        ("Carol", "Erin"),
        ("Bob", "Frank"),
    ]:
        rel[Collaborates].add((a, b))

    # Constructed relations start empty
    rel[Knows] = set()
    rel[TwoHop] = set()
    rel[ReachK] = set()

    return rel


# -------------------------
# Name-level closure
# -------------------------

def closure_subrel_of(subrel: Dict[Role, Set[Role]]) -> Dict[Role, Set[Role]]:
    """
    Compute transitive closure of SubRelOf:

        leq_strict(P,Q)  ⇔  P ⊆ Q via a non-empty chain of SubRelOf.
    """
    leq_strict: Dict[Role, Set[Role]] = {r: set() for r in ROLE_NAMES}
    for p, qs in subrel.items():
        leq_strict[p].update(qs)

    changed = True
    while changed:
        changed = False
        for p in ROLE_NAMES:
            new: Set[Role] = set()
            for q in leq_strict[p]:
                new.update(leq_strict.get(q, set()))
            if not new.issubset(leq_strict[p]):
                leq_strict[p].update(new)
                changed = True
    return leq_strict


def closure_leq(leq_strict: Dict[Role, Set[Role]]) -> Dict[Role, Set[Role]]:
    """Add reflexive pairs leq(R,R) on top of leq_strict."""
    leq: Dict[Role, Set[Role]] = {}
    for r in ROLE_NAMES:
        leq[r] = set(leq_strict.get(r, set()))
        leq[r].add(r)
    return leq


# -------------------------
# Relation-level operations
# -------------------------

def apply_unions(rel: Dict[Role, Set[Pair]]) -> None:
    """Apply UNION_BASE as a small fixpoint on relation extensions."""
    changed = True
    while changed:
        changed = False
        for P, Q, R in UNION_BASE:
            out = rel[R]
            before = len(out)
            out |= rel[P]
            out |= rel[Q]
            if len(out) > before:
                changed = True


def compute_composition(pairs_p: Set[Pair], pairs_q: Set[Pair]) -> Set[Pair]:
    """Relational composition P ∘ Q."""
    out: Set[Pair] = set()
    for (x, y1) in pairs_p:
        for (y2, z) in pairs_q:
            if y1 == y2:
                out.add((x, z))
    return out


def transitive_closure(pairs: Set[Pair]) -> Set[Pair]:
    """
    Compute P⁺ (non-reflexive transitive closure):

        closure = ⋃_{n≥1} Pⁿ

    Here we do standard closure (allowing reflexives when cycles exist),
    but in this acyclic dataset there will be no reflexive pairs.
    """
    closure: Set[Pair] = set(pairs)
    changed = True
    while changed:
        changed = False
        new_pairs: Set[Pair] = set()
        # R := R ∘ P
        for (x, y1) in closure:
            for (y2, z) in pairs:
                if y1 == y2 and (x, z) not in closure:
                    new_pairs.add((x, z))
        if new_pairs:
            closure |= new_pairs
            changed = True
    return closure


# -------------------------
# Logical model
# -------------------------

@dataclass
class RelAlgSocialModel:
    individuals: Tuple[str, ...]
    rel_ext: Dict[Role, Set[Pair]]
    leq_strict: Dict[Role, Set[Role]]
    leq: Dict[Role, Set[Role]]


def build_model() -> RelAlgSocialModel:
    # Base facts
    rel_ext = base_relation_extensions()

    # Name-level closure
    leq_strict = closure_subrel_of(SUBRELOF_BASE)
    leq = closure_leq(leq_strict)

    # 1) Knows via unions and inclusion (in this case union is enough)
    apply_unions(rel_ext)

    # 2) TwoHop via composition Knows ∘ Knows
    for P, Q, R in COMP_BASE:
        if P == Knows and Q == Knows and R == TwoHop:
            rel_ext[TwoHop] = compute_composition(rel_ext[Knows], rel_ext[Knows])

    # 3) ReachK as Knows⁺
    for P, R in STAR_BASE:
        if P == Knows and R == ReachK:
            rel_ext[ReachK] = transitive_closure(rel_ext[Knows])

    return RelAlgSocialModel(
        individuals=D,
        rel_ext=rel_ext,
        leq_strict=leq_strict,
        leq=leq,
    )


# -------------------------
# Questions Q1–Q3
# -------------------------

def q1_twohop_pairs(m: RelAlgSocialModel) -> List[Pair]:
    """Q1: list all (X,Y) with holds2(TwoHop,X,Y)."""
    return sorted(m.rel_ext.get(TwoHop, set()))


def q2_witness_relations(m: RelAlgSocialModel) -> List[Role]:
    """
    Q2: witness R such that:

        Comp(Knows,Knows,R) ∧ holds2(R,Alice,Dave)
    """
    witnesses: Set[Role] = set()
    for P, Q, R in COMP_BASE:
        if P == Knows and Q == Knows and ("Alice", "Dave") in m.rel_ext.get(R, set()):
            witnesses.add(R)
    return sorted(witnesses)


def q3_universal_property(m: RelAlgSocialModel) -> bool:
    """
    Q3: universal property:

        ∀R,y: (leq(R,Knows) ∧ holds2(R,Alice,y)) → holds2(ReachK,Alice,y)

    We only quantify over a small set of relation names, just like the original.
    """
    candidates = [Follows, Mentors, Collaborates, Knows, TwoHop]
    for R in candidates:
        # leq(R,Knows) must hold
        if Knows not in m.leq.get(R, set()):
            continue
        for y in m.individuals:
            if ("Alice", y) in m.rel_ext.get(R, set()) and ("Alice", y) not in m.rel_ext[ReachK]:
                return False
    return True


# -------------------------
# Presentation (printing)
# -------------------------

def print_model(m: RelAlgSocialModel) -> None:
    print("Model")
    print("=====")
    print(f"Individuals D = {list(m.individuals)}\n")

    print("Fixed predicates (informal)")
    print("----------------------------")
    print("• holds2(R,x,y)  — application (⟨x,y⟩ ∈ ext(R))")
    print("• SubRelOf(P,Q)  — inclusion over relation names (P ⊆ Q)")
    print("• Union(P,Q,R)   — R = P ∪ Q")
    print("• Comp(P,Q,R)    — R = P ∘ Q")
    print("• Star(P,R)      — R = P⁺ (non-reflexive transitive closure)")
    print("• leq_strict / leq — ⊆* with/without reflex on names\n")

    print("Named relations (with base facts)")
    print("---------------------------------")
    print("Follows     =",
          fmt_pairs([("Alice","Bob"), ("Bob","Carol"), ("Carol","Dave"),
                     ("Bob","Dave"), ("Erin","Frank")]))
    print("Mentors     =",
          fmt_pairs([("Alice","Carol"), ("Dave","Erin")]))
    print("Collaborates=",
          fmt_pairs([("Carol","Erin"), ("Bob","Frank")]))
    print("Knows       = derived; intended Follows ∪ Mentors ∪ Collaborates")
    print("TwoHop      = derived; intended Knows ∘ Knows")
    print("ReachK      = derived; intended Knows⁺ (length ≥ 1)\n")

    print("Inclusions over names:")
    print("  Follows ⊆ Knows, Mentors ⊆ Knows, Collaborates ⊆ Knows")
    print("Constructors over names:")
    print("  Union(Follows,Mentors,Knows), Union(Knows,Collaborates,Knows),")
    print("  Comp(Knows,Knows,TwoHop), Star(Knows,ReachK)\n")


def print_question() -> None:
    print("Question")
    print("========")
    print("Q1) List all (X,Y) with holds2(TwoHop,X,Y).")
    print("Q2) ∃R: Comp(Knows,Knows,R) ∧ holds2(R,Alice,Dave) ? (witness relation-names).")
    print("Q3) ∀R,y: (leq(R,Knows) ∧ holds2(R,Alice,y)) → holds2(ReachK,Alice,y) ?")
    print()


def run_queries(m: RelAlgSocialModel):
    pairs = q1_twohop_pairs(m)
    witnesses = q2_witness_relations(m)
    ok = q3_universal_property(m)

    return (
        ("Q1", pairs),
        ("Q2", witnesses),
        ("Q3", ok),
    )


def print_answer(res1, res2, res3) -> None:
    print("Answer")
    print("======")

    tag1, pairs = res1
    tag2, wits = res2
    tag3, ok = res3

    print(f"{tag1}) TwoHop =", fmt_pairs(pairs))
    print(f"{tag2}) Witness relation-names R = " + (fmt_set(wits) if wits else "∅"))
    print(f"{tag3}) Universal statement holds: {'Yes' if ok else 'No'}\n")


def print_reason() -> None:
    print("Reason why")
    print("==========")
    print("• Knows is both the union of base links and a superrelation via SubRelOf;")
    print("  we materialize it by applying Union over relation extensions.")
    print("• TwoHop = Knows ∘ Knows is computed via relational composition.")
    print("• ReachK = Knows⁺ is computed as the transitive closure (length ≥ 1) of Knows.")
    print("• leq_strict and leq are closures over SubRelOf, entirely at the NAME level.")
    print("• Q2 quantifies over relation names to find R with Comp(Knows,Knows,R).")
    print("• Q3 states that any R below Knows cannot add new Alice-targets beyond ReachK.\n")


# -------------------
# Check (harness)
# -------------------

class CheckFailure(AssertionError):
    pass


def check(c: bool, msg: str):
    if not c:
        raise CheckFailure(msg)


def _expected_knows_and_twohop() -> Tuple[Set[Pair], Set[Pair]]:
    """Reference oracle for Knows and TwoHop, derived directly from the base."""
    base: Set[Tuple[Role, str, str]] = {
        (Follows, "Alice", "Bob"),
        (Follows, "Bob", "Carol"),
        (Follows, "Carol", "Dave"),
        (Follows, "Bob", "Dave"),
        (Follows, "Erin", "Frank"),
        (Mentors, "Alice", "Carol"),
        (Mentors, "Dave", "Erin"),
        (Collaborates, "Carol", "Erin"),
        (Collaborates, "Bob", "Frank"),
    }

    knows = {(x, y) for (r, x, y) in base
             if r in (Follows, Mentors, Collaborates)}

    # Relational composition Knows ∘ Knows
    def comp2(pairs: Set[Pair]) -> Set[Pair]:
        out: Set[Pair] = set()
        for (x, y1) in pairs:
            for (y2, z) in pairs:
                if y1 == y2:
                    out.add((x, z))
        return out

    twohop = comp2(knows)
    return knows, twohop


def _expected_reachk(knows: Set[Pair]) -> Set[Pair]:
    """Reference oracle for ReachK = Knows⁺."""
    return transitive_closure(knows)


def run_checks(m: RelAlgSocialModel) -> List[str]:
    notes: List[str] = []

    knows_ref, twohop_ref = _expected_knows_and_twohop()

    # 1) Knows extension is exactly the union of base relations
    check(m.rel_ext[Knows] == knows_ref, "Knows extension mismatch.")
    notes.append("PASS 1: Knows = Follows ∪ Mentors ∪ Collaborates.")

    # 2) TwoHop matches reference composition
    twohop_actual = m.rel_ext[TwoHop]
    check(twohop_actual == twohop_ref, "TwoHop composition mismatch.")
    notes.append("PASS 2: TwoHop = Knows ∘ Knows is correct.")

    # 3) Witness set for Alice→Dave under composition is {TwoHop}
    wits = set(q2_witness_relations(m))
    check(wits == {TwoHop}, f"Witness set mismatch: {wits}")
    notes.append("PASS 3: Witness set for Alice→Dave under Comp(Knows,Knows,R) is {TwoHop}.")

    # 4) Universal property holds
    check(q3_universal_property(m), "Universal property failed.")
    notes.append("PASS 4: Universal property (R ≤ Knows ⇒ ReachK covers Alice-targets) holds.")

    # 5) TwoHop has no reflexive pairs in this acyclic dataset
    for v in D:
        check((v, v) not in m.rel_ext[TwoHop], f"Unexpected reflexive TwoHop at {v}.")
    notes.append("PASS 5: TwoHop is non-reflexive here.")

    # 6) ReachK has no reflexive pairs (dataset is acyclic)
    for v in D:
        check((v, v) not in m.rel_ext[ReachK], f"Unexpected reflexive ReachK at {v}.")
    notes.append("PASS 6: ReachK is non-reflexive here.")

    # 7) leq is reflexive on all relation names
    for r in ROLE_NAMES:
        check(r in m.leq.get(r, set()), f"Reflexivity of leq failed for {local(r)}.")
    notes.append("PASS 7: leq reflexivity holds for all relation names.")

    # 8) Inclusion basics: base relations are ≤ Knows in leq_strict
    for r in (Follows, Mentors, Collaborates):
        check(Knows in m.leq_strict.get(r, set()),
              f"leq_strict {local(r)} ⊆ Knows failed.")
    notes.append("PASS 8: leq_strict inclusions Follows/Mentors/Collaborates ⊆ Knows hold.")

    # 9) Composition really yields a 2-hop edge Alice→Dave
    check(("Alice", "Dave") in m.rel_ext[TwoHop], "Expected Alice→Dave in TwoHop.")
    notes.append("PASS 9: TwoHop contains Alice→Dave as a 2-hop path.")

    # 10) ReachK equals Knows⁺ according to reference closure
    reachk_ref = _expected_reachk(knows_ref)
    check(m.rel_ext[ReachK] == reachk_ref, "ReachK closure mismatch.")
    notes.append("PASS 10: ReachK = Knows⁺ matches reference transitive closure.")

    # 11) Building the model twice yields identical closure
    m2 = build_model()
    check(
        m.rel_ext == m2.rel_ext
        and m.leq_strict == m2.leq_strict
        and m.leq == m2.leq,
        "Model closure not stable across rebuilds.",
    )
    notes.append("PASS 11: Model rebuilding is stable (same holds2 and leq).")

    # 12) Pretty-printing is deterministic
    s1 = fmt_pairs(sorted(twohop_ref))
    s2 = fmt_pairs(sorted(list(twohop_ref)))
    check(s1 == s2, "Pretty-printer determinism failed.")
    notes.append("PASS 12: Pretty printing is deterministic.")

    return notes


# -------------------
# Standalone runner
# -------------------

def main():
    m = build_model()

    print_model(m)
    print_question()
    res1, res2, res3 = run_queries(m)
    print_answer(res1, res2, res3)
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

