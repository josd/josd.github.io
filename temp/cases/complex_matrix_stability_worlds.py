#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
complex_matrix_stability_worlds.py
==================================

Discrete-time stability for 2×2 complex systems
-----------------------------------------------
This script is a tiny, self-contained Python program about stability of
discrete-time linear systems

    x_{k+1} = A x_k

where A is a 2×2 complex matrix. Such models occur in control, signal
processing, and numerical algorithms. Stability is governed by the
eigenvalues of A:

  • The system is **stable** if all eigenvalues λ of A satisfy |λ| ≤ 1.
  • It is **damped** (strictly stable) if all eigenvalues satisfy |λ| ≤ 0.9.

The code can be used directly to test stability of a given 2×2 complex
matrix A via exact eigenvalues (spectral radius). On top of that, it also
compares several *approximate* stability checks.


Four "worlds" of stability tests
--------------------------------
We consider four "worlds" w ∈ {0,1,2,3}, each with its own way to decide
whether a matrix A is stable or damped:

  World 0: exact spectral-radius test (ground truth)
    - Eigenvalues of A are computed analytically.
    - stable(A) = (max |λ| ≤ 1.0)
    - damped(A) = (max |λ| ≤ 0.9)

  World 1: Gershgorin-disc test (conservative)
    - Uses Gershgorin circles:
          disc 1: center a11, radius |a12|
          disc 2: center a22, radius |a21|
    - Approximate stability:
          max(|a11|+|a12|, |a22|+|a21|) ≤ threshold.
    - Two thresholds:
          1.0 for "stable", 0.9 for "damped".
    - This is sound but incomplete: it never calls an actually unstable
      matrix stable, but it may reject some systems that are in fact stable.

  World 2: diagonal-only test (too coarse)
    - Looks only at a11 and a22:
          stable(A) ≈ (max(|a11|, |a22|) ≤ threshold)
    - Ignores off-diagonal coupling.
    - Very cheap, but can be badly wrong.

  World 3: tiny-norm heuristic (deliberately broken)
    - Uses the Frobenius norm:
          ||A||_F = sqrt(sum |a_ij|^2).
    - Declares A stable only if ||A||_F ≤ 0.5,
      and damped only if ||A||_F ≤ 0.4.
    - This almost never matches true eigenvalue-based stability.


Real-world angle
----------------
World 0 models the **correct** stability test used in engineering:
compute eigenvalues and check their magnitudes. World 1 is a classical
analytic bound (Gershgorin discs) that can be used when explicit
eigenvalues are hard to get. Worlds 2 and 3 mimic very cheap but crude
heuristics: "look at the diagonal only" or "trust a small norm".

The helper functions:

  - spectral_radius(A)
  - stable_true(A)
  - damped_true(A)

give a direct, realistic stability check for any 2×2 complex A.


Higher-order look, first-order core
-----------------------------------
We follow the “higher-order look, first-order core” pattern
(https://josd.github.io/higher-order-look-first-order-core/):

  • First-order core:
      - 2×2 complex matrices as tuples of Python complex numbers;
      - exact eigenvalue computation for 2×2 matrices;
      - four world-dependent stability predicates (one exact, three approximations);
      - random sampling of small integer-valued complex matrices to test:

          CorrectStable:
            in world w,  stable_w(A) == stable_true(A)  for all sampled A.

          CorrectDamped:
            in world w,  damped_w(A) == damped_true(A)  for all sampled A.

  • Higher-order look:
      - worlds: W = {0,1,2,3};
      - theorem-names (intensions):

            thm:CorrectStable
            thm:CorrectDamped

      - a unary predicate

            Holds₁(P, w)

        read extensionally from:

            EXT1: Dict[str, Set[int]]

        so that:

            Holds1(P, w)  iff  w ∈ EXT1[P],

        i.e. world w empirically satisfies theorem P (no mismatches on samples).

      - a binary relation-name

            rel:stronger

        relating intensions:

            Holds₂("rel:stronger", thm:CorrectDamped, thm:CorrectStable)

        expressing that in this tiny universe, whenever a stability test is
        entirely correct for "damped" systems, it is also entirely correct for
        "stable" systems. Implementation:

            EXT2["rel:stronger"] = { (thm:CorrectDamped, thm:CorrectStable) }
            Holds2(R, X, Y)  iff  (X, Y) ∈ EXT2[R].

All real semantics (spectral radius, Gershgorin, norms) live in the simple
first-order core. Holds₁ and Holds₂ just read off the resulting extensional
model (EXT1, EXT2).


What the script prints
----------------------
Running:

    python3 complex_matrix_stability_worlds.py

prints three ARC-style sections:

  1) Answer
     • description of the four worlds and two theorem-names;
     • a table of empirical stats per world:
           world | test description     | Stable (ok/total) | Damped (ok/total)
     • Holds₁ judgements for each world and theorem-name.

  2) Reason why
     • a short explanation of how stability is computed from eigenvalues;
     • how Gershgorin, diagonal-only, and norm heuristics behave;
     • and how the Holds₁ / Holds₂ picture is built.

  3) Check (harness)
     • at least six independent tests checking that:
         - eigenvalues and spectral radius behave as expected on simple matrices;
         - world 0 matches ground truth on concrete examples;
         - worlds 1, 2, 3 each misclassify at least one chosen system;
         - statistics match the expected pattern:
             world 0 satisfies both theorems,
             worlds 1–3 satisfy neither;
         - EXT1 / Holds₁ agree with the stats;
         - the Holds₂ “stronger” relation is respected:

               whenever Holds1(thm:CorrectDamped, w) is true,
               Holds1(thm:CorrectStable, w) is also true.

