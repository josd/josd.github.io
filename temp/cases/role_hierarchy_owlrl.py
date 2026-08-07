# -*- coding: utf-8 -*-
"""
OWL RL–ish Role Hierarchy + Inverses (Hayes–Menzel style)

We represent role *names* (intensions) like ex:parentOf, ex:childOf, ex:teaches, ...
and use a fixed application predicate in code:

    role_ext[R]  ⊆ IND × IND      # ⟨x,y⟩ ∈ extension of role-name R
    class_ext[C] ⊆ IND            # x   ∈ extension of class-name C

Meta over **role names** (all over NAME-domain):
    SubRelOf(P,Q)      — role inclusion (P ⊆ Q)
    InverseOf(P,Q)     — inverse roles (P = Q⁻¹)
    Symmetric(P)       — symmetric role P
    Transitive(P)      — transitive role P
    SubRelChain(P,Q,R) — property chain (P∘Q ⊆ R)
    Domain(P,C), Range(P,C) — typing of role P: dom = C, rng = C

Meta over **class names**:
    SubClassOf(C,D)    — class inclusion (C ⊆ D)

We compute the OWL-RL-ish closure using specialized Python functions (set/dict
manipulation).

Questions (same as original file):

  Q1) Enumerate all ⟨x,y⟩ with holds2(ancestorOf,x,y).
  Q2) Witness role-names R s.t. leq(R,advises) ∧ holds2(R,Grace,Erin).
  Q3) Typing check: ∀y, if holds2(advises,Grace,y) then Professor(Grace) ∧ Student(y)?
  Q4) Inverse check: childOf = parentOf⁻¹ (list and compare).
  Q5) Symmetry check: marriedTo(Erin,Frank) ⇒ marriedTo(Frank,Erin).

How to run
----------

    python role_hierarchy_owlrl.py
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Set, Tuple
from collections import defaultdict


# -------------------------
# Domain (individuals)
# -------------------------

IND = Tuple[str, ...]
D: IND = (
    "Alice",
    "Bob",
    "Carol",
    "Dave",
    "Erin",
    "Frank",
    "Grace",
    "Helen",
)


# -------------------------
# Names (roles & classes)
# -------------------------

EX = "ex:"

# roles
parentOf = EX + "parentOf"
childOf = EX + "childOf"
ancestorOf = EX + "ancestorOf"
marriedTo = EX + "marriedTo"
teaches = EX + "teaches"
supervises = EX + "supervises"
advises = EX + "advises"

# classes
Person = EX + "Person"
Student = EX + "Student"
Professor = EX + "Professor"

Role = str
Cls = str
Pair = Tuple[str, str]


# -----------------------------
# Meta-knowledge (TBox-ish)
# -----------------------------

# Role hierarchy SubRelOf(P,Q): P ⊆ Q
SUB_RELOF: Dict[Role, Set[Role]] = {
    parentOf: {ancestorOf},
    teaches: {advises},
    supervises: {advises},
}

# InverseOf(P,Q): (we make this symmetric at build time)
INVERSE_BASE: Set[Tuple[Role, Role]] = {
    (parentOf, childOf),
}

# Symmetric roles
SYMMETRIC: Set[Role] = {marriedTo}

# Transitive roles
TRANSITIVE: Set[Role] = {ancestorOf}

# Property chains P∘Q ⊆ R
SUBREL_CHAIN: Set[Tuple[Role, Role, Role]] = {
    (parentOf, parentOf, ancestorOf)
}

# Domain/Range typing
DOMAIN_BASE: Dict[Role, Set[Cls]] = {
    advises: {Professor},
}
RANGE_BASE: Dict[Role, Set[Cls]] = {
    advises: {Student},
}

# Class hierarchy
SUBCLASS_BASE: Dict[Cls, Set[Cls]] = {
    Student: {Person},
    Professor: {Person},
}

# All role names and class names used
ROLE_NAMES: Set[Role] = {
    parentOf,
    childOf,
    ancestorOf,
    marriedTo,
    teaches,
    supervises,
    advises,
}

CLASS_NAMES: Set[Cls] = {
    Person,
    Student,
    Professor,
}


# -----------------------------
# Base role extensions (ABox)
# -----------------------------

def base_role_extensions() -> Dict[Role, Set[Pair]]:
    """Return the base (explicit) role extensions before reasoning."""
    ext: Dict[Role, Set[Pair]] = {r: set() for r in ROLE_NAMES}

    # parentOf facts
    for a, b in [("Alice", "Bob"), ("Bob", "Carol"), ("Carol", "Dave")]:
        ext[parentOf].add((a, b))

    # marriedTo facts
    ext[marriedTo].add(("Erin", "Frank"))

    # teaches
    ext[teaches].add(("Grace", "Carol"))
    ext[teaches].add(("Grace", "Dave"))

    # supervises
    ext[supervises].add(("Grace", "Erin"))

    return ext


# =====================
#  Specialized closure
# =====================

def compute_inverse_map(pairs: Set[Tuple[Role, Role]]) -> Dict[Role, Set[Role]]:
    """Make InverseOf symmetric and map each role to its inverse(s)."""
    inv: Dict[Role, Set[Role]] = defaultdict(set)
    for p, q in pairs:
        inv[p].add(q)
        inv[q].add(p)
    return inv


def closure_subrel_of(subrel: Dict[Role, Set[Role]]) -> Dict[Role, Set[Role]]:
    """
    Compute transitive closure of SubRelOf.
    Returns leq_strict: for each P, the strict super-roles Q with P ⊆ Q.
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
    """Add reflexive leq(P,P) on top of leq_strict."""
    leq: Dict[Role, Set[Role]] = {}
    for r in ROLE_NAMES:
        leq[r] = set(leq_strict.get(r, set()))
        leq[r].add(r)
    return leq


