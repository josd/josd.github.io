#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
complex_matrix_adjoint_worlds.py
================================

Adjointhood on 2×2 complex matrices
-----------------------------------
This script explores four different “adjoint-like” operations A ↦ A★ on
2×2 complex matrices, and two properties that such an adjoint is expected
to satisfy in a *-algebra / Hilbert space context:

  (AdjointInvolution)
      (A★)★ = A

  (AdjointConjLin)
      (λA)★ = conjugate(λ) · A★    for all complex scalars λ

We take four worlds w ∈ {0,1,2,3}, each with its own operation ★₍w₎:

  World 0: Hermitian adjoint (conjugate transpose)
      A★₀ = A* = conjugate(A) transposed

  World 1: plain transpose
      A★₁ = Aᵀ

  World 2: entrywise conjugation
      A★₂ = conjugate(A)

  World 3: identity (deliberately broken)
      A★₃ = A

All worlds use 2×2 complex matrices with the usual entrywise addition.


Mathematical expectations
-------------------------
For complex matrices:

  • The usual Hermitian adjoint A ↦ A* (world 0) satisfies both
        (A*)* = A
        (λA)* = conjugate(λ) · A*.

  • The transpose A ↦ Aᵀ (world 1) satisfies (Aᵀ)ᵀ = A but is linear
    rather than conjugate-linear:
        (λA)ᵀ = λ · Aᵀ, which in general is not equal to
        conjugate(λ) · Aᵀ when λ has non-zero imaginary part.

  • Entrywise conjugation A ↦ conjugate(A) (world 2) satisfies both
        conjugate(conjugate(A)) = A
        conjugate(λA) = conjugate(λ) · conjugate(A).

  • The identity A ↦ A (world 3) satisfies
        (A)★ = A, so (A★)★ = A,
    but (λA)★ = λA, not conjugate(λ)A in general.

Thus:

  • AdjointInvolution holds in all four worlds.
  • AdjointConjLin holds only in worlds 0 and 2.


Higher-order look, first-order core
-----------------------------------
We follow the “higher-order look, first-order core” pattern
(described at https://josd.github.io/higher-order-look-first-order-core/):

  • First-order core:
      - 2×2 matrices with complex entries, represented as Python `complex`;
      - a fixed matrix addition A + B (entrywise);
      - four world-dependent star-operations ★₍w₎ on matrices;
      - random testing of:
          AdjointInvolution:  (A★)★ = A
          AdjointConjLin:     (λA)★ = conjugate(λ) · A★

        for small random complex scalars λ and random matrices A.

  • Higher-order look:
      - worlds: W = {0,1,2,3};
      - theorem-names (intensions):
            thm:AdjointInvolution
            thm:AdjointConjLin

      - a single unary predicate

            Holds₁(P, w)

        interpreted extensionally via a map

            EXT1: Dict[str, Set[int]]

        so that

            Holds1(P, w)  iff  w ∈ EXT1[P];

        i.e., world w empirically satisfies theorem P (all samples checked).

      - a binary relation-name

            rel:stronger

        relating intensions by

            Holds₂("rel:stronger", thm:AdjointConjLin, thm:AdjointInvolution),

        expressing that in this tiny universe, whenever AdjointConjLin holds
        in a world, AdjointInvolution holds there too. Implementation:

            EXT2["rel:stronger"] = { (thm:AdjointConjLin, thm:AdjointInvolution) }
            Holds2(R, X, Y)  iff  (X, Y) ∈ EXT2[R].

All semantic content (complex arithmetic, star-operations, tests) lives in the
first-order core; Holds₁ and Holds₂ simply read off the resulting extensional
model (EXT1, EXT2).


What the script prints
----------------------
Running:

    python3 complex_matrix_adjoint_worlds.py

produces three ARC-style sections:

  1) Answer
     • describes the four star-operations and the two theorem-names;
     • prints a table of empirical results per world:
           world | star description        | Invol (ok/total) | ConjLin (ok/total)
     • prints Holds₁ judgements for each world and theorem-name.

  2) Reason why
     • explains how each star-operation behaves on 2×2 complex matrices,
       and how the higher-order-looking Holds₁ / Holds₂ predicates are
       built from the underlying numerical tests.

  3) Check (harness)
     • at least six independent checks, verifying that:
         - the star-operations behave as advertised on a concrete matrix;
         - (A★)★ = A holds in all four worlds on concrete examples;
         - AdjointConjLin holds concretely in worlds 0 and 2, and fails
           concretely in worlds 1 and 3;
         - the empirical statistics match the expected pattern:
             involution holds in all worlds,
             conjugate-linearity holds only in worlds 0 and 2;
         - EXT1 / Holds₁ agree with the statistics;
         - the Holds₂-level “stronger” relation is respected:
             whenever Holds1(thm:AdjointConjLin, w) is true,
             Holds1(thm:AdjointInvolution, w) is also true.

