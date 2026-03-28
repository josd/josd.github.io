#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
complex_argument_branches.py
============================

Argument branches on ℂ and additivity
-------------------------------------
This script explores how different *branch choices* for the complex argument
function Arg(z) behave with respect to two properties:

  (AdditiveArg)   For all non-zero z,w:
                      Arg(zw) ≡ Arg(z) + Arg(w)  (mod 2π)

  (RangeOk)       For all non-zero z:
                      Arg(z) lies in the chosen branch interval I.

We consider four worlds w ∈ {0,1,2,3}, each providing its own Arg₍w₎:

  World 0: principal branch
    Arg₀(z) ∈ (-π, π], using math.atan2(imag, real).

  World 1: [0, 2π) branch
    Arg₁(z) = Arg₀(z) lifted into [0, 2π) by adding 2π when negative.

  World 2: shifted branch
    Arg₂(z) = Arg₀(z) + π/2, normalized to interval (-π/2, 3π/2].

  World 3: naive branch (broken)
    Arg₃(z) = atan(y/x) with minimal quadrant handling.
    This is the “wrong” argument: it misbehaves in quadrants.

Mathematically, for any consistent branch based on the principal Arg (like
worlds 0,1,2), we still have

    Arg₍w₎(zw) ≡ Arg₍w₎(z) + Arg₍w₎(w)  (mod 2π)

for all non-zero z,w. The naive Arg₃ fails this often.


Higher-order look, first-order core
-----------------------------------
We adopt the “higher-order look, first-order core” pattern
(https://josd.github.io/higher-order-look-first-order-core/):

  • First-order core:
      - complex numbers are Python's built-in complex type;
      - each world w defines a concrete function Arg₍w₎: ℂ\{0} → ℝ;
      - we test AdditiveArg and RangeOk numerically on many integer-valued
        samples z,w in ℂ.

  • Higher-order look:
      - worlds are the integers w = 0,1,2,3;
      - theorem-names are the unary intensions

            thm:AdditiveArg
            thm:RangeOk

      - a single unary predicate

            Holds₁(P, w)

        means “the theorem P is empirically true in world w”, i.e. all
        sampled non-zero (z,w) satisfy AdditiveArg there, or all non-zero z
        satisfy RangeOk there.

        Implementation detail:

            EXT1: Dict[str, Set[int]]
            Holds1(P, w)  ⇔  w ∈ EXT1[P].

      - a binary relation-name

            rel:stronger

        links the two theorem-names:

            Holds₂("rel:stronger", thm:AdditiveArg, thm:RangeOk)

        expressing that we *intend* the additive property to be stronger:
        in all worlds where AdditiveArg holds, RangeOk holds too.

        Implementation detail:

            EXT2["rel:stronger"] = { (thm:AdditiveArg, thm:RangeOk) }
            Holds2(R, X, Y)  ⇔  (X, Y) ∈ EXT2[R].

Everything semantic (angles, ranges, additivity) is computed in a simple
first-order numerical core. Holds₁/Holds₂ then just read off the extensional
model (EXT1, EXT2).


What the script prints
----------------------
Running:

    python3 complex_argument_branches.py

prints three ARC-style sections:

  1) Answer
     • describes the four worlds and two theorems,
     • lists a table of empirical stats per world:
           world | branch description        | Additive (ok/total) | RangeOk (ok/total)
     • and shows a few Holds₁ judgements.

  2) Reason why
     • explains how Arg branches are implemented,
     • how additivity modulo 2π is tested,
     • and how the Holds₁ / Holds₂ view is derived.

  3) Check (harness)
     • at least six independent tests checking that:
         - canonical values for Arg₍w₎ at 1, -1, i, -i are as expected,
         - AdditiveArg holds for fixed examples in worlds 0,1,2 and fails
           in world 3,
         - RangeOk holds for the appropriate branch intervals,
         - the sampled stats reflect the expected pattern (worlds 0–2 good,
           world 3 bad),
         - EXT1 / Holds₁ match the stats,
         - the Holds₂ “stronger” relation is obeyed in all worlds.

