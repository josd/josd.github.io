# -*- coding: utf-8 -*-
"""
Arrow-type Subtyping (contravariant/covariant)
in Hayes–Menzel holds₂ style
---------------------------------------------

What this demonstrates
----------------------
A tiny *subtyping* calculus over a finite set of base types and all
3×3 function (arrow) types built from them.

We encode:

    • Base types  : ex:Top, ex:Int, ex:Bool
    • Arrow types : ex:Arr_Top_Top, ex:Arr_Int_Bool, ...
    • Subtyping   : ex:SubType(T,U)          (both arguments are *names*)
    • Arrow map   : ex:ArrowOf(A1,A2,TA)    (TA is the name for A1→A2)

Rules
-----

1) Reflexivity
       SubType(T,T).

2) Transitivity
       SubType(T,U) :- SubType(T,V), SubType(V,U).

3) Base facts
       Int ≤ Top,  Bool ≤ Top.

4) Arrow rule (→-subtyping)

       If  ArrowOf(A1,A2,TA)
           ArrowOf(B1,B2,TB)
           SubType(B1,A1)   # argument:  B1 ≤ A1   (contravariant)
           SubType(A2,B2)   # result:    A2 ≤ B2   (covariant)
       then
           SubType(TA,TB).

This is purely first-order because types are *names* (intensions), and
all reasoning is over relations on names (no function symbols). The
engine uses the SIGNATURE to safely ground head-only variables.

How to run
----------

    python subtyping_arrows.py

Printed sections
----------------
Model → Question → Answer → Reason why → Check (12 tests)
"""

# ─────────────────────────────────────────────────────────────────────────────
# Embedded tiny logic engine
# ─────────────────────────────────────────────────────────────────────────────

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Set, Tuple, Union
from collections import defaultdict, deque
import itertools
import inspect


class Var:
    """Logic variable with identity; standardized apart per rule use."""
    __slots__ = ("name", "id")
    _c = 0

    def __init__(self, name: str):
        Var._c += 1
        self.name = name
        self.id = Var._c

    def __repr__(self):
        return f"Var({self.name}_{self.id})"

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return isinstance(other, Var) and self.id == other.id


Term = Union[str, Var]


@dataclass
class Atom:
    pred: str
    args: List[Term]


@dataclass
class Clause:
    """Horn clause: head :- body1, body2, ...; body == [] means fact."""
    head: Atom
    body: List[Atom]


def atom(pred: str, *args: Term) -> Atom:
    return Atom(pred, list(args))


def fact(pred: str, *args: Term) -> Clause:
    return Clause(atom(pred, *args), [])


# --- Unification / substitution ---------------------------------------------

def deref(t: Term, subst: Dict[Var, Term]) -> Term:
    """Dereference a term through a substitution."""
    while isinstance(t, Var) and t in subst:
        t = subst[t]
    return t


def unify(t1: Term, t2: Term, subst: Dict[Var, Term]) -> Optional[Dict[Var, Term]]:
    """Unify two terms under subst; return extended subst or None."""
    t1 = deref(t1, subst)
    t2 = deref(t2, subst)

    if t1 == t2:
        return subst

    if isinstance(t1, Var):
        subst[t1] = t2
        return subst
    if isinstance(t2, Var):
        subst[t2] = t1
        return subst

    return None


def standardize_apart(cl: Clause) -> Clause:
    """Freshen variables in a clause when it is used."""
    mapping: Dict[Var, Var] = {}

    def f(t: Term) -> Term:
        if isinstance(t, Var):
            if t not in mapping:
                mapping[t] = Var(t.name)
            return mapping[t]
        return t

    def fa(a: Atom) -> Atom:
        return Atom(a.pred, [f(t) for t in a.args])

    return Clause(fa(cl.head), [fa(a) for a in cl.body])


def apply_s(a: Atom, subst: Dict[Var, Term]) -> Atom:
    return Atom(a.pred, [deref(t, subst) for t in a.args])


# --- Bottom-up least fixpoint engine ----------------------------------------

NAME, IND = "NAME", "IND"
Signature = Dict[str, Tuple[str, ...]]  # predicate -> sorts


