#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
matrix_products_worlds.py
=========================

Four worlds of 2×2 matrices and two “theorems”
----------------------------------------------
This script explores how *matrix multiplication* behaves when we change the
underlying product, while keeping the same set of 2×2 real matrices and the
same entrywise addition.

We build four “worlds”, each with its own binary product ⊗ on 2×2 matrices:

  World 0: standard matrix product
    (A ⊗₀ B) = A · B      (usual linear algebra)

  World 1: Hadamard (entrywise) product
    (A ⊗₁ B) = A ◦ B      where (A ◦ B)ᵢⱼ = Aᵢⱼ · Bᵢⱼ

  World 2: symmetric (Jordan-like) product
    (A ⊗₂ B) = A·B + B·A  (AB + BA, not in general associative)

  World 3: deliberately broken product
    (A ⊗₃ B) = A·B + A    (non-associative and not distributive)

All worlds share the same addition ⊕, namely entrywise sum of matrices.

We then look at two algebraic properties of the product:

  (AssocMult)    associativity of multiplication
                   ∀A,B,C: (A⊗B)⊗C = A⊗(B⊗C)

  (DistLeft)     left distributivity over addition
                   ∀A,B,C: A⊗(B⊕C) = (A⊗B) ⊕ (A⊗C)


Higher-order look, first-order core
-----------------------------------
Following the “higher-order look, first-order core” pattern
(https://josd.github.io/higher-order-look-first-order-core/):

  • First-order core:
      - concrete 2×2 matrices with real entries (represented as Python floats),
      - fixed addition ⊕ (entrywise),
      - four concrete products ⊗₀, ⊗₁, ⊗₂, ⊗₃ implemented as functions,
      - random testing of the equations for AssocMult and DistLeft in each
        world using small integer entries.

  • Higher-order look:
      - worlds are integers w ∈ {0,1,2,3},
      - theorem-names are unary predicates on worlds:
            thm:AssocMult
            thm:DistLeft
      - a single unary predicate

            Holds₁(P, w)

        is read extensionally from a table EXT1, meaning:
            Holds1(P, w)  ⇔  world w empirically satisfies theorem P,

        i.e., all sampled triples (or pairs) in world w satisfy the equation.

      - a binary relation-name:

            rel:stronger

        relates theorem-intensions by:

            Holds₂("rel:stronger", thm:AssocMult, thm:DistLeft)

        to reflect the idea that, in this tiny universe, whenever multiplication
        is associative in a world, it is also left-distributive there.

        Implementation detail:
          EXT2["rel:stronger"] = { (thm:AssocMult, thm:DistLeft) } and
          Holds2(R, X, Y) ⇔ (X, Y) ∈ EXT2[R].

There is no external reasoner. All semantics are in the first-order core:
concrete matrix arithmetic and random testing. Holds₁ and Holds₂ merely read
off the resulting extensional model (EXT1, EXT2).


What the script prints
----------------------
Running:

    python3 matrix_products_worlds.py

prints three ARC-style sections:

  1) Answer
     • describes the four worlds and two “theorems”,
     • prints a table of empirical stats per world:
           world | product description         | Assoc (ok/total) | DistLeft (ok/total)
     • and shows several Holds₁ judgements.

  2) Reason why
     • explains the four products and their algebraic behaviour in plain
       matrix algebra terms,
     • and explains how the Holds₁ / Holds₂ picture is constructed.

  3) Check (harness)
     • at least six independent tests checking that:
         - basic matrix arithmetic behaves as expected,
         - worlds 0 and 1 are associative (and pass left-distributivity),
         - world 2 fails associativity but still satisfies left-distributivity,
         - world 3 fails both properties,
         - EXT1 / Holds₁ match the statistics, and
         - the Holds₂ “stronger” relation is respected:
             whenever Holdings1(thm:AssocMult, w) is true, so is Holds1(thm:DistLeft, w).

