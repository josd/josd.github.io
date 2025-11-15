#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
complex_matrix_gain_worlds.py
=============================

2×2 complex system matrices and worst-case gain
-----------------------------------------------
This script is a small, self-contained Python “lab” for exploring different
tests for the worst-case gain of a 2×2 complex matrix, as used in simple
discrete-time linear systems and filters.

Think of a linear system that maps an input vector u to an output vector y:

    y = A u

where A is a 2×2 complex matrix (for example, a two-channel filter or a
two-antenna MIMO channel at a fixed frequency).

If we measure signals with the usual Euclidean norm, the worst-case gain
of the system is the operator 2-norm of A:

    ||A||₂ = max over unit vectors u of ||A u||₂.

This tells us how much the system can amplify some input direction. A typical
engineering requirement is:

  • the system must not amplify by more than some factor G_max, say G_max = 1.0.

For example, if your hardware saturates or clips above unit amplitude, and
your designed system matrix A at a given frequency has ||A||₂ > 1, then there
exists an input that will be amplified too much.

For a 2×2 complex matrix A, we can compute ||A||₂ exactly: it is equal to the
square root of the largest eigenvalue of the Hermitian matrix A* A (the Gram
matrix). Those eigenvalues are the squares of the singular values of A.


Four worlds of gain estimation
------------------------------
We consider four “worlds” w ∈ {0,1,2,3}. In each world there is a predicate

    safe_w(A)

meaning “this world thinks the system matrix A is safe with respect to the
gain limit G_max = 1.0”.

Each world computes (or approximates) worst-case gain in its own way.

  World 0: true spectral gain (ground truth)
    • Computes ||A||₂ exactly via the largest eigenvalue of A* A.
    • Defines:
          safe_0(A)   iff   ||A||₂ ≤ 1.0  (up to a small tolerance).
    • This is what you would use in a serious numerical library.

  World 1: Frobenius norm bound (conservative)
    • Computes the Frobenius norm:
          ||A||_F = sqrt(sum |a_ij|²).
      For any matrix A, we know:
          ||A||₂ ≤ ||A||_F.
    • Defines:
          safe_1(A)   iff   ||A||_F ≤ 1.0.
    • This test is cheap and conservative:
        - if world 1 says “safe”, then A is truly safe;
        - but it may reject some safe matrices as “unsafe”.

  World 2: column-length heuristic (too optimistic)
    • Looks only at the lengths of the columns of A:
          c₁, c₂ = columns of A
          col_norm_j = ||c_j||₂
    • Defines:
          safe_2(A)   iff   max_j col_norm_j ≤ 1.0.
    • This is not a valid upper bound on ||A||₂: the worst amplification may
      happen for a combination of columns, not just for a single column. So
      world 2 can wrongly declare some dangerous matrices safe.

  World 3: max-entry heuristic (very crude)
    • Looks only at the largest entry in absolute value:
          m = max_ij |a_ij|.
    • Defines:
          safe_3(A)   iff   m ≤ 1.0.
    • This ignores how entries combine; it is a very rough heuristic and can
      easily miss dangerous matrices whose individual entries are small but
      cooperate to produce a large gain.


Real-world angle
----------------
You can think of A as the frequency-response matrix of a 2×2 filter at a
particular frequency, or as the gain matrix of a small two-channel amplifier.
The real engineering question is:

  “Is this matrix safe with respect to my maximum allowed gain G_max = 1.0?”

World 0 answers that question using the correct spectral norm. Worlds 1–3
offer various shortcuts; world 1 is safe but pessimistic, while worlds 2
and 3 can be dangerously optimistic.