Python 3.9+; no external packages.
"""

from __future__ import annotations

from random import randrange, seed
from typing import Dict, List, Tuple, Set

seed(0)  # deterministic randomness

Matrix = Tuple[Tuple[complex, complex], Tuple[complex, complex]]

# -----------------------------------------------------------------------------
# Basic 2×2 complex matrix utilities
# -----------------------------------------------------------------------------

def mat(a11: complex, a12: complex, a21: complex, a22: complex) -> Matrix:
    return (
        (complex(a11), complex(a12)),
        (complex(a21), complex(a22)),
    )


def mat_add(A: Matrix, B: Matrix) -> Matrix:
    return (
        (A[0][0] + B[0][0], A[0][1] + B[0][1]),
        (A[1][0] + B[1][0], A[1][1] + B[1][1]),
    )


def mat_scale(A: Matrix, lam: complex) -> Matrix:
    return (
        (lam * A[0][0], lam * A[0][1]),
        (lam * A[1][0], lam * A[1][1]),
    )


def mat_equal(A: Matrix, B: Matrix, tol: float = 1e-9) -> bool:
    return (
        abs(A[0][0] - B[0][0]) <= tol and
        abs(A[0][1] - B[0][1]) <= tol and
        abs(A[1][0] - B[1][0]) <= tol and
        abs(A[1][1] - B[1][1]) <= tol
    )


def random_complex_scalar(max_abs: int = 3) -> complex:
    """Random complex scalar with integer real/imag parts in [-max_abs, max_abs]."""
    re = randrange(-max_abs, max_abs + 1)
    im = randrange(-max_abs, max_abs + 1)
    return complex(re, im)


def random_complex_matrix(max_abs: int = 3) -> Matrix:
    """Random 2×2 complex matrix with integer real/imag parts."""
    return mat(
        complex(randrange(-max_abs, max_abs + 1), randrange(-max_abs, max_abs + 1)),
        complex(randrange(-max_abs, max_abs + 1), randrange(-max_abs, max_abs + 1)),
        complex(randrange(-max_abs, max_abs + 1), randrange(-max_abs, max_abs + 1)),
        complex(randrange(-max_abs, max_abs + 1), randrange(-max_abs, max_abs + 1)),
    )


# -----------------------------------------------------------------------------
# Worlds and adjoint-like operations
# -----------------------------------------------------------------------------

WORLD_IDS = (0, 1, 2, 3)

WORLD_DESCRIPTIONS: Dict[int, str] = {
    0: "A★ = conj(A)ᵀ  (Hermitian adjoint)",
    1: "A★ = Aᵀ        (transpose only)",
    2: "A★ = conj(A)   (entrywise conjugate)",
    3: "A★ = A         (identity, broken)",
}


def matrix_star(A: Matrix, world: int) -> Matrix:
    """
    World-specific adjoint-like operation A ↦ A★:

      world 0: Hermitian adjoint: conj(A)ᵀ
      world 1: transpose only:   Aᵀ
      world 2: entrywise conjugation: conj(A)
      world 3: identity: A
    """
    (a11, a12), (a21, a22) = A

    if world == 0:
        # conj transpose
        return (
            (a11.conjugate(), a21.conjugate()),
            (a12.conjugate(), a22.conjugate()),
        )
    if world == 1:
        # transpose only
        return (
            (a11, a21),
            (a12, a22),
        )
    if world == 2:
        # entrywise conjugation
        return (
            (a11.conjugate(), a12.conjugate()),
            (a21.conjugate(), a22.conjugate()),
        )
    if world == 3:
        # identity
        return A

    raise ValueError(f"Unknown world id {world!r}")


# -----------------------------------------------------------------------------
# Empirical tests: AdjointInvolution and AdjointConjLin
# -----------------------------------------------------------------------------

TRIALS_PER_WORLD = 250
TOL = 1e-9


def test_involution(world: int, trials: int) -> Tuple[int, int]:
    """
    Test AdjointInvolution:

        (A★)★ = A

    Returns (ok_count, total_count).
    """
    ok = 0
    total = 0

    for _ in range(trials):
        A = random_complex_matrix()
        star = matrix_star(A, world)
        starstar = matrix_star(star, world)
        if mat_equal(starstar, A, TOL):
            ok += 1
        total += 1

    return ok, total


def test_conjugate_linearity(world: int, trials: int) -> Tuple[int, int]:
    """
    Test AdjointConjLin:

        (λA)★ = conjugate(λ) · A★

    Returns (ok_count, total_count).
    """
    ok = 0
    total = 0

    # For worlds 1 and 3, include a known failing example deterministically.
    if world in (1, 3):
        A = mat(1 + 2j, 3 - 4j, -1 + 0.5j, 2 - 3j)
        lam = 1 + 1j
        lhs = matrix_star(mat_scale(A, lam), world)
        rhs = mat_scale(matrix_star(A, world), lam.conjugate())
        if mat_equal(lhs, rhs, TOL):
            ok += 1
        total += 1  # we expect this to be a failure, so ok should stay 0

    for _ in range(trials):
        A = random_complex_matrix()
        lam = random_complex_scalar()
        lhs = matrix_star(mat_scale(A, lam), world)
        rhs = mat_scale(matrix_star(A, world), lam.conjugate())
        if mat_equal(lhs, rhs, TOL):
            ok += 1
        total += 1

    return ok, total


def estimate_adj_theorems() -> Tuple[List[str], Dict[int, Dict[str, int]]]:
    """
    For each world, test AdjointInvolution and AdjointConjLin and collect stats.

    Returns:
      (table_lines, stats)

      stats[world] = {
        "invol_ok": int,
        "invol_total": int,
        "invol_holds": 0 or 1,
        "conj_ok": int,
        "conj_total": int,
        "conj_holds": 0 or 1,
      }
    """
    lines: List[str] = []
    stats: Dict[int, Dict[str, int]] = {}

    header = "world | star description                 | Invol (ok/total) | ConjLin (ok/total)"
    lines.append(header)
    lines.append("-" * len(header))

    for w in WORLD_IDS:
        invol_ok, invol_total = test_involution(w, TRIALS_PER_WORLD)
        conj_ok, conj_total = test_conjugate_linearity(w, TRIALS_PER_WORLD)

        invol_holds = int(invol_total > 0 and invol_ok == invol_total)
        conj_holds = int(conj_total > 0 and conj_ok == conj_total)

        stats[w] = {
            "invol_ok": invol_ok,
            "invol_total": invol_total,
            "invol_holds": invol_holds,
            "conj_ok": conj_ok,
            "conj_total": conj_total,
            "conj_holds": conj_holds,
        }

        desc = WORLD_DESCRIPTIONS[w]
        lines.append(
            f"{w:<5}| {desc:<30} | {invol_ok}/{invol_total:<17} | {conj_ok}/{conj_total}"
        )

    lines.append("")
    lines.append(
        "Heuristically, we expect: AdjointInvolution to hold in all worlds "
        "(taking star twice returns the original matrix), and "
        "AdjointConjLin to hold only in worlds 0 (Hermitian adjoint) and 2 "
        "(entrywise conjugation)."
    )

    return lines, stats


# -----------------------------------------------------------------------------
# Higher-order look: Holds₁ / Holds₂ and model extensions
# -----------------------------------------------------------------------------

EXT1: Dict[str, Set[int]] = {}                 # unary: name ↦ {worlds}
EXT2: Dict[str, Set[Tuple[str, str]]] = {}     # binary: name ↦ set of pairs

STRONGER_REL = "rel:stronger"


def thm_int(name: str) -> str:
    """Encode a theorem name as a unary predicate-name, e.g. 'AdjointInvolution' → 'thm:AdjointInvolution'."""
    return f"thm:{name}"


def build_model_extensions(stats: Dict[int, Dict[str, int]]) -> None:
    """
    Populate EXT1 and EXT2 from the empirical stats:

      • Worlds are w ∈ {0,1,2,3}.
      • INTENSIONS:
          - thm:AdjointInvolution
          - thm:AdjointConjLin
      • EXT1[intension] = set of worlds where the theorem holds in all samples.
      • EXT2[STRONGER_REL] = { (thm:AdjointConjLin, thm:AdjointInvolution) }.
    """
    EXT1.clear()
    EXT2.clear()

    t_invol = thm_int("AdjointInvolution")
    t_conj = thm_int("AdjointConjLin")

    EXT1[t_invol] = set(w for w, s in stats.items() if s.get("invol_holds", 0))
    EXT1[t_conj] = set(w for w, s in stats.items() if s.get("conj_holds", 0))

    EXT2[STRONGER_REL] = {(t_conj, t_invol)}


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

      1) Check that matrix_star behaves as advertised on a concrete matrix.
      2) Check (A★)★ = A concretely in each world.
      3) Check AdjointConjLin concretely succeeds in worlds 0 and 2, fails in 1 and 3.
      4) Check that stats match the expected pattern (invol_holds everywhere, conj_holds only in worlds 0,2).
      5) Check that EXT1 / Holds₁ agree with the stats.
      6) Check that Holds₂ 'stronger' relation is present and respected:
           whenever AdjointConjLin holds in a world, AdjointInvolution holds there too.
    """
    notes: List[str] = []

    # 1) matrix_star on a concrete matrix
    A = mat(1 + 2j, 3 - 4j, -1 + 0.5j, 2 - 3j)

    # World 0: Hermitian adjoint
    star0 = matrix_star(A, 0)
    expected0 = (
        (A[0][0].conjugate(), A[1][0].conjugate()),
        (A[0][1].conjugate(), A[1][1].conjugate()),
    )
    check(mat_equal(star0, expected0), "World 0: matrix_star must be conjugate transpose.")

    # World 1: transpose only
    star1 = matrix_star(A, 1)
    expected1 = (
        (A[0][0], A[1][0]),
        (A[0][1], A[1][1]),
    )
    check(mat_equal(star1, expected1), "World 1: matrix_star must be plain transpose.")

    # World 2: entrywise conjugation
    star2 = matrix_star(A, 2)
    expected2 = (
        (A[0][0].conjugate(), A[0][1].conjugate()),
        (A[1][0].conjugate(), A[1][1].conjugate()),
    )
    check(mat_equal(star2, expected2), "World 2: matrix_star must be entrywise conjugation.")

    # World 3: identity
    star3 = matrix_star(A, 3)
    check(mat_equal(star3, A), "World 3: matrix_star must be identity.")

    notes.append("PASS 1: matrix_star behaves as advertised in all worlds on a concrete matrix.")

    # 2) (A★)★ = A concretely
    for w_id in WORLD_IDS:
        B = random_complex_matrix()
        star = matrix_star(B, w_id)
        starstar = matrix_star(star, w_id)
        check(
            mat_equal(starstar, B),
            f"World {w_id}: (A★)★ = A must hold concretely.",
        )

    notes.append("PASS 2: AdjointInvolution holds concretely in all worlds.")

    # 3) AdjointConjLin: concrete success/failure
    lam = 2 + 3j
    mu = -1 + 0.5j
    X = random_complex_matrix()
    Y = random_complex_matrix()

    # Worlds 0 and 2: conjugate linearity should hold.
    for w_id in (0, 2):
        left = matrix_star(mat_add(mat_scale(X, lam), mat_scale(Y, mu)), w_id)
        right = mat_add(
            mat_scale(matrix_star(X, w_id), lam.conjugate()),
            mat_scale(matrix_star(Y, w_id), mu.conjugate()),
        )
        check(
            mat_equal(left, right),
            f"World {w_id}: AdjointConjLin must hold for (λX+μY).",
        )

    # Worlds 1 and 3: choose λ with nonzero imaginary part; property must fail.
    lam_bad = 1 + 2j
    X_bad = A  # reuse concrete A
    for w_id in (1, 3):
        left = matrix_star(mat_scale(X_bad, lam_bad), w_id)
        right = mat_scale(matrix_star(X_bad, w_id), lam_bad.conjugate())
        check(
            not mat_equal(left, right),
            f"World {w_id}: AdjointConjLin must fail for λ=1+2i on a non-real matrix.",
        )

    notes.append("PASS 3: AdjointConjLin holds concretely in worlds 0,2 and fails in worlds 1,3.")

    # 4) Stats expectations
    #   invol_holds should be 1 in all worlds;
    #   conj_holds should be 1 only in worlds 0 and 2.
    for w_id in WORLD_IDS:
        s = stats[w_id]
        check(
            s["invol_holds"] == 1,
            f"World {w_id}: expected AdjointInvolution to hold empirically, got stats {s}.",
        )

    for w_id in WORLD_IDS:
        s = stats[w_id]
        if w_id in (0, 2):
            check(
                s["conj_holds"] == 1,
                f"World {w_id}: expected AdjointConjLin to hold empirically, got stats {s}.",
            )
        else:
            check(
                s["conj_holds"] == 0,
                f"World {w_id}: expected AdjointConjLin NOT to hold empirically, got stats {s}.",
            )

    notes.append("PASS 4: Empirical statistics match the expected pattern across worlds.")

    # 5) EXT1 / Holds₁ agreement
    t_invol = thm_int("AdjointInvolution")
    t_conj = thm_int("AdjointConjLin")

    for w_id in WORLD_IDS:
        s = stats[w_id]
        check(
            Holds1(t_invol, w_id) == bool(s["invol_holds"]),
            f"Holds1(thm:AdjointInvolution, {w_id}) disagrees with stats.",
        )
        check(
            Holds1(t_conj, w_id) == bool(s["conj_holds"]),
            f"Holds1(thm:AdjointConjLin, {w_id}) disagrees with stats.",
        )

    notes.append("PASS 5: Holds₁/EXT1 match the empirical statistics for all worlds and theorems.")

    # 6) Holds₂ 'stronger' relation:
    #    Whenever AdjointConjLin holds in a world, AdjointInvolution must also hold there.
    check(
        Holds2(STRONGER_REL, t_conj, t_invol),
        "Holds2(rel:stronger, thm:AdjointConjLin, thm:AdjointInvolution) must be true.",
    )
    for w_id in WORLD_IDS:
        if Holds1(t_conj, w_id):
            check(
                Holds1(t_invol, w_id),
                f"In world {w_id}, AdjointConjLin holds but AdjointInvolution does not.",
            )

    notes.append("PASS 6: 'AdjointConjLin' is stronger than 'AdjointInvolution' in all worlds where it holds.")

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
    "We study four adjoint-like operations A ↦ A★ on 2×2 complex matrices:\n"
    "  world 0: A★ = conj(A)ᵀ  (Hermitian adjoint),\n"
    "  world 1: A★ = Aᵀ        (transpose only),\n"
    "  world 2: A★ = conj(A)   (entrywise conjugation),\n"
    "  world 3: A★ = A         (identity, deliberately broken),\n"
    "and two theorem-names:\n"
    "  AdjointInvolution:   (A★)★ = A,\n"
    "  AdjointConjLin:      (λA)★ = conjugate(λ) · A★.\n"
    "In the intended C*-algebra picture, a genuine adjoint should satisfy both.\n"
)