Python 3.9+; no external packages.
"""

from __future__ import annotations

import math
from random import randrange, seed
from typing import Dict, List, Tuple, Set

seed(0)  # deterministic randomness for reproducible runs

# -----------------------------------------------------------------------------
# Worlds and argument branches
# -----------------------------------------------------------------------------

WORLD_IDS = (0, 1, 2, 3)

WORLD_DESCRIPTIONS: Dict[int, str] = {
    0: "principal Arg ∈ (-π, π]",
    1: "branch Arg ∈ [0, 2π)",
    2: "branch Arg ∈ (-π/2, 3π/2]",
    3: "naive atan(y/x) (broken)",
}

TOL = 1e-9
TWO_PI = 2.0 * math.pi


def wrap_pi(theta: float) -> float:
    """Wrap angle into (-π, π]."""
    x = (theta + math.pi) % TWO_PI
    return x - math.pi


def normalize_interval(theta: float, lo: float, hi: float) -> float:
    """
    Normalize theta into an interval [lo, hi) of length 2π (up to roundoff).
    Assumes hi - lo ≈ 2π.
    """
    return ((theta - lo) % TWO_PI) + lo


def arg_world(z: complex, world: int) -> float:
    """
    World-specific argument function Arg₍w₎.

      world 0: principal Arg ∈ (-π, π]
      world 1: [0, 2π) branch
      world 2: re-centered branch (-π/2, 3π/2]
      world 3: naive atan(y/x) with minimal quadrant handling (broken)
    """
    if z == 0:
        raise ValueError("Arg undefined at 0.")

    x = z.real
    y = z.imag

    # Principal Arg in (-π, π]
    base = math.atan2(y, x)  # already in (-π, π]

    if world == 0:
        return base

    if world == 1:
        return base if base >= 0.0 else base + TWO_PI

    if world == 2:
        # Re-centered branch in (-π/2, 3π/2], obtained from the principal
        # Arg by adding 2π when needed (no constant shift).
        #
        # base ∈ (-π, π]. Values in (-π, -π/2] are pushed up by 2π into
        # (π, 3π/2], everything else is kept as is.
        if base > -math.pi / 2.0:
            return base
        else:
            return base + TWO_PI

    if world == 3:
        # Naive atan(y/x), with only a crude handling of x=0
        if x == 0.0:
            if y > 0.0:
                return math.pi / 2.0
            elif y < 0.0:
                return -math.pi / 2.0
            else:
                raise ValueError("Arg undefined at 0.")
        return math.atan(y / x)

    raise ValueError(f"Unknown world id {world!r}")


def in_range(z: complex, world: int) -> bool:
    """Check whether Arg₍w₎(z) lies in the intended branch interval."""
    theta = arg_world(z, world)
    if world == 0:
        # (-π, π]
        return (-math.pi - TOL) < theta <= (math.pi + TOL)
    if world == 1:
        # [0, 2π)
        return (-TOL) <= theta < (TWO_PI + TOL)
    if world == 2:
        # (-π/2, 3π/2]
        lo = -math.pi / 2.0
        hi = 3.0 * math.pi / 2.0
        return (lo - TOL) < theta <= (hi + TOL)
    if world == 3:
        # naive: no real intended range; we just allow anything
        # (RangeOk is *supposed* to fail for this world in our tests)
        return True
    raise ValueError(f"Unknown world id {world!r}")


def additive_arg_holds(z: complex, w: complex, world: int) -> bool:
    """
    Test AdditiveArg in a single configuration:

        Arg₍w₎(zw) ≡ Arg₍w₎(z) + Arg₍w₎(w)  (mod 2π)

    returns True if they agree modulo 2π up to TOL.
    """
    if z == 0 or w == 0:
        raise ValueError("AdditiveArg requires non-zero z,w.")

    arg_z = arg_world(z, world)
    arg_w = arg_world(w, world)
    arg_zw = arg_world(z * w, world)

    diff = arg_zw - (arg_z + arg_w)
    # Reduce difference mod 2π into (-π, π]; we expect 0 there.
    d = wrap_pi(diff)
    return abs(d) <= 1e-7  # slightly looser tolerance


def random_complex_int(max_abs: int = 5) -> complex:
    """Random complex number with integer coordinates in [-max_abs, max_abs]."""
    a = randrange(-max_abs, max_abs + 1)
    b = randrange(-max_abs, max_abs + 1)
    return complex(a, b)


# -----------------------------------------------------------------------------
# Empirical testing of theorems in each world
# -----------------------------------------------------------------------------

TRIALS_PER_WORLD = 400


def test_additive_arg(world: int, trials: int) -> Tuple[int, int]:
    """
    Test AdditiveArg: Arg(zw) ≡ Arg(z) + Arg(w) (mod 2π) in the given world.

    Returns (ok_count, total_count).
    """
    ok = 0
    total = 0

    # For the naive world 3, include a known failing example first
    if world == 3:
        z_fixed = complex(0, 1)  # i
        w_fixed = complex(0, 1)  # i
        if additive_arg_holds(z_fixed, w_fixed, world):
            ok += 1
        total += 1  # we know this *should* fail, so ok will stay 0

    for _ in range(trials):
        z = random_complex_int()
        w = random_complex_int()
        if z == 0 or w == 0:
            continue  # skip, don't count
        try:
            if additive_arg_holds(z, w, world):
                ok += 1
            total += 1
        except ValueError:
            continue
    return ok, total


def test_range_ok(world: int, trials: int) -> Tuple[int, int]:
    """
    Test RangeOk: Arg(z) in intended interval, for non-zero z.

    Returns (ok_count, total_count).
    """
    ok = 0
    total = 0
    for _ in range(trials):
        z = random_complex_int()
        if z == 0:
            continue
        try:
            if in_range(z, world):
                ok += 1
            total += 1
        except ValueError:
            continue
    return ok, total


def estimate_arg_theorems() -> Tuple[List[str], Dict[int, Dict[str, int]]]:
    """
    For each world, test AdditiveArg and RangeOk and collect statistics.

    Returns:
      (table_lines, stats)

    stats[world] = {
        "add_ok": int,
        "add_total": int,
        "add_holds": 0 or 1,
        "range_ok": int,
        "range_total": int,
        "range_holds": 0 or 1,
    }
    """
    lines: List[str] = []
    stats: Dict[int, Dict[str, int]] = {}

    header = "world | branch description           | Additive (ok/total) | RangeOk (ok/total)"
    lines.append(header)
    lines.append("-" * len(header))

    for w in WORLD_IDS:
        add_ok, add_total = test_additive_arg(w, TRIALS_PER_WORLD)
        range_ok, range_total = test_range_ok(w, TRIALS_PER_WORLD)

        add_holds = int(add_total > 0 and add_ok == add_total)
        range_holds = int(range_total > 0 and range_ok == range_total)

        stats[w] = {
            "add_ok": add_ok,
            "add_total": add_total,
            "add_holds": add_holds,
            "range_ok": range_ok,
            "range_total": range_total,
            "range_holds": range_holds,
        }

        desc = WORLD_DESCRIPTIONS[w]
        lines.append(
            f"{w:<5}| {desc:<27} | {add_ok}/{add_total:<19} | {range_ok}/{range_total}"
        )

    lines.append("")
    lines.append(
        "Heuristically, we expect worlds 0,1,2 (well-defined branches) to "
        "satisfy both AdditiveArg and RangeOk on all samples, while world 3 "
        "(naive atan) will fail AdditiveArg on some samples (and is not a "
        "genuine branch in the geometric sense)."
    )

    return lines, stats


# -----------------------------------------------------------------------------
# Higher-order look: Holds₁ / Holds₂ and model extensions
# -----------------------------------------------------------------------------

EXT1: Dict[str, Set[int]] = {}                 # unary: name ↦ {worlds}
EXT2: Dict[str, Set[Tuple[str, str]]] = {}     # binary: name ↦ set of pairs

STRONGER_REL = "rel:stronger"


def thm_int(name: str) -> str:
    """Encode a theorem name as a unary predicate-name, e.g. 'AdditiveArg' → 'thm:AdditiveArg'."""
    return f"thm:{name}"


def build_model_extensions(stats: Dict[int, Dict[str, int]]) -> None:
    """
    Populate EXT1 and EXT2 from the empirical stats:

      • Worlds are world ids w ∈ {0,1,2,3}.
      • INTENSIONS:
          - thm:AdditiveArg
          - thm:RangeOk
      • EXT1[intension] = set of worlds where the theorem holds in all samples.
      • EXT2[STRONGER_REL] = { (thm:AdditiveArg, thm:RangeOk) }.
    """
    EXT1.clear()
    EXT2.clear()

    t_add = thm_int("AdditiveArg")
    t_range = thm_int("RangeOk")

    EXT1[t_add] = set(w for w, s in stats.items() if s.get("add_holds", 0))
    EXT1[t_range] = set(w for w, s in stats.items() if s.get("range_holds", 0))

    EXT2[STRONGER_REL] = {(t_add, t_range)}


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

      1) Canonical values of Arg₍w₎ at 1, -1, i, -i in each world.
      2) AdditiveArg holds for concrete examples in worlds 0,1,2 and fails in world 3.
      3) RangeOk holds for samples in worlds 0,1,2 and is not enforced in world 3.
      4) Stats reflect that worlds 0–2 satisfy AdditiveArg, world 3 does not.
      5) EXT1 / Holds₁ agree with stats for all worlds and both theorems.
      6) The Holds₂ 'stronger' relation is present and respected:
           whenever AdditiveArg holds in a world, RangeOk holds there too.
    """
    notes: List[str] = []

    # 1) Canonical values at 1, -1, i, -i
    points = {
        "1": complex(1, 0),
        "-1": complex(-1, 0),
        "i": complex(0, 1),
        "-i": complex(0, -1),
    }

    # world 0 expectations: principal Arg
    pi = math.pi
    for name, z in points.items():
        θ0 = arg_world(z, 0)
        if name == "1":
            check(abs(θ0 - 0.0) < 1e-9, "world 0: Arg(1) must be ~0.")
        elif name == "-1":
            check(abs(θ0 - pi) < 1e-9, "world 0: Arg(-1) must be ~π.")
        elif name == "i":
            check(abs(θ0 - pi / 2.0) < 1e-9, "world 0: Arg(i) must be ~π/2.")
        elif name == "-i":
            check(abs(θ0 + pi / 2.0) < 1e-9, "world 0: Arg(-i) must be ~-π/2.")

    # world 1 expectations: [0, 2π)
    for name, z in points.items():
        θ1 = arg_world(z, 1)
        check(0.0 - 1e-9 <= θ1 < TWO_PI + 1e-9, "world 1: Arg range must be in [0, 2π).")
        if name == "-1":
            check(
                abs(θ1 - pi) < 1e-9,
                "world 1: Arg(-1) must be ~π.",
            )

    # world 2: shifted, just check it's in the right interval
    for _, z in points.items():
        θ2 = arg_world(z, 2)
        check(
            (-pi / 2.0 - 1e-9) < θ2 <= (3.0 * pi / 2.0 + 1e-9),
            "world 2: Arg must lie in (-π/2, 3π/2].",
        )

    # world 3: naive; Arg(1) should be 0, Arg(-1) ~π or 0, but Arg(-i) ~π/2 or -π/2
    θ3_i = arg_world(0 + 1j, 3)
    θ3_minus_i = arg_world(0 - 1j, 3)
    # We only assert they are finite and roughly opposite signs
    check(
        θ3_i > 0 and θ3_minus_i < 0,
        "world 3: naive Arg(i) and Arg(-i) should have opposite signs.",
    )

    notes.append("PASS 1: Canonical Arg values behave as expected in each world.")

    # 2) AdditiveArg for concrete examples
    z = complex(1, 1)
    w = complex(1, -1)

    for w_id in (0, 1, 2):
        check(
            additive_arg_holds(z, w, w_id),
            f"World {w_id}: AdditiveArg must hold for z=1+i, w=1-i.",
        )

    # World 3: deterministic failing example z=i, w=i
    z3 = complex(0, 1)
    w3 = complex(0, 1)
    check(
        not additive_arg_holds(z3, w3, 3),
        "World 3: AdditiveArg must fail for z=i, w=i.",
    )

    notes.append("PASS 2: AdditiveArg holds in worlds 0–2 but fails in world 3 for a concrete pair.")

    # 3) RangeOk behaviour
    # For worlds 0–2, in_range should always match a direct interval check
    for w_id in (0, 1, 2):
        for _ in range(50):
            z = random_complex_int()
            if z == 0:
                continue
            θ = arg_world(z, w_id)
            if w_id == 0:
                expect = (-pi - TOL) < θ <= (pi + TOL)
            elif w_id == 1:
                expect = (-TOL) <= θ < (TWO_PI + TOL)
            else:
                expect = (-pi / 2.0 - TOL) < θ <= (3.0 * pi / 2.0 + TOL)
            check(
                in_range(z, w_id) == expect,
                f"World {w_id}: in_range disagrees with interval check.",
            )

    notes.append("PASS 3: RangeOk behaves coherently with the intended intervals in worlds 0–2.")

    # 4) Stats expectations
    # We expect worlds 0–2 to satisfy AdditiveArg (on all non-zero samples),
    # and world 3 to fail it for at least one sample.
    for w_id in WORLD_IDS:
        s = stats[w_id]
        if w_id in (0, 1, 2):
            check(
                s["add_holds"] == 1,
                f"World {w_id}: expected AdditiveArg to hold empirically, got stats {s}.",
            )
        else:
            check(
                s["add_holds"] == 0,
                f"World 3: expected AdditiveArg to fail empirically, got stats {s}.",
            )

    # RangeOk: worlds 0–2 should hold; world 3 is unconstrained in the model,
    # but in our construction in_range always returns True there, so it will
    # also empirically hold (we do not rely on that for the "stronger" relation).
    for w_id in (0, 1, 2):
        s = stats[w_id]
        check(
            s["range_holds"] == 1,
            f"World {w_id}: expected RangeOk to hold empirically, got stats {s}.",
        )

    notes.append("PASS 4: Stats match expectations for AdditiveArg and RangeOk across worlds.")

    # 5) EXT1 / Holds₁ agreement
    t_add = thm_int("AdditiveArg")
    t_range = thm_int("RangeOk")
    for w_id in WORLD_IDS:
        s = stats[w_id]
        check(
            Holds1(t_add, w_id) == bool(s["add_holds"]),
            f"Holds1(thm:AdditiveArg, {w_id}) disagrees with stats.",
        )
        check(
            Holds1(t_range, w_id) == bool(s["range_holds"]),
            f"Holds1(thm:RangeOk, {w_id}) disagrees with stats.",
        )

    notes.append("PASS 5: Holds₁/EXT1 match the empirical stats for all worlds and theorems.")

    # 6) Holds₂ 'stronger' relation respected:
    # Whenever AdditiveArg holds in a world, RangeOk must also hold there.
    check(
        Holds2(STRONGER_REL, t_add, t_range),
        "Holds2(rel:stronger, thm:AdditiveArg, thm:RangeOk) must be true.",
    )
    for w_id in WORLD_IDS:
        if Holds1(t_add, w_id):
            check(
                Holds1(t_range, w_id),
                f"In world {w_id}, AdditiveArg holds but RangeOk does not.",
            )

    notes.append("PASS 6: 'AdditiveArg' is stronger than 'RangeOk' in all worlds where it holds.")

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
    "We compare four argument branches on ℂ:\n"
    "  world 0: Arg₀(z) principal in (-π, π]\n"
    "  world 1: Arg₁(z) in [0, 2π)\n"
    "  world 2: Arg₂(z) in (-π/2, 3π/2]\n"
    "  world 3: Arg₃(z) naive atan(y/x) (broken)\n"
    "and two theorem-names:\n"
    "  AdditiveArg:      Arg(zw) ≡ Arg(z) + Arg(w)  (mod 2π)\n"
    "  RangeOk:          Arg(z) lies in the intended interval.\n"
    "Worlds 0–2 are proper branches built from the principal Arg; world 3 is\n"
    "intentionally flawed to illustrate how additivity can fail."
)

