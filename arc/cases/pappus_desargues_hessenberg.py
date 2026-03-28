#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pappus_desargues_hessenberg.py
==============================

Hessenberg (1905): Pappus ⇒ Desargues
-------------------------------------
This script is a small, self-contained Python program illustrating – in a very
literal way – Hessenberg’s theorem:

    In a projective plane, if Pappus’ theorem holds for all configurations,
    then Desargues’ theorem holds for all configurations.

Concretely, we work inside finite projective planes PG(2, p) over the prime
fields GF(p) for a handful of small primes p. In such planes both Pappus and
Desargues are known to hold (because these planes come from fields), so any
random configuration that satisfies the hypotheses of the theorem should also
satisfy its conclusion.

The program prints three sections:

1) Answer
   - restates Hessenberg’s theorem,
   - reports empirical statistics for Pappus and Desargues in PG(2, p)
     for several primes p,
   - and shows how these statistics are seen through a small Holds₁/Holds₂
     “higher-order look, first-order core” lens.

2) Reason why
   - explains the geometric model: points, lines, incidence and collinearity
     in homogeneous coordinates over GF(p),
   - explains how Pappus and Desargues configurations are tested,
   - and explains the Holds₁ / Holds₂ reading.

3) Check (harness)
   - runs several independent tests to sanity-check:
       • the basic projective geometry primitives,
       • the Pappus and Desargues testers on small planes,
       • the empirical truth of Pappus and Desargues for each prime,
       • the consistency of the Holds₁ / Holds₂ model with those results,
       • and the “Pappus ⇒ Desargues” implication at the level of Holds₁.


Higher-order look, first-order core
-----------------------------------
We follow the “higher-order look, first-order core” pattern described in
https://josd.github.io/higher-order-look-first-order-core/ :

  • First-order core:
      - exact projective geometry over GF(p) using 3-component homogeneous
        coordinates for points and lines;
      - incidence (dot product), joins/meets (cross product), and collinearity.

  • Higher-order look:
      - each theorem T (here just Pappus, Desargues) is represented by a unary
        predicate-name "thm:T";
      - each world w is one of the tested planes PG(2, p), identified simply
        by the prime p;
      - a fixed, extensional interpretation EXT1 says in which worlds each
        theorem holds, and we define

            Holds1(P, w)  ⇔  w ∈ EXT1[P].

      - a binary relation "rel:implies" on these intensions records that
        Pappus implies Desargues at the theorem level, and we interpret

            Holds2("rel:implies", X, Y)  ⇔  (X, Y) ∈ EXT2["rel:implies"].

All the work to *decide* whether a theorem holds in a world is done in plain
first-order Python code: random, but exact, sampling of configurations inside
PG(2, p). The Holds₁ / Holds₂ predicates then simply read off the resulting
extensional model (EXT1, EXT2).

This does not by itself prove Hessenberg’s theorem (it only samples finitely
many configurations in a few finite planes), but it does provide a concrete,
computational illustration that is fully transparent and reasoner-free.
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


def random_line_and_span_points(p: int) -> Tuple[Tuple[int, int, int], Tuple[int, int, int], Tuple[int, int, int]]:
    """
    Construct a random line by choosing two random affine points U,V and
    returning (L, U, V) where L is the line through U and V.
    """
    U, V = random_distinct_points(2, p)
    L = line_through(U, V, p)
    return L, U, V


def noncollinear_triple(p: int) -> Tuple[Tuple[int, int, int], Tuple[int, int, int], Tuple[int, int, int]]:
    """Return A,B,C (affine) that are not collinear."""
    while True:
        A, B, C = random_distinct_points(3, p)
        if not collinear(A, B, C, p):
            return A, B, C


# -----------------------------------------------------------------------------
# Pappus and Desargues testers (random configurations)
# -----------------------------------------------------------------------------