Python 3.9+; no external packages.
"""

from __future__ import annotations

from random import randrange, seed
from typing import Dict, List, Tuple, Set

seed(0)  # deterministic randomness for reproducible behaviour

Matrix = Tuple[Tuple[float, float], Tuple[float, float]]


# -----------------------------------------------------------------------------
# Basic 2×2 matrix utilities
# -----------------------------------------------------------------------------

def mat(a11: float, a12: float, a21: float, a22: float) -> Matrix:
    return ((float(a11), float(a12)), (float(a21), float(a22)))


def mat_zero() -> Matrix:
    return mat(0.0, 0.0, 0.0, 0.0)


def mat_identity() -> Matrix:
    return mat(1.0, 0.0, 0.0, 1.0)


def mat_add(A: Matrix, B: Matrix) -> Matrix:
    return (
        (A[0][0] + B[0][0], A[0][1] + B[0][1]),
        (A[1][0] + B[1][0], A[1][1] + B[1][1]),
    )


def mat_std_mul(A: Matrix, B: Matrix) -> Matrix:
    """Standard matrix product A·B."""
    a11, a12 = A[0]
    a21, a22 = A[1]
    b11, b12 = B[0]
    b21, b22 = B[1]
    return (
        (a11 * b11 + a12 * b21, a11 * b12 + a12 * b22),
        (a21 * b11 + a22 * b21, a21 * b12 + a22 * b22),
    )


def mat_hadamard(A: Matrix, B: Matrix) -> Matrix:
    """Entrywise (Hadamard) product."""
    return (
        (A[0][0] * B[0][0], A[0][1] * B[0][1]),
        (A[1][0] * B[1][0], A[1][1] * B[1][1]),
    )


def mat_equal(A: Matrix, B: Matrix, tol: float = 1e-9) -> bool:
    return (
        abs(A[0][0] - B[0][0]) <= tol and
        abs(A[0][1] - B[0][1]) <= tol and
        abs(A[1][0] - B[1][0]) <= tol and
        abs(A[1][1] - B[1][1]) <= tol
    )


def random_matrix_int(max_abs: int = 3) -> Matrix:
    """Matrix with integer entries in [-max_abs, max_abs]."""
    return mat(
        randrange(-max_abs, max_abs + 1),
        randrange(-max_abs, max_abs + 1),
        randrange(-max_abs, max_abs + 1),
        randrange(-max_abs, max_abs + 1),
    )


# -----------------------------------------------------------------------------
# World-specific multiplication
# -----------------------------------------------------------------------------

WORLD_IDS = (0, 1, 2, 3)

WORLD_DESCRIPTIONS: Dict[int, str] = {
    0: "standard product A·B",
    1: "Hadamard product A∘B",
    2: "symmetric AB+BA",
    3: "broken AB+A",
}


def mat_mul_world(A: Matrix, B: Matrix, world: int) -> Matrix:
    """
    World-specific binary product ⊗₍world₎ on matrices.

      world 0: A ⊗₀ B = A·B
      world 1: A ⊗₁ B = A∘B  (Hadamard)
      world 2: A ⊗₂ B = A·B + B·A
      world 3: A ⊗₃ B = A·B + A
    """
    if world == 0:
        return mat_std_mul(A, B)
    if world == 1:
        return mat_hadamard(A, B)
    if world == 2:
        return mat_add(mat_std_mul(A, B), mat_std_mul(B, A))
    if world == 3:
        return mat_add(mat_std_mul(A, B), A)
    raise ValueError(f"Unknown world id {world!r}")


# -----------------------------------------------------------------------------
# Empirical tests: associativity and left-distributivity
# -----------------------------------------------------------------------------

TRIALS_PER_WORLD = 200


def test_associativity(world: int, trials: int) -> Tuple[int, int]:
    """
    Empirically test associativity:

        (A⊗B)⊗C = A⊗(B⊗C)

    Returns (ok_count, total_count).
    """
    ok = 0
    total = 0

    # For worlds 2 and 3, include a known *failing* triple deterministically.
    if world == 2:
        # A=E11, B=E12, C=E21
        A = mat(1, 0, 0, 0)
        B = mat(0, 1, 0, 0)
        C = mat(0, 0, 1, 0)
        left = mat_mul_world(mat_mul_world(A, B, world), C, world)
        right = mat_mul_world(A, mat_mul_world(B, C, world), world)
        if mat_equal(left, right):
            ok += 1
        total += 1  # this should be a failing example

    if world == 3:
        # A=I, B=I, C=I is non-associative for AB+A
        A = mat_identity()
        B = mat_identity()
        C = mat_identity()
        left = mat_mul_world(mat_mul_world(A, B, world), C, world)
        right = mat_mul_world(A, mat_mul_world(B, C, world), world)
        if mat_equal(left, right):
            ok += 1
        total += 1  # also expected to fail

    for _ in range(trials):
        A = random_matrix_int()
        B = random_matrix_int()
        C = random_matrix_int()
        left = mat_mul_world(mat_mul_world(A, B, world), C, world)
        right = mat_mul_world(A, mat_mul_world(B, C, world), world)
        if mat_equal(left, right):
            ok += 1
        total += 1

    return ok, total


def test_left_distributivity(world: int, trials: int) -> Tuple[int, int]:
    """
    Empirically test left-distributivity:

        A⊗(B⊕C) = (A⊗B) ⊕ (A⊗C)

    Returns (ok_count, total_count).
    """
    ok = 0
    total = 0

    # For world 3, include a known *failing* triple deterministically.
    if world == 3:
        A = mat_identity()
        B = mat_identity()
        C = mat_identity()
        left = mat_mul_world(A, mat_add(B, C), world)
        right = mat_add(mat_mul_world(A, B, world), mat_mul_world(A, C, world))
        if mat_equal(left, right):
            ok += 1
        total += 1  # this should fail

    for _ in range(trials):
        A = random_matrix_int()
        B = random_matrix_int()
        C = random_matrix_int()
        left = mat_mul_world(A, mat_add(B, C), world)
        right = mat_add(mat_mul_world(A, B, world), mat_mul_world(A, C, world))
        if mat_equal(left, right):
            ok += 1
        total += 1

    return ok, total


def estimate_matrix_theorems() -> Tuple[List[str], Dict[int, Dict[str, int]]]:
    """
    For each world, test associativity and left-distributivity and collect stats.

    Returns:
      (table_lines, stats)

      stats[world] = {
        "assoc_ok": int,
        "assoc_total": int,
        "assoc_holds": 0 or 1,
        "dist_ok": int,
        "dist_total": int,
        "dist_holds": 0 or 1,
      }
    """
    lines: List[str] = []
    stats: Dict[int, Dict[str, int]] = {}

    header = "world | product description        | Assoc (ok/total) | DistLeft (ok/total)"
    lines.append(header)
    lines.append("-" * len(header))

    for w in WORLD_IDS:
        assoc_ok, assoc_total = test_associativity(w, TRIALS_PER_WORLD)
        dist_ok, dist_total = test_left_distributivity(w, TRIALS_PER_WORLD)

        assoc_holds = int(assoc_total > 0 and assoc_ok == assoc_total)
        dist_holds = int(dist_total > 0 and dist_ok == dist_total)

        stats[w] = {
            "assoc_ok": assoc_ok,
            "assoc_total": assoc_total,
            "assoc_holds": assoc_holds,
            "dist_ok": dist_ok,
            "dist_total": dist_total,
            "dist_holds": dist_holds,
        }

        desc = WORLD_DESCRIPTIONS[w]
        lines.append(
            f"{w:<5}| {desc:<26} | {assoc_ok}/{assoc_total:<16} | {dist_ok}/{dist_total}"
        )

    lines.append("")
    lines.append(
        "Heuristically, we expect: worlds 0 and 1 (standard and Hadamard) to "
        "satisfy both associativity and left-distributivity; world 2 to be "
        "non-associative but still left-distributive (bilinear AB+BA); and "
        "world 3 to fail both properties."
    )

    return lines, stats


# -----------------------------------------------------------------------------
# Higher-order look: Holds₁ / Holds₂ and model extensions
# -----------------------------------------------------------------------------

EXT1: Dict[str, Set[int]] = {}                 # unary: name ↦ {worlds}
EXT2: Dict[str, Set[Tuple[str, str]]] = {}     # binary: name ↦ set of pairs

STRONGER_REL = "rel:stronger"


def thm_int(name: str) -> str:
    """Encode a theorem name as a unary predicate-name, e.g. 'AssocMult' → 'thm:AssocMult'."""
    return f"thm:{name}"


def build_model_extensions(stats: Dict[int, Dict[str, int]]) -> None:
    """
    Populate EXT1 and EXT2 from the empirical stats:

      • Worlds are w ∈ {0,1,2,3}.
      • INTENSIONS:
          - thm:AssocMult
          - thm:DistLeft
      • EXT1[intension] = set of worlds where the theorem holds in all samples.
      • EXT2[STRONGER_REL] = { (thm:AssocMult, thm:DistLeft) }.
    """
    EXT1.clear()
    EXT2.clear()

    t_assoc = thm_int("AssocMult")
    t_dist = thm_int("DistLeft")

    EXT1[t_assoc] = set(w for w, s in stats.items() if s.get("assoc_holds", 0))
    EXT1[t_dist] = set(w for w, s in stats.items() if s.get("dist_holds", 0))

    EXT2[STRONGER_REL] = {(t_assoc, t_dist)}


def Holds1(pname: str, world: int) -> bool:
    """
    Unary Holds₁ predicate:

        Holds1(P, w)

    is true exactly when world `w` is in the extension EXT1[P].
    """
    return world in EXT1.get(pname, set())


def Holds2(rname: str, x: str, y: str) -> bool:
    """
    Binary Holds₂ predicate:

        Holds2(R, x, y)

    is true exactly when (x, y) ∈ EXT2[R].
    """
    return (x, y) in EXT2.get(rname, set())


# -----------------------------------------------------------------------------
# Check (harness)
# -----------------------------------------------------------------------------

class CheckFailure(AssertionError):
    pass


def check(cond: bool, msg: str) -> None:
    if not cond:
        raise CheckFailure(msg)


def run_checks(stats: Dict[int, Dict[str, int]]) -> List[str]:
    """
    Run independent tests:

      1) Basic matrix arithmetic behaves as expected (standard and Hadamard).
      2) Associativity: worlds 0 and 1 satisfy it on a concrete triple; world 2 fails it.
      3) Left-distributivity: worlds 0,1,2 satisfy concrete tests; world 3 fails.
      4) Stats reflect the expected pattern across the four worlds.
      5) EXT1 / Holds₁ agree with the stats.
      6) Holds₂ 'stronger' relation is present and respected:
           whenever AssocMult holds in a world, DistLeft holds there too.
    """
    notes: List[str] = []

    # 1) Basic arithmetic sanity: standard and Hadamard
    A = mat(1, 2, 3, 4)
    B = mat(0, 1, -1, 2)
    C = mat(2, 0, 0, 1)

    # (A+B)·C = A·C + B·C for standard product
    left_std = mat_std_mul(mat_add(A, B), C)
    right_std = mat_add(mat_std_mul(A, C), mat_std_mul(B, C))
    check(mat_equal(left_std, right_std), "Standard product must distribute over addition.")

    # Hadamard: entrywise
    had = mat_hadamard(A, B)
    expected_had = mat(A[0][0]*B[0][0], A[0][1]*B[0][1], A[1][0]*B[1][0], A[1][1]*B[1][1])
    check(mat_equal(had, expected_had), "Hadamard product must be entrywise multiplication.")

    notes.append("PASS 1: Basic matrix arithmetic (standard, Hadamard) behaves as expected.")

    # 2) Associativity concrete checks
    # For worlds 0 and 1, any triple should satisfy associativity.
    for w_id in (0, 1):
        left = mat_mul_world(mat_mul_world(A, B, w_id), C, w_id)
        right = mat_mul_world(A, mat_mul_world(B, C, w_id), w_id)
        check(
            mat_equal(left, right),
            f"World {w_id}: associativity must hold for a concrete triple.",
        )

    # For world 2, verify the known non-associative triple fails.
    A2 = mat(1, 0, 0, 0)  # E11
    B2 = mat(0, 1, 0, 0)  # E12
    C2 = mat(0, 0, 1, 0)  # E21
    left2 = mat_mul_world(mat_mul_world(A2, B2, 2), C2, 2)
    right2 = mat_mul_world(A2, mat_mul_world(B2, C2, 2), 2)
    check(
        not mat_equal(left2, right2),
        "World 2: associativity must fail for the E11,E12,E21 triple.",
    )

    notes.append("PASS 2: Associativity holds in worlds 0–1 and fails for a concrete triple in world 2.")

    # 3) Left-distributivity concrete checks
    # Worlds 0,1,2: bilinear products should satisfy left-distributivity.
    for w_id in (0, 1, 2):
        left = mat_mul_world(A, mat_add(B, C), w_id)
        right = mat_add(mat_mul_world(A, B, w_id), mat_mul_world(A, C, w_id))
        check(
            mat_equal(left, right),
            f"World {w_id}: left-distributivity must hold for a concrete triple.",
        )

    # World 3: known failing triple A=I, B=I, C=I
    A3 = mat_identity()
    B3 = mat_identity()
    C3 = mat_identity()
    left3 = mat_mul_world(A3, mat_add(B3, C3), 3)
    right3 = mat_add(mat_mul_world(A3, B3, 3), mat_mul_world(A3, C3, 3))
    check(
        not mat_equal(left3, right3),
        "World 3: left-distributivity must fail for A=B=C=I.",
    )

    notes.append("PASS 3: Left-distributivity holds concretely in worlds 0–2 and fails in world 3.")

    # 4) Stats expectations
    #   worlds 0,1: assoc_holds=1, dist_holds=1
    #   world 2:    assoc_holds=0, dist_holds=1
    #   world 3:    assoc_holds=0, dist_holds=0
    for w_id in WORLD_IDS:
        s = stats[w_id]
        if w_id in (0, 1):
            check(
                s["assoc_holds"] == 1 and s["dist_holds"] == 1,
                f"World {w_id}: expected both theorems to hold empirically, got {s}.",
            )
        elif w_id == 2:
            check(
                s["assoc_holds"] == 0 and s["dist_holds"] == 1,
                f"World 2: expected non-associative but left-distributive, got {s}.",
            )
        else:
            check(
                s["assoc_holds"] == 0 and s["dist_holds"] == 0,
                f"World 3: expected both theorems to fail empirically, got {s}.",
            )

    notes.append("PASS 4: Statistics match the expected pattern for all four worlds.")

    # 5) EXT1 / Holds₁ agreement
    t_assoc = thm_int("AssocMult")
    t_dist = thm_int("DistLeft")
    for w_id in WORLD_IDS:
        s = stats[w_id]
        check(
            Holds1(t_assoc, w_id) == bool(s["assoc_holds"]),
            f"Holds1(thm:AssocMult, {w_id}) disagrees with stats.",
        )
        check(
            Holds1(t_dist, w_id) == bool(s["dist_holds"]),
            f"Holds1(thm:DistLeft, {w_id}) disagrees with stats.",
        )

    notes.append("PASS 5: Holds₁/EXT1 match the empirical statistics for all worlds and theorems.")

    # 6) Holds₂ 'stronger' relation:
    # Whenever AssocMult holds in a world, DistLeft must also hold there.
    check(
        Holds2(STRONGER_REL, t_assoc, t_dist),
        "Holds2(rel:stronger, thm:AssocMult, thm:DistLeft) must be true.",
    )
    for w_id in WORLD_IDS:
        if Holds1(t_assoc, w_id):
            check(
                Holds1(t_dist, w_id),
                f"In world {w_id}, AssocMult holds but DistLeft does not.",
            )

    notes.append("PASS 6: 'AssocMult' is stronger than 'DistLeft' in all worlds where it holds.")

    return notes


def arc_check(stats: Dict[int, Dict[str, int]]) -> None:
    print("Check (harness)")
    print("---------------")
    try:
        notes = run_checks(stats)
    except CheckFailure as e:
        print("FAIL:", e)
        raise
    else:
        for line in notes:
            print(line)
        print("All checks passed.")
    print()


# -----------------------------------------------------------------------------
# ARC: Answer / Reason why
# -----------------------------------------------------------------------------

ANSWER_TEXT = (
    "We consider 2×2 real matrices with four different products:\n"
    "  world 0: A ⊗₀ B = A·B (standard matrix product),\n"
    "  world 1: A ⊗₁ B = A∘B (Hadamard / entrywise product),\n"
    "  world 2: A ⊗₂ B = A·B + B·A (symmetric, Jordan-like product),\n"
    "  world 3: A ⊗₃ B = A·B + A (deliberately broken).\n"
    "and a shared addition A⊕B given by entrywise sum.\n"
    "We treat two properties as theorems:\n"
    "  AssocMult:   (A⊗B)⊗C = A⊗(B⊗C),\n"
    "  DistLeft:    A⊗(B⊕C) = (A⊗B) ⊕ (A⊗C).\n"
)

REASON_TEXT = (
    "The first-order core of this script is plain 2×2 matrix arithmetic:\n"
    "  • matrices are tuples of floats,\n"
    "  • addition is entrywise, shared by all worlds,\n"
    "  • products differ by world (standard, Hadamard, AB+BA, AB+A).\n"
    "\n"
    "For each world we sample many random triples A,B,C with small integer\n"
    "entries and test the equations for AssocMult and DistLeft. From these\n"
    "tests we decide whether a world \"empirically\" satisfies each theorem,\n"
    "and we build an extensional model:\n"
    "  • worlds: w ∈ {0,1,2,3},\n"
    "  • theorem-names: thm:AssocMult, thm:DistLeft,\n"
    "  • EXT1[thm:AssocMult] = { w | all sampled triples satisfy associativity },\n"
    "  • EXT1[thm:DistLeft]  = { w | all sampled triples satisfy left-distributivity }.\n"
    "\n"
    "We then define a unary predicate Holds₁ by\n"
    "  Holds1(P, w)  ⇔  w ∈ EXT1[P],\n"
    "and a binary predicate Holds₂ using\n"
    "  EXT2[rel:stronger] = { (thm:AssocMult, thm:DistLeft) },\n"
    "so that\n"
    "  Holds2(rel:stronger, X, Y)  ⇔  (X, Y) ∈ EXT2[rel:stronger].\n"
    "\n"
    "Thus the seemingly higher-order claims\n"
    "  \"world 2 is non-associative but left-distributive\"\n"
    "or\n"
    "  \"AssocMult is stronger than DistLeft in this toy universe\"\n"
    "are represented via Holds₁/Holds₂ over a finite set of intensions, while\n"
    "all mathematical content lives in a simple, first-order-style matrix engine."
)


def arc_answer(table_lines: List[str]) -> None:
    print("Answer")
    print("------")
    print(ANSWER_TEXT)
    print("Empirical results (random tests over small integer matrices):")
    print()
    for line in table_lines:
        print(line)
    print()
    print("Holds₁ view on theorem-names:")
    t_assoc = thm_int("AssocMult")
    t_dist = thm_int("DistLeft")
    for w in WORLD_IDS:
        print(
            f"  world {w}: Holds1({t_assoc}, {w})={Holds1(t_assoc, w)}, "
            f"Holds1({t_dist}, {w})={Holds1(t_dist, w)}"
        )
    print()


def arc_reason() -> None:
    print("Reason why")
    print("----------")
    print(REASON_TEXT)
    print()


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

def main() -> None:
    table_lines, stats = estimate_matrix_theorems()
    build_model_extensions(stats)
    arc_answer(table_lines)
    arc_reason()
    arc_check(stats)


if __name__ == "__main__":
    main()

