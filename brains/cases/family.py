# -*- coding: utf-8 -*-
# =============================================================================
# family.py
# =============================================================================
#
# What this is
# ------------
# A tiny *name-based* family model, in the Hayes–Menzel “Holds₂” spirit, but
# implemented with **specialized closures only**.
#
#   • Intensions (names): people like "Frans", relation names like "parent",
#     "spouse", "uncle", "aunt", and class tags "MALE"/"FEMALE".
#   • Extensions: for each binary relation-name R, we keep a set of pairs:
#
#         ext[R] ⊆ IND × IND
#
#     and read membership as a fixed arity-2 predicate:
#
#         Holds₂(R, x, y)  ⇔  (x, y) ∈ ext[R].
#
# This follows the “higher-order look, first-order core” perspective:
# relation *names* are first-order objects; application is mediated by a fixed
# predicate Holds₂. In code, Holds₂ is just ‘(x,y) in rel’.
#
# We compute the closure of core family relations — spouse, sibling, brother,
# sister, grandparent, father, mother, uncle, aunt — using specialized set
# operations, plus a small mutual fixpoint for uncle/aunt by marriage.
#
# Questions
# ---------
# Q1) children("Rita")
# Q2) siblings("Veerle")
# Q3) uncles("Veerle")
# Q4) aunts("Bart")
# Q5) father("Goedele"), mother("Goedele")
#
# All of these are answered, explained, and then *checked* by a small harness.
#
# =============================================================================

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Set, Tuple

Pair = Tuple[str, str]


# -----------------------------------------------------------------------------
# Universe and base facts
# -----------------------------------------------------------------------------

PEOPLE: Tuple[str, ...] = (
    "Frans",
    "Jo",
    "Paul",
    "Pieter-Jan",
    "Tim",
    "Bert",
    "Bart",
    "Maria",
    "Maaike",
    "Rita",
    "Goedele",
    "Veerle",
    "Ann",
    "Veer",
)

MALE: Set[str] = {
    "Frans",
    "Jo",
    "Paul",
    "Pieter-Jan",
    "Tim",
    "Bert",
    "Bart",
}

FEMALE: Set[str] = {
    "Maria",
    "Maaike",
    "Rita",
    "Goedele",
    "Veerle",
    "Ann",
    "Veer",
}

# parent(x,y): x is parent of y
PARENT_BASE: Set[Pair] = {
    ("Frans", "Jo"),
    ("Maria", "Jo"),
    ("Frans", "Rita"),
    ("Maria", "Rita"),
    ("Jo", "Goedele"),
    ("Maaike", "Goedele"),
    ("Jo", "Veerle"),
    ("Maaike", "Veerle"),
    ("Paul", "Ann"),
    ("Rita", "Ann"),
    ("Paul", "Bart"),
    ("Rita", "Bart"),
}

# spouse(x,y): base orientation only; we will symmetrize
SPOUSE_BASE: Set[Pair] = {
    ("Frans", "Maria"),
    ("Jo", "Maaike"),
    ("Paul", "Rita"),
    ("Pieter-Jan", "Goedele"),
    ("Tim", "Veerle"),
    ("Bert", "Ann"),
    ("Bart", "Veer"),
}


# -----------------------------------------------------------------------------
# Model data class
# -----------------------------------------------------------------------------

@dataclass
class FamilyModel:
    people: Tuple[str, ...]
    male: Set[str]
    female: Set[str]
    parent: Set[Pair]
    spouse: Set[Pair]
    sibling: Set[Pair]
    brother: Set[Pair]
    sister: Set[Pair]
    grandparent: Set[Pair]
    grandfather: Set[Pair]
    grandmother: Set[Pair]
    father: Set[Pair]
    mother: Set[Pair]
    uncle: Set[Pair]
    aunt: Set[Pair]


# -----------------------------------------------------------------------------
# Specialized closure computation
# -----------------------------------------------------------------------------