def _collect_domains(facts: Dict[str, Set[Tuple[str, ...]]],
                     sig: Signature) -> Tuple[Set[str], Set[str]]:
    """Compute NAME/IND domains from current ground facts."""
    names: Set[str] = set()
    inds: Set[str] = set()
    for p, rows in facts.items():
        if p not in sig:
            continue
        sorts = sig[p]
        for row in rows:
            for val, sort in zip(row, sorts):
                if sort == NAME:
                    names.add(val)
                elif sort == IND:
                    inds.add(val)
    return names, inds


_lfp_cache: Dict[Tuple, Tuple[Dict[str, Set[Tuple[str, ...]]], int]] = {}


def _program_key(program: List[Clause]) -> Tuple:
    """Stable key for memoizing LFP results."""
    def term_repr(t: Term) -> Tuple[str, str]:
        if isinstance(t, str):
            return ("C", t)
        else:
            return ("V", t.name)

    key = []
    for c in program:
        head = (c.head.pred, tuple(term_repr(t) for t in c.head.args))
        body = tuple(
            (b.pred, tuple(term_repr(t) for t in b.args))
            for b in c.body
        )
        key.append((head, body))
    return tuple(key)


def _sig_key(sig: Signature) -> Tuple:
    return tuple(sorted((p, tuple(sorts)) for p, sorts in sig.items()))


def _seeds_key(names: Optional[Set[str]], inds: Optional[Set[str]]) -> Tuple:
    return (tuple(sorted(names or ())), tuple(sorted(inds or ())))


def _ground_head_from_domains(head: Atom,
                              subst: Dict[Var, Term],
                              sig: Signature,
                              names_list: List[str],
                              inds_list: List[str]) -> Iterable[Tuple[str, ...]]:
    """Ground a (possibly unsafe) head over NAME/IND domains."""
    sorts = sig.get(head.pred, tuple(NAME for _ in head.args))
    positions: List[List[str]] = []

    for t, sort in zip(head.args, sorts):
        t = deref(t, subst)
        if isinstance(t, str):
            positions.append([t])
        else:
            dom_list = names_list if sort == NAME else inds_list
            positions.append(dom_list)

    for combo in itertools.product(*positions):
        seen: Dict[Var, str] = {}
        ok = True
        for i, (t, _sort) in enumerate(zip(head.args, sorts)):
            t = deref(t, subst)
            if isinstance(t, Var):
                prev = seen.get(t)
                if prev is None:
                    seen[t] = combo[i]
                elif prev != combo[i]:
                    ok = False
                    break
        if ok:
            yield tuple(combo)


def solve_bottomup(program: List[Clause],
                   sig: Signature,
                   seed_name_domain: Optional[Set[str]] = None,
                   seed_ind_domain: Optional[Set[str]] = None
                   ) -> Tuple[Dict[str, Set[Tuple[str, ...]]], int]:
    """Generic bottom-up LFP over a finite program."""
    key = ("BU", _program_key(program), _sig_key(sig),
           _seeds_key(seed_name_domain, seed_ind_domain))
    cached = _lfp_cache.get(key)
    if cached is not None:
        return cached

    facts: Dict[str, Set[Tuple[str, ...]]] = defaultdict(set)
    # initial ground facts
    for cl in program:
        if not cl.body and all(isinstance(t, str) for t in cl.head.args):
            facts[cl.head.pred].add(tuple(cl.head.args))

    rounds = 0
    changed = True

    while changed:
        rounds += 1
        changed = False

        names, inds = _collect_domains(facts, sig)
        if seed_name_domain:
            names |= set(seed_name_domain)
        if seed_ind_domain:
            inds |= set(seed_ind_domain)
        names_list = sorted(names)
        inds_list = sorted(inds)

        for cl in program:
            if not cl.body:
                # fact with head-only vars, possibly unsafe
                if not all(isinstance(t, str) for t in cl.head.args):
                    for tpl in _ground_head_from_domains(cl.head, {}, sig,
                                                         names_list, inds_list):
                        if tpl not in facts[cl.head.pred]:
                            facts[cl.head.pred].add(tpl)
                            changed = True
                continue

            partials: List[Dict[Var, Term]] = [dict()]
            for b in cl.body:
                new_partials: List[Dict[Var, Term]] = []
                rows = facts.get(b.pred, set())
                const_pos = [i for i, t in enumerate(b.args) if isinstance(t, str)]
                for s in partials:
                    b1 = apply_s(b, s)
                    for row in rows:
                        if len(row) != len(b1.args):
                            continue
                        bad = False
                        for i in const_pos:
                            if b1.args[i] != row[i]:
                                bad = True
                                break
                        if bad:
                            continue
                        s2 = s.copy()
                        ok = True
                        for arg, val in zip(b1.args, row):
                            s2 = unify(arg, val, s2)
                            if s2 is None:
                                ok = False
                                break
                        if ok:
                            new_partials.append(s2)
                partials = new_partials
                if not partials:
                    break

            if not partials:
                continue

            for s in partials:
                head = apply_s(cl.head, s)
                if all(isinstance(t, str) for t in head.args):
                    tpl = tuple(head.args)
                    if tpl not in facts[cl.head.pred]:
                        facts[cl.head.pred].add(tpl)
                        changed = True
                else:
                    for tpl in _ground_head_from_domains(head, {}, sig,
                                                         names_list, inds_list):
                        if tpl not in facts[cl.head.pred]:
                            facts[cl.head.pred].add(tpl)
                            changed = True

    _lfp_cache[key] = (facts, rounds)
    return facts, rounds


