#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
complex_matrix_unitary_worlds.py
================================

When is a 2×2 complex matrix really unitary?
--------------------------------------------
This script is a small, self-contained Python “lab” for exploring different
tests for whether a 2×2 complex matrix A is unitary.

In linear algebra and quantum mechanics, a matrix U is unitary when it
preserves inner products (and hence norms) in C²:

    U* U = I

where U* is the conjugate transpose, and I is the identity matrix. This means:
  • U does not change lengths of vectors;
  • U does not change angles between vectors;
  • U is a “rotation-like” transformation in complex space.

Here we implement the *correct* unitarity test and three simpler or more
specialised alternatives, and then treat each of them as a separate “world”.
We ask, in a logical way:

  • In which worlds is the world’s unitarity test always correct?
  • In which worlds does the test at least never produce false positives?
  • How do those “theorems” about tests relate to each other?


Four worlds
-----------
We consider four worlds w ∈ {0,1,2,3}. In each world there is a predicate
is_unitary_w(A) that decides whether a matrix A is “unitary” in that world.

  World 0: True unitarity (ground truth)
    is_unitary_0(A) holds exactly when A* A = I
    (up to a small numerical tolerance).

  World 1: Special unitary (extra restriction)
    is_unitary_1(A) holds when:
      - A is unitary in the true sense (A* A = I), and
      - det(A) is (numerically) equal to +1.
    So world 1 recognises only 2×2 matrices in SU(2): unitary with determinant 1.

  World 2: Column-length heuristic
    is_unitary_2(A) holds when:
      - each column of A has length 1,
      - but we do NOT check orthogonality between the columns.
    This is a cheap necessary condition for unitarity, but not sufficient:
    a matrix can have unit-length columns without being unitary.

  World 3: Determinant-magnitude heuristic
    is_unitary_3(A) holds when:
      - the modulus of det(A) is approximately 1.
    This is another necessary condition: a unitary 2×2 matrix always has
    |det(A)| = 1, but the converse is false in general.


Real unitarity vs tests
-----------------------
We define a “true” unitarity predicate:

    unitary_true(A): A is unitary in the standard sense (A* A = I).

Each world then uses its own test is_unitary_w(A) as above. We compare the
world’s judgement with the true judgement along two dimensions:

  (CorrectUnitaryTest)
      The world’s unitarity test is completely correct:
        for all A,  is_unitary_w(A) == unitary_true(A).

  (NoFalseUnitary)
      The world never has false positives:
        for all A,  is_unitary_w(A) implies unitary_true(A).

In practice we cannot test “for all A”, so we approximate this by:
  • several carefully chosen concrete matrices; and
  • random 2×2 complex matrices with small integer entries.

We then record, for each world, whether any mismatches were observed. This
gives an extensional model of which theorems hold in which worlds.