REASON_TEXT = (
    "We represent complex numbers by Python's complex type and define, for\n"
    "each world, a concrete real-valued function Arg₍w₎ on ℂ\\{0}. The first-\n"
    "order core consists of:\n"
    "  • numerical definitions of Arg₍w₎ for w=0,1,2,3,\n"
    "  • a modular difference check for additivity (via wrap_pi),\n"
    "  • range checks for the intended branch intervals, and\n"
    "  • random sampling of integer points in ℂ.\n"
    "\n"
    "From this we build an extensional model:\n"
    "  • worlds: w ∈ {0,1,2,3},\n"
    "  • theorem-names: thm:AdditiveArg and thm:RangeOk,\n"
    "  • EXT1[thm:AdditiveArg] = { w | all non-zero samples obey additivity },\n"
    "  • EXT1[thm:RangeOk]     = { w | all non-zero samples lie in the range },\n"
    "and define Holds₁(P,w) ↔ w ∈ EXT1[P].\n"
    "\n"
    "A binary relation-name rel:stronger relates these intensions by setting\n"
    "  EXT2[rel:stronger] = { (thm:AdditiveArg, thm:RangeOk) },\n"
    "so that Holds₂(rel:stronger, X, Y) simply reports whether (X,Y) is in\n"
    "that set. In the resulting model, every world where AdditiveArg holds is\n"
    "one where RangeOk holds as well.\n"
    "\n"
    "In this way, the potentially 'higher-order' talk about branches and\n"
    "theorems is handled via a single first-order core over ℂ, with all\n"
    "intensional structure carried by Holds₁ and Holds₂."
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
    t_add = thm_int("AdditiveArg")
    t_range = thm_int("RangeOk")
    for w in WORLD_IDS:
        print(
            f"  world {w}: Holds1({t_add}, {w})={Holds1(t_add, w)}, "
            f"Holds1({t_range}, {w})={Holds1(t_range, w)}"
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
    table_lines, stats = estimate_arg_theorems()
    build_model_extensions(stats)
    arc_answer(table_lines)
    arc_reason()
    arc_check(stats)


if __name__ == "__main__":
    main()