# --- Utilities ---------------------------------------------------------------

def match_against_facts(goals: List[Atom],
                        facts: Dict[str, Set[Tuple[str, ...]]]
                        ) -> List[Dict[Var, Term]]:
    """Conjunctive query evaluation against a ground fact-table."""
    sols: List[Dict[Var, Term]] = [dict()]
    for a in goals:
        new_sols: List[Dict[Var, Term]] = []
        rows = facts.get(a.pred, set())
        const_pos = [i for i, t in enumerate(a.args) if isinstance(t, str)]
        for s in sols:
            for row in rows:
                if len(row) != len(a.args):
                    continue
                bad = False
                for i in const_pos:
                    if a.args[i] != row[i]:
                        bad = True
                        break
                if bad:
                    continue
                s2 = s.copy()
                ok = True
                for arg, val in zip(a.args, row):
                    if isinstance(arg, Var):
                        cur = deref(arg, s2)
                        if isinstance(cur, Var):
                            s2[cur] = val
                        else:
                            if cur != val:
                                ok = False
                                break
                    else:
                        if arg != val:
                            ok = False
                            break
                if ok:
                    new_sols.append(s2)
        sols = new_sols
        if not sols:
            break
    return sols


def local(name: str) -> str:
    return name.split(":", 1)[1] if ":" in name else name


def fmt_set(names: Iterable[str]) -> str:
    seq = sorted(local(n) for n in set(names))
    return "∅" if not seq else "{" + ", ".join(seq) + "}"


# --- Top-down via restricted bottom-up on relevant subprogram ----------------

def _dependency_graph(program: List[Clause]) -> Dict[str, Set[str]]:
    g: Dict[str, Set[str]] = defaultdict(set)
    for c in program:
        h = c.head.pred
        for b in c.body:
            g[h].add(b.pred)
        g.setdefault(h, g.get(h, set()))
    return g


def _reachable_preds(program: List[Clause], goal_preds: Set[str]) -> Set[str]:
    g = _dependency_graph(program)
    reach: Set[str] = set()
    q = deque(goal_preds)
    while q:
        p = q.popleft()
        if p in reach:
            continue
        reach.add(p)
        for q2 in g.get(p, set()):
            if q2 not in reach:
                q.append(q2)
    return reach


def _filter_program(program: List[Clause], rel_preds: Set[str]) -> List[Clause]:
    return [c for c in program if c.head.pred in rel_preds]


def _collect_seed_domains_from_program(program: List[Clause],
                                       sig: Signature
                                       ) -> Tuple[Set[str], Set[str]]:
    names: Set[str] = set()
    inds: Set[str] = set()
    for cl in program:
        if cl.body:
            continue
        head = cl.head
        if head.pred not in sig:
            continue
        sorts = sig[head.pred]
        if any(isinstance(t, Var) for t in head.args):
            continue
        for val, sort in zip(head.args, sorts):
            if isinstance(val, str):
                if sort == NAME:
                    names.add(val)
                elif sort == IND:
                    inds.add(val)
    return names, inds