def propagate_domain_range(
    domain_base: Dict[Role, Set[Cls]],
    range_base: Dict[Role, Set[Cls]],
    leq_strict: Dict[Role, Set[Role]],
    inverse_of: Dict[Role, Set[Role]],
) -> Tuple[Dict[Role, Set[Cls]], Dict[Role, Set[Cls]]]:
    """
    Implement:

        Domain(P,C) :- SubRelOf(P,Q), Domain(Q,C).
        Range(P,C)  :- SubRelOf(P,Q), Range(Q,C).
        Range(Q,C)  :- InverseOf(P,Q), Domain(P,C).
        Domain(Q,C) :- InverseOf(P,Q), Range(P,C).

    using a simple fixpoint.
    """
    domain: Dict[Role, Set[Cls]] = defaultdict(set)
    range_: Dict[Role, Set[Cls]] = defaultdict(set)

    for r, cs in domain_base.items():
        domain[r].update(cs)
    for r, cs in range_base.items():
        range_[r].update(cs)

    changed = True
    while changed:
        changed = False

        # propagate down the subrole hierarchy
        for p in ROLE_NAMES:
            for q in leq_strict.get(p, set()):
                for c in domain.get(q, set()):
                    if c not in domain[p]:
                        domain[p].add(c)
                        changed = True
                for c in range_.get(q, set()):
                    if c not in range_[p]:
                        range_[p].add(c)
                        changed = True

        # propagate through inverses
        for p, invs in inverse_of.items():
            for q in invs:
                for c in domain.get(p, set()):
                    if c not in range_[q]:
                        range_[q].add(c)
                        changed = True
                for c in range_.get(p, set()):
                    if c not in domain[q]:
                        domain[q].add(c)
                        changed = True

    return dict(domain), dict(range_)


def closure_subclass(subcls_base: Dict[Cls, Set[Cls]]) -> Dict[Cls, Set[Cls]]:
    """Transitive closure of SubClassOf."""
    sup: Dict[Cls, Set[Cls]] = {c: set() for c in CLASS_NAMES}
    for c, ds in subcls_base.items():
        sup[c].update(ds)

    changed = True
    while changed:
        changed = False
        for c in CLASS_NAMES:
            new: Set[Cls] = set()
            for d in sup[c]:
                new.update(sup.get(d, set()))
            if not new.issubset(sup[c]):
                sup[c].update(new)
                changed = True
    return sup