def sample_pappus_trial(p: int, max_attempts: int = 250) -> Tuple[Optional[bool], Optional[Tuple]]:
    """
    Build a random Pappus configuration on two distinct lines and test the
    collinearity of the three “opposite-side” intersection points.

    Returns: (result, data)
      result ∈ {True, False, None}
        • True / False: test executed and passed/failed
        • None: degeneracy (coincident lines or undefined intersections)
      data: tuple with the points used, for potential inspection.
    """
    for _ in range(max_attempts):
        # First line with three distinct points A,B,C
        L, U, V = random_line_and_span_points(p)
        A, B = U, V
        C = None
        for __ in range(30):
            C = point_on_span(U, V, p)
            if not projectively_equal(C, A, p) and not projectively_equal(C, B, p):
                break

        # Second, distinct line with three distinct points A',B',C'
        while True:
            M, U2, V2 = random_line_and_span_points(p)
            if M != L:
                break
        A2, B2 = U2, V2
        C2 = None
        for __ in range(30):
            C2 = point_on_span(U2, V2, p)
            if not projectively_equal(C2, A2, p) and not projectively_equal(C2, B2, p):
                break

        # Lines for opposite sides
        L1 = line_through(A, B2, p)
        L2 = line_through(A2, B, p)
        L3 = line_through(A, C2, p)
        L4 = line_through(A2, C, p)  # type: ignore[arg-type]
        L5 = line_through(B, C2, p)
        L6 = line_through(B2, C, p)  # type: ignore[arg-type]

        # Filter degeneracies (coincident opposite sides)
        if L1 == L2 or L3 == L4 or L5 == L6:
            continue

        # Intersections X,Y,Z
        X = intersect(L1, L2, p)
        Y = intersect(L3, L4, p)
        Z = intersect(L5, L6, p)
        if X == (0, 0, 0) or Y == (0, 0, 0) or Z == (0, 0, 0):
            continue

        return collinear(X, Y, Z, p), (A, B, C, A2, B2, C2, X, Y, Z)

    return None, None


def sample_desargues_trial(p: int, max_attempts: int = 250) -> Tuple[Optional[bool], Optional[Tuple]]:
    """
    Build a random Desargues configuration from a random concurrency point O,
    with triangles ABC and A'B'C' chosen so that AA', BB', CC' concur at O.
    Test that the intersections P,Q,R of corresponding sides are collinear.

    Returns: (result, data) with same semantics as sample_pappus_trial.
    """
    for _ in range(max_attempts):
        O = random_affine_point(p)
        A, B, C = noncollinear_triple(p)

        def on_OP_not_O_or_P(O_: Tuple[int, int, int], P_: Tuple[int, int, int]) -> Optional[Tuple[int, int, int]]:
            # Randomly pick a point on line OP but distinct from O and P.
            for __ in range(60):
                a = randrange(1, p)
                b = randrange(1, p)
                Q = (
                    (a * O_[0] + b * P_[0]) % p,
                    (a * O_[1] + b * P_[1]) % p,
                    (a * O_[2] + b * P_[2]) % p,
                )
                if not projectively_equal(Q, O_, p) and not projectively_equal(Q, P_, p):
                    # Collinearity with O_,P_ is automatic from the linear form
                    if collinear(Q, O_, P_, p):
                        return Q
            return None

        Ap = on_OP_not_O_or_P(O, A)
        Bp = on_OP_not_O_or_P(O, B)
        Cp = on_OP_not_O_or_P(O, C)
        if None in (Ap, Bp, Cp):
            continue

        # Intersections of corresponding sides
        L_AB, L_ApBp = line_through(A, B, p), line_through(Ap, Bp, p)  # type: ignore[arg-type]
        L_AC, L_ApCp = line_through(A, C, p), line_through(Ap, Cp, p)  # type: ignore[arg-type]
        L_BC, L_BpCp = line_through(B, C, p), line_through(Bp, Cp, p)  # type: ignore[arg-type]

        # Filter degeneracies (coincident lines leading to undefined P,Q,R)
        if L_AB == L_ApBp or L_AC == L_ApCp or L_BC == L_BpCp:
            continue

        Ppt = intersect(L_AB, L_ApBp, p)
        Qpt = intersect(L_AC, L_ApCp, p)
        Rpt = intersect(L_BC, L_BpCp, p)
        if Ppt == (0, 0, 0) or Qpt == (0, 0, 0) or Rpt == (0, 0, 0):
            continue

        return collinear(Ppt, Qpt, Rpt, p), (A, B, C, Ap, Bp, Cp, O, Ppt, Qpt, Rpt)

    return None, None