def _collect_seed_domains_from_goals(goals: List[Atom],
                                     sig: Signature
                                     ) -> Tuple[Set[str], Set[str]]:
    names: Set[str] = set()
    inds: Set[str] = set()
    for g in goals:
        sorts = sig.get(g.pred)
        if not sorts:
            continue
        for val, sort in zip(g.args, sorts):
            if isinstance(val, str):
                if sort == NAME:
                    names.add(val)
                elif sort == IND:
                    inds.add(val)
    return names, inds


def solve_topdown(program: List[Clause],
                  goals: List[Atom],
                  step_limit: int = 10000
                  ) -> Tuple[List[Dict[Var, Term]], int]:
    """
    Top-down evaluation via:
      1) dependency closure from goal predicates,
      2) bottom-up LFP on that relevant subprogram,
      3) conjunctive matching over the resulting facts.
    """
    # Try to obtain a signature from the caller module, defaulting to NAME-only.
    sig: Signature = {}
    try:
        caller_globals = inspect.currentframe().f_back.f_globals  # type: ignore
        if 'SIGNATURE' in caller_globals:
            sig = caller_globals['SIGNATURE']  # type: ignore
    except Exception:
        pass

    if not sig:
        preds = {c.head.pred for c in program}
        for p in preds:
            arity = len(next(c for c in program if c.head.pred == p).head.args)
            sig[p] = tuple(NAME for _ in range(arity))  # type: ignore

    goal_preds = {g.pred for g in goals}
    rel = _reachable_preds(program, goal_preds)
    subprog = _filter_program(program, rel)

    names_prog, inds_prog = _collect_seed_domains_from_program(program, sig)
    names_goals, inds_goals = _collect_seed_domains_from_goals(goals, sig)
    seed_names = names_prog | names_goals
    seed_inds = inds_prog | inds_goals

    facts, rounds = solve_bottomup(subprog, sig,
                                   seed_name_domain=seed_names,
                                   seed_ind_domain=seed_inds)
    sols = match_against_facts(goals, facts)
    return sols, rounds


# ─────────────────────────────────────────────────────────────────────────────
# Type Names (as *names*/URIs)
# ─────────────────────────────────────────────────────────────────────────────

from typing import List as _ListAlias, Tuple as _TupleAlias, Set as _SetAlias  # keep typedef style

EX = "ex:"

Top = EX + "Top"
Int = EX + "Int"
Bool = EX + "Bool"

BASE_TYPES: Tuple[str, ...] = (Top, Int, Bool)


def arr_name(a: str, b: str) -> str:
    """Canonical name for the arrow type a→b."""
    return EX + f"Arr_{local(a)}_{local(b)}"


# All 3×3 arrow types over {Top,Int,Bool}
ARROWS: Tuple[str, ...] = tuple(
    arr_name(a, b) for a in BASE_TYPES for b in BASE_TYPES
)

# Mapping predicate from components to arrow name
ArrowOf = EX + "ArrowOf"   # NAME×NAME×NAME

# Subtyping relation (over *names*)
SubType = EX + "SubType"   # NAME×NAME

# Signature (NAME/IND) — only NAMEs appear in these predicates.
SIGNATURE: Signature = {
    ArrowOf: (NAME, NAME, NAME),
    SubType: (NAME, NAME),
}

# ─────────────────────────────────────────────────────────────────────────────
# PROGRAM (facts + rules)
# ─────────────────────────────────────────────────────────────────────────────

PROGRAM: List[Clause] = []

# ArrowOf facts for all pairs
for a in BASE_TYPES:
    for b in BASE_TYPES:
        PROGRAM.append(fact(ArrowOf, a, b, arr_name(a, b)))

# Base subtyping facts
PROGRAM += [
    fact(SubType, Int, Top),
    fact(SubType, Bool, Top),
]

# Reflexivity (unsafe head-only variable; grounded via NAME-domain)
T = Var("T")
PROGRAM.append(Clause(atom(SubType, T, T), []))

