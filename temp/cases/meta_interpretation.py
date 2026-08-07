#!/usr/bin/env python3
r"""
meta_interpretation.py
======================

Overview
--------
This module is a small, self-contained Python reconstruction of a classic
Prolog-style **meta-interpreter** example. It interprets a tiny object
program that defines factorial using Peano arithmetic and the predicates

    factorial(N, F)
    prod(N, M, P)
    sum(N, M, P)

The original is written in N3/Prolog style. Here we rebuild it entirely in
Python, without calling any external reasoner or Prolog engine.


Higher-order look, first-order core
-----------------------------------
We follow the idea of **“higher-order look, first-order core”**:

* At the surface, we work with *goals as data*:
    - atomic goals like `factorial(s(N), F)` are represented as terms,
    - a meta-predicate `mi/2` takes a **list of goals** and interprets them,
    - the object program (the clauses for factorial/2, prod/3, sum/3) is
      “run” by a meta-interpreter rather than by Python directly.

  This looks higher-order because goals and programs are themselves manipulated
  as data (e.g. `mi([factorial(...), prod(...), ...], [])`).

* Under the hood, everything is implemented with a **first-order core**:
    - a tiny term language (`Var`, `Fun`, and Python lists),
    - a small unification algorithm over these terms,
    - and a fixed family of predicates

          holds1(Goals)                -- lists of goals (whole queries)
          holds2(Goal)                 -- single atomic goal p(t1,...,tn)
          holds3(PredName, ArgList)    -- predicate name + explicit arg list

      implemented as the Python functions:
          holds1(goals)        → (Subst, Trace)
          holds2(goal, s, tr)  → (BodyGoals, Subst)
          holds3(p, args, s,tr) = holds2(Fun(p,args), s, tr)

      For example, the atomic goal

          factorial(N,F)

      is represented as `Fun("factorial", (N, F))` and interpreted by:

          holds2(Fun("factorial", (N, F)), s, trace)
          # equivalently:
          holds3("factorial", [N, F], s, trace)

      while the meta-interpreter over lists is `holds1`, corresponding to
      `mi/2` in the original program.

There is **no external Prolog engine**, no higher-order unification, and no
quantification over predicate symbols. Predicate names like "factorial" or
"sum" are just strings (first-order objects), and all “meta” behaviour is
implemented as ordinary Python code over these first-order structures.


What happens when you run it
----------------------------
Running this file as a script:

    python meta_interpretation.py

does the following:

1. Builds the nested query corresponding to the original meta-interpreter call:

       mi([mi([factorial(5, F)], [])], [])

   where `5` is encoded as the Peano term `s(s(s(s(s(0)))))`.

2. Executes the meta-interpreter until the goal list is exhausted, using
   deterministic leftmost rewriting:

       holds1([Fun("mi", ([Fun("factorial", (s^5(0), F))], []))])

3. Prints:
    - **Answer**:
        - the value of `F` as a Peano term (e.g. `s^120(0)`),
        - the same value as a Python integer (e.g. `120`).
    - **Reason why**:
        - a short trace of the first rewrite steps and a summary of the
          object-level rules used (as they appear inside `holds2`).
    - **Check (harness)**:
        - several independent tests (factorial(0), factorial(1), factorial(3),
          factorial(5), determinism, and a small sanity check on the growth of
          rewrite steps with `n`).

The harness ensures that the result of the meta-interpretation agrees with
Python’s own `math.factorial` for the tested inputs and that the interpreter
is deterministic for this program.
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
    """Convenience constructor for a fresh logic variable."""
    return Var(name, _next_id())


@dataclass(frozen=True)
class Fun:
    """
    Compound term f(t1,...,tn).

    Conceptually, an atomic goal `p(t1,...,tn)` is a `Fun("p", (t1,...,tn))`,
    which we interpret via the fixed predicate `holds2`.
    """

    functor: str
    args: Tuple[Any, ...]  # Fun, Var, lists (for goal lists), or atoms

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
# holds2 / holds3: semantics of atomic goals
# -----------------------------------------------------------------------------
#
# We interpret each atomic goal `p(t1,...,tn)` as a `Fun("p", (t1,...,tn))`
# and define its meaning via:
#
#   holds2(goal, s, trace) -> (BodyGoals, Subst)
#
# and a thin, more explicitly “predicate-oriented” variant:
#
#   holds3(pred_name, arg_list, s, trace)
#       = holds2(Fun(pred_name, tuple(arg_list)), s, trace)
#
# This is exactly the “Holds₂” idea in code: predicate names are first-order
# objects, and their application is mediated by a fixed interpreter.


def holds2(goal: Fun, s: Subst, trace: List[str]) -> Tuple[List[Fun], Subst]:
    """
    Given a goal (a Fun predicate application), return (body_goals, updated_subst).

    This is the semantic core: it is our `holds2` in the sense of the
    higher-order look, first-order core pattern.
    """
    goal = apply_subst(goal, s)

    # ---- meta-level: mi/2 -------------------------------------------------
    if goal.functor == "mi" and len(goal.args) == 2:
        goals_list, second = goal.args
        assert isinstance(goals_list, list), "mi/2 expects a list of goals as first arg"
        assert second == [], "mi/2 second argument must be [] in this program"

        if not goals_list:
            trace.append("holds2(mi([], [])) ⇒ []")
            return [], s

        # mi([G|Gs], []) :
        G = goals_list[0]
        Gs = goals_list[1:]

        bodyG, s = holds2(G, s, trace)
        new_mi = Fun("mi", (bodyG + Gs, []))
        trace.append("holds2(mi([G|Gs], [])) ⇒ [mi(Goals, [])] where Goals = body(G) ++ Gs")
        return [new_mi], s

    # ---- factorial/2 ------------------------------------------------------

    # Base: factorial(0, s(0)).
    pat = Fun("factorial", (ZERO, S(ZERO)))
    s_try = s.copy()
    if unify(goal, pat, s_try) is not None:
        trace.append("holds2(factorial(0, s(0))) ⇒ []")
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
        trace.append("holds2(factorial(s(N), F)) ⇒ [factorial(N, F1), prod(s(N), F1, F)]")
        return body, s_try

    # ---- prod/3 -----------------------------------------------------------

    # Base: prod(0, _, 0).
    M_ = V("_")
    pat = Fun("prod", (ZERO, M_, ZERO))
    s_try = s.copy()
    if unify(goal, pat, s_try) is not None:
        trace.append("holds2(prod(0, _, 0)) ⇒ []")
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
        trace.append("holds2(prod(s(N), M, P)) ⇒ [prod(N, M, K), sum(K, M, P)]")
        return body, s_try

    # ---- sum/3 ------------------------------------------------------------

    # Base: sum(0, M, M).
    M = V("M")
    pat = Fun("sum", (ZERO, M, M))
    s_try = s.copy()
    if unify(goal, pat, s_try) is not None:
        trace.append("holds2(sum(0, M, M)) ⇒ []")
        return [], s_try

    # Rec: sum(s(N), M, s(K)) :-
    #          sum(N, M, K).
    N, M, K = V("N"), V("M"), V("K")
    pat = Fun("sum", (S(N), M, S(K)))
    s_try = s.copy()
    if unify(goal, pat, s_try) is not None:
        body = [Fun("sum", (N, M, K))]
        body = [apply_subst(b, s_try) for b in body]
        trace.append("holds2(sum(s(N), M, s(K))) ⇒ [sum(N, M, K)]")
        return body, s_try

    # If we reach here, the goal does not match any clause
    raise ValueError(f"No matching clause for goal: {goal}")


def holds3(pred: str, args: List[Term], s: Subst, trace: List[str]) -> Tuple[List[Fun], Subst]:
    """
    A more explicitly predicate-oriented entry point:

        holds3("factorial", [N, F], s, trace)

    is just sugar for:

        holds2(Fun("factorial", (N, F)), s, trace)

    This makes the predicate symbol itself a first-order argument, which is
    useful if you want to talk *about* predicate names as data.
    """
    goal = Fun(pred, tuple(args))
    return holds2(goal, s, trace)


# -----------------------------------------------------------------------------
# holds1: meta-interpretation loop over lists of goals
# -----------------------------------------------------------------------------
#
# holds1 corresponds to mi/2 at the level of whole goal lists. It repeatedly
# applies holds2/holds3 to the leftmost goal until the list is empty.


def holds1(goals: List[Fun]) -> Tuple[Subst, List[str]]:
    """
    Perform deterministic rewriting, mirroring the Prolog meta-interpreter:

      • While there are goals, take the leftmost goal G.
      • Replace it by its body via holds2(G, subst, trace).
      • Stop when the goal list is empty.

    Returns:
      (final_substitution, trace_of_rewrite_steps).
    """
    s: Subst = {}
    trace: List[str] = []
    steps = 0

    while goals:
        g = goals.pop(0)
        body, s = holds2(g, s, trace)
        goals = body + goals  # leftmost rewriting
        steps += 1

        # Safety guard in case someone edits the clauses into a non-terminating one
        if steps > 20000:
            raise RuntimeError("Too many steps; likely non-terminating.")

    return s, trace


# For backwards compatibility with earlier versions in this repo:
def solve(goals: List[Fun]) -> Tuple[Subst, List[str]]:
    """Alias for holds1(goals) to keep the old name used in other code."""
    return holds1(goals)


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
    s, trace = holds1(goals)
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

    lines.append("We run the meta-interpreter via a fixed family of predicates:")
    lines.append("  holds1  for goal lists (mi/2-level),")
    lines.append("  holds2  for atomic goals Fun('p', args),")
    lines.append("  holds3  for (predicate-name, argument-list) pairs.\n")

    for i, step in enumerate(trace[:k_first], 1):
        lines.append(f" {i:>2}. {step}")
    if len(trace) > k_first:
        lines.append(f" … {len(trace) - k_first} more rewrite steps …")

    lines.append("")
    lines.append("Rules used (in the order they are matched inside holds2):")
    lines.append("  mi([], []).")
    lines.append("  mi([G|Gs], []) → mi(Goals, []) via expansion of G.")
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
    subst, trace = holds1(goals)
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