Higher-order look, first-order core
-----------------------------------
We follow the “higher-order look, first-order core” pattern
(described at https://josd.github.io/higher-order-look-first-order-core/):

  • First-order core:
      - 2×2 complex matrices as pairs of Python complex numbers;
      - basic operations: matrix multiplication, conjugate transpose,
        determinant, Frobenius norm;
      - a “true” unitarity test unitary_true(A);
      - four world-specific tests is_unitary_w(A);
      - random sampling of matrices to compare world tests with true unitarity.

  • Higher-order look:
      - worlds: W = {0,1,2,3};
      - theorem-names (intensions):
            thm:CorrectUnitaryTest
            thm:NoFalseUnitary

      - a unary predicate

            Holds₁(P, w)

        interpreted extensionally via a map

            EXT1: Dict[str, Set[int]]

        such that:

            Holds1(P, w)  iff  w ∈ EXT1[P].

        For example:
          Holds1(thm:CorrectUnitaryTest, 0) says
            “in world 0 the unitarity test is correct on all samples”.

      - a binary relation-name

            rel:stronger

        with a binary predicate

            Holds₂(rel:stronger, X, Y)

        interpreted by a map

            EXT2: Dict[str, Set[(str, str)]]

        so that:

            Holds2(R, X, Y)  iff  (X, Y) ∈ EXT2[R].

        In this script we encode the idea that a fully correct test is
        stronger than a merely sound one (no false positives) by setting:

            EXT2["rel:stronger"] = {
              (thm:CorrectUnitaryTest, thm:NoFalseUnitary)
            }.

        So whenever a world satisfies CorrectUnitaryTest, we expect it also
        to satisfy NoFalseUnitary.


Expected pattern
----------------
From the definitions we expect:

  • world 0:
      - uses the true unitarity predicate,
      - so it satisfies both CorrectUnitaryTest and NoFalseUnitary.

  • world 1:
      - only recognises special unitary matrices (determinant ≈ 1),
      - so it is sound (never calls a non-unitary matrix unitary),
      - but it is incomplete (misses some genuine unitaries),
      - therefore it satisfies NoFalseUnitary but not CorrectUnitaryTest.

  • world 2:
      - only checks that both columns have length 1,
      - can easily accept non-unitaries (columns of unit length but not
        orthogonal),
      - so it has false positives and is not correct overall.

  • world 3:
      - only checks that |det(A)| ≈ 1,
      - which is a very weak condition,
      - so it also has false positives and is not correct overall.

The script confirms this pattern by random sampling and a small family of
hand-picked matrices, and then packages the result via Holds₁ and Holds₂.


What the script prints
----------------------
Running:

    python3 complex_matrix_unitary_worlds.py

produces three ARC-style sections:

  1) Answer
     • describes the four worlds and the two theorem-names;
     • prints a table of empirical results per world:
           world | test description           | Correct (ok/total) | Sound (ok/total)
     • shows the Holds₁ view:
           Holds1(thm:CorrectUnitaryTest, w)
           Holds1(thm:NoFalseUnitary, w).

  2) Reason why
     • explains the notion of unitarity (U*U = I and norm preservation);
     • explains how each world approximates or specialises this notion;
     • explains how the Holds₁ / Holds₂ view is built from the extensional
       statistics.

  3) Check (harness)
     • at least six independent tests checking that:
         - the true unitarity predicate works on explicit matrices;
         - world 1 is a stricter “special unitary” view;
         - worlds 2 and 3 really do produce false positives;
         - the statistics match the expected pattern;
         - EXT1 / Holds₁ are consistent with those statistics;
         - the Holds₂-level “stronger” relation is respected in all worlds.