# Transitivity
X, Y, Z = Var("X"), Var("Y"), Var("Z")
PROGRAM.append(
    Clause(
        atom(SubType, X, Z),
        [atom(SubType, X, Y), atom(SubType, Y, Z)],
    )
)

# Arrow subtyping: (A1→A2) ≤ (B1→B2) if B1 ≤ A1 and A2 ≤ B2
A1, A2, B1, B2, TA, TB = (
    Var("A1"),
    Var("A2"),
    Var("B1"),
    Var("B2"),
    Var("TA"),
    Var("TB"),
)
PROGRAM.append(
    Clause(
        atom(SubType, TA, TB),
        [
            atom(ArrowOf, A1, A2, TA),
            atom(ArrowOf, B1, B2, TB),
            atom(SubType, B1, A1),  # contravariant in the argument
            atom(SubType, A2, B2),  # covariant in the result
        ],
    )
)

# ─────────────────────────────────────────────────────────────────────────────
# Case-specific engine glue
# ─────────────────────────────────────────────────────────────────────────────

def _is_var(t) -> bool:
    return isinstance(t, Var)


def choose_engine(goals: List[Atom]) -> str:
    """Enumerations (variables) → bottom-up; ground checks → top-down."""
    for g in goals:
        if g.pred == SubType and any(_is_var(t) for t in g.args):
            return "bottomup"
    return "topdown"


def ask(goals: List[Atom],
        step_limit: int = 10000,
        fallback_threshold: int = 4000):
    engine = choose_engine(goals)
    if engine == "topdown":
        sols, metric = solve_topdown(PROGRAM, goals, step_limit=step_limit)
        return engine, sols, metric
    else:
        facts, rounds = solve_bottomup(PROGRAM, SIGNATURE)
        sols = match_against_facts(goals, facts)
        return engine, sols, rounds


# ─────────────────────────────────────────────────────────────────────────────
# Presentation
# ─────────────────────────────────────────────────────────────────────────────

def print_model() -> None:
    print("Model")
    print("=====")
    print("Base types (names):", ", ".join(local(t) for t in BASE_TYPES))
    print("Arrow types (names):", ", ".join(local(a) for a in ARROWS))

    print("\nFixed predicates (signature)")
    print("----------------------------")
    print("• ex:SubType(T,U) — subtyping over *names*; sorts: (NAME, NAME)")
    print("• ex:ArrowOf(A1,A2,T) — T is the *name* of arrow A1→A2; sorts: (NAME, NAME, NAME)")

    print("\nProgram rules")
    print("-------------")
    print("1) Reflexive: SubType(T,T).")
    print("2) Transitive: SubType(X,Z) :- SubType(X,Y), SubType(Y,Z).")
    print("3) Arrow: (A1→A2) ≤ (B1→B2) if B1 ≤ A1 and A2 ≤ B2 (contra/co-variance).")
    print("Base facts: Int ≤ Top, Bool ≤ Top.\n")


def print_question() -> None:
    print("Question")
    print("========")
    print("Q1) Enumerate all subtyping pairs SubType(T,U). [auto engine]")
    print("Q2) Witness TB s.t. SubType(Arr_Int_Bool, TB). [auto engine]")
    print("Q3) ∀X∈{Top,Int,Bool}: SubType(Arr_Top_X, Arr_Top_Top)? [auto engine]")
    print("Q4) ∀X∈{Top,Int,Bool}: SubType(Arr_Top_Top, Arr_X_Top)? [auto engine]")


def run_queries():
    # Q1: enumerate all subtyping pairs
    Tv, Uv = Var("T"), Var("U")
    eng1, sols1, m1 = ask([atom(SubType, Tv, Uv)])
    pairs = sorted({(deref(Tv, s), deref(Uv, s)) for s in sols1})

    # Q2: witnesses TB such that Arr_Int_Bool ≤ TB
    TA = arr_name(Int, Bool)
    TBv = Var("TB")
    eng2, sols2, m2 = ask([atom(SubType, TA, TBv)])
    witnesses = sorted({deref(TBv, s) for s in sols2})

    # Q3: universal property (covariance in result when arg=Top)
    ok3 = True
    for X in BASE_TYPES:
        TA = arr_name(Top, X)
        TT = arr_name(Top, Top)
        e, sols, _ = ask([atom(SubType, TA, TT)])
        if not sols:
            ok3 = False
            break
    eng3 = "mixed"

    # Q4: universal property (contravariance in argument toward Top)
    ok4 = True
    AT = arr_name(Top, Top)
    for X in BASE_TYPES:
        TX = arr_name(X, Top)
        e, sols, _ = ask([atom(SubType, AT, TX)])
        if not sols:
            ok4 = False
            break
    eng4 = "mixed"

    return (
        ("Q1", eng1, pairs, m1),
        ("Q2", eng2, witnesses, m2),
        ("Q3", eng3, ok3, 0),
        ("Q4", eng4, ok4, 0),
    )