REASON_TEXT = (
    "The first-order core of this script is straightforward complex matrix\n"
    "arithmetic: 2×2 matrices as pairs of Python complex numbers, entrywise\n"
    "addition, and four concrete definitions of A★. For each world, we sample\n"
    "many random matrices A and complex scalars λ and test the equations\n"
    "  (A★)★ = A          (AdjointInvolution),\n"
    "  (λA)★ = conjugate(λ) · A★ (AdjointConjLin).\n"
    "\n"
    "From the test results we build an extensional model:\n"
    "  • worlds: w ∈ {0,1,2,3},\n"
    "  • theorem-names: thm:AdjointInvolution, thm:AdjointConjLin,\n"
    "  • EXT1[thm:AdjointInvolution] = { w | all sampled A satisfy (A★)★ = A },\n"
    "  • EXT1[thm:AdjointConjLin]    = { w | all sampled (λ,A) satisfy (λA)★ = conjugate(λ) · A★ }.\n"
    "\n"
    "We then set Holds₁(P, w) ↔ w ∈ EXT1[P]. A binary relation-name\n"
    "rel:stronger is given by EXT2[rel:stronger] = { (thm:AdjointConjLin,\n"
    "thm:AdjointInvolution) }, and Holds₂ is defined by membership in EXT2.\n"
    "Thus, in this tiny universe, whenever AdjointConjLin holds in a world\n"
    "(only worlds 0 and 2), AdjointInvolution holds there as well.\n"
    "\n"
    "All the 'higher-order' talk about which adjoint axioms hold where is\n"
    "implemented via Holds₁/Holds₂ on a finite set of intensions, while all\n"
    "the actual mathematical content lives in the concrete star-operations and\n"
    "numeric tests on complex matrices."
)


def arc_answer(table_lines: List[str]) -> None:
    print("Answer")
    print("------")
    print(ANSWER_TEXT)
    print("Empirical results (random tests over small complex matrices):")
    print()
    for line in table_lines:
        print(line)
    print()
    print("Holds₁ view on theorem-names:")
    t_invol = thm_int("AdjointInvolution")
    t_conj = thm_int("AdjointConjLin")
    for w in WORLD_IDS:
        print(
            f"  world {w}: Holds1({t_invol}, {w})={Holds1(t_invol, w)}, "
            f"Holds1({t_conj}, {w})={Holds1(t_conj, w)}"
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
    table_lines, stats = estimate_adj_theorems()
    build_model_extensions(stats)
    arc_answer(table_lines)
    arc_reason()
    arc_check(stats)


if __name__ == "__main__":
    main()