Higher-order look, first-order core
-----------------------------------
We follow the “higher-order look, first-order core” pattern
(https://josd.github.io/higher-order-look-first-order-core/):

  • First-order core:
      - 2×2 complex matrices as tuples of Python complex numbers;
      - basic operations: matrix multiplication, conjugate transpose,
        Frobenius norm, column norms, max entry;
      - exact operator 2-norm via eigenvalues of A* A;
      - a true safety test safe_true(A) using ||A||₂ ≤ 1;
      - four world-specific safety tests safe_world(world, A);
      - random sampling of small complex matrices to compare world tests
        with the true safety test.

  • Higher-order look:
      - worlds: W = {0,1,2,3};
      - theorem-names (intensions):

            thm:CorrectSafetyTest
            thm:NoFalseSafe

      - a unary predicate

            Holds₁(P, w)

        interpreted extensionally via a map

            EXT1: Dict[str, Set[int]]

        such that:

            Holds1(P, w)  iff  w ∈ EXT1[P],

        i.e. world w empirically satisfies theorem P on all sampled matrices.

      - a binary relation-name

            rel:stronger

        with a binary predicate

            Holds₂(rel:stronger, X, Y)

        interpreted by a map

            EXT2: Dict[str, Set[(str, str)]]

        so that:

            Holds2(R, X, Y)  iff  (X, Y) ∈ EXT2[R].

        We encode the idea that a fully correct safety test is stronger than
        a merely “no false safe decisions” test by setting:

            EXT2["rel:stronger"] = {
              (thm:CorrectSafetyTest, thm:NoFalseSafe)
            }.

In this tiny universe we expect:

  • world 0 (true spectral norm) to satisfy both CorrectSafetyTest and
    NoFalseSafe;
  • world 1 (Frobenius bound) to satisfy NoFalseSafe but not CorrectSafetyTest
    (it may falsely reject safe matrices);
  • worlds 2 and 3 (column-length and max-entry heuristics) to fail both
    properties, because they can declare unsafe matrices safe.


What the script prints
----------------------
Running:

    python3 complex_matrix_gain_worlds.py

produces three ARC-style sections:

  1) Answer
     • description of the four worlds and the two theorem-names;
     • a table of empirical results per world:
           world | test description           | Correct (ok/total) | NoFalseSafe (ok/total)
     • Holds₁ judgements for each world and theorem-name.

  2) Reason why
     • an informal explanation of worst-case gain and the spectral norm;
     • how each world’s test behaves (exact, conservative, or risky);
     • how the Holds₁ / Holds₂ view is built from the extensional statistics.

  3) Check (harness)
     • at least six independent tests checking that:
         - the spectral norm behaves as expected on simple matrices;
         - world 0’s safety test matches the true one on explicit examples;
         - world 1 is more conservative (it rejects some safe matrices);
         - worlds 2 and 3 have clear false “safe” decisions;
         - the statistics match the intended pattern across worlds;
         - EXT1 / Holds₁ are consistent with those statistics;
         - the Holds₂ “stronger” relation is respected:
             whenever CorrectSafetyTest holds in a world,
             NoFalseSafe also holds there.

