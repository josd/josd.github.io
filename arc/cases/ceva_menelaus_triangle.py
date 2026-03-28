#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ceva_menelaus_triangle.py
=========================

Ceva and Menelaus in finite projective planes
---------------------------------------------
This script is a small, self-contained Python program that empirically
illustrates two classical projective theorems about triangles:

  • Ceva’s theorem:
      In a triangle ABC, let D,E,F lie on BC, CA, AB (possibly on the
      extensions). The cevians AD, BE, CF are concurrent if and only if

          (BD/DC) · (CE/EA) · (AF/FB) = 1

      where the segment ratios are taken as *signed* ratios in a 1D
      coordinate on each side.

  • Menelaus’ theorem:
      In the same triangle ABC, let D,E,F lie on (possibly extended) sides
      BC, CA, AB and assume they are collinear. Then

          (BD/DC) · (CE/EA) · (AF/FB) = -1

      and conversely, this product being -1 characterizes collinearity.

We work in finite projective planes PG(2, p) over prime fields GF(p) for a
small list of primes p. In such field planes both Ceva and Menelaus hold
exactly, so *every* nondegenerate sampled configuration should satisfy the
corresponding equivalence:

  • (AD, BE, CF concurrent)   ↔   Ceva product = 1
  • (D, E, F collinear)       ↔   Menelaus product = -1

The program samples many random triangles and side-points in PG(2, p) for
each prime p, checks these equivalences, and builds a tiny extensional model
for two theorem-names "thm:Ceva" and "thm:Menelaus" over the set of worlds

  W = { p ∈ tested primes }.


Higher-order look, first-order core
-----------------------------------
We follow the “higher-order look, first-order core” pattern
(https://josd.github.io/higher-order-look-first-order-core/):

  • First-order core:
      - Points and lines are 3-component homogeneous coordinates over GF(p).
      - Incidence is dot product; joins/meets are cross products.
      - Triangle sides and cevians are lines; concurrency and collinearity
        are expressed by incidence.
      - Ceva/Menelaus products are computed from 1D coordinates along sides,
        in GF(p).

  • Higher-order look:
      - Intensions "thm:Ceva" and "thm:Menelaus" name unary predicates over
        worlds (primes p).
      - The unary predicate

            Holds₁(P, w)

        says that theorem-name P is empirically true in world w, i.e. all
        sampled nondegenerate configurations in PG(2, w) satisfy the
        corresponding equivalence.

        This is implemented extensionally via:

            EXT1: Dict[str, Set[int]]

        so that Holds1(P, w) ⇔ w ∈ EXT1[P].

      - A binary relation-name "rel:dual" on intensions records Ceva/Menelaus
        duality, and we interpret

            Holds₂("rel:dual", X, Y)

        extensionally via:

            EXT2["rel:dual"] ⊆ { ("thm:Ceva", "thm:Menelaus"),
                                 ("thm:Menelaus", "thm:Ceva") }.

There is no external reasoner; all projective geometry, ratios, Ceva and
Menelaus checks, and Holds₁ / Holds₂ facts are computed in this file.


What the script prints
----------------------
When run:

    python3 ceva_menelaus_triangle.py

it prints three ARC-style sections:

  1) Answer
     • a short reminder of the Ceva and Menelaus statements,
     • a table of empirical stats for each prime p:
           p  | Ceva (ok/total) | Menelaus (ok/total)
       where (ok/total) is the number of sampled configurations whose
       equivalence test passed, and whether that reached 100%,
     • and a few sample Holds₁ judgements.

  2) Reason why
     • a short explanation of the GF(p) projective model,
     • how Ceva and Menelaus products are computed via 1D side-coordinates,
     • and how the Holds₁ / Holds₂ view is derived from this first-order core.

  3) Check (harness)
     • at least six independent checks, including that:
         - the basic projective primitives behave correctly,
         - Ceva equivalence holds for sampled configurations in PG(2, 3),
         - Menelaus equivalence holds for sampled configurations in PG(2, 3),
         - for each prime, all nondegenerate samples satisfy the theorems,
         - EXT1 / Holds₁ match the statistics per world,
         - the Holds₂-level “duality” relation between Ceva and Menelaus
           is present and consistent.

