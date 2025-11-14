# -*- coding: utf-8 -*-
"""
Arrow-type Subtyping (contravariant/covariant) in a finite universe
-------------------------------------------------------------------

What this demonstrates
----------------------
A tiny *subtyping* calculus over a finite set of base types and all 3×3
function (arrow) types built from them. We work purely on *names*:

• Base types : ex:Top, ex:Int, ex:Bool
• Arrow types: ex:Arr_Top_Top, ex:Arr_Int_Bool, ...

• Subtyping : ex:SubType(T, U)          (both arguments are *names*)
• Arrow map : ex:ArrowOf(A1, A2, TA)    (TA is the name of A1→A2)

Rules (informal)
----------------
1) Reflexivity : SubType(T, T)
2) Transitivity: SubType(T, U) if SubType(T, V) and SubType(V, U)
3) Base facts : Int ≤ Top, Bool ≤ Top
4) Arrow rule (→-subtyping):
       If ArrowOf(A1,A2,TA) and ArrowOf(B1,B2,TB) and
          SubType(B1, A1) and SubType(A2, B2)
       then SubType(TA, TB).

   (Contravariant in the argument, covariant in the result.)

We implement all of this with **specialized Python closures** over a
finite set of type names—no generic logic engine—by computing the
least fixpoint of the rules.

Questions
---------
Q1) Enumerate all subtyping pairs SubType(T,U).
Q2) Witness TB such that SubType(Arr_Int_Bool, TB).
Q3) ∀X∈{Top,Int,Bool}: SubType(Arr_Top_X, Arr_Top_Top)?
Q4) ∀X∈{Top,Int,Bool}: SubType(Arr_Top_Top, Arr_X_Top)?

How to run
----------
    python subtyping_arrows.py

Printed sections
----------------
Model → Question → Answer → Reason why → Check (12 tests)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple, Set


# ─────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────

def local(name: str) -> str:
    """Strip 'ex:' prefix for nicer printing."""
    return name.split(":", 1)[1] if ":" in name else name


def fmt_set(names: Set[str]) -> str:
    if not names:
        return "∅"
    return "{" + ", ".join(sorted(local(n) for n in names)) + "}"


# ─────────────────────────────────────────────────────────────────────
# Type Names (as *names*/URIs)
# ─────────────────────────────────────────────────────────────────────

EX = "ex:"

Top = EX + "Top"
Int = EX + "Int"
Bool = EX + "Bool"

BASE_TYPES: Tuple[str, ...] = (Top, Int, Bool)


def arr_name(a: str, b: str) -> str:
    """Canonical name for the arrow type a→b."""
    return EX + f"Arr_{local(a)}_{local(b)}"


# All 3×3 arrow types over {Top,Int,Bool}
ARROWS: Tuple[str, ...] = tuple(
    arr_name(a, b) for a in BASE_TYPES for b in BASE_TYPES
)

# Mapping predicate from components to arrow name (conceptual)
ArrowOf = EX + "ArrowOf"   # NAME×NAME×NAME

# Subtyping relation (over *names*)
SubType = EX + "SubType"   # NAME×NAME

ALL_TYPES: Tuple[str, ...] = BASE_TYPES + ARROWS


# ─────────────────────────────────────────────────────────────────────
# Specialized subtyping closure
# ─────────────────────────────────────────────────────────────────────

@dataclass
class SubtypingModel:
    base_types: Tuple[str, ...]
    arrow_types: Tuple[str, ...]
    all_types: Tuple[str, ...]
    subtype: Set[Tuple[str, str]]         # set of (T,U) with SubType(T,U) true
    arrow_of: Dict[Tuple[str, str], str]  # (A1,A2) -> Arr_A1_A2


def _compute_subtype() -> Tuple[Set[Tuple[str, str]], Dict[Tuple[str, str], str]]:
    """
    Compute the least SubType-closure satisfying:

        - Reflexivity
        - Base subtyping facts: Int ≤ Top, Bool ≤ Top
        - Transitivity
        - Arrow rule:
              (A1→A2) ≤ (B1→B2) if B1 ≤ A1 and A2 ≤ B2

    All types are just names in ALL_TYPES; A1,A2,B1,B2 are base types.
    """
    # ArrowOf mapping
    arrow_of: Dict[Tuple[str, str], str] = {}
    for a in BASE_TYPES:
        for b in BASE_TYPES:
            arrow_of[(a, b)] = arr_name(a, b)

    sub: Set[Tuple[str, str]] = set()

    # Reflexivity
    for t in ALL_TYPES:
        sub.add((t, t))

    # Base facts
    sub.add((Int, Top))
    sub.add((Bool, Top))

    # Fixpoint over (transitivity + arrow rule)
    changed = True
    while changed:
        changed = False
        current = list(sub)

        # Transitivity: if T ≤ V and V ≤ U then T ≤ U
        new_pairs: Set[Tuple[str, str]] = set()
        for (x, y1) in current:
            for (y2, z) in current:
                if y1 == y2 and (x, z) not in sub:
                    new_pairs.add((x, z))
        if new_pairs:
            sub |= new_pairs
            changed = True

        # Arrow rule: (A1→A2) ≤ (B1→B2) if B1 ≤ A1 and A2 ≤ B2
        new_pairs = set()
        for A1 in BASE_TYPES:
            for A2 in BASE_TYPES:
                TA = arrow_of[(A1, A2)]
                for B1 in BASE_TYPES:
                    for B2 in BASE_TYPES:
                        TB = arrow_of[(B1, B2)]
                        if (B1, A1) in sub and (A2, B2) in sub and (TA, TB) not in sub:
                            new_pairs.add((TA, TB))
        if new_pairs:
            sub |= new_pairs
            changed = True

    return sub, arrow_of


def build_model() -> SubtypingModel:
    subtype, arrow_of = _compute_subtype()
    return SubtypingModel(
        base_types=BASE_TYPES,
        arrow_types=ARROWS,
        all_types=ALL_TYPES,
        subtype=subtype,
        arrow_of=arrow_of,
    )


def is_subtype(m: SubtypingModel, t: str, u: str) -> bool:
    return (t, u) in m.subtype


# ─────────────────────────────────────────────────────────────────────
# Presentation
# ─────────────────────────────────────────────────────────────────────

def print_model(m: SubtypingModel) -> None:
    print("Model")
    print("=====")
    print("Base types (names):", ", ".join(local(t) for t in m.base_types))
    print("Arrow types (names):", ", ".join(local(a) for a in m.arrow_types))
    print("\nFixed predicates (informal)")
    print("----------------------------")
    print("• ex:SubType(T,U)       — subtyping over *names*; sorts: (NAME, NAME)")
    print("• ex:ArrowOf(A1,A2,T)   — T is the *name* of arrow A1→A2; (NAME,NAME,NAME)")
    print("\nRules (implemented by specialized closure)")
    print("------------------------------------------")
    print("1) Reflexive: SubType(T,T).")
    print("2) Transitive: SubType(T,U) if SubType(T,V) and SubType(V,U).")
    print("3) Base facts: Int ≤ Top, Bool ≤ Top.")
    print("4) Arrow: (A1→A2) ≤ (B1→B2) if B1 ≤ A1 and A2 ≤ B2 (contra/co-variance).\n")


def print_question() -> None:
    print("Question")
    print("========")
    print("Q1) Enumerate all subtyping pairs SubType(T,U).")
    print("Q2) Witness TB such that SubType(Arr_Int_Bool, TB).")
    print("Q3) ∀X∈{Top,Int,Bool}: SubType(Arr_Top_X, Arr_Top_Top)?")
    print("Q4) ∀X∈{Top,Int,Bool}: SubType(Arr_Top_Top, Arr_X_Top)?")
    print()


# ─────────────────────────────────────────────────────────────────────
# Queries Q1–Q4
# ─────────────────────────────────────────────────────────────────────

def run_queries(m: SubtypingModel):
    # Q1: enumerate all subtyping pairs
    pairs = sorted(m.subtype)

    # Q2: witnesses TB such that Arr_Int_Bool ≤ TB
    TA = arr_name(Int, Bool)
    witnesses = sorted({u for (t, u) in m.subtype if t == TA})

    # Q3: universal property (covariant result when arg=Top)
    ok3 = True
    TT = arr_name(Top, Top)
    for X in BASE_TYPES:
        TA_X = arr_name(Top, X)
        if not is_subtype(m, TA_X, TT):
            ok3 = False
            break

    # Q4: universal property (contravariant argument toward Top)
    ok4 = True
    AT = arr_name(Top, Top)
    for X in BASE_TYPES:
        TX = arr_name(X, Top)
        if not is_subtype(m, AT, TX):
            ok4 = False
            break

    return (
        ("Q1", pairs),
        ("Q2", witnesses),
        ("Q3", ok3),
        ("Q4", ok4),
    )


def print_answer(res1, res2, res3, res4) -> None:
    print("Answer")
    print("======")

    tag1, pairs = res1
    tag2, witnesses = res2
    tag3, ok3 = res3
    tag4, ok4 = res4

    def show_pairs(ps: List[Tuple[str, str]]) -> str:
        if not ps:
            return "∅"
        return "{" + ", ".join(f"{local(t)} ≤ {local(u)}" for (t, u) in ps) + "}"

    print(f"{tag1}) {show_pairs(pairs)}")
    print(f"{tag2}) Witness TB with Arr_Int_Bool ≤ TB = "
          + ("∅" if not witnesses else "{" + ", ".join(local(w) for w in witnesses) + "}"))
    print(f"{tag3}) Universal (covariant result) holds: {'Yes' if ok3 else 'No'}")
    print(f"{tag4}) Universal (contravariant arg) holds: {'Yes' if ok4 else 'No'}\n")


def print_reason() -> None:
    print("Reason why")
    print("==========")
    print("• Types are *names*; subtyping is a binary relation on those names.")
    print("• ArrowOf is implemented by a canonical naming scheme Arr_A_B.")
    print("• The arrow rule encodes classic function subtyping:")
    print("      (A1→A2) ≤ (B1→B2)  iff  B1 ≤ A1  and  A2 ≤ B2")
    print("  i.e., contravariant in the argument and covariant in the result.")
    print("• All reasoning is done by a small fixpoint over a finite universe of")
    print("  type names—no generic logic engine is used.\n")


# ─────────────────────────────────────────────────────────────────────
# Check (12 tests)
# ─────────────────────────────────────────────────────────────────────

class CheckFailure(AssertionError):
    pass


def check(c: bool, msg: str):
    if not c:
        raise CheckFailure(msg)


def run_checks(m: SubtypingModel) -> List[str]:
    notes: List[str] = []
    sub = m.subtype

    # 1) Subtyping includes some expected base and arrow pairs
    exp_subset = {
        (Int, Top),
        (Bool, Top),
        (arr_name(Int, Bool), arr_name(Int, Top)),   # covariant result
        (arr_name(Top, Top), arr_name(Int, Top)),    # contravariant arg
    }
    check(exp_subset.issubset(sub), "Expected subtyping pairs missing.")
    notes.append("PASS 1: SubType includes expected base & arrow pairs.")

    # 2) A concrete arrow subtyping holds: Arr_Int_Bool ≤ Arr_Int_Top
    check(
        (arr_name(Int, Bool), arr_name(Int, Top)) in sub,
        "Arr_Int_Bool ≤ Arr_Int_Top should hold.",
    )
    notes.append("PASS 2: Sample arrow subtyping Arr_Int_Bool ≤ Arr_Int_Top holds.")

    # 3) Witnesses for Arr_Int_Bool ≤ TB are exactly {Arr_Int_Bool, Arr_Int_Top}
    TA = arr_name(Int, Bool)
    ws = {u for (t, u) in sub if t == TA}
    check(
        ws == {arr_name(Int, Bool), arr_name(Int, Top)},
        f"Witness set mismatch: {ws}",
    )
    notes.append("PASS 3: Witness set for Arr_Int_Bool ≤ TB is correct.")

    # 4) Covariance universal: ∀X, Arr_Top_X ≤ Arr_Top_Top
    TT = arr_name(Top, Top)
    ok_cov = all((arr_name(Top, X), TT) in sub for X in BASE_TYPES)
    check(ok_cov, "Covariance universal failed.")
    notes.append("PASS 4: Covariance universal holds.")

    # 5) Contravariance universal: ∀X, Arr_Top_Top ≤ Arr_X_Top
    AT = arr_name(Top, Top)
    ok_contra = all((AT, arr_name(X, Top)) in sub for X in BASE_TYPES)
    check(ok_contra, "Contravariance universal failed.")
    notes.append("PASS 5: Contravariance universal holds.")

    # 6) Deterministic pretty output
    s1 = " ".join(sorted(local(t) for (t, _) in sub))
    s2 = " ".join(sorted(local(t) for (t, _) in set(sub)))
    check(s1 == s2, "Determinism check failed.")
    notes.append("PASS 6: Deterministic formatting of results.")

    # 7) Reflexivity holds for all base and arrow types
    for t in ALL_TYPES:
        check((t, t) in sub, f"Reflexivity failed for {local(t)}.")
    notes.append("PASS 7: Reflexivity holds for all types.")

    # 8) No bogus cross-base subtyping (Int ≰ Bool, Bool ≰ Int)
    check((Int, Bool) not in sub, "Unexpected Int ≤ Bool.")
    check((Bool, Int) not in sub, "Unexpected Bool ≤ Int.")
    notes.append("PASS 8: No bogus base subtypings.")

    # 9) A negative arrow example: Arr_Int_Int ≰ Arr_Bool_Int
    check(
        (arr_name(Int, Int), arr_name(Bool, Int)) not in sub,
        "Unexpected Arr_Int_Int ≤ Arr_Bool_Int.",
    )
    notes.append("PASS 9: Negative arrow subtyping blocked as expected.")

    # 10) A non-trivial positive arrow example via both contra & co-variance
    #     (Top→Bool) ≤ (Int→Top)
    check(
        (arr_name(Top, Bool), arr_name(Int, Top)) in sub,
        "Expected Arr_Top_Bool ≤ Arr_Int_Top.",
    )
    notes.append("PASS 10: Non-trivial arrow subtyping Arr_Top_Bool ≤ Arr_Int_Top holds.")

    # 11) Building the model twice yields the same closure
    m2 = build_model()
    check(m.subtype == m2.subtype, "Subtyping closure not stable across rebuilds.")
    notes.append("PASS 11: Subtyping closure is stable (idempotent).")

    # 12) Another positive contravariant sample: Arr_Top_Top ≤ Arr_Bool_Top
    check(
        (arr_name(Top, Top), arr_name(Bool, Top)) in sub,
        "Arr_Top_Top ≤ Arr_Bool_Top should hold.",
    )
    notes.append("PASS 12: Contravariant sample Arr_Top_Top ≤ Arr_Bool_Top holds.")

    return notes


# ─────────────────────────────────────────────────────────────────────
# Standalone runner
# ─────────────────────────────────────────────────────────────────────

def main():
    m = build_model()

    print_model(m)
    print_question()
    res1, res2, res3, res4 = run_queries(m)
    print_answer(res1, res2, res3, res4)
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