def saturate_roles(
    role_ext: Dict[Role, Set[Pair]],
    leq_strict: Dict[Role, Set[Role]],
    inverse_of: Dict[Role, Set[Role]],
    symmetric_roles: Set[Role],
    transitive_roles: Set[Role],
    chains: Set[Tuple[Role, Role, Role]],
) -> Dict[Role, Set[Pair]]:
    """
    Perform role-level closure:

        - symmetric(P): add (y,x) when (x,y) ∈ P
        - inverseOf(P,Q): add (y,x) ∈ Q when (x,y) ∈ P
        - subRelOf(P,Q): lift pairs along inclusion (P ⊆ Q)
        - transitive(P): close P transitively
        - property chains P∘Q ⊆ R
    """
    changed = True
    while changed:
        changed = False

        # Symmetric
        for p in symmetric_roles:
            current = list(role_ext[p])
            for x, y in current:
                if (y, x) not in role_ext[p]:
                    role_ext[p].add((y, x))
                    changed = True

        # Inverses
        for p, pairs in list(role_ext.items()):
            for x, y in list(pairs):
                for q in inverse_of.get(p, set()):
                    if (y, x) not in role_ext[q]:
                        role_ext[q].add((y, x))
                        changed = True

        # Inclusion: P ⊆ Q
        for p in ROLE_NAMES:
            for x, y in list(role_ext[p]):
                for q in leq_strict.get(p, set()):
                    if (x, y) not in role_ext[q]:
                        role_ext[q].add((x, y))
                        changed = True

        # Property chains: P∘Q ⊆ R
        for p, q, r in chains:
            # P: x->y, Q: y->z ⇒ R: x->z
            pairs_p = list(role_ext[p])
            pairs_q = list(role_ext[q])
            for x, y in pairs_p:
                for y2, z in pairs_q:
                    if y2 == y and (x, z) not in role_ext[r]:
                        role_ext[r].add((x, z))
                        changed = True

        # Transitivity
        for p in transitive_roles:
            pairs = list(role_ext[p])
            for x, y in pairs:
                for y2, z in pairs:
                    if y2 == y and (x, z) not in role_ext[p]:
                        role_ext[p].add((x, z))
                        changed = True

    return role_ext


def compute_class_memberships(
    role_ext: Dict[Role, Set[Pair]],
    domain: Dict[Role, Set[Cls]],
    range_: Dict[Role, Set[Cls]],
    subclass_sup: Dict[Cls, Set[Cls]],
) -> Dict[Cls, Set[str]]:
    """
    Compute unary class memberships from role extension + typing + subclass:

        holds1(C,x) :- Domain(P,C), holds2(P,x,y).
        holds1(C,y) :- Range(P,C),  holds2(P,x,y).
        holds1(D,x) :- SubClassOf(C,D), holds1(C,x).
    """
    class_ext: Dict[Cls, Set[str]] = defaultdict(set)

    # From Domain / Range
    for p, pairs in role_ext.items():
        for x, y in pairs:
            for c in domain.get(p, set()):
                class_ext[c].add(x)
            for c in range_.get(p, set()):
                class_ext[c].add(y)

    # SubClassOf closure: push instances up the hierarchy
    closed: Dict[Cls, Set[str]] = defaultdict(set)
    for c, inds in class_ext.items():
        closed[c].update(inds)
        for sup in subclass_sup.get(c, set()):
            closed[sup].update(inds)

    return dict(closed)


# =====================
#  High-level Model API
# =====================

@dataclass
class RoleHierarchyModel:
    individuals: IND
    role_ext: Dict[Role, Set[Pair]]
    class_ext: Dict[Cls, Set[str]]
    leq_strict: Dict[Role, Set[Role]]
    leq: Dict[Role, Set[Role]]
    domain: Dict[Role, Set[Cls]]
    range: Dict[Role, Set[Cls]]


def build_model() -> RoleHierarchyModel:
    """Build the logical model using specialized closure functions."""
    # Base role facts
    role_ext = base_role_extensions()

    # Role hierarchy & meta-knowledge
    leq_strict = closure_subrel_of(SUB_RELOF)
    leq = closure_leq(leq_strict)
    inverse_of = compute_inverse_map(INVERSE_BASE)

    # Domain / Range propagation
    domain, range_ = propagate_domain_range(
        DOMAIN_BASE, RANGE_BASE, leq_strict, inverse_of
    )

    # Role-level saturation
    role_ext = saturate_roles(
        role_ext,
        leq_strict,
        inverse_of,
        SYMMETRIC,
        TRANSITIVE,
        SUBREL_CHAIN,
    )

    # Class hierarchy
    subclass_sup = closure_subclass(SUBCLASS_BASE)

    # Unary class memberships
    class_ext = compute_class_memberships(role_ext, domain, range_, subclass_sup)

    return RoleHierarchyModel(
        individuals=D,
        role_ext=role_ext,
        class_ext=class_ext,
        leq_strict=leq_strict,
        leq=leq,
        domain=domain,
        range=range_,
    )


# =====================
#  Questions Q1–Q5
# =====================