Python 3.9+; no external packages.
"""

from __future__ import annotations

from random import randrange, seed
from typing import Dict, List, Optional, Sequence, Tuple, Set

seed(0)  # deterministic randomness for reproducible runs


# -----------------------------------------------------------------------------
# Basic finite projective geometry over GF(p)
# -----------------------------------------------------------------------------

def inv_mod(a: int, p: int) -> int:
    """Multiplicative inverse in GF(p), for prime p and a ≠ 0."""
    a %= p
    if a == 0:
        raise ZeroDivisionError("No inverse for 0 in a field.")
    # Fermat's little theorem: a^(p-2) ≡ a^{-1} (mod p)
    return pow(a, p - 2, p)


def norm_point(P: Tuple[int, int, int], p: int) -> Tuple[int, int, int]:
    """
    Normalize a homogeneous point (or line) to a canonical representative:
    divide by the first nonzero coordinate so equality is testable by tuples.
    """
    x, y, z = P
    x %= p
    y %= p
    z %= p
    if (x, y, z) == (0, 0, 0):
        return (0, 0, 0)
    for v in (x, y, z):
        if v % p != 0:
            inv = inv_mod(v, p)
            return ((x * inv) % p, (y * inv) % p, (z * inv) % p)
    # unreachable mathematically
    return (0, 0, 0)


def projectively_equal(P: Tuple[int, int, int], Q: Tuple[int, int, int], p: int) -> bool:
    """Check equality up to nonzero scalar via normalized reps."""
    return norm_point(P, p) == norm_point(Q, p)


def cross(u: Tuple[int, int, int], v: Tuple[int, int, int], p: int) -> Tuple[int, int, int]:
    """
    Projective join/meet via cross product mod p:
      • if u,v are points, u×v is the line through them;
      • if u,v are lines, u×v is their intersection point.
    """
    (x1, y1, z1) = u
    (x2, y2, z2) = v
    return (
        (y1 * z2 - z1 * y2) % p,
        (z1 * x2 - x1 * z2) % p,
        (x1 * y2 - y1 * x2) % p,
    )


def dot(l: Tuple[int, int, int], P: Tuple[int, int, int], p: int) -> int:
    """Incidence test: l·P == 0 (mod p) means P lies on line l."""
    a, b, c = l
    x, y, z = P
    return (a * x + b * y + c * z) % p


def line_through(P: Tuple[int, int, int], Q: Tuple[int, int, int], p: int) -> Tuple[int, int, int]:
    """Return the normalized line through two points P,Q."""
    L = cross(P, Q, p)
    return norm_point(L, p)


def intersect(L1: Tuple[int, int, int], L2: Tuple[int, int, int], p: int) -> Tuple[int, int, int]:
    """Return the normalized intersection point of lines L1,L2."""
    P = cross(L1, L2, p)
    return norm_point(P, p)


def collinear(P: Tuple[int, int, int], Q: Tuple[int, int, int], R: Tuple[int, int, int], p: int) -> bool:
    """True iff P, Q, R are collinear: (P×Q)·R == 0."""
    return dot(cross(P, Q, p), R, p) == 0


def random_affine_point(p: int) -> Tuple[int, int, int]:
    """Random point with z=1 (i.e., not on the line at infinity)."""
    return (randrange(p), randrange(p), 1)


def random_point(p: int) -> Tuple[int, int, int]:
    """Random homogeneous point (not all coords 0)."""
    while True:
        x, y, z = randrange(p), randrange(p), randrange(p)
        if (x, y, z) != (0, 0, 0):
            return (x, y, z)


def random_distinct_points(n: int, p: int) -> List[Tuple[int, int, int]]:
    """
    Return n distinct (up to projective equality) affine points.
    Avoids coincidences by normalizing and comparing representatives.
    """
    pts: List[Tuple[int, int, int]] = []
    while len(pts) < n:
        P = random_affine_point(p)
        if all(not projectively_equal(P, Q, p) for Q in pts):
            pts.append(P)
    return pts


def point_on_span(U: Tuple[int, int, int], V: Tuple[int, int, int], p: int) -> Tuple[int, int, int]:
    """
    Sample a random nonzero linear combination αU+βV (homogeneous).
    If U,V are points on a line L, this returns another point on L with high prob.
    """
    while True:
        a, b = randrange(p), randrange(p)
        if (a, b) != (0, 0):
            P = (
                (a * U[0] + b * V[0]) % p,
                (a * U[1] + b * V[1]) % p,
                (a * U[2] + b * V[2]) % p,
            )
            if P != (0, 0, 0):
                return P


def noncollinear_triple(p: int) -> Tuple[Tuple[int, int, int], Tuple[int, int, int], Tuple[int, int, int]]:
    """Return A,B,C (affine) that are not collinear."""
    while True:
        A, B, C = random_distinct_points(3, p)
        if not collinear(A, B, C, p):
            return A, B, C


def affine(P: Tuple[int, int, int], p: int) -> Tuple[int, int, int]:
    """
    Normalize a point to affine coordinates (x/z, y/z, 1).
    Raises ValueError if P lies on the line at infinity (z=0).
    """
    x, y, z = norm_point(P, p)
    if z == 0:
        raise ValueError("Point at infinity cannot be put in affine chart.")
    inv = inv_mod(z, p)
    return (x * inv % p, y * inv % p, 1)


def ratio_on_line(U: Tuple[int, int, int], V: Tuple[int, int, int], P: Tuple[int, int, int], p: int) -> int:
    """
    Compute the signed ratio (UP/ PV) on the line through U and V, expressed
    as a field element in GF(p):

        If we choose a 1D coordinate s with U ↦ 0 and V ↦ 1, then P has
        coordinate s(P), and we define

            (UP / PV) = s(P) / (1 - s(P)).

    This is well-defined as long as P ≠ U,V and the chosen coordinate
    discriminates U,V.
    """
    U = affine(U, p)
    V = affine(V, p)
    P = affine(P, p)
    ux, uy, _ = U
    vx, vy, _ = V
    px, py, _ = P

    if ux != vx:
        s = (px - ux) * inv_mod((vx - ux) % p, p) % p
    elif uy != vy:
        s = (py - uy) * inv_mod((vy - uy) % p, p) % p
    else:
        raise ValueError("U and V must be distinct points on a line.")

    if s == 0 or s == 1:
        raise ValueError("P coincides with U or V; ratio undefined.")

    return s * inv_mod((1 - s) % p, p) % p


def ceva_product(
    A: Tuple[int, int, int],
    B: Tuple[int, int, int],
    C: Tuple[int, int, int],
    D: Tuple[int, int, int],
    E: Tuple[int, int, int],
    F: Tuple[int, int, int],
    p: int,
) -> int:
    """Ceva product (BD/DC)*(CE/EA)*(AF/FB) in GF(p)."""
    r1 = ratio_on_line(B, C, D, p)
    r2 = ratio_on_line(C, A, E, p)
    r3 = ratio_on_line(A, B, F, p)
    return (((r1 * r2) % p) * r3) % p


def menelaus_product(
    A: Tuple[int, int, int],
    B: Tuple[int, int, int],
    C: Tuple[int, int, int],
    D: Tuple[int, int, int],
    E: Tuple[int, int, int],
    F: Tuple[int, int, int],
    p: int,
) -> int:
    """Menelaus product (BD/DC)*(CE/EA)*(AF/FB) in GF(p)."""
    return ceva_product(A, B, C, D, E, F, p)


# -----------------------------------------------------------------------------
# Ceva and Menelaus random equivalence tests
# -----------------------------------------------------------------------------

def sample_ceva_equiv_trial(p: int) -> Tuple[bool, int]:
    """
    Sample a random Ceva configuration in PG(2, p):

      - choose a nondegenerate triangle A,B,C;
      - choose D on BC, E on CA, F on AB (avoiding degeneracies);
      - compute:
          * concurrent = [AD, BE, CF are concurrent],
          * product = Ceva product.

    Return (concurrent, product). Ceva equivalence holds in this configuration
    iff concurrent == (product == 1 mod p).
    """
    while True:
        A, B, C = noncollinear_triple(p)

        # D on BC
        for _ in range(40):
            D = point_on_span(B, C, p)
            if (
                norm_point(D, p)[2] != 0
                and not projectively_equal(D, B, p)
                and not projectively_equal(D, C, p)
            ):
                try:
                    _ = ratio_on_line(B, C, D, p)
                    break
                except ValueError:
                    continue
        else:
            continue

        # E on CA
        for _ in range(40):
            E = point_on_span(C, A, p)
            if (
                norm_point(E, p)[2] != 0
                and not projectively_equal(E, C, p)
                and not projectively_equal(E, A, p)
            ):
                try:
                    _ = ratio_on_line(C, A, E, p)
                    break
                except ValueError:
                    continue
        else:
            continue

        # F on AB
        for _ in range(40):
            F = point_on_span(A, B, p)
            if (
                norm_point(F, p)[2] != 0
                and not projectively_equal(F, A, p)
                and not projectively_equal(F, B, p)
            ):
                try:
                    _ = ratio_on_line(A, B, F, p)
                    break
                except ValueError:
                    continue
        else:
            continue

        # concurrency check
        L_AD = line_through(A, D, p)
        L_BE = line_through(B, E, p)
        O = intersect(L_AD, L_BE, p)
        concurrent = collinear(C, F, O, p)
        product = ceva_product(A, B, C, D, E, F, p)
        return concurrent, product


def sample_menelaus_equiv_trial(p: int) -> Tuple[bool, int]:
    """
    Sample a random Menelaus configuration in PG(2, p):

      - choose a nondegenerate triangle A,B,C;
      - choose D on BC, E on CA, F on AB (avoiding degeneracies);
      - compute:
          * col = [D,E,F collinear],
          * product = Menelaus product.

    Return (col, product). Menelaus equivalence holds in this configuration
    iff col == (product == -1 mod p).
    """
    while True:
        A, B, C = noncollinear_triple(p)

        def rand_on_side(U, V):
            for _ in range(40):
                P = point_on_span(U, V, p)
                if (
                    norm_point(P, p)[2] != 0
                    and not projectively_equal(P, U, p)
                    and not projectively_equal(P, V, p)
                ):
                    try:
                        _ = ratio_on_line(U, V, P, p)
                        return P
                    except ValueError:
                        continue
            return None

        D = rand_on_side(B, C)
        if D is None:
            continue
        E = rand_on_side(C, A)
        if E is None:
            continue
        F = rand_on_side(A, B)
        if F is None:
            continue

        col = collinear(D, E, F, p)
        product = menelaus_product(A, B, C, D, E, F, p)
        return col, product


# -----------------------------------------------------------------------------
# Empirical evaluation of Ceva and Menelaus in PG(2, p)
# -----------------------------------------------------------------------------

PRIMES_TO_TEST: Tuple[int, ...] = (5, 7, 11)
TRIALS_PER_PRIME: int = 120


def estimate_triangle_theorems(
    primes: Sequence[int],
    trials: int,
) -> Tuple[List[str], Dict[int, Dict[str, int]]]:
    """
    For each prime p, run `trials` random Ceva and Menelaus configurations
    in PG(2, p) and collect statistics.

    Returns:
      (table_lines, stats)

      stats[p] = {
        "ceva_ok": int,
        "ceva_total": int,
        "ceva_holds": 0 or 1,
        "men_ok": int,
        "men_total": int,
        "men_holds": 0 or 1,
      }
    """
    lines: List[str] = []
    stats: Dict[int, Dict[str, int]] = {}

    header = "p  | Ceva (ok/total) | Menelaus (ok/total)"
    lines.append(header)
    lines.append("-" * len(header))

    for p in primes:
        ceva_ok = men_ok = 0
        ceva_total = men_total = 0

        for _ in range(trials):
            c_conc, c_prod = sample_ceva_equiv_trial(p)
            ceva_total += 1
            ceva_ok += int(bool(c_conc == (c_prod == 1 % p)))

            m_col, m_prod = sample_menelaus_equiv_trial(p)
            men_total += 1
            men_ok += int(bool(m_col == (m_prod == (p - 1) % p)))

        ceva_holds = int(ceva_ok == ceva_total)
        men_holds = int(men_ok == men_total)

        stats[p] = {
            "ceva_ok": ceva_ok,
            "ceva_total": ceva_total,
            "ceva_holds": ceva_holds,
            "men_ok": men_ok,
            "men_total": men_total,
            "men_holds": men_holds,
        }

        lines.append(f"{p:<2} | {ceva_ok}/{ceva_total:<14} | {men_ok}/{men_total}")

    lines.append("")
    lines.append(
        "Note: In field planes PG(2, p), the algebraic forms of Ceva and "
        "Menelaus hold exactly, so the stats should show 100% success "
        "for nondegenerate samples."
    )

    return lines, stats


# -----------------------------------------------------------------------------
# Higher-order look: Holds₁ / Holds₂ and model extensions
# -----------------------------------------------------------------------------

EXT1: Dict[str, Set[int]] = {}                 # unary: name ↦ {worlds}
EXT2: Dict[str, Set[Tuple[str, str]]] = {}     # binary: name ↦ set of pairs

DUAL_REL = "rel:dual"


def thm_int(name: str) -> str:
    """Encode a theorem name as a unary predicate-name, e.g. 'Ceva' → 'thm:Ceva'."""
    return f"thm:{name}"


def build_model_extensions(stats: Dict[int, Dict[str, int]]) -> None:
    """
    Populate EXT1 and EXT2 from the empirical stats:

      • Worlds are primes p ∈ PRIMES_TO_TEST.
      • INTENSIONS:
          - thm:Ceva, thm:Menelaus.
      • EXT1[intension] = set of primes p where the theorem is empirically
        seen to hold in PG(2, p), i.e. all sampled configs satisfied its
        equivalence.
      • EXT2[DUAL_REL] = { (thm:Ceva, thm:Menelaus),
                           (thm:Menelaus, thm:Ceva) }.
    """
    EXT1.clear()
    EXT2.clear()

    ceva_name = thm_int("Ceva")
    men_name = thm_int("Menelaus")

    EXT1[ceva_name] = set(
        p for p, s in stats.items() if s.get("ceva_holds", 0)
    )
    EXT1[men_name] = set(
        p for p, s in stats.items() if s.get("men_holds", 0)
    )

    EXT2[DUAL_REL] = {(ceva_name, men_name), (men_name, ceva_name)}


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
    Run several independent tests:

      1) Basic projective primitives behave as expected.
      2) Ceva equivalence holds in sampled configurations in PG(2, 5).
      3) Menelaus equivalence holds in sampled configurations in PG(2, 5).
      4) For each tested prime, all samples passed for both theorems.
      5) EXT1 / Holds₁ agree with stats for each world.
      6) The Holds₂-level 'duality' relation between Ceva and Menelaus holds.
    """
    notes: List[str] = []

    # 1) Basic primitives: line_through and collinear behave sensibly.
    p0 = 5
    A, B, C = random_distinct_points(3, p0)
    L_AB = line_through(A, B, p0)
    check(dot(L_AB, A, p0) == 0 and dot(L_AB, B, p0) == 0,
          "A and B must lie on line(A,B).")
    notes.append("PASS 1: Basic projective primitives (line_through/dot) behave as expected.")

    # 2) Ceva equivalence in PG(2, 5) for several configurations
    for _ in range(30):
        conc, prod = sample_ceva_equiv_trial(5)
        check(conc == (prod == 1 % 5),
              "Ceva equivalence failed in PG(2, 5) for a sampled configuration.")
    notes.append("PASS 2: Ceva equivalence holds in sampled configurations in PG(2, 5).")

    # 3) Menelaus equivalence in PG(2, 5) for several configurations
    for _ in range(30):
        col, prod = sample_menelaus_equiv_trial(5)
        check(col == (prod == (5 - 1) % 5),
              "Menelaus equivalence failed in PG(2, 5) for a sampled configuration.")
    notes.append("PASS 3: Menelaus equivalence holds in sampled configurations in PG(2, 5).")

    # 4) For each prime, every sampled configuration passed for both theorems
    for p, s in stats.items():
        ceva_total = s["ceva_total"]
        men_total = s["men_total"]
        ceva_ok = s["ceva_ok"]
        men_ok = s["men_ok"]

        check(
            ceva_total > 0 and men_total > 0,
            f"For p={p}, expected at least one Ceva and Menelaus sample.",
        )
        check(
            ceva_ok == ceva_total,
            f"For p={p}, some Ceva samples failed: {ceva_ok}/{ceva_total}.",
        )
        check(
            men_ok == men_total,
            f"For p={p}, some Menelaus samples failed: {men_ok}/{men_total}.",
        )

    notes.append("PASS 4: All sampled configurations satisfy Ceva and Menelaus for each tested p.")

    # 5) EXT1 / Holds₁ agree with stats
    ceva_name = thm_int("Ceva")
    men_name = thm_int("Menelaus")

    for p, s in stats.items():
        ceva_holds = bool(s["ceva_holds"])
        men_holds = bool(s["men_holds"])
        check(
            Holds1(ceva_name, p) == ceva_holds,
            f"Holds1(thm:Ceva, {p}) disagrees with stats.",
        )
        check(
            Holds1(men_name, p) == men_holds,
            f"Holds1(thm:Menelaus, {p}) disagrees with stats.",
        )

    notes.append("PASS 5: Holds₁/EXT1 match the empirical theorem statistics per world.")

    # 6) Holds₂-level duality between Ceva and Menelaus
    check(
        Holds2(DUAL_REL, ceva_name, men_name)
        and Holds2(DUAL_REL, men_name, ceva_name),
        "Ceva and Menelaus must be mutually related by rel:dual.",
    )
    notes.append("PASS 6: Holds₂-level duality between Ceva and Menelaus is present and symmetric.")

    return notes