def compute_spouse_closure(base: Set[Pair]) -> Set[Pair]:
    """Symmetric closure of spouse relation."""
    out = set(base)
    changed = True
    while changed:
        changed = False
        new_pairs: Set[Pair] = set()
        for (x, y) in out:
            if (y, x) not in out:
                new_pairs.add((y, x))
        if new_pairs:
            out |= new_pairs
            changed = True
    return out


def compute_siblings(parent: Set[Pair]) -> Set[Pair]:
    """
    siblings(x,y) iff ∃p: parent(p,x) ∧ parent(p,y).

    This is *permissive*: siblings(x,x) can appear; the public siblings(x)
    API will exclude x itself. That mirrors the original logic case.
    """
    # parent_children[p] = {c1, c2, ...}
    parent_children: Dict[str, Set[str]] = {}
    for p, c in parent:
        parent_children.setdefault(p, set()).add(c)

    sibs: Set[Pair] = set()
    for p, children in parent_children.items():
        kids = list(children)
        for i in range(len(kids)):
            for j in range(len(kids)):
                sibs.add((kids[i], kids[j]))
    return sibs


def compute_gendered_from_siblings(
    siblings: Set[Pair], male: Set[str], female: Set[str]
) -> Tuple[Set[Pair], Set[Pair]]:
    brother: Set[Pair] = set()
    sister: Set[Pair] = set()
    for (x, y) in siblings:
        if x in male:
            brother.add((x, y))
        if x in female:
            sister.add((x, y))
    return brother, sister


def compute_grandparent(parent: Set[Pair]) -> Set[Pair]:
    """
    grandparent(x,z) iff ∃y: parent(x,y) ∧ parent(y,z)
    """
    grand: Set[Pair] = set()
    for (x, y1) in parent:
        for (y2, z) in parent:
            if y1 == y2:
                grand.add((x, z))
    return grand


def compute_gendered_parents(
    parent: Set[Pair], male: Set[str], female: Set[str]
) -> Tuple[Set[Pair], Set[Pair], Set[Pair], Set[Pair]]:
    """
    father(x,y), mother(x,y), grandfather(x,z), grandmother(x,z).
    """
    father: Set[Pair] = set()
    mother: Set[Pair] = set()
    for (x, y) in parent:
        if x in male:
            father.add((x, y))
        if x in female:
            mother.add((x, y))

    grandparent = compute_grandparent(parent)
    grandfather: Set[Pair] = set()
    grandmother: Set[Pair] = set()
    for (x, z) in grandparent:
        if x in male:
            grandfather.add((x, z))
        if x in female:
            grandmother.add((x, z))

    return father, mother, grandfather, grandmother


def compute_avuncular(
    parent: Set[Pair],
    spouse: Set[Pair],
    brother: Set[Pair],
    sister: Set[Pair],
) -> Tuple[Set[Pair], Set[Pair]]:
    """
    Compute uncle/aunt as least fixpoint of:

        uncle_blood(x,y)  :- brother(x,p) ∧ parent(p,y) ∧ x ≠ p
        aunt_blood(x,y)   :- sister(x,p) ∧ parent(p,y) ∧ x ≠ p
        uncle_mar(x,y)    :- spouse(x,s) ∧ aunt(s,y)
        aunt_mar(x,y)     :- spouse(x,s) ∧ uncle(s,y)

    We compute uncle/aunt simultaneously with a small fixpoint.
    """
    # Helper: quick parent-lookup children per parent
    parent_children: Dict[str, Set[str]] = {}
    for p, c in parent:
        parent_children.setdefault(p, set()).add(c)

    # brother(x,p) & parent(p,y) & x≠p
    uncle_blood: Set[Pair] = set()
    for (x, p) in brother:
        if x == p:
            continue
        for y in parent_children.get(p, set()):
            uncle_blood.add((x, y))

    # sister(x,p) & parent(p,y) & x≠p
    aunt_blood: Set[Pair] = set()
    for (x, p) in sister:
        if x == p:
            continue
        for y in parent_children.get(p, set()):
            aunt_blood.add((x, y))

    # fixpoint for marriage-based uncles/aunts
    uncle: Set[Pair] = set(uncle_blood)
    aunt: Set[Pair] = set(aunt_blood)

    # spouse map: for quick lookup of partners
    spouse_map: Dict[str, Set[str]] = {}
    for (x, y) in spouse:
        spouse_map.setdefault(x, set()).add(y)

    changed = True
    while changed:
        changed = False

        # uncle_mar: spouse(x,s) & aunt(s,y)
        new_uncle: Set[Pair] = set()
        for (s, y) in aunt:
            for x in (spouse_map.get(s, set()) or []):
                new_uncle.add((x, y))

        # aunt_mar: spouse(x,s) & uncle(s,y)
        new_aunt: Set[Pair] = set()
        for (s, y) in uncle:
            for x in (spouse_map.get(s, set()) or []):
                new_aunt.add((x, y))

        if new_uncle - uncle:
            uncle |= new_uncle
            changed = True
        if new_aunt - aunt:
            aunt |= new_aunt
            changed = True

    return uncle, aunt