def q1_ancestor_pairs(m: RoleHierarchyModel) -> List[Pair]:
    """Q1: enumerate all (x,y) with holds2(ancestorOf,x,y)."""
    return sorted(m.role_ext.get(ancestorOf, set()))


def q2_witness_roles(m: RoleHierarchyModel) -> List[Role]:
    """
    Q2: Witness role-names R such that:

        leq(R, advises) ∧ holds2(R, Grace, Erin)
    """
    result: Set[Role] = set()
    for r in ROLE_NAMES:
        if advises in m.leq.get(r, set()) and ("Grace", "Erin") in m.role_ext.get(r, set()):
            result.add(r)
    return sorted(result)


def q3_typing_ok(m: RoleHierarchyModel) -> bool:
    """
    Q3: Typing check:

        ∀y, if holds2(advises,Grace,y) then Professor(Grace) ∧ Student(y)?
    """
    advisees = {y for (x, y) in m.role_ext.get(advises, set()) if x == "Grace"}
    # check Professor(Grace)
    if "Grace" not in m.class_ext.get(Professor, set()):
        return False
    # check Student(y) for all advisees
    for y in advisees:
        if y not in m.class_ext.get(Student, set()):
            return False
    return True


def q4_childOf_inverse(m: RoleHierarchyModel) -> Tuple[Set[Pair], Set[Pair]]:
    """
    Q4: Inverse check.

    Return:
        (childOf_pairs, parentOf_inverse_pairs)
    """
    child_pairs = set(m.role_ext.get(childOf, set()))
    parent_inv = {(b, a) for (a, b) in m.role_ext.get(parentOf, set())}
    return child_pairs, parent_inv


def q5_symmetry_ok(m: RoleHierarchyModel) -> bool:
    """
    Q5: Symmetry check:

        marriedTo(Erin,Frank) ⇒ marriedTo(Frank,Erin)?
    """
    return ("Frank", "Erin") in m.role_ext.get(marriedTo, set())


# =====================
#  Presentation helpers
# =====================

def local(name: str) -> str:
    return name.split(":", 1)[1] if ":" in name else name


def fmt_pairs(pairs: Iterable[Pair]) -> str:
    seq = sorted(pairs)
    return "∅" if not seq else "{" + ", ".join(f"⟨{a},{b}⟩" for (a, b) in seq) + "}"


def fmt_set(names: Iterable[str]) -> str:
    seq = sorted(local(n) for n in set(names))
    return "∅" if not seq else "{" + ", ".join(seq) + "}"


# =====================
#  Printing
# =====================

def print_model() -> None:
    print("Model")
    print("=====")
    print(f"Individuals D = {list(D)}\n")

    print("Relations and typing (after closure)")
    print("------------------------------------")
    print("parentOf  =", fmt_pairs(m.role_ext[parentOf]))
    print("childOf   =", fmt_pairs(m.role_ext[childOf]))
    print("ancestorOf=", fmt_pairs(m.role_ext[ancestorOf]))
    print("marriedTo =", fmt_pairs(m.role_ext[marriedTo]))
    print("teaches   =", fmt_pairs(m.role_ext[teaches]))
    print("supervises=", fmt_pairs(m.role_ext[supervises]))
    print("advises   =", fmt_pairs(m.role_ext[advises]), "\n")

    print("Class extensions:")
    for c in sorted(CLASS_NAMES):
        print(f"  {local(c):9s} =", sorted(m.class_ext.get(c, set())))
    print()


def print_question() -> None:
    print("Question")
    print("========")
    print("Q1) List all (x,y) with holds2(ancestorOf,x,y).")
    print("Q2) ∃R: leq(R,advises) ∧ holds2(R,Grace,Erin) ? (witness names)")
    print("Q3) ∀y: holds2(advises,Grace,y) → Professor(Grace) ∧ Student(y) ?")
    print("Q4) Inverse check: list (x,y) with childOf(x,y) and compare to parentOf⁻¹.")
    print("Q5) Symmetry check: marriedTo(Erin,Frank) ⇒ marriedTo(Frank,Erin).\n")


def run_queries(m: RoleHierarchyModel):
    anc_pairs = q1_ancestor_pairs(m)
    witnesses = q2_witness_roles(m)
    typing_ok = q3_typing_ok(m)
    child_pairs, parent_inv = q4_childOf_inverse(m)
    sym_ok = q5_symmetry_ok(m)

    return (
        ("Q1", anc_pairs),
        ("Q2", witnesses),
        ("Q3", typing_ok),
        ("Q4", child_pairs, parent_inv),
        ("Q5", sym_ok),
    )