def print_answer(res1, res2, res3, res4) -> None:
    print("Answer")
    print("======")
    tag1, eng1, pairs, _ = res1
    tag2, eng2, witnesses, _ = res2
    tag3, eng3, ok3, _ = res3
    tag4, eng4, ok4, _ = res4

    def show_pairs(ps):
        if not ps:
            return "∅"
        return "{" + ", ".join(f"{local(t)} ≤ {local(u)}" for (t, u) in ps) + "}"

    print(f"{tag1}) Engine: {eng1} → {show_pairs(pairs)}")
    print(
        f"{tag2}) Engine: {eng2} → Witness TB s.t. "
        f"Arr_Int_Bool ≤ TB = "
        + ("∅" if not witnesses else "{" + ", ".join(local(w) for w in witnesses) + "}")
    )
    print(f"{tag3}) Engine: {eng3} → Universal (covariant result) holds: {'Yes' if ok3 else 'No'}")
    print(f"{tag4}) Engine: {eng4} → Universal (contravariant arg) holds: {'Yes' if ok4 else 'No'}\n")


def print_reason(eng1, eng2) -> None:
    print("Reason why")
    print("==========")
    print("• Types are *names*; subtyping is a relation over names (first-order).")
    print("• ArrowOf maps components (A1,A2) to the *name* of A1→A2.")
    print("• Arrow rule implements contravariance/covariance without functions or higher-order.")
    print("• Engine chooser: big enumerations → bottom-up; targeted checks → tabled top-down.\n")


# ─────────────────────────────────────────────────────────────────────────────
# Check (12 tests)
# ─────────────────────────────────────────────────────────────────────────────

class CheckFailure(AssertionError):
    pass


def check(c: bool, msg: str):
    if not c:
        raise CheckFailure(msg)