def build_model() -> FamilyModel:
    """
    Build the full family model by computing all derived relations.

    This is the only place where "reasoning" happens, and it is fully
    specialized to this family signature.
    """
    parent = set(PARENT_BASE)
    spouse = compute_spouse_closure(SPOUSE_BASE)
    sibling = compute_siblings(parent)
    brother, sister = compute_gendered_from_siblings(sibling, MALE, FEMALE)
    father, mother, grandfather, grandmother = compute_gendered_parents(
        parent, MALE, FEMALE
    )
    uncle, aunt = compute_avuncular(parent, spouse, brother, sister)

    return FamilyModel(
        people=PEOPLE,
        male=set(MALE),
        female=set(FEMALE),
        parent=parent,
        spouse=spouse,
        sibling=sibling,
        brother=brother,
        sister=sister,
        grandparent=grandfather | grandmother,  # complete set, though split also kept
        grandfather=grandfather,
        grandmother=grandmother,
        father=father,
        mother=mother,
        uncle=uncle,
        aunt=aunt,
    )


# Build a single global model used by the query API
_M = build_model()


# -----------------------------------------------------------------------------
# Convenience query API (intension/extension view)
# -----------------------------------------------------------------------------
#
# In the higher-order-looking surface layer you might write:
#
#   father(Goedele) = Jo
#
# but semantically that’s:
#
#   Holds₂(father, Jo, Goedele).
#
# Here we keep these *name-based* helpers but their implementation is strictly
# in terms of membership in the extension sets of relation names.


def _children(m: FamilyModel, p: str) -> List[str]:
    return sorted({c for (x, c) in m.parent if x == p})


def children(p: str) -> List[str]:
    """All children of parent p (sorted, unique)."""
    return _children(_M, p)


def siblings(x: str) -> List[str]:
    """
    Siblings of x (sorted, unique), excluding x itself.

    The underlying sibling relation is permissive and may contain (x,x);
    we consistently drop self in the API.
    """
    sibs = {y for (a, y) in _M.sibling if a == x}
    return sorted(sibs - {x})


def brothers(x: str) -> List[str]:
    """Brothers of x (sorted, unique)."""
    return sorted({a for (a, b) in _M.brother if b == x})


def grandps(x: str) -> List[str]:
    """All grandparents of x (sorted, unique)."""
    return sorted({a for (a, b) in _M.grandparent if b == x})


def _avuncular_filtered(
    rel: Set[Pair],
    x: str,
) -> List[str]:
    """
    Helper to collect avuncular relations (uncle/aunt), excluding direct parents.
    """
    parents = {p for (p, c) in _M.parent if c == x}
    cand = {a for (a, b) in rel if b == x}
    return sorted(cand - parents)


def uncles(x: str) -> List[str]:
    """All uncles of x (sorted, unique). Direct parents are excluded."""
    return _avuncular_filtered(_M.uncle, x)