# -----------------------------------------------------------------------------
# Empirical evaluation of Pappus and Desargues in PG(2, p)
# -----------------------------------------------------------------------------

PRIMES_TO_TEST: Tuple[int, ...] = (3, 5, 7, 11)
TRIALS_PER_PRIME: int = 120


def estimate_plane_theorems(
    primes: Sequence[int],
    trials: int,
) -> Tuple[List[str], Dict[int, Dict[str, int]]]:
    """
    For each prime p, run `trials` random Pappus and Desargues configurations
    in PG(2, p) and collect statistics.

    Returns:
      (table_lines, stats)

      stats[p] = {
        "pappus_ok": int,
        "pappus_total": int,
        "pappus_holds": 0 or 1,
        "desargues_ok": int,
        "desargues_total": int,
        "desargues_holds": 0 or 1,
      }
    """
    lines: List[str] = []
    stats: Dict[int, Dict[str, int]] = {}

    header = "p  | Pappus (ok/total) | Desargues (ok/total)"
    lines.append(header)
    lines.append("-" * len(header))

    for p in primes:
        pap_ok = des_ok = 0
        pap_total = des_total = 0

        for _ in range(trials):
            r1, _ = sample_pappus_trial(p)
            if r1 is not None:
                pap_total += 1
                pap_ok += int(bool(r1))

            r2, _ = sample_desargues_trial(p)
            if r2 is not None:
                des_total += 1
                des_ok += int(bool(r2))

        pappus_holds = int(pap_total > 0 and pap_ok == pap_total)
        desargues_holds = int(des_total > 0 and des_ok == des_total)

        stats[p] = {
            "pappus_ok": pap_ok,
            "pappus_total": pap_total,
            "pappus_holds": pappus_holds,
            "desargues_ok": des_ok,
            "desargues_total": des_total,
            "desargues_holds": desargues_holds,
        }

        lines.append(f"{p:<2} | {pap_ok}/{pap_total:<13} | {des_ok}/{des_total}")

    lines.append("")
    lines.append(
        "Note: PG(2, p) over a field GF(p) is known to satisfy both Pappus and "
        "Desargues exactly; the statistics above should therefore show 100% success."
    )

    return lines, stats


# -----------------------------------------------------------------------------
# Higher-order look: Holds₁ / Holds₂ and model extensions
# -----------------------------------------------------------------------------

EXT1: Dict[str, Set[int]] = {}                 # unary: name ↦ {worlds}
EXT2: Dict[str, Set[Tuple[str, str]]] = {}     # binary: name ↦ set of pairs

IMPLIES_REL = "rel:implies"


def thm_int(name: str) -> str:
    """Encode a theorem name as a unary predicate-name, e.g. 'Pappus' → 'thm:Pappus'."""
    return f"thm:{name}"


