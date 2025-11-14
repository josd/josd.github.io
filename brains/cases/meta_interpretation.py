#!/usr/bin/env python3
r"""
meta_interpretation.py
======================

What this file is
-----------------
This module is a small, self-contained Python reimplementation of a classic
Prolog-style meta-interpreter. It does **not** depend on any external logic
engine or Prolog runtime.

Instead, it explicitly encodes:
  - a tiny first-order term language (variables, functors, lists),
  - a simple unification algorithm, and
  - a deterministic meta-interpreter for a specific object program.

The object program here is a factorial definition expressed using Peano
arithmetic and three predicates:

  factorial(N, F)
  prod(N, M, P)
  sum(N, M, P)

The meta-interpreter `mi/2` runs over *lists of goals*, expanding the leftmost
goal at each step according to these clauses.


How it works (in one paragraph)
-------------------------------
Terms are represented as Python objects (Var, Fun, lists). A small unifier
operates on these terms to accumulate substitutions. The meta-interpreter
maintains a list of goals; while the list is non-empty, it takes the leftmost
goal, rewrites it using a Python version of the `head_body_/3` clauses, and
splices the resulting body back into the goal list. This is a direct
translation of the Prolog meta-interpreter but executed entirely in Python.


What the program does by default
--------------------------------
When you run this file as a script:

  python meta_interpretation.py

it constructs the nested query:

  mi([mi([factorial(5, F)], [])], [])

where 5 is encoded as the Peano term s(s(s(s(s(0))))). It then:

  1. Runs the meta-interpreter until the goal list is empty.
  2. Prints the value of F both as a Peano term and as a Python integer.
  3. Prints a short human-readable trace of the first rewrite steps
     ("Reason why").
  4. Runs a small test harness ("Check (harness)") that verifies several
     factorial values (0, 1, 3, 5), checks determinism, and checks that the
     number of rewrite steps grows with n.


Why this exists
---------------
This file demonstrates how a Prolog meta-interpreter can be rebuilt in a
"reasoner-free" way: all logical machinery (terms, unification, goal
reduction) is encoded directly in Python, but the overall structure – a
meta-interpreter that executes an object program – remains recognisably the
same. It fits the idea of a "higher-order look, first-order core": meta-level
constructs (`mi/2`, goal lists) are represented as first-order data operated
on by a fixed algorithm.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union


# -----------------------------------------------------------------------------
# Term representation (first-order core)
# -----------------------------------------------------------------------------

_unique_id = 0


def _next_id() -> int:
    global _unique_id
    _unique_id += 1
    return _unique_id


@dataclass(frozen=True)
class Var:
    """Logic variable (syntactic, not Python variable)."""

    name: str
    id: int

    def __repr__(self) -> str:
        return f"{self.name}_{self.id}"


def V(name: str) -> Var:
    """Convenience constructor for fresh variables."""
    return Var(name, _next_id())


@dataclass(frozen=True)
class Fun:
    """Compound term f(t1,...,tn). Also used for Peano numerals."""

    functor: str
    args: Tuple[Any, ...]  # Fun, Var, Python lists (for goal lists), or atoms

    def __repr__(self) -> str:
        if not self.args:
            return self.functor
        return f"{self.functor}({', '.join(map(_term_str, self.args))})"


Term = Union[Var, Fun, List[Any], str]


def _term_str(t: Term) -> str:
    if isinstance(t, list):
        return "[" + ", ".join(map(_term_str, t)) + "]"
    return repr(t)


# Peano numerals: 0, s(0), s(s(0)), ...
ZERO = Fun("0", ())


def S(x: Term) -> Fun:
    return Fun("s", (x,))


def peano(n: int) -> Term:
    """Encode a Python int as a Peano numeral."""
    t: Term = ZERO
    for _ in range(n):
        t = S(t)
    return t


def peano_to_int(t: Term) -> int:
    """Decode a Peano numeral into a Python int (with a small sanity check)."""
    count = 0
    while isinstance(t, Fun) and t.functor == "s" and len(t.args) == 1:
        t = t.args[0]
        count += 1
    if t != ZERO:
        raise ValueError("Not a canonical Peano numeral")
    return count


# -----------------------------------------------------------------------------
# Unification (tiny, first-order, with a light occurs-check)
# -----------------------------------------------------------------------------

Subst = Dict[Var, Term]


def deref(x: Term, s: Subst) -> Term:
    """Follow a variable through the substitution until it stabilises."""
    while isinstance(x, Var) and x in s:
        x = s[x]
    return x


def occurs(v: Var, t: Term, s: Subst) -> bool:
    """Occurs-check to avoid infinite self-references."""
    t = deref(t, s)
    if v == t:
        return True
    if isinstance(t, Var):
        return False
    if isinstance(t, list):
        return any(occurs(v, ti, s) for ti in t)
    if isinstance(t, Fun):
        return any(occurs(v, ti, s) for ti in t.args)
    return False


def unify(a: Term, b: Term, s: Subst) -> Optional[Subst]:
    """Unify two terms under substitution s; return updated s or None."""
    a = deref(a, s)
    b = deref(b, s)

    if a == b:
        return s

    # variable on the left
    if isinstance(a, Var):
        if occurs(a, b, s):
            return None
        s[a] = b
        return s

    # variable on the right
    if isinstance(b, Var):
        if occurs(b, a, s):
            return None
        s[b] = a
        return s

    # lists
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return None
        for x, y in zip(a, b):
            if (s := unify(x, y, s)) is None:
                return None
        return s

    # functors
    if isinstance(a, Fun) and isinstance(b, Fun):
        if a.functor != b.functor or len(a.args) != len(b.args):
            return None
        for x, y in zip(a.args, b.args):
            if (s := unify(x, y, s)) is None:
                return None
        return s

    # atoms that differ, or mismatched shapes
    return None


def apply_subst(t: Term, s: Subst) -> Term:
    """Apply substitution s to a term (deeply)."""
    t = deref(t, s)
    if isinstance(t, Var):
        return t
    if isinstance(t, Fun):
        return Fun(t.functor, tuple(apply_subst(ai, s) for ai in t.args))
    if isinstance(t, list):
        return [apply_subst(ai, s) for ai in t]
    # atoms (strings) are immutable
    return t


# -----------------------------------------------------------------------------
# Object program: head_body_/3 and mi/2 as Python rules
# -----------------------------------------------------------------------------
#
# We don’t represent clauses as data; instead we mirror the clause order in
# a single dispatcher `expand_goal`. This keeps the meta-interpreter simple:
#
#   • goals are Fun terms
#   • the meta-interpreter keeps a list of goals
#   • each step: take the leftmost goal, expand it with `head_body_`, splice.


def expand_goal(goal: Fun, s: Subst, trace: List[str]) -> Tuple[List[Fun], Subst]:
    """
    Given one goal (a Fun), return (body_goals, updated_subst).

    - `goal` is the current goal (already in head position).
    - `body_goals` is the list of goals that replaces `goal`.
    - `s` is the current substitution Π.

    We mirror the order of clauses in the Prolog `head_body_/3` and the
    implicit handling of `mi/2`.
    """
    goal = apply_subst(goal, s)

    # ---- meta-level: mi/2 -------------------------------------------------
    if goal.functor == "mi" and len(goal.args) == 2:
        goals_list, second = goal.args
        assert isinstance(goals_list, list), "mi/2 expects a list of goals as first arg"
        assert second == [], "mi/2 second argument must be [] in this program"

        if not goals_list:
            trace.append("mi([], []) ⇒ []")
            return [], s

        # mi([G|Gs], []) :-
        #     head_body_(G, Goals, Gs),
        #     mi(Goals, []).
        G = goals_list[0]
        Gs = goals_list[1:]

        bodyG, s = expand_goal(G, s, trace)
        new_mi = Fun("mi", (bodyG + Gs, []))
        trace.append("mi([G|Gs], []) ⇒ mi(Goals, []) where Goals = body(G) ++ Gs")
        return [new_mi], s

    # ---- factorial/2 ------------------------------------------------------

    # Base: factorial(0, s(0)).
    pat = Fun("factorial", (ZERO, S(ZERO)))
    s_try = s.copy()
    if unify(goal, pat, s_try) is not None:
        trace.append("factorial(0, s(0)) ⇒ []")
        return [], s_try

    # Rec: factorial(s(N), F) :-
    #          factorial(N, F1),
    #          prod(s(N), F1, F).
    N, Fv = V("N"), V("F")
    pat = Fun("factorial", (S(N), Fv))
    s_try = s.copy()
    if unify(goal, pat, s_try) is not None:
        F1 = V("F1")
        body = [
            Fun("factorial", (N, F1)),
            Fun("prod", (S(N), F1, Fv)),
        ]
        body = [apply_subst(b, s_try) for b in body]
        trace.append("factorial(s(N), F) ⇒ [factorial(N, F1), prod(s(N), F1, F)]")
        return body, s_try

    # ---- prod/3 -----------------------------------------------------------

    # Base: prod(0, _, 0).
    M_ = V("_")
    pat = Fun("prod", (ZERO, M_, ZERO))
    s_try = s.copy()
    if unify(goal, pat, s_try) is not None:
        trace.append("prod(0, _, 0) ⇒ []")
        return [], s_try

    # Rec: prod(s(N), M, P) :-
    #          prod(N, M, K),
    #          sum(K, M, P).
    N, M, P = V("N"), V("M"), V("P")
    pat = Fun("prod", (S(N), M, P))
    s_try = s.copy()
    if unify(goal, pat, s_try) is not None:
        K = V("K")
        body = [
            Fun("prod", (N, M, K)),
            Fun("sum", (K, M, P)),
        ]
        body = [apply_subst(b, s_try) for b in body]
        trace.append("prod(s(N), M, P) ⇒ [prod(N, M, K), sum(K, M, P)]")
        return body, s_try

    # ---- sum/3 ------------------------------------------------------------

    # Base: sum(0, M, M).
    M = V("M")
    pat = Fun("sum", (ZERO, M, M))
    s_try = s.copy()
    if unify(goal, pat, s_try) is not None:
        trace.append("sum(0, M, M) ⇒ []")
        return [], s_try

    # Rec: sum(s(N), M, s(K)) :-
    #          sum(N, M, K).
    N, M, K = V("N"), V("M"), V("K")
    pat = Fun("sum", (S(N), M, S(K)))
    s_try = s.copy()
    if unify(goal, pat, s_try) is not None:
        body = [Fun("sum", (N, M, K))]
        body = [apply_subst(b, s_try) for b in body]
        trace.append("sum(s(N), M, s(K)) ⇒ [sum(N, M, K)]")
        return body, s_try

    # If we reach here, the goal does not match any clause
    raise ValueError(f"No matching clause for goal: {goal}")


# -----------------------------------------------------------------------------
# Meta-interpretation loop (deterministic leftmost rewriting)
# -----------------------------------------------------------------------------

def solve(goals: List[Fun]) -> Tuple[Subst, List[str]]:
    """
    Perform deterministic rewriting, mirroring mi/2:

      • While there are goals, take the leftmost goal G.
      • Replace it by its body via expand_goal.
      • Stop when the goal list is empty.

    Returns:
      (final_substitution, trace_of_rewrite_steps).
    """
    s: Subst = {}
    trace: List[str] = []
    steps = 0

    while goals:
        g = goals.pop(0)
        body, s = expand_goal(g, s, trace)
        goals = body + goals  # leftmost rewriting
        steps += 1

        # Safety guard in case someone edits the clauses into a non-terminating one
        if steps > 20000:
            raise RuntimeError("Too many steps; likely non-terminating.")

    return s, trace


# -----------------------------------------------------------------------------
# Build the exact Prolog query as term structure
# -----------------------------------------------------------------------------

def make_query_for_factorial(n: int) -> Tuple[List[Fun], Var]:
    """
    Build the nested query from the Prolog file:

        true :+ mi([mi([factorial(s^n(0), F)], [])], []).

    Returns (initial_goal_list, variable_F).
    """
    F = V("F")
    inner_list = [Fun("factorial", (peano(n), F))]
    inner_mi = Fun("mi", (inner_list, []))
    outer_goals = [inner_mi]
    outer_mi = Fun("mi", (outer_goals, []))
    return [outer_mi], F


def solve_factorial(n: int) -> Tuple[int, List[str]]:
    """Helper: solve factorial(n, F) via the meta-interpreter and return (F_int, trace)."""
    goals, F = make_query_for_factorial(n)
    s, trace = solve(goals)
    F_val = apply_subst(F, s)
    k = peano_to_int(F_val)
    return k, trace


# -----------------------------------------------------------------------------
# Pretty-printing and explanation
# -----------------------------------------------------------------------------

def fmt_peano(t: Term, max_s: int = 50) -> str:
    """
    Compact pretty-printer:

        s^k(0)    if t is a Peano numeral with k layers
        repr(t)   otherwise (possibly truncated)
    """
    try:
        k = peano_to_int(t)
        return f"s^{k}(0)"
    except Exception:
        s = repr(t)
        if len(s) > 200:
            return s[:200] + "..."
        return s


def reason_text(trace: List[str], n: int, k_first: int = 10) -> str:
    """Human-readable explanation of the first few rewrite steps."""
    lines: List[str] = []

    lines.append("We run the meta-interpreter `mi/2` exactly as in the Prolog program,")
    lines.append("rewriting the leftmost goal each step using `head_body_/3`:\n")

    for i, step in enumerate(trace[:k_first], 1):
        lines.append(f" {i:>2}. {step}")
    if len(trace) > k_first:
        lines.append(f" … {len(trace) - k_first} more rewrite steps …")

    lines.append("")
    lines.append("Rules used (in order of matching):")
    lines.append("  factorial(0, s(0)).")
    lines.append("  factorial(s(N), F) → factorial(N, F1), prod(s(N), F1, F).")
    lines.append("  prod(0, _, 0).")
    lines.append("  prod(s(N), M, P) → prod(N, M, K), sum(K, M, P).")
    lines.append("  sum(0, M, M).")
    lines.append("  sum(s(N), M, s(K)) → sum(N, M, K).")
    lines.append("")
    lines.append(
        f"This yields factorial({n}) by repeated unfolding into `prod` and `sum` over Peano numbers."
    )

    return "\n".join(lines)


# -----------------------------------------------------------------------------
# Check (harness) — multiple independent tests
# -----------------------------------------------------------------------------

class CheckFailure(AssertionError):
    pass


def check(cond: bool, msg: str) -> None:
    if not cond:
        raise CheckFailure(msg)


def run_checks() -> List[str]:
    from math import factorial as fact

    notes: List[str] = []

    # 1) factorial(0) = 1
    k0, _ = solve_factorial(0)
    check(k0 == fact(0), f"factorial(0) should be {fact(0)}, got {k0}.")
    notes.append("PASS 1: factorial(0) via meta-interpreter is 1.")

    # 2) factorial(1) = 1
    k1, _ = solve_factorial(1)
    check(k1 == fact(1), f"factorial(1) should be {fact(1)}, got {k1}.")
    notes.append("PASS 2: factorial(1) via meta-interpreter is 1.")

    # 3) factorial(3) = 6
    k3, _ = solve_factorial(3)
    check(k3 == fact(3), f"factorial(3) should be {fact(3)}, got {k3}.")
    notes.append("PASS 3: factorial(3) via meta-interpreter is 6.")

    # 4) factorial(5) = 120 (the original query)
    k5, trace5 = solve_factorial(5)
    check(k5 == fact(5), f"factorial(5) should be {fact(5)}, got {k5}.")
    notes.append("PASS 4: factorial(5) via meta-interpreter is 120.")

    # 5) Determinism: running factorial(5) twice gives the same result and a non-empty trace
    k5_2, trace5_2 = solve_factorial(5)
    check(k5_2 == k5, "Second run for factorial(5) produced a different result.")
    check(len(trace5) > 0 and len(trace5_2) > 0, "Traces for factorial(5) should be non-empty.")
    notes.append("PASS 5: meta-interpreter is deterministic for factorial(5) (same result, non-empty traces).")

    # 6) Monotone effort: more steps for larger n (rough sanity check on recursion shape)
    k2, trace2 = solve_factorial(2)
    k4, trace4 = solve_factorial(4)
    check(len(trace2) < len(trace4) < len(trace5),
          "Expected more rewrite steps for larger n (trace length monotonicity).")
    notes.append("PASS 6: number of rewrite steps grows with n (2 < 4 < 5).")

    return notes


# -----------------------------------------------------------------------------
# Main (ARC-style output)
# -----------------------------------------------------------------------------

def main() -> None:
    n = 5  # the Prolog query uses s(s(s(s(s(0))))) i.e. factorial(5, F)

    # Run once for Answer + Reason why
    goals, F = make_query_for_factorial(n)
    subst, trace = solve(goals)
    F_val = apply_subst(F, subst)
    k = peano_to_int(F_val)

    # ----- Answer -----
    print("Answer")
    print("------")
    print("Query:")
    print(" true :+ mi([mi([factorial(s^5(0), F)], [])], []).")
    print("Result:")
    print(f" F (Peano) : {fmt_peano(F_val)}")
    print(f" F (int)   : {k}")
    print()

    # ----- Reason why -----
    print("Reason why")
    print("----------")
    print(reason_text(trace, n, k_first=12))
    print()

    # ----- Check (harness) -----
    print("Check (harness)")
    print("----------------")
    try:
        for note in run_checks():
            print(note)
    except CheckFailure as e:
        print("FAIL:", e)
        raise


if __name__ == "__main__":
    main()