Python 3.9+; no external packages.
"""

from __future__ import annotations

import math
from random import randrange, seed
from typing import Dict, List, Tuple, Set

seed(0)  # deterministic randomness for reproducible runs

Matrix = Tuple[Tuple[complex, complex], Tuple[complex, complex]]


# -----------------------------------------------------------------------------
# Basic 2×2 complex matrix utilities
# -----------------------------------------------------------------------------

def mat(a11: complex, a12: complex, a21: complex, a22: complex) -> Matrix:
    return (
        (complex(a11), complex(a12)),
        (complex(a21), complex(a22)),
    )


def random_complex_matrix(max_abs: int = 2) -> Matrix:
    """Random 2×2 complex matrix with integer real/imag parts in [-max_abs, max_abs]."""
    def rnd() -> complex:
        return complex(
            randrange(-max_abs, max_abs + 1),
            randrange(-max_abs, max_abs + 1),
        )
    return mat(rnd(), rnd(), rnd(), rnd())


def mat_mul(A: Matrix, B: Matrix) -> Matrix:
    """Matrix product A·B."""
    (a11, a12), (a21, a22) = A
    (b11, b12), (b21, b22) = B
    return (
        (a11 * b11 + a12 * b21, a11 * b12 + a12 * b22),
        (a21 * b11 + a22 * b21, a21 * b12 + a22 * b22),
    )


def mat_conj_transpose(A: Matrix) -> Matrix:
    """Conjugate transpose A*."""
    (a11, a12), (a21, a22) = A
    return (
        (a11.conjugate(), a21.conjugate()),
        (a12.conjugate(), a22.conjugate()),
    )


def mat_equal(A: Matrix, B: Matrix, tol: float = 1e-9) -> bool:
    return (
        abs(A[0][0] - B[0][0]) <= tol and
        abs(A[0][1] - B[0][1]) <= tol and
        abs(A[1][0] - B[1][0]) <= tol and
        abs(A[1][1] - B[1][1]) <= tol
    )


def mat_identity() -> Matrix:
    return ((1 + 0j, 0 + 0j), (0 + 0j, 1 + 0j))


def mat_det(A: Matrix) -> complex:
    (a11, a12), (a21, a22) = A
    return a11 * a22 - a12 * a21


def column_norms(A: Matrix) -> Tuple[float, float]:
    """Return (norm of column 1, norm of column 2)."""
    (a11, a12), (a21, a22) = A
    n1 = math.sqrt(abs(a11) ** 2 + abs(a21) ** 2)
    n2 = math.sqrt(abs(a12) ** 2 + abs(a22) ** 2)
    return n1, n2


def frobenius_norm(A: Matrix) -> float:
    (a11, a12), (a21, a22) = A
    return math.sqrt(
        abs(a11) ** 2 + abs(a12) ** 2 +
        abs(a21) ** 2 + abs(a22) ** 2
    )


# -----------------------------------------------------------------------------
# True unitarity and world-specific tests
# -----------------------------------------------------------------------------

def unitary_true(A: Matrix, tol: float = 1e-9) -> bool:
    """True unitarity: A* A = I."""
    A_star = mat_conj_transpose(A)
    prod = mat_mul(A_star, A)
    return mat_equal(prod, mat_identity(), tol)


WORLD_IDS = (0, 1, 2, 3)

WORLD_DESCRIPTIONS: Dict[int, str] = {
    0: "true unitarity (U*U ≈ I)",
    1: "special unitary (U*U ≈ I and det ≈ 1)",
    2: "columns have unit norm",
    3: "determinant has modulus 1",
}


def is_unitary_world(world: int, A: Matrix, tol: float = 1e-9) -> bool:
    """
    World-specific unitarity tests:

      world 0: true unitarity (U*U = I).
      world 1: special unitary (true unitarity and det ≈ 1).
      world 2: both columns have norm 1 (no orthogonality check).
      world 3: |det(A)| ≈ 1 (determinant magnitude heuristic).
    """
    if world == 0:
        return unitary_true(A, tol)

    if world == 1:
        if not unitary_true(A, tol):
            return False
        d = mat_det(A)
        return abs(d - 1) <= tol

    if world == 2:
        n1, n2 = column_norms(A)
        return abs(n1 - 1.0) <= tol and abs(n2 - 1.0) <= tol

    if world == 3:
        d = mat_det(A)
        return abs(abs(d) - 1.0) <= tol

    raise ValueError(f"Unknown world id {world!r}")


# -----------------------------------------------------------------------------
# Empirical theorems: CorrectUnitaryTest and NoFalseUnitary
# -----------------------------------------------------------------------------

TRIALS_PER_WORLD = 200


def test_correct_unitary(world: int, trials: int) -> Tuple[int, int]:
    """
    Test theorem CorrectUnitaryTest in a world:

      correct if is_unitary_world(world, A) == unitary_true(A)
      for all sampled matrices A.

    Returns (ok_count, total_count).
    """
    ok = 0
    total = 0

    # Deterministic misclassification examples for worlds 1,2,3
    if world == 1:
        # U_special: unitary with det = 1, both tests agree.
        U_special = mat(0, 1, -1, 0)        # rotation-like, det = 1
        if is_unitary_world(world, U_special) == unitary_true(U_special):
            ok += 1
        total += 1

        # U_not_special: unitary but det != 1 (e.g. diag(1, i))
        U_not_special = mat(1, 0, 0, 1j)
        # world 1 says False, true says True → mismatch
        if is_unitary_world(world, U_not_special) == unitary_true(U_not_special):
            ok += 1
        total += 1

    elif world == 2:
        # M_col_unit: columns length 1 but not orthogonal → non-unitary.
        c1 = (1 + 0j, 0 + 0j)
        c2 = (0.5 + 0j, math.sqrt(3) / 2 + 0j)
        M_col_unit = ((c1[0], c2[0]), (c1[1], c2[1]))
        if is_unitary_world(world, M_col_unit) == unitary_true(M_col_unit):
            ok += 1
        total += 1

    elif world == 3:
        # M_det1: |det| = 1 but not unitary, e.g. [[1, 1], [0, 1]].
        M_det1 = mat(1, 1, 0, 1)
        if is_unitary_world(world, M_det1) == unitary_true(M_det1):
            ok += 1
        total += 1

    # Random tests
    for _ in range(trials):
        A = random_complex_matrix()
        truth = unitary_true(A)
        approx = is_unitary_world(world, A)
        if truth == approx:
            ok += 1
        total += 1

    return ok, total


def test_sound_unitary(world: int, trials: int) -> Tuple[int, int]:
    """
    Test theorem NoFalseUnitary in a world:

      sound if whenever is_unitary_world(world, A) is True,
      then unitary_true(A) is also True (no false positives).

    Returns (ok_count, total_count), where:
      - total_count is the number of matrices for which the world said "unitary",
      - ok_count is how many of those were truly unitary.
    """
    ok = 0
    total = 0

    # Deterministic tests to force each world's behaviour.
    if world == 0:
        # Identity: truly unitary, world 0 says unitary.
        I = mat_identity()
        if is_unitary_world(world, I):
            total += 1
            if unitary_true(I):
                ok += 1

    elif world == 1:
        # U_special: in SU(2) → world 1 says unitary; truly unitary.
        U_special = mat(0, 1, -1, 0)
        if is_unitary_world(world, U_special):
            total += 1
            if unitary_true(U_special):
                ok += 1

        # U_not_special: unitary but det != 1 → world 1 says False, so
        # it does not affect soundness (only completeness).
        U_not_special = mat(1, 0, 0, 1j)
        if is_unitary_world(world, U_not_special):
            total += 1
            if unitary_true(U_not_special):
                ok += 1

    elif world == 2:
        # M_col_unit: world 2 says unitary, but it is not truly unitary.
        c1 = (1 + 0j, 0 + 0j)
        c2 = (0.5 + 0j, math.sqrt(3) / 2 + 0j)
        M_col_unit = ((c1[0], c2[0]), (c1[1], c2[1]))
        if is_unitary_world(world, M_col_unit):
            total += 1
            if unitary_true(M_col_unit):
                ok += 1

    elif world == 3:
        # M_det1: world 3 says unitary, but it is not truly unitary.
        M_det1 = mat(1, 1, 0, 1)
        if is_unitary_world(world, M_det1):
            total += 1
            if unitary_true(M_det1):
                ok += 1

    # Random matrices: if any are labelled "unitary", they must truly be unitary
    # to preserve soundness.
    for _ in range(trials):
        A = random_complex_matrix()
        approx = is_unitary_world(world, A)
        if approx:
            total += 1
            if unitary_true(A):
                ok += 1

    return ok, total


def estimate_unitary_theorems() -> Tuple[List[str], Dict[int, Dict[str, int]]]:
    """
    For each world, test CorrectUnitaryTest and NoFalseUnitary and collect stats.

    Returns:
      (table_lines, stats)

      stats[world] = {
        "correct_ok": int,
        "correct_total": int,
        "correct_holds": 0 or 1,
        "sound_ok": int,
        "sound_total": int,
        "sound_holds": 0 or 1,
      }
    """
    lines: List[str] = []
    stats: Dict[int, Dict[str, int]] = {}

    header = "world | test description                 | Correct (ok/total) | Sound (ok/total)"
    lines.append(header)
    lines.append("-" * len(header))

    for w in WORLD_IDS:
        correct_ok, correct_total = test_correct_unitary(w, TRIALS_PER_WORLD)
        sound_ok, sound_total = test_sound_unitary(w, TRIALS_PER_WORLD)

        correct_holds = int(correct_total > 0 and correct_ok == correct_total)
        sound_holds = int(sound_total > 0 and sound_ok == sound_total)

        stats[w] = {
            "correct_ok": correct_ok,
            "correct_total": correct_total,
            "correct_holds": correct_holds,
            "sound_ok": sound_ok,
            "sound_total": sound_total,
            "sound_holds": sound_holds,
        }

        desc = WORLD_DESCRIPTIONS[w]
        lines.append(
            f"{w:<5}| {desc:<32} | {correct_ok}/{correct_total:<19} | {sound_ok}/{sound_total}"
        )

    lines.append("")
    lines.append(
        "Heuristically, we expect: world 0 (true unitarity) to satisfy both "
        "CorrectUnitaryTest and NoFalseUnitary; world 1 (special unitary) to "
        "satisfy NoFalseUnitary but not CorrectUnitaryTest; worlds 2 and 3 to "
        "violate both properties due to false positives."
    )

    return lines, stats


# -----------------------------------------------------------------------------
# Higher-order look: Holds₁ / Holds₂ and model extensions
# -----------------------------------------------------------------------------

EXT1: Dict[str, Set[int]] = {}                 # unary: name ↦ {worlds}
EXT2: Dict[str, Set[Tuple[str, str]]] = {}     # binary: name ↦ set of pairs

STRONGER_REL = "rel:stronger"


def thm_int(name: str) -> str:
    """Encode a theorem name as a unary predicate-name, e.g. 'CorrectUnitaryTest' → 'thm:CorrectUnitaryTest'."""
    return f"thm:{name}"


def build_model_extensions(stats: Dict[int, Dict[str, int]]) -> None:
    """
    Populate EXT1 and EXT2 from the empirical stats:

      • Worlds are w ∈ {0,1,2,3}.
      • INTENSIONS:
          - thm:CorrectUnitaryTest
          - thm:NoFalseUnitary
      • EXT1[intension] = set of worlds where the theorem holds on all samples.
      • EXT2[STRONGER_REL] = { (thm:CorrectUnitaryTest, thm:NoFalseUnitary) }.
    """
    EXT1.clear()
    EXT2.clear()

    t_correct = thm_int("CorrectUnitaryTest")
    t_sound = thm_int("NoFalseUnitary")

    EXT1[t_correct] = set(w for w, s in stats.items() if s.get("correct_holds", 0))
    EXT1[t_sound] = set(w for w, s in stats.items() if s.get("sound_holds", 0))

    EXT2[STRONGER_REL] = {(t_correct, t_sound)}


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

      1) True unitarity correctly classifies some explicit matrices.
      2) World 1 is strictly more restrictive than world 0.
      3) World 2 has a clear false positive (unit-length columns but not unitary).
      4) World 3 has a clear false positive (|det| = 1 but not unitary).
      5) Statistics match the intended pattern across worlds.
      6) EXT1 / Holds₁ agree with stats, and Holds₂ 'stronger' relation is
         respected: whenever CorrectUnitaryTest holds, NoFalseUnitary holds.
    """
    notes: List[str] = []

    # 1) True unitarity on explicit matrices
    I = mat_identity()
    U_rot = mat(0, 1, -1, 0)                 # 90-degree-like rotation, unitary, det=1
    U_diag_complex = mat(1, 0, 0, 1j)        # unitary with det = i
    N_nonunit = mat(1, 1, 0, 1)              # upper triangular, not unitary

    check(unitary_true(I), "Identity must be unitary.")
    check(unitary_true(U_rot), "U_rot must be unitary.")
    check(unitary_true(U_diag_complex), "U_diag_complex must be unitary.")
    check(not unitary_true(N_nonunit), "N_nonunit must NOT be unitary.")

    notes.append("PASS 1: unitary_true correctly classifies several explicit matrices.")

    # 2) World 1 stricter than world 0
    # world 0 recognises both U_rot and U_diag_complex as unitary
    check(is_unitary_world(0, U_rot), "World 0 must accept U_rot.")
    check(is_unitary_world(0, U_diag_complex), "World 0 must accept U_diag_complex.")

    # world 1 accepts U_rot but rejects U_diag_complex (det ≈ i, not 1)
    check(is_unitary_world(1, U_rot), "World 1 must accept U_rot (special unitary).")
    check(
        not is_unitary_world(1, U_diag_complex),
        "World 1 must reject U_diag_complex (det ≠ 1).",
    )

    notes.append("PASS 2: World 1 is strictly more restrictive than world 0 (special unitary).")

    # 3) World 2 false positive: columns unit length but not unitary
    c1 = (1 + 0j, 0 + 0j)
    c2 = (0.5 + 0j, math.sqrt(3) / 2 + 0j)
    M_col_unit = ((c1[0], c2[0]), (c1[1], c2[1]))

    check(is_unitary_world(2, M_col_unit), "World 2 must accept M_col_unit (columns length 1).")
    check(
        not unitary_true(M_col_unit),
        "M_col_unit must NOT be truly unitary (columns not orthogonal).",
    )

    notes.append("PASS 3: World 2 has a clear false positive for unitarity.")

    # 4) World 3 false positive: |det| = 1 but not unitary
    M_det1 = mat(1, 1, 0, 1)
    check(is_unitary_world(3, M_det1), "World 3 must accept M_det1 (|det|=1).")
    check(
        not unitary_true(M_det1),
        "M_det1 must NOT be truly unitary (does not preserve inner products).",
    )

    notes.append("PASS 4: World 3 has a clear false positive for unitarity.")

    # 5) Statistics pattern
    # Expected:
    #   world 0: correct_holds=1, sound_holds=1
    #   world 1: correct_holds=0, sound_holds=1
    #   world 2: correct_holds=0, sound_holds=0
    #   world 3: correct_holds=0, sound_holds=0
    for w_id in WORLD_IDS:
        s = stats[w_id]
        if w_id == 0:
            check(
                s["correct_holds"] == 1 and s["sound_holds"] == 1,
                f"World 0: expected both theorems to hold, got {s}.",
            )
        elif w_id == 1:
            check(
                s["correct_holds"] == 0 and s["sound_holds"] == 1,
                f"World 1: expected only NoFalseUnitary to hold, got {s}.",
            )
        else:
            check(
                s["correct_holds"] == 0 and s["sound_holds"] == 0,
                f"World {w_id}: expected both theorems to fail, got {s}.",
            )

    notes.append("PASS 5: Statistics match the intended pattern across all worlds.")

    # 6) EXT1 / Holds₁ agreement and Holds₂ stronger relation
    t_correct = thm_int("CorrectUnitaryTest")
    t_sound = thm_int("NoFalseUnitary")

    for w_id in WORLD_IDS:
        s = stats[w_id]
        check(
            Holds1(t_correct, w_id) == bool(s["correct_holds"]),
            f"Holds1(thm:CorrectUnitaryTest, {w_id}) disagrees with stats.",
        )
        check(
            Holds1(t_sound, w_id) == bool(s["sound_holds"]),
            f"Holds1(thm:NoFalseUnitary, {w_id}) disagrees with stats.",
        )

    check(
        Holds2(STRONGER_REL, t_correct, t_sound),
        "Holds2(rel:stronger, thm:CorrectUnitaryTest, thm:NoFalseUnitary) must be true.",
    )
    for w_id in WORLD_IDS:
        if Holds1(t_correct, w_id):
            check(
                Holds1(t_sound, w_id),
                f"In world {w_id}, CorrectUnitaryTest holds but NoFalseUnitary does not.",
            )

    notes.append("PASS 6: Holds₁/EXT1 are consistent and CorrectUnitaryTest is stronger than NoFalseUnitary.")

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
    "We compare four unitarity tests for 2×2 complex matrices:\n"
    "  world 0: true unitarity (U*U ≈ I),\n"
    "  world 1: special unitary (U*U ≈ I and det ≈ 1),\n"
    "  world 2: columns have unit norm (no orthogonality check),\n"
    "  world 3: |det(A)| ≈ 1 (determinant-magnitude heuristic),\n"
    "and two theorem-names:\n"
    "  CorrectUnitaryTest:  world w's test agrees with true unitarity,\n"
    "  NoFalseUnitary:      world w never labels a non-unitary matrix as unitary.\n"
    "Intuitively, world 0 is the ideal reference, world 1 is a stricter\n"
    "special-unitary view, and worlds 2 and 3 are cheap but unreliable heuristics.\n"
)