Python 3.9+; no external packages.
"""

from __future__ import annotations

import cmath
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
    """Random 2×2 complex matrix with integer real/imag parts."""
    def rnd() -> complex:
        return complex(
            randrange(-max_abs, max_abs + 1),
            randrange(-max_abs, max_abs + 1),
        )

    return mat(rnd(), rnd(), rnd(), rnd())


def mat_equal(A: Matrix, B: Matrix, tol: float = 1e-9) -> bool:
    return (
        abs(A[0][0] - B[0][0]) <= tol and
        abs(A[0][1] - B[0][1]) <= tol and
        abs(A[1][0] - B[1][0]) <= tol and
        abs(A[1][1] - B[1][1]) <= tol
    )


def frobenius_norm(A: Matrix) -> float:
    return math.sqrt(
        abs(A[0][0]) ** 2 + abs(A[0][1]) ** 2 +
        abs(A[1][0]) ** 2 + abs(A[1][1]) ** 2
    )


# -----------------------------------------------------------------------------
# Exact eigenvalues and true stability
# -----------------------------------------------------------------------------

def eigenvalues_2x2(A: Matrix) -> Tuple[complex, complex]:
    """
    Analytic eigenvalues for a 2×2 matrix:

        A = [[a, b],
             [c, d]]

    Characteristic polynomial: λ² - (a+d)λ + (ad - bc).
    """
    (a11, a12), (a21, a22) = A
    tr = a11 + a22
    det = a11 * a22 - a12 * a21
    disc = tr * tr - 4 * det
    root = cmath.sqrt(disc)
    lam1 = (tr + root) / 2
    lam2 = (tr - root) / 2
    return lam1, lam2


def spectral_radius(A: Matrix) -> float:
    lam1, lam2 = eigenvalues_2x2(A)
    return max(abs(lam1), abs(lam2))


def stable_true(A: Matrix, tol: float = 1e-9) -> bool:
    """True discrete-time stability: all eigenvalues inside or on the unit circle."""
    return spectral_radius(A) <= 1.0 + tol


def damped_true(A: Matrix, tol: float = 1e-9) -> bool:
    """
    "Damped" system: all eigenvalues strictly inside the unit circle,
    with a safety margin 0.9.
    """
    return spectral_radius(A) <= 0.9 + tol


# -----------------------------------------------------------------------------
# World-specific approximate stability tests
# -----------------------------------------------------------------------------

WORLD_IDS = (0, 1, 2, 3)

WORLD_DESCRIPTIONS: Dict[int, str] = {
    0: "exact spectral radius (ground truth)",
    1: "Gershgorin discs (conservative bound)",
    2: "diagonal-only heuristic",
    3: "tiny Frobenius norm heuristic",
}


def gershgorin_radius(A: Matrix) -> float:
    """Maximal Gershgorin-disc bound for eigenvalues."""
    (a11, a12), (a21, a22) = A
    r1 = abs(a12)
    r2 = abs(a21)
    return max(abs(a11) + r1, abs(a22) + r2)


def gershgorin_stable(A: Matrix, threshold: float, tol: float = 1e-9) -> bool:
    return gershgorin_radius(A) <= threshold + tol


def diag_stable(A: Matrix, threshold: float, tol: float = 1e-9) -> bool:
    (a11, _), (_, a22) = A
    return max(abs(a11), abs(a22)) <= threshold + tol


def fro_stable(A: Matrix, threshold: float, tol: float = 1e-9) -> bool:
    return frobenius_norm(A) <= threshold + tol


def classify_world(world: int, A: Matrix) -> Tuple[bool, bool]:
    """
    World-specific stable/damped classification:

      returns (is_stable, is_damped).

    Worlds:
      0: exact eigenvalue-based classification (ground truth).
      1: Gershgorin discs with thresholds 1.0 / 0.9.
      2: diagonal-only with thresholds 1.0 / 0.9.
      3: Frobenius-norm heuristic with thresholds 0.5 / 0.4.
    """
    if world == 0:
        return stable_true(A), damped_true(A)

    if world == 1:
        st = gershgorin_stable(A, 1.0)
        dp = gershgorin_stable(A, 0.9)
        return st, dp

    if world == 2:
        st = diag_stable(A, 1.0)
        dp = diag_stable(A, 0.9)
        return st, dp

    if world == 3:
        st = fro_stable(A, 0.5)
        dp = fro_stable(A, 0.4)
        return st, dp

    raise ValueError(f"Unknown world id {world!r}")


# -----------------------------------------------------------------------------
# Empirical theorems: CorrectStable and CorrectDamped
# -----------------------------------------------------------------------------

TRIALS_PER_WORLD = 200


def test_correct_stable(world: int, trials: int) -> Tuple[int, int]:
    """
    Test theorem CorrectStable in a world:

      correct if stable_w(A) == stable_true(A) for all sampled A.

    Returns (ok_count, total_count).
    """
    ok = 0
    total = 0

    # Deterministic misclassification examples for worlds 1,2,3.
    if world == 1:
        # Stable in truth, but Gershgorin rejects (large off-diagonal).
        A = mat(0.0, 2.0, 0.0, 0.0)   # eigenvalues 0,0
        truth = stable_true(A)
        approx, _ = classify_world(world, A)
        if truth == approx:
            ok += 1
        total += 1
    elif world == 2:
        # Unstable in truth, but diagonal-only test says "stable".
        A = mat(0.0, 2.0, -2.0, 0.0)  # eigenvalues ±2i, radius 2
        truth = stable_true(A)
        approx, _ = classify_world(world, A)
        if truth == approx:
            ok += 1
        total += 1
    elif world == 3:
        # Stable in truth (unit circle), but norm threshold rejects.
        A = mat(1.0, 0.0, 0.0, 1.0)   # identity, eigenvalues 1,1
        truth = stable_true(A)
        approx, _ = classify_world(world, A)
        if truth == approx:
            ok += 1
        total += 1

    for _ in range(trials):
        A = random_complex_matrix()
        truth = stable_true(A)
        approx, _ = classify_world(world, A)
        if truth == approx:
            ok += 1
        total += 1

    return ok, total


def test_correct_damped(world: int, trials: int) -> Tuple[int, int]:
    """
    Test theorem CorrectDamped in a world:

      correct if damped_w(A) == damped_true(A) for all sampled A.

    Returns (ok_count, total_count).
    """
    ok = 0
    total = 0

    # Deterministic misclassification examples for worlds 1,2,3.
    if world == 1:
        # Damped in truth (eigenvalues at 0), but Gershgorin with 0.9 rejects.
        A = mat(0.0, 1.2, 0.0, 0.0)   # eigenvalues 0,0
        truth = damped_true(A)
        _, approx = classify_world(world, A)
        if truth == approx:
            ok += 1
        total += 1
    elif world == 2:
        # Not damped in truth, but diagonal-only says "damped".
        A = mat(0.0, 1.0, -1.0, 0.0)  # eigenvalues ±i, radius 1
        truth = damped_true(A)
        _, approx = classify_world(world, A)
        if truth == approx:
            ok += 1
        total += 1
    elif world == 3:
        # Damped in truth: 0.8 I (eigenvalues 0.8); norm threshold rejects.
        A = mat(0.8, 0.0, 0.0, 0.8)
        truth = damped_true(A)
        _, approx = classify_world(world, A)
        if truth == approx:
            ok += 1
        total += 1

    for _ in range(trials):
        A = random_complex_matrix()
        truth = damped_true(A)
        _, approx = classify_world(world, A)
        if truth == approx:
            ok += 1
        total += 1

    return ok, total


def estimate_stability_theorems() -> Tuple[List[str], Dict[int, Dict[str, int]]]:
    """
    For each world, test CorrectStable and CorrectDamped and collect stats.

    Returns:
      (table_lines, stats)

      stats[world] = {
        "stab_ok": int,
        "stab_total": int,
        "stab_holds": 0 or 1,
        "damp_ok": int,
        "damp_total": int,
        "damp_holds": 0 or 1,
      }
    """
    lines: List[str] = []
    stats: Dict[int, Dict[str, int]] = {}

    header = "world | test description                 | Stable (ok/total) | Damped (ok/total)"
    lines.append(header)
    lines.append("-" * len(header))

    for w in WORLD_IDS:
        stab_ok, stab_total = test_correct_stable(w, TRIALS_PER_WORLD)
        damp_ok, damp_total = test_correct_damped(w, TRIALS_PER_WORLD)

        stab_holds = int(stab_total > 0 and stab_ok == stab_total)
        damp_holds = int(damp_total > 0 and damp_ok == damp_total)

        stats[w] = {
            "stab_ok": stab_ok,
            "stab_total": stab_total,
            "stab_holds": stab_holds,
            "damp_ok": damp_ok,
            "damp_total": damp_total,
            "damp_holds": damp_holds,
        }

        desc = WORLD_DESCRIPTIONS[w]
        lines.append(
            f"{w:<5}| {desc:<32} | {stab_ok}/{stab_total:<18} | {damp_ok}/{damp_total}"
        )

    lines.append("")
    lines.append(
        "Heuristically, we expect: world 0 (exact spectral radius) to satisfy both "
        "CorrectStable and CorrectDamped; worlds 1, 2, and 3 to violate both, due "
        "to their coarse or overly conservative heuristics."
    )

    return lines, stats


# -----------------------------------------------------------------------------
# Higher-order look: Holds₁ / Holds₂ and model extensions
# -----------------------------------------------------------------------------

EXT1: Dict[str, Set[int]] = {}                 # unary: name ↦ {worlds}
EXT2: Dict[str, Set[Tuple[str, str]]] = {}     # binary: name ↦ set of pairs

STRONGER_REL = "rel:stronger"


def thm_int(name: str) -> str:
    """Encode a theorem name as a unary predicate-name, e.g. 'CorrectStable' → 'thm:CorrectStable'."""
    return f"thm:{name}"


def build_model_extensions(stats: Dict[int, Dict[str, int]]) -> None:
    """
    Populate EXT1 and EXT2 from the empirical stats:

      • Worlds are w ∈ {0,1,2,3}.
      • INTENSIONS:
          - thm:CorrectStable
          - thm:CorrectDamped
      • EXT1[intension] = set of worlds where the theorem holds on all samples.
      • EXT2[STRONGER_REL] = { (thm:CorrectDamped, thm:CorrectStable) }.
    """
    EXT1.clear()
    EXT2.clear()

    t_stab = thm_int("CorrectStable")
    t_damp = thm_int("CorrectDamped")

    EXT1[t_stab] = set(w for w, s in stats.items() if s.get("stab_holds", 0))
    EXT1[t_damp] = set(w for w, s in stats.items() if s.get("damp_holds", 0))

    EXT2[STRONGER_REL] = {(t_damp, t_stab)}


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

      1) Eigenvalues and spectral radius behave as expected on simple matrices.
      2) World 0 classification matches true stability on concrete examples.
      3) Worlds 1, 2, 3 misclassify at least one chosen matrix for stability.
      4) Worlds 1, 2, 3 misclassify at least one chosen matrix for damping.
      5) Statistics match the expected pattern across worlds.
      6) EXT1 / Holds₁ agree with stats, and the Holds₂ 'stronger' relation
         is respected: whenever CorrectDamped holds in a world, CorrectStable
         holds there too.
    """
    notes: List[str] = []

    # 1) Eigenvalues and spectral radius sanity
    # A rotation-like unitary with eigenvalues on the unit circle.
    A_rot = mat(0.0, 1.0, -1.0, 0.0)  # eigenvalues ±i
    lam1, lam2 = eigenvalues_2x2(A_rot)
    check(abs(abs(lam1) - 1.0) < 1e-9 and abs(abs(lam2) - 1.0) < 1e-9,
          "Rotation matrix must have eigenvalues on the unit circle.")
    check(abs(spectral_radius(A_rot) - 1.0) < 1e-9,
          "spectral_radius must be 1 for the rotation matrix.")

    # A simple unstable diagonal
    A_unst = mat(1.2, 0.0, 0.0, 0.8)
    lam1u, lam2u = eigenvalues_2x2(A_unst)
    check(abs(lam1u - 1.2) < 1e-9 or abs(lam2u - 1.2) < 1e-9,
          "Diagonal matrix must have eigenvalue 1.2.")
    check(spectral_radius(A_unst) > 1.0,
          "Diagonal matrix with entry 1.2 must be unstable.")

    notes.append("PASS 1: Eigenvalues and spectral radius behave as expected on simple examples.")

    # 2) World 0 classification vs truth (some fixed examples)
    examples = [
        ("identity", mat(1.0, 0.0, 0.0, 1.0)),
        ("damped diag", mat(0.8, 0.0, 0.0, 0.7)),
        ("unstable diag", mat(1.1, 0.0, 0.0, 0.9)),
        ("rotation", A_rot),
    ]
    for name, A in examples:
        st_true = stable_true(A)
        dp_true = damped_true(A)
        st0, dp0 = classify_world(0, A)
        check(
            st_true == st0 and dp_true == dp0,
            f"World 0 must match true stability for {name}.",
        )

    notes.append("PASS 2: World 0 matches the true stability tests on several examples.")

    # 3) Stability misclassification for worlds 1, 2, 3
    # Using the same matrices as in the deterministic part of test_correct_stable.
    A1 = mat(0.0, 2.0, 0.0, 0.0)   # stable_true, but world 1 rejects
    st_true_A1 = stable_true(A1)
    st1, _ = classify_world(1, A1)
    check(st_true_A1 != st1, "World 1 must misclassify stability for A1.")

    A2 = mat(0.0, 2.0, -2.0, 0.0)  # unstable_true, but world 2 thinks stable
    st_true_A2 = stable_true(A2)
    st2, _ = classify_world(2, A2)
    check(st_true_A2 != st2, "World 2 must misclassify stability for A2.")

    A3 = mat(1.0, 0.0, 0.0, 1.0)   # stable_true, but world 3 rejects
    st_true_A3 = stable_true(A3)
    st3, _ = classify_world(3, A3)
    check(st_true_A3 != st3, "World 3 must misclassify stability for A3.")

    notes.append("PASS 3: Worlds 1,2,3 each misclassify at least one matrix for stability.")

    # 4) Damping misclassification for worlds 1, 2, 3
    A1d = mat(0.0, 1.2, 0.0, 0.0)  # damped_true, but world 1 rejects
    dp_true_A1d = damped_true(A1d)
    _, dp1 = classify_world(1, A1d)
    check(dp_true_A1d != dp1, "World 1 must misclassify damping for A1d.")

    A2d = mat(0.0, 1.0, -1.0, 0.0)  # not damped_true, but world 2 says damped
    dp_true_A2d = damped_true(A2d)
    _, dp2 = classify_world(2, A2d)
    check(dp_true_A2d != dp2, "World 2 must misclassify damping for A2d.")

    A3d = mat(0.8, 0.0, 0.0, 0.8)   # damped_true, but world 3 rejects
    dp_true_A3d = damped_true(A3d)
    _, dp3 = classify_world(3, A3d)
    check(dp_true_A3d != dp3, "World 3 must misclassify damping for A3d.")

    notes.append("PASS 4: Worlds 1,2,3 each misclassify at least one matrix for damping.")

    # 5) Statistics pattern
    # Expected:
    #   world 0: stab_holds=1, damp_holds=1
    #   worlds 1,2,3: stab_holds=0, damp_holds=0
    for w_id in WORLD_IDS:
        s = stats[w_id]
        if w_id == 0:
            check(
                s["stab_holds"] == 1 and s["damp_holds"] == 1,
                f"World 0: expected both theorems to hold, got {s}.",
            )
        else:
            check(
                s["stab_holds"] == 0 and s["damp_holds"] == 0,
                f"World {w_id}: expected both theorems to fail, got {s}.",
            )

    notes.append("PASS 5: Statistics match the expected pattern across all worlds.")

    # 6) EXT1 / Holds₁ agreement and Holds₂ stronger relation
    t_stab = thm_int("CorrectStable")
    t_damp = thm_int("CorrectDamped")

    for w_id in WORLD_IDS:
        s = stats[w_id]
        check(
            Holds1(t_stab, w_id) == bool(s["stab_holds"]),
            f"Holds1(thm:CorrectStable, {w_id}) disagrees with stats.",
        )
        check(
            Holds1(t_damp, w_id) == bool(s["damp_holds"]),
            f"Holds1(thm:CorrectDamped, {w_id}) disagrees with stats.",
        )

    check(
        Holds2(STRONGER_REL, t_damp, t_stab),
        "Holds2(rel:stronger, thm:CorrectDamped, thm:CorrectStable) must be true.",
    )
    for w_id in WORLD_IDS:
        if Holds1(t_damp, w_id):
            check(
                Holds1(t_stab, w_id),
                f"In world {w_id}, CorrectDamped holds but CorrectStable does not.",
            )

    notes.append("PASS 6: Holds₁/EXT1 are consistent with stats and 'CorrectDamped' is stronger than 'CorrectStable'.")

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
    "We model four different stability tests for 2×2 complex system matrices:\n"
    "  world 0: exact spectral radius (eigenvalues),\n"
    "  world 1: Gershgorin-circle bound,\n"
    "  world 2: diagonal-only heuristic,\n"
    "  world 3: tiny Frobenius-norm heuristic,\n"
    "and two theorem-names:\n"
    "  CorrectStable:  world w's 'stable' predicate agrees with true stability,\n"
    "  CorrectDamped:  world w's 'damped' predicate agrees with true damping.\n"
    "Only world 0 represents the ideal engineer's check; the others are\n"
    "approximations of varying quality.\n"
)