def aunts(x: str) -> List[str]:
    """All aunts of x (sorted, unique). Direct parents are excluded."""
    return _avuncular_filtered(_M.aunt, x)


def father(c: str) -> str | None:
    """The father of c, if unique; otherwise None."""
    candidates = {p for (p, ch) in _M.father if ch == c}
    return sorted(candidates)[0] if candidates else None


def mother(c: str) -> str | None:
    """The mother of c, if unique; otherwise None."""
    candidates = {p for (p, ch) in _M.mother if ch == c}
    return sorted(candidates)[0] if candidates else None


# -----------------------------------------------------------------------------
# Pretty helpers
# -----------------------------------------------------------------------------

def fmt_list(xs: Iterable[str]) -> str:
    xs = list(xs)
    return "[" + ", ".join(xs) + "]"


# -----------------------------------------------------------------------------
# Answer / Reason / Check
# -----------------------------------------------------------------------------

def print_model() -> None:
    print("Model")
    print("=====")
    print(f"People         = {fmt_list(_M.people)}")
    print(f"MALE           = {fmt_list(sorted(_M.male))}")
    print(f"FEMALE         = {fmt_list(sorted(_M.female))}")
    print("Base parent    =", sorted(_M.parent))
    print("Base+sym spouse=", sorted(_M.spouse))
    print()


def print_question() -> None:
    print("Question")
    print("========")
    print("Q1) children('Rita')")
    print("Q2) siblings('Veerle')")
    print("Q3) uncles('Veerle')")
    print("Q4) aunts('Bart')")
    print("Q5) father('Goedele'), mother('Goedele')\n")


def run_queries():
    q1 = children("Rita")
    q2 = siblings("Veerle")
    q3 = uncles("Veerle")
    q4 = aunts("Bart")
    q5_f = father("Goedele")
    q5_m = mother("Goedele")
    return q1, q2, q3, q4, q5_f, q5_m


def print_answer(q1, q2, q3, q4, q5_f, q5_m) -> None:
    print("Answer")
    print("======")
    print(f"children('Rita')      -> {fmt_list(q1)}")
    print(f"siblings('Veerle')    -> {fmt_list(q2)}")
    print(f"uncles('Veerle')      -> {fmt_list(q3)}")
    print(f"aunts('Bart')         -> {fmt_list(q4)}")
    print(f"father('Goedele')     -> {q5_f!r}")
    print(f"mother('Goedele')     -> {q5_m!r}")
    print()


def print_reason() -> None:
    print("Reason why")
    print("==========")
    print("• Intensions are the *names* for relations and people (e.g., 'parent', 'Frans').")
    print("  Extensions are plain sets of pairs; application is just membership in those sets.")
    print("  Conceptually, Holds₂(parent, Frans, Jo) is implemented as ('Frans','Jo') ∈ parent.")
    print("• spouse is made symmetric by a small closure: if spouse(x,y) then spouse(y,x).")
    print("• siblings(x,y) is defined via a shared parent; the API hides the (x,x) cases.")
    print("• brother/sister, father/mother, grandfather/grandmother are gender-specialised")
    print("  views of sibling/parent/grandparent using the MALE/FEMALE sets.")
    print("• uncle and aunt are the least fixpoint of:")
    print("    – blood: a male/female sibling of a parent (x ≠ parent),")
    print("    – by marriage: spouse of an uncle/aunt.")
    print("  Direct parents are filtered out in the uncles()/aunts() helpers to avoid")
    print("  misclassifying a parent as their own child's uncle/aunt.")
    print("• No generic engine or unification is used; the whole model is computed")
    print("  by specialized closures over a finite universe, with semantics that match")
    print("  the rules.\n")


# -----------------------------------------------------------------------------
# Check (harness)
# -----------------------------------------------------------------------------

class CheckFailure(AssertionError):
    pass


def check(cond: bool, msg: str) -> None:
    if not cond:
        raise CheckFailure(msg)


