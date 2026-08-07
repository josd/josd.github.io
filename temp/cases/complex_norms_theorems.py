#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
complex_norms_theorems.py
=========================

Complex numbers, norms, and two “theorems”
-----------------------------------------
This script explores how two familiar properties of the complex absolute value

  (TΔ) Triangle inequality:
      ∀z,w ∈ ℂ: |z + w| ≤ |z| + |w|

  (TM) Multiplicative modulus:
      ∀z,w ∈ ℂ: |z w| = |z|·|w|

behave if we replace the usual modulus |·| by various alternative norms on ℂ,
viewed as ℝ².

We consider four “worlds”, each with its own candidate norm ‖·‖₍w₎:

  World 0 (Euclidean norm)
    ‖x + iy‖₀ = sqrt(x² + y²)

  World 1 (ℓ¹ norm)
    ‖x + iy‖₁ = |x| + |y|

  World 2 (ℓ∞ norm)
    ‖x + iy‖∞ = max(|x|, |y|)

  World 3 (elliptic norm)
    ‖x + iy‖E = sqrt(x² + 2 y²)

Mathematically:

  • All four are genuine norms on ℂ ≅ ℝ², so the triangle inequality holds
    for each of them.
  • The multiplicative modulus property (TM) is special: for the usual
    complex absolute value it holds exactly, but for generic norms it fails.

We use random tests over small integer complex numbers to build an
*extensional* model:

  • Worlds are the integers w ∈ {0,1,2,3}.
  • Intensions (unary predicate-names):
        thm:TriangleIneq
        thm:MultiplicativeModulus
  • A single unary predicate:

        Holds₁(P, w)

    means “the theorem named by P is empirically true in world w”, i.e. all
    our random samples in that world satisfy the property.

    Implementation detail:
      EXT1: Dict[str, Set[int]]
      Holds1(P, w) ⇔ w ∈ EXT1[P].

  • A binary relation-name:

        rel:stronger

    relates the intensions

        (thm:MultiplicativeModulus, thm:TriangleIneq),

    expressing that we *intend* to treat the multiplicative-modulus property
    as “stronger” than the triangle inequality in this tiny logical picture.

    Implementation detail:
      EXT2["rel:stronger"] ⊆ { (thm:MultiplicativeModulus, thm:TriangleIneq) }
      Holds2(R, X, Y) ⇔ (X, Y) ∈ EXT2[R].

All the semantic work is done in first-order-looking Python code:

  • random generation of small complex pairs,
  • numerical checks of TΔ and TM with a tolerance for floating-point error,
  • and determination of which worlds satisfy which theorems.

Holds₁ and Holds₂ then simply *read off* the resulting extensional model:
this is the “higher-order look, first-order core” pattern.


What the script prints
----------------------
Running:

    python3 complex_norms_theorems.py

produces three ARC-style sections:

  1) Answer
     • describes the four norms and the two properties,
     • prints a table of empirical stats per world:
           world | norm          | Triangle (ok/total) | MultMod (ok/total)
     • and shows sample Holds₁ judgements.

  2) Reason why
     • explains how ℂ is represented, how norms are implemented,
     • how the two properties are tested in each world,
     • and how the Holds₁ / Holds₂ view is built from that core.

  3) Check (harness)
     • at least six independent tests checking that:
         - each norm satisfies basic norm axioms (0, homogeneity, non-negativity),
         - the Euclidean norm passes a concrete multiplicativity test,
         - the non-Euclidean norms fail multiplicativity for fixed examples,
         - the stats reflect that world 0 satisfies both theorems,
         - EXT1 / Holds₁ agree with the stats per world,
         - the Holds₂-level “stronger” relation is present and respected
           (whenever TM holds, TΔ also holds in that world).