def print_answer(res1, res2, res3, res4, res5) -> None:
    print("Answer")
    print("======")

    tag1, anc = res1
    tag2, wits = res2
    tag3, ok = res3
    tag4, child_pairs, parent_inv = res4
    tag5, sym_ok = res5

    print(f"{tag1}) ancestorOf =", fmt_pairs(anc))
    print(f"{tag2}) Witness role-names R = {fmt_set(wits) if wits else '∅'}")
    print(f"{tag3}) Typing statement holds: {'Yes' if ok else 'No'}")
    print(f"{tag4}) childOf pairs         = {fmt_pairs(child_pairs)}")
    print(f"    parentOf⁻¹ expected   = {fmt_pairs(parent_inv)}")
    print(f"{tag5}) Symmetry consequence Frank↔Erin: {'Yes' if sym_ok else 'No'}\n")


def print_reason() -> None:
    print("Reason why")
    print("==========")
    print("• Role inclusions (SubRelOf) are closed transitively and used to lift pairs.")
    print("• Inverses & symmetry are handled by explicit pair-generation over role_ext.")
    print("• Transitivity on ancestorOf closes ancestor chains; parentOf∘parentOf ⊆ ancestorOf")
    print("  is handled via a dedicated property-chain step.")
    print("• Domain/Range typing and SubClassOf propagate unary class membership.")
    print("• No generic logic engine is used: just specialized set/dict closures.\n")


# =====================
#  Checks
# =====================

class CheckFailure(AssertionError):
    pass


def check(c: bool, msg: str):
    if not c:
        raise CheckFailure(msg)


def run_checks(m: RoleHierarchyModel) -> List[str]:
    notes: List[str] = []

    # Expected ancestorOf from the chain
    exp_anc = {
        ("Alice", "Bob"),
        ("Alice", "Carol"),
        ("Alice", "Dave"),
        ("Bob", "Carol"),
        ("Bob", "Dave"),
        ("Carol", "Dave"),
    }

    # 1) ancestorOf closure
    anc = set(m.role_ext[ancestorOf])
    check(anc == exp_anc, f"ancestorOf mismatch: {anc} vs {exp_anc}")
    notes.append("PASS 1: ancestorOf closure is correct.")

    # 2) Q2 witnesses are {supervises, advises}
    wits = set(q2_witness_roles(m))
    check(
        wits == {supervises, advises},
        f"Witness set mismatch: {wits}",
    )
    notes.append("PASS 2: Witness set for Grace→Erin under advises is {supervises, advises}.")

    # 3) Typing property for advises
    check(q3_typing_ok(m), "Typing property for advises failed.")
    notes.append("PASS 3: Typing property holds for advises (Professor/Student).")

    # 4) Inverse correctness childOf = parentOf⁻¹
    child_pairs, parent_inv = q4_childOf_inverse(m)
    check(child_pairs == parent_inv, "childOf inverse mismatch.")
    notes.append("PASS 4: childOf = parentOf⁻¹ holds.")

    # 5) Symmetry of marriedTo
    check(q5_symmetry_ok(m), "Symmetric marriedTo missing reverse.")
    notes.append("PASS 5: Symmetry of marriedTo holds.")

    # 6) SubClassOf propagation: every Student / Professor is a Person
    for c in (Student, Professor):
        for x in m.class_ext.get(c, set()):
            check(
                x in m.class_ext.get(Person, set()),
                f"Subclass propagation failed: {x} in {local(c)} but not in Person.",
            )
    notes.append("PASS 6: SubClassOf propagation to Person holds.")

    # 7) Domain/Range propagation down subroles: teaches/supervises get same typing as advises
    for r in (teaches, supervises):
        check(
            Professor in m.domain.get(r, set()),
            f"Domain propagation failed for {local(r)}.",
        )
        check(
            Student in m.range.get(r, set()),
            f"Range propagation failed for {local(r)}.",
        )
    notes.append("PASS 7: Domain/Range propagate down role hierarchy.")

    # 8) Deterministic pretty-printing of pairs
    s1 = fmt_pairs(sorted(exp_anc))
    s2 = fmt_pairs(sorted(list(exp_anc)))
    check(s1 == s2, "Pretty-printer determinism failed.")
    notes.append("PASS 8: Pretty printing is deterministic.")

    return notes


# =====================
#  Standalone runner
# =====================

def main():
    global m  # so print_model can see it (simple demo style)
    m = build_model()

    print_model()
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