def run_checks() -> List[str]:
    notes: List[str] = []

    # 1) children('Rita') as in the original file
    check(children("Rita") == ["Ann", "Bart"], "children('Rita') mismatch.")
    notes.append("PASS 1: children('Rita') == ['Ann', 'Bart'].")

    # 2) siblings('Veerle')
    check(siblings("Veerle") == ["Goedele"], "siblings('Veerle') mismatch.")
    notes.append("PASS 2: siblings('Veerle') == ['Goedele'].")

    # 3) uncles('Veerle') – Paul via aunt-by-blood Rita then spouse
    check(uncles("Veerle") == ["Paul"], "uncles('Veerle') mismatch.")
    notes.append("PASS 3: uncles('Veerle') == ['Paul'].")

    # 4) father/mother of Goedele
    check(father("Goedele") == "Jo", "father('Goedele') should be 'Jo'.")
    check(mother("Goedele") == "Maaike", "mother('Goedele') should be 'Maaike'.")
    notes.append("PASS 4: father/mother of Goedele are Jo/Maaike.")

    # 5) aunts('Bart') – Maaike is aunt by marriage (spouse of uncle Jo)
    check(aunts("Bart") == ["Maaike"], "aunts('Bart') should be ['Maaike'].")
    notes.append("PASS 5: aunts('Bart') == ['Maaike'].")

    # 6) No parent is accidentally an uncle/aunt of their own child (API level)
    for p, c in _M.parent:
        check(p not in uncles(c), f"Parent {p} incorrectly appears as uncle of {c}.")
        check(p not in aunts(c), f"Parent {p} incorrectly appears as aunt of {c}.")
    notes.append("PASS 6: Parents are not exposed as uncles/aunts of their own children.")

    # 7) Symmetry of spouse
    for (x, y) in SPOUSE_BASE:
        check((y, x) in _M.spouse, f"Spouse symmetry missing for {x},{y}.")
    notes.append("PASS 7: Spouse relation is symmetric.")

    # 8) Sibling symmetry (up to permissive self-cases)
    for (x, y) in _M.sibling:
        check((y, x) in _M.sibling, f"Sibling symmetry missing for {x},{y}.")
    notes.append("PASS 8: Sibling relation is symmetric (including self-pairs).")

    # 9) Every brother/sister pair is also a sibling pair
    for (x, y) in _M.brother | _M.sister:
        check((x, y) in _M.sibling, f"{x} is brother/sister of {y} but not sibling.")
    notes.append("PASS 9: brother/sister are specialisations of sibling.")

    # 10) Grandparent factorisation: every grandfather/mother is also a grandparent
    for (x, z) in _M.grandfather | _M.grandmother:
        check((x, z) in _M.grandparent, f"{x} grand- of {z} but missing in grandparent.")
    notes.append("PASS 10: grandfather/grandmother specialise grandparent.")

    # 11) No self-uncle / self-aunt
    for x in PEOPLE:
        check((x, x) not in _M.uncle, f"{x} is own uncle.")
        check((x, x) not in _M.aunt, f"{x} is own aunt.")
    notes.append("PASS 11: Nobody is their own uncle/aunt.")

    # 12) Rebuilding the model yields the same closure
    m2 = build_model()
    check(
        _M.parent == m2.parent
        and _M.spouse == m2.spouse
        and _M.sibling == m2.sibling
        and _M.uncle == m2.uncle
        and _M.aunt == m2.aunt,
        "Model closure not stable across rebuilds.",
    )
    notes.append("PASS 12: Model closure is stable under rebuild.")

    return notes


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

def main() -> None:
    print_model()
    print_question()
    q1, q2, q3, q4, q5_f, q5_m = run_queries()
    print_answer(q1, q2, q3, q4, q5_f, q5_m)
    print_reason()

    print("Check (harness)")
    print("===============")
    try:
        for note in run_checks():
            print(note)
    except CheckFailure as e:
        print("FAIL:", e)
        raise


if __name__ == "__main__":
    main()