# -----------------------------------------------------------------------------
# ARC: Answer / Reason why / Check
# -----------------------------------------------------------------------------

ANSWER_TEXT = (
    "Ceva and Menelaus (field-plane versions):\n"
    "  • Ceva: For a triangle ABC with points D∈BC, E∈CA, F∈AB, the cevians\n"
    "      AD, BE, CF are concurrent ⇔ (BD/DC)·(CE/EA)·(AF/FB) = 1.\n"
    "  • Menelaus: For a triangle ABC with D∈BC, E∈CA, F∈AB, the points\n"
    "      D, E, F are collinear ⇔ (BD/DC)·(CE/EA)·(AF/FB) = -1.\n"
    "Over a field, these are purely algebraic statements about ratios, and\n"
    "hold in finite projective planes PG(2, p) over GF(p)."
)

REASON_TEXT = (
    "We model PG(2, p) with homogeneous coordinates over GF(p):\n"
    "  • Points and lines are 3-component vectors modulo p, up to scalar.\n"
    "  • Incidence is dot product; joins/meets are cross products.\n"
    "  • Triangles, cevians, and intersections are all first-order data.\n"
    "\n"
    "On each side of a triangle, we introduce a 1D coordinate s with the\n"
    "endpoints mapped to 0 and 1. Any interior or exterior point P has a\n"
    "coordinate s(P) in GF(p), and the signed segment ratio is then\n"
    "\n"
    "      (UP / PV) = s(P) / (1 - s(P)).\n"
    "\n"
    "The Ceva and Menelaus products are just products of these ratios. For\n"
    "each sampled configuration in PG(2, p), we compute:\n"
    "  • concurrency or collinearity (via incidence), and\n"
    "  • the corresponding product in GF(p).\n"
    "\n"
    "The first-order core is the exact projective and algebraic computation.\n"
    "From it we extract a higher-order-looking model:\n"
    "  • worlds w are primes p,\n"
    "  • theorem names P∈{thm:Ceva, thm:Menelaus},\n"
    "  • Holds₁(P, w) is true iff every sampled config in PG(2, w) satisfies\n"
    "    the equivalence for P,\n"
    "  • Holds₂(rel:dual, thm:Ceva, thm:Menelaus) and its converse record\n"
    "    that we are treating them as dual theorems at the intensional level.\n"
    "\n"
    "Thus the whole story fits the 'higher-order look, first-order core'\n"
    "paradigm: theorem-names and their duality relation live in an intensional\n"
    "layer, while all semantic content is computed by a single first-order\n"
    "engine over GF(p)-geometry."
)


def arc_answer(table_lines: List[str]) -> None:
    print("Answer")
    print("------")
    print(ANSWER_TEXT)
    print()
    print("Empirical checks in PG(2, p):")
    print()
    for line in table_lines:
        print(line)
    print()

    # Show some Holds₁ values
    print("Holds₁ view on theorem-names:")
    ceva_name = thm_int("Ceva")
    men_name = thm_int("Menelaus")
    for p in PRIMES_TO_TEST:
        print(
            f"  p={p}: Holds1({ceva_name}, {p})={Holds1(ceva_name, p)}, "
            f"Holds1({men_name}, {p})={Holds1(men_name, p)}"
        )
    print()


def arc_reason() -> None:
    print("Reason why")
    print("----------")
    print(REASON_TEXT)
    print()


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
# Main
# -----------------------------------------------------------------------------

def main() -> None:
    table_lines, stats = estimate_triangle_theorems(PRIMES_TO_TEST, TRIALS_PER_PRIME)
    build_model_extensions(stats)
    arc_answer(table_lines)
    arc_reason()
    arc_check(stats)


if __name__ == "__main__":
    main()

