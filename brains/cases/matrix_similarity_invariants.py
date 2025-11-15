#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
matrix_similarity_invariants.py
===============================

Similarity and 'determinant-like' invariants on 2×2 matrices
------------------------------------------------------------
This script is a small, self-contained Python program that compares four
different scalar-valued functions f(A) on 2×2 real matrices:

  f₀(A):   det(A)          = a11 a22 - a12 a21
  f₁(A):   permanent(A)    = a11 a22 + a12 a21
  f₂(A):   diag_prod(A)    = a11 a22
  f₃(A):   trace(A)        = a11 + a22

We treat each choice of fᵢ as a different “world” and empirically test two
“theorems” about f(A) in that world:

  (MultThm)       multiplicativity:
                      f(AB) = f(A) f(B)

  (SimInvThm)     similarity invariance:
                      f(SAS⁻¹) = f(A) for all invertible S


Worlds
------
Worlds are indexed by integers w ∈ {0, 1, 2, 3}:

  • world 0: f₀ = determinant
  • world 1: f₁ = permanent (2×2)
  • world 2: f₂ = product of diagonal entries
  • world 3: f₃ = trace

Mathematically (for 2×2 matrices over a field):

  • det is multiplicative and similarity-invariant.
  • permanent (even in 2×2) is not multiplicative and not similarity-invariant.
  • the diagonal product a11 a22 is not multiplicative and not similarity-invariant.
  • trace is similarity-invariant but not multiplicative.

We illustrate this numerically by random sampling over small integer matrices.


Higher-order look, first-order core
-----------------------------------
We follow the “higher-order look, first-order core” pattern
(https://josd.github.io/higher-order-look-first-order-core/):

  • First-order core:
      - 2×2 matrices with real entries (implemented as Python floats),
      - standard matrix multiplication and matrix inverse (2×2 explicit),
      - four scalar functions f₀,…,f₃,
      - random sampling over small integer matrices to test:
            MultThm:    f(AB) = f(A) f(B),
            SimInvThm:  f(SAS⁻¹) = f(A) (for random invertible S).

  • Higher-order look:
      - worlds W = {0,1,2,3},
      - theorem-names (intensions):
            thm:MultThm
            thm:SimInvThm
      - a unary predicate

            Holds₁(P, w)

        meaning: “the theorem named by P holds in world w”, i.e. all sampled
        configurations in world w satisfy that equation. This is implemented
        extensionally:

            EXT1: Dict[str, Set[int]]
            Holds1(P, w)  ⇔  w ∈ EXT1[P].

      - a binary relation-name

            rel:stronger

        relating intensions by:

            Holds₂("rel:stronger", thm:MultThm, thm:SimInvThm)

        expressing that, in this tiny universe, multiplicativity implies
        similarity invariance: every world where MultThm holds also satisfies
        SimInvThm. Formally:

            EXT2["rel:stronger"] = { (thm:MultThm, thm:SimInvThm) }
            Holds2(R, X, Y)  ⇔  (X, Y) ∈ EXT2[R].

All semantics (matrix arithmetic, sampling, scalar functions) live in the
first-order core. Holds₁ / Holds₂ just read off the resulting extensional
model (EXT1, EXT2).


What the script prints
----------------------
Running:

    python3 matrix_similarity_invariants.py

prints three ARC-style sections:

  1) Answer
     • describes the four worlds and two theorems,
     • shows a table of empirical stats per world:
           world | f description           | Mult (ok/total) | SimInv (ok/total)
     • and prints Holds₁ judgements for each world and theorem-name.

  2) Reason why
     • explains the four scalar functions and their algebraic behaviour
       under multiplication and similarity,
     • and explains how the Holds₁ / Holds₂ viewpoint is constructed.

  3) Check (harness)
     • at least six independent tests, including:
         - concrete checks of multiplicativity and similarity invariance
           for det and trace,
         - concrete counterexamples for permanent and diag_prod,
         - sanity checks on the stats pattern,
         - consistency of EXT1 and Holds₁,
         - and that the Holds₂ “stronger” relation is respected in all worlds.

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