REASON_TEXT = (
    "In the first-order core, we represent 2×2 complex matrices as tuples of\n"
    "Python complex numbers and compute eigenvalues analytically from the\n"
    "characteristic polynomial. True stability and damping are determined from\n"
    "the spectral radius: max |λ| ≤ 1 for stability, and ≤ 0.9 for damping.\n"
    "\n"
    "Each world defines its own approximate (stable, damped) classification:\n"
    "  • world 0 uses the true spectral-radius tests;\n"
    "  • world 1 uses a Gershgorin-disc bound in the complex plane;\n"
    "  • world 2 looks only at the diagonal entries;\n"
    "  • world 3 relies on a very small Frobenius-norm threshold.\n"
    "\n"
    "For each world we sample many random matrices and compare its decisions\n"
    "with the exact ones, building an extensional model:\n"
    "  • worlds: w ∈ {0,1,2,3},\n"
    "  • theorem-names: thm:CorrectStable, thm:CorrectDamped,\n"
    "  • EXT1[thm:CorrectStable] = { w | all samples satisfy stable_w(A)=stable_true(A) },\n"
    "  • EXT1[thm:CorrectDamped] = { w | all samples satisfy damped_w(A)=damped_true(A) }.\n"
    "\n"
    "We then define Holds₁(P, w) to mean w ∈ EXT1[P]. A binary relation-name\n"
    "rel:stronger is given by EXT2[rel:stronger] = { (thm:CorrectDamped,\n"
    "thm:CorrectStable) }, and Holds₂ is just membership in EXT2. In this small\n"
    "universe, whenever a world gets all damping decisions right (only world 0),\n"
    "it also gets all stability decisions right.\n"
    "\n"
    "Thus, a concrete real-world question — 'Is this 2×2 complex system stable\n"
    "or damped?' — is answered in the core by the exact eigenvalue test, while\n"
    "the higher-order structure (Holds₁/Holds₂) organises which approximate\n"
    "tests are globally reliable across the sampled systems."
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
    t_stab = thm_int("CorrectStable")
    t_damp = thm_int("CorrectDamped")
    for w in WORLD_IDS:
        print(
            f"  world {w}: Holds1({t_stab}, {w})={Holds1(t_stab, w)}, "
            f"Holds1({t_damp}, {w})={Holds1(t_damp, w)}"
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
    table_lines, stats = estimate_stability_theorems()
    build_model_extensions(stats)
    arc_answer(table_lines)
    arc_reason()
    arc_check(stats)


if __name__ == "__main__":
    main()