Python 3.9+; no external packages.
"""

from __future__ import annotations

from random import randrange, seed
from typing import Dict, List, Tuple, Set

seed(0)  # deterministic randomness for reproducible runs


# -----------------------------------------------------------------------------
# Worlds and norms on ℂ
# -----------------------------------------------------------------------------

WORLD_IDS = (0, 1, 2, 3)

WORLD_DESCRIPTIONS: Dict[int, str] = {
    0: "Euclidean ‖z‖ = sqrt(x² + y²)",
    1: "ℓ¹        ‖z‖ = |x| + |y|",
    2: "ℓ∞        ‖z‖ = max(|x|, |y|)",
    3: "Elliptic  ‖z‖ = sqrt(x² + 2 y²)",
}


def complex_norm(z: complex, world: int) -> float:
    """
    Compute the norm of z in the given world.

    world 0: Euclidean norm
    world 1: ℓ¹ norm
    world 2: ℓ∞ norm
    world 3: elliptic norm sqrt(x² + 2y²)
    """
    x = z.real
    y = z.imag
    if world == 0:
        return (x * x + y * y) ** 0.5
    elif world == 1:
        return abs(x) + abs(y)
    elif world == 2:
        return max(abs(x), abs(y))
    elif world == 3:
        return (x * x + 2.0 * y * y) ** 0.5
    else:
        raise ValueError(f"Unknown world id {world!r}")


def random_complex_int(max_abs: int = 5) -> complex:
    """Random complex number with integer coordinates in [-max_abs, max_abs]."""
    a = randrange(-max_abs, max_abs + 1)
    b = randrange(-max_abs, max_abs + 1)
    return complex(a, b)


# -----------------------------------------------------------------------------
# Empirical testing of theorems in each world
# -----------------------------------------------------------------------------

TRIALS_PER_WORLD = 300
TOL = 1e-9  # numerical tolerance for equality


def test_triangle_inequality(world: int, trials: int) -> Tuple[int, int]:
    """
    Test the triangle inequality ‖z+w‖ ≤ ‖z‖ + ‖w‖ in the given world.

    Returns (ok_count, total_count).
    """
    ok = 0
    total = 0
    for _ in range(trials):
        z = random_complex_int()
        w = random_complex_int()
        lhs = complex_norm(z + w, world)
        rhs = complex_norm(z, world) + complex_norm(w, world)
        if lhs <= rhs + TOL:
            ok += 1
        total += 1
    return ok, total


def test_multiplicative_modulus(world: int, trials: int) -> Tuple[int, int]:
    """
    Test the multiplicative modulus property ‖zw‖ = ‖z‖·‖w‖ in the given world.

    Returns (ok_count, total_count).
    """
    ok = 0
    total = 0
    for _ in range(trials):
        z = random_complex_int()
        w = random_complex_int()
        lhs = complex_norm(z * w, world)
        rhs = complex_norm(z, world) * complex_norm(w, world)
        if abs(lhs - rhs) <= TOL:
            ok += 1
        total += 1
    return ok, total


def estimate_norm_theorems() -> Tuple[List[str], Dict[int, Dict[str, int]]]:
    """
    For each world, test both properties and collect statistics.

    Returns:
      (table_lines, stats)

    stats[world] = {
        "tri_ok": int,
        "tri_total": int,
        "tri_holds": 0 or 1,
        "mult_ok": int,
        "mult_total": int,
        "mult_holds": 0 or 1,
    }
    """
    lines: List[str] = []
    stats: Dict[int, Dict[str, int]] = {}

    header = "world | norm description                 | Triangle (ok/total) | MultMod (ok/total)"
    lines.append(header)
    lines.append("-" * len(header))

    for w in WORLD_IDS:
        tri_ok, tri_total = test_triangle_inequality(w, TRIALS_PER_WORLD)
        mult_ok, mult_total = test_multiplicative_modulus(w, TRIALS_PER_WORLD)

        tri_holds = int(tri_ok == tri_total)
        mult_holds = int(mult_ok == mult_total)

        stats[w] = {
            "tri_ok": tri_ok,
            "tri_total": tri_total,
            "tri_holds": tri_holds,
            "mult_ok": mult_ok,
            "mult_total": mult_total,
            "mult_holds": mult_holds,
        }

        desc = WORLD_DESCRIPTIONS[w]
        lines.append(
            f"{w:<5}| {desc:<30} | {tri_ok}/{tri_total:<18} | {mult_ok}/{mult_total}"
        )

    lines.append("")
    lines.append(
        "Heuristically, we expect: world 0 satisfies both Triangle and "
        "MultiplicativeModulus, while the other worlds satisfy Triangle but "
        "fail MultiplicativeModulus."
    )

    return lines, stats


# -----------------------------------------------------------------------------
# Higher-order look: Holds₁ / Holds₂ and model extensions
# -----------------------------------------------------------------------------

EXT1: Dict[str, Set[int]] = {}                 # unary: name ↦ {worlds}
EXT2: Dict[str, Set[Tuple[str, str]]] = {}     # binary: name ↦ set of pairs

STRONGER_REL = "rel:stronger"


def thm_int(name: str) -> str:
    """Encode a theorem name as a unary predicate-name, e.g. 'TriangleIneq' → 'thm:TriangleIneq'."""
    return f"thm:{name}"


def build_model_extensions(stats: Dict[int, Dict[str, int]]) -> None:
    """
    Populate EXT1 and EXT2 from the empirical stats:

      • Worlds are world ids w ∈ {0,1,2,3}.
      • INTENSIONS:
          - thm:TriangleIneq
          - thm:MultiplicativeModulus
      • EXT1[intension] = set of worlds where the theorem holds in all samples.
      • EXT2[STRONGER_REL] = { (thm:MultiplicativeModulus, thm:TriangleIneq) }.
    """
    EXT1.clear()
    EXT2.clear()

    t_tri = thm_int("TriangleIneq")
    t_mult = thm_int("MultiplicativeModulus")

    EXT1[t_tri] = set(w for w, s in stats.items() if s.get("tri_holds", 0))
    EXT1[t_mult] = set(w for w, s in stats.items() if s.get("mult_holds", 0))

    EXT2[STRONGER_REL] = {(t_mult, t_tri)}


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
    Run a set of independent checks:

      1) Each norm satisfies basic properties (‖0‖=0, homogeneity, non-negativity).
      2) Euclidean norm (world 0) is multiplicative on a concrete example.
      3) Non-Euclidean norms (worlds 1,2,3) fail multiplicativity on fixed examples.
      4) Stats reflect that world 0 satisfies both theorems, others fail multiplicativity.
      5) EXT1 / Holds₁ agree with stats for each world and theorem.
      6) The Holds₂-level 'stronger' relation is present and respected:
           whenever MultiplicativeModulus holds in a world, TriangleIneq holds there too.
    """
    notes: List[str] = []

    # 1) Basic norm properties
    for w in WORLD_IDS:
        # ‖0‖ = 0 and non-negativity.
        n0 = complex_norm(0 + 0j, w)
        check(abs(n0) <= TOL, f"World {w}: norm of zero must be 0.")
        for _ in range(20):
            z = random_complex_int()
            nz = complex_norm(z, w)
            check(nz >= -TOL, f"World {w}: norm must be non-negative (got {nz}).")

            # Homogeneity ‖λz‖ = |λ| ‖z‖ for integer λ
            lam = randrange(-3, 4)
            nz2 = complex_norm(lam * z, w)
            check(
                abs(nz2 - abs(lam) * nz) <= 1e-8,
                f"World {w}: homogeneity failed for λ={lam}, z={z}.",
            )

    notes.append("PASS 1: All world norms satisfy basic norm properties in sampled tests.")

    # 2) Euclidean norm multiplicative for a concrete pair
    z = 3 + 4j
    w = 1 - 2j
    lhs = complex_norm(z * w, 0)
    rhs = complex_norm(z, 0) * complex_norm(w, 0)
    check(abs(lhs - rhs) <= 1e-9, "World 0: Euclidean norm must be multiplicative on a concrete example.")
    notes.append("PASS 2: World 0 (Euclidean) shows concrete multiplicativity of the modulus.")

    # 3) Non-Euclidean norms fail multiplicativity for fixed examples
    # World 1 (ℓ¹): z = 1+i, w = 1+i
    z1 = 1 + 1j
    w1 = 1 + 1j
    lhs1 = complex_norm(z1 * w1, 1)
    rhs1 = complex_norm(z1, 1) * complex_norm(w1, 1)
    check(
        abs(lhs1 - rhs1) > 1e-6,
        "World 1 (ℓ¹) should fail multiplicativity for z=w=1+i.",
    )

    # World 2 (ℓ∞): z = 1+2i, w = 2+i
    z2 = 1 + 2j
    w2 = 2 + 1j
    lhs2 = complex_norm(z2 * w2, 2)
    rhs2 = complex_norm(z2, 2) * complex_norm(w2, 2)
    check(
        abs(lhs2 - rhs2) > 1e-6,
        "World 2 (ℓ∞) should fail multiplicativity for z=1+2i, w=2+i.",
    )

    # World 3 (elliptic): z = 1+i, w = 1+i
    z3 = 1 + 1j
    w3 = 1 + 1j
    lhs3 = complex_norm(z3 * w3, 3)
    rhs3 = complex_norm(z3, 3) * complex_norm(w3, 3)
    check(
        abs(lhs3 - rhs3) > 1e-6,
        "World 3 (elliptic) should fail multiplicativity for z=w=1+i.",
    )

    notes.append("PASS 3: Worlds 1,2,3 all fail multiplicativity on fixed examples.")

    # 4) Stats expectations: world 0 satisfies both; others fail multiplicativity
    s0 = stats[0]
    check(
        s0["tri_holds"] == 1 and s0["mult_holds"] == 1,
        f"World 0 should satisfy both TriangleIneq and MultiplicativeModulus, got {s0}.",
    )

    for w in WORLD_IDS:
        if w == 0:
            continue
        sw = stats[w]
        check(
            sw["mult_holds"] == 0,
            f"World {w} should fail MultiplicativeModulus in sampled tests, got {sw['mult_holds']}.",
        )

    notes.append("PASS 4: Stats reflect that only world 0 satisfies multiplicativity, all satisfy triangle inequality.")

    # 5) EXT1 / Holds₁ agreement with stats
    t_tri = thm_int("TriangleIneq")
    t_mult = thm_int("MultiplicativeModulus")
    for w in WORLD_IDS:
        st = stats[w]
        check(
            Holds1(t_tri, w) == bool(st["tri_holds"]),
            f"Holds1(thm:TriangleIneq, {w}) disagrees with stats.",
        )
        check(
            Holds1(t_mult, w) == bool(st["mult_holds"]),
            f"Holds1(thm:MultiplicativeModulus, {w}) disagrees with stats.",
        )
    notes.append("PASS 5: Holds₁/EXT1 match empirical stats for all worlds and theorems.")

    # 6) Holds₂-level 'stronger' relation respected
    check(
        Holds2(STRONGER_REL, t_mult, t_tri),
        "Holds2(rel:stronger, thm:MultiplicativeModulus, thm:TriangleIneq) must be true.",
    )
    for w in WORLD_IDS:
        if Holds1(t_mult, w):
            check(
                Holds1(t_tri, w),
                f"In world {w}, MultiplicativeModulus holds but TriangleIneq does not.",
            )
    notes.append("PASS 6: 'MultiplicativeModulus' is stronger than 'TriangleIneq' in all worlds where it holds.")

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
    "We compare four norms on ℂ:\n"
    "  world 0: Euclidean   ‖x+iy‖ = sqrt(x² + y²)\n"
    "  world 1: ℓ¹          ‖x+iy‖ = |x| + |y|\n"
    "  world 2: ℓ∞          ‖x+iy‖ = max(|x|, |y|)\n"
    "  world 3: Elliptic    ‖x+iy‖ = sqrt(x² + 2 y²)\n"
    "and two theorems:\n"
    "  TriangleIneq:        ‖z+w‖ ≤ ‖z‖ + ‖w‖\n"
    "  MultiplicativeModulus: ‖zw‖ = ‖z‖‖w‖.\n"
    "The usual complex absolute value is world 0; it is the only one that is\n"
    "both a norm and multiplicative in the sense of MultiplicativeModulus."
)