Python 3.9+; no external packages.
"""

from __future__ import annotations

import math
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


def frobenius_norm(A: Matrix) -> float:
    (a11, a12), (a21, a22) = A
    return math.sqrt(
        abs(a11) ** 2 + abs(a12) ** 2 +
        abs(a21) ** 2 + abs(a22) ** 2
    )


def max_column_norm(A: Matrix) -> float:
    """Maximum Euclidean norm of the columns of A."""
    (a11, a12), (a21, a22) = A
    n1 = math.sqrt(abs(a11) ** 2 + abs(a21) ** 2)
    n2 = math.sqrt(abs(a12) ** 2 + abs(a22) ** 2)
    return max(n1, n2)


def max_abs_entry(A: Matrix) -> float:
    (a11, a12), (a21, a22) = A
    return max(abs(a11), abs(a12), abs(a21), abs(a22))


# -----------------------------------------------------------------------------
# Spectral norm via eigenvalues of A* A
# -----------------------------------------------------------------------------

def eigenvalues_hermitian_2x2(H: Matrix) -> Tuple[float, float]:
    """
    Eigenvalues of a 2×2 Hermitian matrix H.

    For H = [[a, b],
             [conj(b), d]] with real a, d, we have:
      trace  t = a + d
      det    Δ = ad - |b|²
      discriminant = t² - 4Δ ≥ 0
      eigenvalues λ₁,₂ = (t ± sqrt(discriminant)) / 2
    """
    (h11, h12), (h21, h22) = H
    a = h11.real
    d = h22.real
    det = (h11 * h22 - h12 * h21).real
    trace = a + d
    disc = trace * trace - 4.0 * det
    if disc < 0:
        disc = 0.0  # guard against tiny negative due to rounding
    root = math.sqrt(disc)
    lam1 = (trace + root) / 2.0
    lam2 = (trace - root) / 2.0
    return lam1, lam2


def spectral_norm(A: Matrix) -> float:
    """
    Operator 2-norm ||A||₂ = sqrt(λ_max(A* A)).

    A* A is Hermitian and positive semidefinite; we compute its eigenvalues
    and take the square root of the larger one.
    """
    A_star = mat_conj_transpose(A)
    H = mat_mul(A_star, A)  # Gram matrix (Hermitian)
    lam1, lam2 = eigenvalues_hermitian_2x2(H)
    lam_max = max(lam1, lam2, 0.0)
    return math.sqrt(lam_max)


# -----------------------------------------------------------------------------
# True safety and world-specific safety tests
# -----------------------------------------------------------------------------

GAIN_LIMIT = 1.0
TOL = 1e-9

WORLD_IDS = (0, 1, 2, 3)

WORLD_DESCRIPTIONS: Dict[int, str] = {
    0: "true spectral norm (ground truth)",
    1: "Frobenius norm bound (conservative)",
    2: "column-length heuristic",
    3: "max-entry heuristic",
}


def safe_true(A: Matrix, limit: float = GAIN_LIMIT, tol: float = TOL) -> bool:
    """True safety: ||A||₂ ≤ limit."""
    return spectral_norm(A) <= limit + tol


def safe_world(world: int, A: Matrix, limit: float = GAIN_LIMIT, tol: float = TOL) -> bool:
    """
    World-specific safety tests:

      world 0: true spectral norm (ground truth).
      world 1: Frobenius norm <= limit.
      world 2: max column norm <= limit.
      world 3: max absolute entry <= limit.
    """
    if world == 0:
        return safe_true(A, limit, tol)

    if world == 1:
        return frobenius_norm(A) <= limit + tol

    if world == 2:
        return max_column_norm(A) <= limit + tol

    if world == 3:
        return max_abs_entry(A) <= limit + tol

    raise ValueError(f"Unknown world id {world!r}")


# -----------------------------------------------------------------------------
# Empirical theorems: CorrectSafetyTest and NoFalseSafe
# -----------------------------------------------------------------------------

TRIALS_PER_WORLD = 200


def test_correct_safety(world: int, trials: int) -> Tuple[int, int]:
    """
    Test theorem CorrectSafetyTest in a world:

      correct if safe_world(world, A) == safe_true(A)
      for all sampled matrices A.

    Returns (ok_count, total_count).
    """
    ok = 0
    total = 0

    # Deterministic misclassification examples for worlds 1,2,3
    if world == 1:
        # A_frob_bad: safe_true but Frobenius > 1 → world 1 rejects.
        # diag(1, 0.7): spectral_norm = 1, frobenius ≈ 1.22 > 1.
        A_frob_bad = mat(1.0, 0.0, 0.0, 0.7)
        truth = safe_true(A_frob_bad)
        approx = safe_world(world, A_frob_bad)
        if truth == approx:
            ok += 1
        total += 1

    elif world == 2:
        # A_col_bad: columns each of norm 1, but spectral norm = sqrt(2) > 1.
        # Columns (1,0) and (1,0) → rank-1 matrix with largest singular value sqrt(2).
        A_col_bad = mat(1.0, 1.0, 0.0, 0.0)
        truth = safe_true(A_col_bad)
        approx = safe_world(world, A_col_bad)
        if truth == approx:
            ok += 1
        total += 1

    elif world == 3:
        # A_entry_bad: every entry ≤1 in magnitude, but spectral norm = 2.
        A_entry_bad = mat(1.0, 1.0, 1.0, 1.0)
        truth = safe_true(A_entry_bad)
        approx = safe_world(world, A_entry_bad)
        if truth == approx:
            ok += 1
        total += 1

    # Random matrices
    for _ in range(trials):
        A = random_complex_matrix()
        truth = safe_true(A)
        approx = safe_world(world, A)
        if truth == approx:
            ok += 1
        total += 1

    return ok, total


def test_no_false_safe(world: int, trials: int) -> Tuple[int, int]:
    """
    Test theorem NoFalseSafe in a world:

      no false safe if whenever safe_world(world, A) is True,
      safe_true(A) is also True (no unsafe matrix is classified safe).

    Returns (ok_count, total_count), where:
      - total_count is the number of matrices for which the world said "safe",
      - ok_count is how many of those were truly safe.
    """
    ok = 0
    total = 0

    # A clearly safe small-gain matrix used in all worlds
    A_small_safe = mat(0.6, 0.0, 0.0, 0.4)
    approx = safe_world(world, A_small_safe)
    if approx:
        total += 1
        if safe_true(A_small_safe):
            ok += 1

    # World-specific deliberate false-safe examples (for 2 and 3)
    if world == 2:
        A_col_bad = mat(1.0, 1.0, 0.0, 0.0)
        approx2 = safe_world(world, A_col_bad)
        if approx2:
            total += 1
            if safe_true(A_col_bad):
                ok += 1
    elif world == 3:
        A_entry_bad = mat(1.0, 1.0, 1.0, 1.0)
        approx3 = safe_world(world, A_entry_bad)
        if approx3:
            total += 1
            if safe_true(A_entry_bad):
                ok += 1

    # Random matrices: whenever the world says "safe", check the truth.
    for _ in range(trials):
        A = random_complex_matrix()
        approx_r = safe_world(world, A)
        if approx_r:
            total += 1
            if safe_true(A):
                ok += 1

    return ok, total


def estimate_safety_theorems() -> Tuple[List[str], Dict[int, Dict[str, int]]]:
    """
    For each world, test CorrectSafetyTest and NoFalseSafe and collect stats.

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

    header = "world | test description                 | Correct (ok/total) | NoFalseSafe (ok/total)"
    lines.append(header)
    lines.append("-" * len(header))

    for w in WORLD_IDS:
        correct_ok, correct_total = test_correct_safety(w, TRIALS_PER_WORLD)
        sound_ok, sound_total = test_no_false_safe(w, TRIALS_PER_WORLD)

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
        "Heuristically, we expect: world 0 (true spectral norm) to satisfy both "
        "CorrectSafetyTest and NoFalseSafe; world 1 (Frobenius bound) to satisfy "
        "NoFalseSafe but not CorrectSafetyTest; worlds 2 and 3 (column-length and "
        "max-entry heuristics) to fail both properties due to false safe decisions."
    )

    return lines, stats