REASON_TEXT = (
    "In the first-order core, we represent 2×2 complex matrices as pairs of\n"
    "Python complex numbers and implement basic operations: multiplication,\n"
    "conjugate transpose, determinant, and norms. The true unitarity predicate\n"
    "unitary_true(A) checks whether A* A is equal to the identity matrix.\n"
    "\n"
    "Each world w defines its own is_unitary_w(A):\n"
    "  • world 0 uses the true unitarity condition directly;\n"
    "  • world 1 additionally insists that det(A) is numerically 1, so it only\n"
    "    recognises special unitary matrices;\n"
    "  • world 2 checks only that both columns have length 1, ignoring whether\n"
    "    they are orthogonal;\n"
    "  • world 3 checks only that |det(A)| is 1, a very weak necessary condition.\n"
    "\n"
    "We then test two meta-properties over many random matrices and some\n"
    "carefully chosen examples:\n"
    "  CorrectUnitaryTest: is_unitary_w(A) always matches unitary_true(A),\n"
    "  NoFalseUnitary:     whenever is_unitary_w(A) is True, unitary_true(A)\n"
    "                      is also True (no false positives).\n"
    "\n"
    "From the empirical results we build an extensional model:\n"
    "  • worlds: w ∈ {0,1,2,3},\n"
    "  • theorem-names: thm:CorrectUnitaryTest, thm:NoFalseUnitary,\n"
    "  • EXT1[thm:CorrectUnitaryTest] = { w | world w's test is always correct },\n"
    "  • EXT1[thm:NoFalseUnitary]     = { w | world w's test has no false positives }.\n"
    "\n"
    "We define Holds₁(P, w) to mean w ∈ EXT1[P]. At the binary level, we\n"
    "introduce a relation-name rel:stronger with EXT2[rel:stronger] =\n"
    "  { (thm:CorrectUnitaryTest, thm:NoFalseUnitary) },\n"
    "and let Holds₂ be membership in EXT2. This captures the intuitive idea\n"
    "that a fully correct test is stronger than a merely sound one: in every\n"
    "world where CorrectUnitaryTest holds, NoFalseUnitary holds as well.\n"
    "\n"
    "All the 'higher-order' talk about theorems and their relationships is\n"
    "handled extensionally through Holds₁ and Holds₂, while the actual\n"
    "mathematical content lives in a simple complex-matrix engine in the\n"
    "first-order core."
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
    t_correct = thm_int("CorrectUnitaryTest")
    t_sound = thm_int("NoFalseUnitary")
    for w in WORLD_IDS:
        print(
            f"  world {w}: Holds1({t_correct}, {w})={Holds1(t_correct, w)}, "
            f"Holds1({t_sound}, {w})={Holds1(t_sound, w)}"
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
    table_lines, stats = estimate_unitary_theorems()
    build_model_extensions(stats)
    arc_answer(table_lines)
    arc_reason()
    arc_check(stats)


if __name__ == "__main__":
    main()