def mat_add(A: Matrix, B: Matrix) -> Matrix:
    return (
        (A[0][0] + B[0][0], A[0][1] + B[0][1]),
        (A[1][0] + B[1][0], A[1][1] + B[1][1]),
    )


def mat_mul(A: Matrix, B: Matrix) -> Matrix:
    """Standard matrix product A·B."""
    a11, a12 = A[0]
    a21, a22 = A[1]
    b11, b12 = B[0]
    b21, b22 = B[1]
    return (
        (a11 * b11 + a12 * b21, a11 * b12 + a12 * b22),
        (a21 * b11 + a22 * b21, a21 * b12 + a22 * b22),
    )


def mat_det(A: Matrix) -> float:
    a11, a12 = A[0]
    a21, a22 = A[1]
    return a11 * a22 - a12 * a21


def mat_inv(A: Matrix) -> Matrix:
    """Inverse of a 2×2 matrix, assuming det ≠ 0."""
    a11, a12 = A[0]
    a21, a22 = A[1]
    d = mat_det(A)
    if abs(d) < 1e-12:
        raise ValueError("Singular matrix, cannot invert.")
    inv_d = 1.0 / d
    return (
        ( a22 * inv_d, -a12 * inv_d),
        (-a21 * inv_d,  a11 * inv_d),
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


def random_invertible_matrix_int(max_abs: int = 3) -> Matrix:
    """
    Random integer matrix with det ≠ 0.
    Keeps trying until it finds an invertible one.
    """
    while True:
        A = random_matrix_int(max_abs)
        if abs(mat_det(A)) > 0.5:  # avoid tiny determinants
            return A


# -----------------------------------------------------------------------------
# Worlds and scalar functions f₍world₎(A)
# -----------------------------------------------------------------------------

WORLD_IDS = (0, 1, 2, 3)

WORLD_DESCRIPTIONS: Dict[int, str] = {
    0: "det(A)",
    1: "permanent(A) = a11 a22 + a12 a21",
    2: "diag_prod(A) = a11 a22",
    3: "trace(A) = a11 + a22",
}


def scalar_det(A: Matrix) -> float:
    return mat_det(A)


def scalar_perm(A: Matrix) -> float:
    """2×2 permanent: a11 a22 + a12 a21."""
    a11, a12 = A[0]
    a21, a22 = A[1]
    return a11 * a22 + a12 * a21


def scalar_diag_prod(A: Matrix) -> float:
    a11, _ = A[0]
    _, a22 = A[1]
    return a11 * a22


def scalar_trace(A: Matrix) -> float:
    a11, _ = A[0]
    _, a22 = A[1]
    return a11 + a22


def scalar_world(A: Matrix, world: int) -> float:
    """
    World-specific scalar function f₍world₎(A):

      world 0: determinant
      world 1: permanent
      world 2: product of diagonal entries
      world 3: trace
    """
    if world == 0:
        return scalar_det(A)
    if world == 1:
        return scalar_perm(A)
    if world == 2:
        return scalar_diag_prod(A)
    if world == 3:
        return scalar_trace(A)
    raise ValueError(f"Unknown world id {world!r}")


# -----------------------------------------------------------------------------
# Empirical tests: multiplicativity and similarity invariance
# -----------------------------------------------------------------------------

TRIALS_PER_WORLD = 200
TOL = 1e-9


def test_multiplicativity(world: int, trials: int) -> Tuple[int, int]:
    """
    Empirically test multiplicativity:

        f(AB) = f(A) f(B)

    for the scalar function f₍world₎(·).

    Returns (ok_count, total_count).
    """
    ok = 0
    total = 0

    # For worlds 1,2,3 include a known failing example deterministically.
    if world == 1:
        # Permanent: choose simple matrices where per(AB) ≠ per(A)per(B).
        A = mat(1, 1, 0, 1)
        B = mat(1, 0, 1, 1)
        lhs = scalar_world(mat_mul(A, B), world)
        rhs = scalar_world(A, world) * scalar_world(B, world)
        if abs(lhs - rhs) <= TOL:
            ok += 1
        total += 1
    elif world == 2:
        # Diagonal product: generic counterexample.
        A = mat(1, 1, 0, 1)
        B = mat(1, 0, 1, 1)
        lhs = scalar_world(mat_mul(A, B), world)
        rhs = scalar_world(A, world) * scalar_world(B, world)
        if abs(lhs - rhs) <= TOL:
            ok += 1
        total += 1
    elif world == 3:
        # Trace: trace(AB) != trace(A)trace(B) in general.
        A = mat(1, 2, 0, 1)
        B = mat(0, 1, 1, 0)
        lhs = scalar_world(mat_mul(A, B), world)
        rhs = scalar_world(A, world) * scalar_world(B, world)
        if abs(lhs - rhs) <= TOL:
            ok += 1
        total += 1

    for _ in range(trials):
        A = random_matrix_int()
        B = random_matrix_int()
        lhs = scalar_world(mat_mul(A, B), world)
        rhs = scalar_world(A, world) * scalar_world(B, world)
        if abs(lhs - rhs) <= TOL:
            ok += 1
        total += 1

    return ok, total


def test_similarity_invariance(world: int, trials: int) -> Tuple[int, int]:
    """
    Empirically test similarity invariance:

        f(SAS⁻¹) = f(A)

    for random invertible matrices S.

    Returns (ok_count, total_count).
    """
    ok = 0
    total = 0

    # For worlds 1 and 2, include known failing examples deterministically.
    if world == 1:
        # Permanent is not similarity-invariant in general.
        A = mat(1, 2, 3, 4)
        S = random_invertible_matrix_int()
        Sinv = mat_inv(S)
        B = mat_mul(mat_mul(S, A), Sinv)
        lhs = scalar_world(B, world)
        rhs = scalar_world(A, world)
        if abs(lhs - rhs) <= TOL:
            ok += 1
        total += 1
    elif world == 2:
        # Diagonal product not similarity-invariant.
        A = mat(1, 2, 3, 4)
        S = random_invertible_matrix_int()
        Sinv = mat_inv(S)
        B = mat_mul(mat_mul(S, A), Sinv)
        lhs = scalar_world(B, world)
        rhs = scalar_world(A, world)
        if abs(lhs - rhs) <= TOL:
            ok += 1
        total += 1

    for _ in range(trials):
        A = random_matrix_int()
        S = random_invertible_matrix_int()
        Sinv = mat_inv(S)
        B = mat_mul(mat_mul(S, A), Sinv)
        lhs = scalar_world(B, world)
        rhs = scalar_world(A, world)
        if abs(lhs - rhs) <= TOL:
            ok += 1
        total += 1

    return ok, total


def estimate_scalar_theorems() -> Tuple[List[str], Dict[int, Dict[str, int]]]:
    """
    For each world, test multiplicativity and similarity invariance and
    collect statistics.

    Returns:
      (table_lines, stats)

      stats[world] = {
        "mult_ok": int,
        "mult_total": int,
        "mult_holds": 0 or 1,
        "sim_ok": int,
        "sim_total": int,
        "sim_holds": 0 or 1,
      }
    """
    lines: List[str] = []
    stats: Dict[int, Dict[str, int]] = {}

    header = "world | f description                    | Mult (ok/total) | SimInv (ok/total)"
    lines.append(header)
    lines.append("-" * len(header))

    for w in WORLD_IDS:
        mult_ok, mult_total = test_multiplicativity(w, TRIALS_PER_WORLD)
        sim_ok, sim_total = test_similarity_invariance(w, TRIALS_PER_WORLD)

        mult_holds = int(mult_total > 0 and mult_ok == mult_total)
        sim_holds = int(sim_total > 0 and sim_ok == sim_total)

        stats[w] = {
            "mult_ok": mult_ok,
            "mult_total": mult_total,
            "mult_holds": mult_holds,
            "sim_ok": sim_ok,
            "sim_total": sim_total,
            "sim_holds": sim_holds,
        }

        desc = WORLD_DESCRIPTIONS[w]
        lines.append(
            f"{w:<5}| {desc:<30} | {mult_ok}/{mult_total:<15} | {sim_ok}/{sim_total}"
        )

    lines.append("")
    lines.append(
        "Heuristically, we expect: world 0 (det) to satisfy both multiplicativity "
        "and similarity invariance; world 3 (trace) to satisfy only similarity "
        "invariance; and worlds 1 (permanent) and 2 (diag_prod) to satisfy neither."
    )

    return lines, stats


# -----------------------------------------------------------------------------
# Higher-order look: Holds₁ / Holds₂ and model extensions
# -----------------------------------------------------------------------------

EXT1: Dict[str, Set[int]] = {}                 # unary: name ↦ {worlds}
EXT2: Dict[str, Set[Tuple[str, str]]] = {}     # binary: name ↦ set of pairs

STRONGER_REL = "rel:stronger"


def thm_int(name: str) -> str:
    """Encode a theorem name as a unary predicate-name, e.g. 'MultThm' → 'thm:MultThm'."""
    return f"thm:{name}"


def build_model_extensions(stats: Dict[int, Dict[str, int]]) -> None:
    """
    Populate EXT1 and EXT2 from the empirical stats:

      • Worlds are w ∈ {0,1,2,3}.
      • INTENSIONS:
          - thm:MultThm
          - thm:SimInvThm
      • EXT1[intension] = set of worlds where the theorem holds in all samples.
      • EXT2[STRONGER_REL] = { (thm:MultThm, thm:SimInvThm) }.
    """
    EXT1.clear()
    EXT2.clear()

    t_mult = thm_int("MultThm")
    t_sim = thm_int("SimInvThm")

    EXT1[t_mult] = set(w for w, s in stats.items() if s.get("mult_holds", 0))
    EXT1[t_sim] = set(w for w, s in stats.items() if s.get("sim_holds", 0))

    EXT2[STRONGER_REL] = {(t_mult, t_sim)}


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

      1) Determinant satisfies multiplicativity and similarity invariance
         on fixed examples (world 0).
      2) Trace is similarity-invariant but not multiplicative on fixed examples (world 3).
      3) Permanent and diag_prod fail both properties on fixed examples (worlds 1 and 2).
      4) Statistics match the expected pattern across the four worlds.
      5) EXT1 / Holds₁ agree with the statistics.
      6) Holds₂ 'stronger' relation is present and respected:
           whenever MultThm holds in a world, SimInvThm also holds there.
    """
    notes: List[str] = []

    # 1) Determinant: multiplicativity and similarity invariance (concrete tests)
    A = mat(1, 2, 3, 4)
    B = mat(0, 1, -1, 2)
    S = mat(2, 1, 1, 1)

    # Multiplicativity det(AB) = det(A) det(B)
    detA = scalar_det(A)
    detB = scalar_det(B)
    detAB = scalar_det(mat_mul(A, B))
    check(
        abs(detAB - detA * detB) <= 1e-9,
        "Determinant must be multiplicative on a concrete pair.",
    )

    # Similarity invariance det(SAS⁻¹) = det(A)
    Sinv = mat_inv(S)
    SASinv = mat_mul(mat_mul(S, A), Sinv)
    check(
        abs(scalar_det(SASinv) - detA) <= 1e-9,
        "Determinant must be similarity-invariant on a concrete example.",
    )

    notes.append("PASS 1: Determinant is multiplicative and similarity-invariant on fixed examples (world 0).")

    # 2) Trace: similarity-invariant but not multiplicative (concrete tests)
    T = mat(1, 2, 0, 1)
    U = mat(0, 1, 1, 0)
    traceT = scalar_trace(T)
    traceU = scalar_trace(U)
    traceTU = scalar_trace(mat_mul(T, U))

    check(
        abs(traceTU - traceT * traceU) > 1e-6,
        "Trace should NOT be multiplicative on a generic pair.",
    )

    # Similarity invariance: trace(SAS⁻¹) = trace(A)
    A_tr = mat(3, 5, -1, 2)
    S_tr = random_invertible_matrix_int()
    Str_inv = mat_inv(S_tr)
    B_tr = mat_mul(mat_mul(S_tr, A_tr), Str_inv)
    check(
        abs(scalar_trace(B_tr) - scalar_trace(A_tr)) <= 1e-9,
        "Trace must be similarity-invariant on a concrete example.",
    )

    notes.append("PASS 2: Trace is similarity-invariant but not multiplicative on fixed examples (world 3).")

    # 3) Permanent and diag_prod fail both properties on fixed examples
    A_p = mat(1, 1, 0, 1)
    B_p = mat(1, 0, 1, 1)

    # Permanent multiplicativity fails
    perA = scalar_perm(A_p)
    perB = scalar_perm(B_p)
    perAB = scalar_perm(mat_mul(A_p, B_p))
    check(
        abs(perAB - perA * perB) > 1e-6,
        "Permanent should fail multiplicativity for a chosen pair.",
    )

    # Permanent similarity invariance fails (with some random S)
    S_p = random_invertible_matrix_int()
    S_p_inv = mat_inv(S_p)
    B_sim = mat_mul(mat_mul(S_p, A_p), S_p_inv)
    check(
        abs(scalar_perm(B_sim) - scalar_perm(A_p)) > 1e-6,
        "Permanent should fail similarity invariance for a chosen S,A.",
    )

    # Diagonal product multiplicativity fails
    dpA = scalar_diag_prod(A_p)
    dpB = scalar_diag_prod(B_p)
    dpAB = scalar_diag_prod(mat_mul(A_p, B_p))
    check(
        abs(dpAB - dpA * dpB) > 1e-6,
        "diag_prod should fail multiplicativity for a chosen pair.",
    )

    # Diagonal product similarity invariance fails
    S_d = random_invertible_matrix_int()
    S_d_inv = mat_inv(S_d)
    B_d = mat_mul(mat_mul(S_d, A_p), S_d_inv)
    check(
        abs(scalar_diag_prod(B_d) - scalar_diag_prod(A_p)) > 1e-6,
        "diag_prod should fail similarity invariance for a chosen S,A.",
    )

    notes.append("PASS 3: Permanent and diag_prod fail both multiplicativity and similarity invariance on fixed examples.")

    # 4) Stats expectations:
    #   world 0 (det): mult_holds=1, sim_holds=1
    #   world 1 (perm): mult_holds=0, sim_holds=0
    #   world 2 (diag_prod): mult_holds=0, sim_holds=0
    #   world 3 (trace): mult_holds=0, sim_holds=1
    for w_id in WORLD_IDS:
        s = stats[w_id]
        if w_id == 0:
            check(
                s["mult_holds"] == 1 and s["sim_holds"] == 1,
                f"World 0: expected both theorems to hold, got {s}.",
            )
        elif w_id in (1, 2):
            check(
                s["mult_holds"] == 0 and s["sim_holds"] == 0,
                f"World {w_id}: expected neither theorem to hold, got {s}.",
            )
        else:  # world 3
            check(
                s["mult_holds"] == 0 and s["sim_holds"] == 1,
                f"World 3: expected only SimInvThm to hold, got {s}.",
            )

    notes.append("PASS 4: Statistics match the expected pattern for all four worlds.")

    # 5) EXT1 / Holds₁ agreement with stats
    t_mult = thm_int("MultThm")
    t_sim = thm_int("SimInvThm")

    for w_id in WORLD_IDS:
        s = stats[w_id]
        check(
            Holds1(t_mult, w_id) == bool(s["mult_holds"]),
            f"Holds1(thm:MultThm, {w_id}) disagrees with stats.",
        )
        check(
            Holds1(t_sim, w_id) == bool(s["sim_holds"]),
            f"Holds1(thm:SimInvThm, {w_id}) disagrees with stats.",
        )

    notes.append("PASS 5: Holds₁/EXT1 match the empirical statistics for all worlds and theorems.")

    # 6) Holds₂ 'stronger' relation:
    # Whenever MultThm holds in a world, SimInvThm must also hold there.
    check(
        Holds2(STRONGER_REL, t_mult, t_sim),
        "Holds2(rel:stronger, thm:MultThm, thm:SimInvThm) must be true.",
    )
    for w_id in WORLD_IDS:
        if Holds1(t_mult, w_id):
            check(
                Holds1(t_sim, w_id),
                f"In world {w_id}, MultThm holds but SimInvThm does not.",
            )

    notes.append("PASS 6: 'MultThm' is stronger than 'SimInvThm' in all worlds where it holds.")

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
    "We compare four scalar-valued functions on 2×2 matrices:\n"
    "  world 0: det(A),\n"
    "  world 1: permanent(A) = a11 a22 + a12 a21,\n"
    "  world 2: diag_prod(A) = a11 a22,\n"
    "  world 3: trace(A) = a11 + a22,\n"
    "and two theorem-names:\n"
    "  MultThm:   f(AB) = f(A) f(B),\n"
    "  SimInvThm: f(SAS⁻¹) = f(A) for invertible S.\n"
    "Only the determinant (world 0) satisfies both; the trace (world 3) is\n"
    "similarity-invariant but not multiplicative; and the other two fail both."
)

REASON_TEXT = (
    "The first-order core of this script is standard 2×2 matrix arithmetic:\n"
    "  • matrices are tuples of floats,\n"
    "  • we use the usual matrix product and an explicit inverse formula,\n"
    "  • scalar functions are simple formulas in the entries.\n"
    "\n"
    "For each world we test the equations\n"
    "  MultThm:   f(AB) = f(A) f(B),\n"
    "  SimInvThm: f(SAS⁻¹) = f(A),\n"
    "on many random samples over small integer matrices (and random invertible\n"
    "S). From the results we form an extensional model:\n"
    "  • worlds: w ∈ {0,1,2,3},\n"
    "  • theorem-names: thm:MultThm, thm:SimInvThm,\n"
    "  • EXT1[thm:MultThm] = { w | all sampled pairs satisfy multiplicativity },\n"
    "  • EXT1[thm:SimInvThm] = { w | all sampled pairs satisfy similarity invariance }.\n"
    "\n"
    "We then define Holds₁(P,w) ↔ w ∈ EXT1[P], and introduce a binary relation\n"
    "rel:stronger with EXT2[rel:stronger] = { (thm:MultThm, thm:SimInvThm) }.\n"
    "Thus Holds₂(rel:stronger, X, Y) simply reports membership in EXT2; in this\n"
    "tiny universe, every world where MultThm holds (only world 0) is also one\n"
    "where SimInvThm holds.\n"
    "\n"
    "This fits the 'higher-order look, first-order core' pattern: talk about\n"
    "theorems and their relationships is handled extensionally by Holds₁ and\n    Holds₂, while all mathematical content stays in a simple matrix engine."
)


def arc_answer(table_lines: List[str]) -> None:
    print("Answer")
    print("------")
    print(ANSWER_TEXT)
    print()
    print("Empirical results (random tests over small integer matrices):")
    print()
    for line in table_lines:
        print(line)
    print()
    print("Holds₁ view on theorem-names:")
    t_mult = thm_int("MultThm")
    t_sim = thm_int("SimInvThm")
    for w in WORLD_IDS:
        print(
            f"  world {w}: Holds1({t_mult}, {w})={Holds1(t_mult, w)}, "
            f"Holds1({t_sim}, {w})={Holds1(t_sim, w)}"
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
    table_lines, stats = estimate_scalar_theorems()
    build_model_extensions(stats)
    arc_answer(table_lines)
    arc_reason()
    arc_check(stats)


if __name__ == "__main__":
    main()