REASON_TEXT = (
    "We represent complex numbers as Python's built-in complex type and work\n"
    "over small integer lattice points in ℂ for testing. Each world chooses a\n"
    "different norm on ℂ ≅ ℝ²; the triangle inequality and multiplicativity\n"
    "are then tested numerically on many random pairs (z,w).\n"
    "\n"
    "The first-order core consists of:\n"
    "  • the concrete norm functions ‖·‖₍w₎,\n"
    "  • random generation of sample pairs (z,w),\n"
    "  • boolean tests for TriangleIneq and MultiplicativeModulus.\n"
    "\n"
    "From this we build an extensional model:\n"
    "  • worlds are the integers 0..3 (the four norms),\n"
    "  • theorem-names thm:TriangleIneq and thm:MultiplicativeModulus,\n"
    "  • EXT1[thm:TriangleIneq] = {w | all samples in world w satisfy triangle inequality},\n"
    "  • EXT1[thm:MultiplicativeModulus] = {w | all samples in world w satisfy multiplicativity},\n"
    "and define:\n"
    "  Holds1(P, w) ⇔ w ∈ EXT1[P].\n"
    "\n"
    "A binary relation-name rel:stronger connects the intensions\n"
    "  (thm:MultiplicativeModulus, thm:TriangleIneq)\n"
    "via EXT2[rel:stronger], and\n"
    "  Holds2(rel:stronger, X, Y) ⇔ (X, Y) ∈ EXT2[rel:stronger].\n"
    "\n"
    "Thus the normative statements ('TriangleIneq holds in world 2',\n"
    "'MultiplicativeModulus is stronger than TriangleIneq') are captured by\n"
    "Holds₁ / Holds₂ over a finite set of intensions, while all semantic work\n"
    "is done in a simple first-order numerical core."
)


def arc_answer(table_lines: List[str]) -> None:
    print("Answer")
    print("------")
    print(ANSWER_TEXT)
    print()
    print("Empirical results (random tests over small complex integers):")
    print()
    for line in table_lines:
        print(line)
    print()
    print("Holds₁ view on theorem-names:")
    t_tri = thm_int("TriangleIneq")
    t_mult = thm_int("MultiplicativeModulus")
    for w in WORLD_IDS:
        print(
            f"  world {w}: Holds1({t_tri}, {w})={Holds1(t_tri, w)}, "
            f"Holds1({t_mult}, {w})={Holds1(t_mult, {w})}"
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
    table_lines, stats = estimate_norm_theorems()
    build_model_extensions(stats)
    arc_answer(table_lines)
    arc_reason()
    arc_check(stats)


if __name__ == "__main__":
    main()