def build_model_extensions(stats: Dict[int, Dict[str, int]]) -> None:
    """
    Populate EXT1 and EXT2 from the empirical stats:

      • Worlds are primes p ∈ PRIMES_TO_TEST.
      • INTENSIONS:
          - thm:Pappus, thm:Desargues.
      • EXT1[intension] = set of primes p where the theorem is empirically
        seen to hold in PG(2, p), i.e. all nondegenerate samples passed.
      • EXT2[IMPLIES_REL] = { (thm:Pappus, thm:Desargues) }.
    """
    EXT1.clear()
    EXT2.clear()

    pappus_name = thm_int("Pappus")
    desargues_name = thm_int("Desargues")

    EXT1[pappus_name] = set(
        p for p, s in stats.items() if s.get("pappus_holds", 0)
    )
    EXT1[desargues_name] = set(
        p for p, s in stats.items() if s.get("desargues_holds", 0)
    )

    EXT2[IMPLIES_REL] = {(pappus_name, desargues_name)}


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


def first_nondegenerate_pappus(p: int, attempts: int = 300) -> Optional[bool]:
    """Return the first nondegenerate Pappus verdict in PG(2, p), or None."""
    for _ in range(attempts):
        r, _ = sample_pappus_trial(p)
        if r is not None:
            return r
    return None


def first_nondegenerate_desargues(p: int, attempts: int = 300) -> Optional[bool]:
    """Return the first nondegenerate Desargues verdict in PG(2, p), or None."""
    for _ in range(attempts):
        r, _ = sample_desargues_trial(p)
        if r is not None:
            return r
    return None


def run_checks(stats: Dict[int, Dict[str, int]]) -> List[str]:
    """
    Run several independent tests:

      1) Basic projective geometry primitives behave as expected.
      2) Pappus holds in at least one explicit random configuration in PG(2, 3).
      3) Desargues holds in at least one explicit random configuration in PG(2, 3).
      4) For each tested prime p, all nondegenerate samples passed for both theorems.
      5) EXT1 / Holds₁ agree with the stats for each world.
      6) The Holds₂-level 'Pappus implies Desargues' is respected in all worlds.
    """
    notes: List[str] = []

    # 1) Basic primitives: line_through and collinear behave sensibly.
    p = 5
    A, B, C = random_distinct_points(3, p)
    L_AB = line_through(A, B, p)
    # A and B lie on their join, C typically not (but we only assert the positives)
    check(dot(L_AB, A, p) == 0 and dot(L_AB, B, p) == 0, "A and B must lie on line(A,B).")
    notes.append("PASS 1: Basic projective primitives (line_through/dot) behave as expected.")

    # 2) Pappus in PG(2, 3) for at least one configuration
    r_pap = first_nondegenerate_pappus(3)
    check(r_pap is True, "Expected Pappus to hold in at least one sampled configuration in PG(2, 3).")
    notes.append("PASS 2: Pappus holds in sampled configurations in PG(2, 3).")

    # 3) Desargues in PG(2, 3) for at least one configuration
    r_des = first_nondegenerate_desargues(3)
    check(r_des is True, "Expected Desargues to hold in at least one sampled configuration in PG(2, 3).")
    notes.append("PASS 3: Desargues holds in sampled configurations in PG(2, 3).")

    # 4) For each prime, every nondegenerate sample passed for both theorems
    for p, s in stats.items():
        pap_total = s["pappus_total"]
        des_total = s["desargues_total"]
        pap_ok = s["pappus_ok"]
        des_ok = s["desargues_ok"]

        check(
            pap_total > 0,
            f"For p={p}, there should be at least one nondegenerate Pappus sample.",
        )
        check(
            des_total > 0,
            f"For p={p}, there should be at least one nondegenerate Desargues sample.",
        )
        check(
            pap_ok == pap_total,
            f"For p={p}, some Pappus samples failed: {pap_ok}/{pap_total}.",
        )
        check(
            des_ok == des_total,
            f"For p={p}, some Desargues samples failed: {des_ok}/{des_total}.",
        )

    notes.append("PASS 4: All nondegenerate sampled configurations satisfy Pappus and Desargues.")

    # 5) EXT1 / Holds₁ agree with stats
    pappus_name = thm_int("Pappus")
    desargues_name = thm_int("Desargues")

    for p, s in stats.items():
        pap_holds = bool(s["pappus_holds"])
        des_holds = bool(s["desargues_holds"])
        check(
            Holds1(pappus_name, p) == pap_holds,
            f"Holds1(thm:Pappus, {p}) disagrees with stats.",
        )
        check(
            Holds1(desargues_name, p) == des_holds,
            f"Holds1(thm:Desargues, {p}) disagrees with stats.",
        )

    notes.append("PASS 5: Holds₁/EXT1 match the empirical theorem statistics for each world.")

    # 6) Holds₂-level implication Pappus ⇒ Desargues
    check(
        Holds2(IMPLIES_REL, pappus_name, desargues_name),
        "Holds2(rel:implies, thm:Pappus, thm:Desargues) must be true.",
    )
    for p, s in stats.items():
        if s["pappus_holds"]:
            check(
                s["desargues_holds"],
                f"At world p={p}, Pappus holds but Desargues does not according to stats.",
            )

    notes.append("PASS 6: The Holds₂-level implication Pappus ⇒ Desargues matches all worlds.")

    return notes