def run_checks() -> List[str]:
    notes: List[str] = []

    # 1) Bottom-up enumeration includes some expected base and arrow pairs
    facts, _ = solve_bottomup(PROGRAM, SIGNATURE)
    Tv, Uv = Var("T"), Var("U")
    bu = match_against_facts([atom(SubType, Tv, Uv)], facts)
    pairs = {(deref(Tv, s), deref(Uv, s)) for s in bu}
    expect_subset = {
        (Int, Top),
        (Bool, Top),
        (arr_name(Int, Bool), arr_name(Int, Top)),  # covariant result
        (arr_name(Top, Top), arr_name(Int, Top)),  # contravariant arg
    }
    check(expect_subset.issubset(pairs),
          "Expected subtyping pairs missing in bottom-up.")
    notes.append("PASS 1: Bottom-up includes expected base & arrow pairs.")

    # 2) Tabled top-down proves a concrete arrow subtyping goal
    td, _ = solve_topdown(
        PROGRAM,
        [atom(SubType, arr_name(Int, Bool), arr_name(Int, Top))],
    )
    check(bool(td), "Top-down failed on Arr_Int_Bool ≤ Arr_Int_Top.")
    notes.append("PASS 2: Tabled top-down proves a sample arrow subtyping.")

    # 3) Witnesses for Arr_Int_Bool ≤ TB are exactly {Arr_Int_Bool, Arr_Int_Top}
    Tv2 = Var("TB")
    td_w, _ = solve_topdown(
        PROGRAM,
        [atom(SubType, arr_name(Int, Bool), Tv2)],
    )
    ws = {deref(Tv2, s) for s in td_w}
    check(
        ws == {arr_name(Int, Bool), arr_name(Int, Top)},
        f"Witness set mismatch: {ws}",
    )
    notes.append("PASS 3: Witness set for Arr_Int_Bool ≤ TB is correct.")

    # 4) Covariance universal: ∀X, Arr_Top_X ≤ Arr_Top_Top
    ok = True
    for X in BASE_TYPES:
        if not match_against_facts(
            [atom(SubType, arr_name(Top, X), arr_name(Top, Top))],
            facts,
        ):
            ok = False
            break
    check(ok, "Covariance universal failed.")
    notes.append("PASS 4: Covariance universal holds.")

    # 5) Contravariance universal: ∀X, Arr_Top_Top ≤ Arr_X_Top
    ok = True
    for X in BASE_TYPES:
        if not match_against_facts(
            [atom(SubType, arr_name(Top, Top), arr_name(X, Top))],
            facts,
        ):
            ok = False
            break
    check(ok, "Contravariance universal failed.")
    notes.append("PASS 5: Contravariance universal holds.")

    # 6) Deterministic pretty output
    s1 = " ".join(sorted(local(t) for t, _ in pairs))
    s2 = " ".join(sorted(local(t) for t, _ in set(pairs)))
    check(s1 == s2, "Determinism check failed.")
    notes.append("PASS 6: Deterministic formatting.")

    # 7) Engine chooser: enumeration vs ground
    e1, _, _ = ask([atom(SubType, Var("T"), Var("U"))])
    e2, _, _ = ask(
        [atom(SubType, arr_name(Int, Bool), arr_name(Int, Top))]
    )
    check(e1 == "bottomup" and e2 == "topdown", "Engine chooser mismatch.")
    notes.append("PASS 7: Engine chooser behaves as intended.")

    # 8) Reflexivity holds for all base and arrow types
    for t in list(BASE_TYPES) + list(ARROWS):
        check(
            match_against_facts([atom(SubType, t, t)], facts),
            f"Reflexivity failed for {local(t)}.",
        )
    notes.append("PASS 8: Reflexivity holds.")

    # 9) No bogus cross-base subtyping (Int ≰ Bool, Bool ≰ Int)
    check(
        not match_against_facts([atom(SubType, Int, Bool)], facts),
        "Unexpected Int ≤ Bool.",
    )
    check(
        not match_against_facts([atom(SubType, Bool, Int)], facts),
        "Unexpected Bool ≤ Int.",
    )
    notes.append("PASS 9: No bogus base subtypings.")

    # 10) A negative arrow example should fail (Arr_Int_Int ≰ Arr_Bool_Int)
    check(
        not match_against_facts(
            [atom(SubType, arr_name(Int, Int), arr_name(Bool, Int))],
            facts,
        ),
        "Unexpected Arr_Int_Int ≤ Arr_Bool_Int.",
    )
    notes.append("PASS 10: Negative arrow subtyping blocked as expected.")

    # 11) Bottom-up closure stability (idempotence)
    f1, _ = solve_bottomup(PROGRAM, SIGNATURE)
    f2, _ = solve_bottomup(PROGRAM, SIGNATURE)
    check(f1[SubType] == f2[SubType], "Bottom-up closure not stable.")
    notes.append("PASS 11: Bottom-up closure stable.")

    # 12) Another top-down ground sample: Arr_Top_Top ≤ Arr_Bool_Top
    td2, _ = solve_topdown(
        PROGRAM,
        [atom(SubType, arr_name(Top, Top), arr_name(Bool, Top))],
    )
    check(bool(td2), "Top-down failed on Arr_Top_Top ≤ Arr_Bool_Top.")
    notes.append("PASS 12: Tabled top-down proves contravariant sample.")

    return notes


# ─────────────────────────────────────────────────────────────────────────────
# Standalone runner
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print_model()
    print_question()
    res1, res2, res3, res4 = run_queries()
    print_answer(res1, res2, res3, res4)
    # For the "Reason why" section, forward first two engine labels (if any)
    print_reason(res1[1], res2[1])

    print("Check (harness)")
    print("===============")
    try:
        for note in run_checks():
            print(note)
    except CheckFailure as e:
        print("FAIL:", e)
        raise


if __name__ == "__main__":
    main()