# -----------------------------------------------------------------------------
# Higher-order look: Holds₁ / Holds₂ and model extensions
# -----------------------------------------------------------------------------

EXT1: Dict[str, Set[int]] = {}                 # unary: name ↦ {worlds}
EXT2: Dict[str, Set[Tuple[str, str]]] = {}     # binary: name ↦ set of pairs

STRONGER_REL = "rel:stronger"


def thm_int(name: str) -> str:
    """Encode a theorem name as a unary predicate-name, e.g. 'CorrectSafetyTest' → 'thm:CorrectSafetyTest'."""
    return f"thm:{name}"


def build_model_extensions(stats: Dict[int, Dict[str, int]]) -> None:
    """
    Populate EXT1 and EXT2 from the empirical stats:

      • Worlds are w ∈ {0,1,2,3}.
      • INTENSIONS:
          - thm:CorrectSafetyTest
          - thm:NoFalseSafe
      • EXT1[intension] = set of worlds where the theorem holds on all samples.
      • EXT2[STRONGER_REL] = { (thm:CorrectSafetyTest, thm:NoFalseSafe) }.
    """
    EXT1.clear()
    EXT2.clear()

    t_correct = thm_int("CorrectSafetyTest")
    t_sound = thm_int("NoFalseSafe")

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

      1) Spectral norm behaves as expected on simple matrices and is <= Frobenius norm.
      2) World 0 classification matches safe_true on explicit examples.
      3) World 1 is more conservative than world 0 (rejects some safe matrices).
      4) Worlds 2 and 3 each have a clear false-safe example.
      5) Statistics match the intended pattern across worlds.
      6) EXT1 / Holds₁ agree with stats, and the Holds₂ 'stronger' relation
         is respected: whenever CorrectSafetyTest holds in a world,
         NoFalseSafe holds there too.
    """
    notes: List[str] = []

    # 1) Spectral norm sanity and inequality ||A||₂ ≤ ||A||_F
    I = mat(1.0, 0.0, 0.0, 1.0)
    A_diag = mat(2.0, 0.0, 0.0, 0.5)
    A_rank1 = mat(1.0, 1.0, 0.0, 0.0)

    # Identity: norm = 1
    check(abs(spectral_norm(I) - 1.0) < 1e-9, "spectral_norm(I) must be 1.")

    # Diagonal: spectral_norm is max diagonal magnitude.
    check(
        abs(spectral_norm(A_diag) - 2.0) < 1e-9,
        "spectral_norm(diag(2,0.5)) must be 2.",
    )

    # Rank-1 with columns equal: spectral_norm must be sqrt(2).
    check(
        abs(spectral_norm(A_rank1) - math.sqrt(2.0)) < 1e-9,
        "spectral_norm([[1,1],[0,0]]) must be sqrt(2).",
    )

    # Inequality ||A||₂ ≤ ||A||_F on a few random matrices.
    for _ in range(10):
        A = random_complex_matrix()
        check(
            spectral_norm(A) <= frobenius_norm(A) + 1e-9,
            "spectral_norm(A) must be ≤ frobenius_norm(A).",
        )

    notes.append("PASS 1: spectral_norm behaves as expected and is ≤ Frobenius norm on tested matrices.")

    # 2) World 0 vs safe_true on explicit examples
    examples = [
        ("small safe", mat(0.6, 0.0, 0.0, 0.4)),
        ("borderline safe", I),
        ("unsafe diag", mat(1.5, 0.0, 0.0, 1.0)),
        ("rank-1 unsafe", A_rank1),
    ]
    for name, A in examples:
        true_safe = safe_true(A)
        w0_safe = safe_world(0, A)
        check(
            true_safe == w0_safe,
            f"World 0 must match safe_true for {name} matrix.",
        )

    notes.append("PASS 2: World 0 safety classification matches true safety on explicit examples.")

    # 3) World 1 is more conservative than world 0
    A_frob_bad = mat(1.0, 0.0, 0.0, 0.7)  # safe_true but Frobenius > 1
    check(safe_true(A_frob_bad), "A_frob_bad must be truly safe (spectral_norm ≤ 1).")
    check(
        not safe_world(1, A_frob_bad),
        "World 1 must reject A_frob_bad due to Frobenius norm > 1.",
    )

    notes.append("PASS 3: World 1 is strictly more conservative than world 0 (Frobenius bound).")

    # 4) Worlds 2 and 3 false-safe examples
    A_col_bad = A_rank1  # [[1,1],[0,0]]: column norms 1, spectral_norm = sqrt(2) > 1
    check(
        max_column_norm(A_col_bad) <= GAIN_LIMIT + TOL,
        "A_col_bad's columns must each have norm 1.",
    )
    check(
        not safe_true(A_col_bad),
        "A_col_bad must be truly unsafe (spectral_norm > 1).",
    )
    check(
        safe_world(2, A_col_bad),
        "World 2 must classify A_col_bad as safe (column-length heuristic).",
    )

    A_entry_bad = mat(1.0, 1.0, 1.0, 1.0)
    check(
        max_abs_entry(A_entry_bad) <= GAIN_LIMIT + TOL,
        "A_entry_bad must have all entries with magnitude ≤ 1.",
    )
    check(
        not safe_true(A_entry_bad),
        "A_entry_bad must be truly unsafe (spectral_norm = 2).",
    )
    check(
        safe_world(3, A_entry_bad),
        "World 3 must classify A_entry_bad as safe (max-entry heuristic).",
    )

    notes.append("PASS 4: Worlds 2 and 3 have clear false-safe matrices.")

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
                f"World 1: expected only NoFalseSafe to hold, got {s}.",
            )
        else:
            check(
                s["correct_holds"] == 0 and s["sound_holds"] == 0,
                f"World {w_id}: expected both theorems to fail, got {s}.",
            )

    notes.append("PASS 5: Statistics match the intended pattern across all worlds.")

    # 6) EXT1 / Holds₁ consistency and Holds₂ stronger relation
    t_correct = thm_int("CorrectSafetyTest")
    t_sound = thm_int("NoFalseSafe")

    for w_id in WORLD_IDS:
        s = stats[w_id]
        check(
            Holds1(t_correct, w_id) == bool(s["correct_holds"]),
            f"Holds1(thm:CorrectSafetyTest, {w_id}) disagrees with stats.",
        )
        check(
            Holds1(t_sound, w_id) == bool(s["sound_holds"]),
            f"Holds1(thm:NoFalseSafe, {w_id}) disagrees with stats.",
        )

    check(
        Holds2(STRONGER_REL, t_correct, t_sound),
        "Holds2(rel:stronger, thm:CorrectSafetyTest, thm:NoFalseSafe) must be true.",
    )
    for w_id in WORLD_IDS:
        if Holds1(t_correct, w_id):
            check(
                Holds1(t_sound, w_id),
                f"In world {w_id}, CorrectSafetyTest holds but NoFalseSafe does not.",
            )

    notes.append("PASS 6: Holds₁/EXT1 are consistent and CorrectSafetyTest is stronger than NoFalseSafe.")

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
    "We compare four safety tests for 2×2 complex system matrices with respect to\n"
    "a gain limit G_max = 1:\n"
    "  world 0: true spectral norm (||A||₂) via eigenvalues of A* A,\n"
    "  world 1: Frobenius norm bound (||A||_F ≤ 1 ⇒ safe),\n"
    "  world 2: column-length heuristic (max column norm ≤ 1 ⇒ safe),\n"
    "  world 3: max-entry heuristic (max |a_ij| ≤ 1 ⇒ safe),\n"
    "and two theorem-names:\n"
    "  CorrectSafetyTest:  world w's 'safe' predicate agrees with the true one,\n"
    "  NoFalseSafe:        world w never declares an unsafe matrix safe.\n"
    "In engineering terms, world 0 corresponds to the ideal spectral-gain check,\n"
    "world 1 is a conservative upper bound, and worlds 2 and 3 are cheap but\n"
    "potentially dangerous shortcuts.\n"
)

REASON_TEXT = (
    "In the first-order core, we represent 2×2 complex matrices as pairs of\n"
    "Python complex numbers. We compute the operator 2-norm ||A||₂ by forming\n"
    "the Gram matrix A* A, which is 2×2 Hermitian, and then taking the square\n"
    "root of its largest eigenvalue. This gives an exact worst-case gain for\n"
    "the linear map u ↦ A u under Euclidean norms. The true safety predicate\n"
    "safe_true(A) requires ||A||₂ ≤ 1.\n"
    "\n"
    "Each world defines a simpler or restricted safety test safe_world(w, A):\n"
    "  • world 0 uses safe_true itself;\n"
    "  • world 1 uses the inequality ||A||₂ ≤ ||A||_F and insists ||A||_F ≤ 1,\n"
    "    which is conservative but can reject safe matrices;\n"
    "  • world 2 tests only the lengths of the columns, ignoring combinations\n"
    "    of columns that can produce larger gains (e.g. two equal columns give\n"
    "    a spectral norm of sqrt(2) even though each column has norm 1);\n"
    "  • world 3 tests only the largest individual entry, ignoring how entries\n"
    "    cooperate to amplify certain directions.\n"
    "\n"
    "We test two meta-properties over many random matrices and some deliberate\n"
    "examples: CorrectSafetyTest (no mismatches with safe_true) and NoFalseSafe\n"
    "(no unsafe matrix ever declared safe). From the results we build an\n"
    "extensional model:\n"
    "  • worlds: w ∈ {0,1,2,3},\n"
    "  • theorem-names: thm:CorrectSafetyTest, thm:NoFalseSafe,\n"
    "  • EXT1[thm:CorrectSafetyTest] = { w | safe_world(w,·) matches safe_true on all samples },\n"
    "  • EXT1[thm:NoFalseSafe]       = { w | safe_world(w,·) has no observed false-safe decisions }.\n"
    "\n"
    "We interpret Holds₁(P, w) as membership of w in EXT1[P]. At the binary\n"
    "level, we set EXT2[rel:stronger] = { (thm:CorrectSafetyTest,\n"
    "thm:NoFalseSafe) } and define Holds₂ by membership in EXT2. This captures\n"
    "the idea that a fully correct safety test is stronger than a merely\n"
    "one-sided (no false safe) test: in any world where CorrectSafetyTest holds\n"
    "(here, world 0), NoFalseSafe holds as well. The logical layer is thus a\n"
    "thin wrapper over the concrete numerical behaviour of different gain\n"
    "tests, turning a very practical question—“Is this 2×2 complex system safe\n"
    "under my gain limit?”—into a clean higher-order-looking story."
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
    t_correct = thm_int("CorrectSafetyTest")
    t_sound = thm_int("NoFalseSafe")
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
    table_lines, stats = estimate_safety_theorems()
    build_model_extensions(stats)
    arc_answer(table_lines)
    arc_reason()
    arc_check(stats)


if __name__ == "__main__":
    main()