# -----------------------------------------------------------------------------
# Printed text (Answer + Reason)
# -----------------------------------------------------------------------------

ANSWER_TEXT = (
    "Hessenberg’s theorem (1905): In any projective plane, if Pappus’ theorem "
    "holds for all appropriate configurations (i.e., the plane is Pappian), "
    "then Desargues’ theorem also holds for all configurations "
    "(i.e., the plane is Desarguesian)."
)

REASON_ALGEBRAIC = (
    "Modern algebraic perspective (very compressed):\n"
    "  (1) A Pappian projective plane can be coordinatized by a commutative "
    "division ring, i.e. a field.\n"
    "  (2) Projective planes over any division ring (commutative or not) "
    "satisfy Desargues.\n"
    "  (3) Every field is a division ring.\n"
    "  (4) Hence, in field planes, Pappus ⇒ Desargues."
)

REASON_HESSENBERG_OUTLINE = (
    "Hessenberg’s synthetic route (outline, no coordinates):\n"
    "  • Work in a projective plane where Pappus holds. Study central "
    "collineations (elations and homologies: collineations fixing an 'axis' "
    "line pointwise and a 'center' point).\n"
    "  • Using Pappus, show that compositions of suitable elations behave like "
    "translations on an affine patch; these translations commute, giving a "
    "commutative 'addition' on each affine line.\n"
    "  • Still synthetically, construct 'dilations' (homotheties) from a "
    "chosen triangle and central perspectivities. Their composition rules, "
    "controlled by Pappus configurations, provide a scalar-like multiplication.\n"
    "  • This additive and multiplicative structure behaves like that of a "
    "field; the plane’s collineation group begins to look like the usual "
    "affine/projective group over a field.\n"
    "  • In this setting, if two triangles are perspective from a point O, one "
    "can synthetically construct a perspectivity with axis ℓ taking one "
    "triangle to the other, forcing the intersections of corresponding sides "
    "to lie on ℓ. This is exactly Desargues’ theorem.\n"
    "  • Thus Pappus, via the behavior of central collineations, enforces the "
    "Desargues property without explicit coordinatization."
)


def arc_answer(table_lines: List[str]) -> None:
    print("Answer")
    print("------")
    print(ANSWER_TEXT)
    print()
    print("Empirical check in finite projective planes PG(2, p):")
    print()
    for line in table_lines:
        print(line)
    print()


def arc_reason() -> None:
    print("Reason why")
    print("----------")
    print(REASON_ALGEBRAIC)
    print()
    print(REASON_HESSENBERG_OUTLINE)
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
    table_lines, stats = estimate_plane_theorems(PRIMES_TO_TEST, TRIALS_PER_PRIME)
    build_model_extensions(stats)
    arc_answer(table_lines)
    arc_reason()
    arc_check(stats)


if __name__ == "__main__":
    main()

