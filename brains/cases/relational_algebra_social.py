# -*- coding: utf-8 -*-
"""
Relational Algebra over Social Links (Union, Composition, Star)
in the Hayes–Menzel Style
---------------------------------------------------------------

We work with *relation names* (intensions) like

    ex:Follows, ex:Mentors, ex:Collaborates, ex:Knows, ...

and a **fixed** predicate:

    ex:holds2(R, x, y)

meaning “⟨x,y⟩ is in the extension of the relation-name R”.

We add meta-predicates over **names**:

    • ex:SubRelOf(P,Q)   — inclusion (P ⊆ Q)
    • ex:Union(P,Q,R)    — R = P ∪ Q
    • ex:Comp(P,Q,R)     — R = P ∘ Q (composition)
    • ex:Star(P,R)       — R = P⁺ (non-reflexive transitive closure, length ≥ 1)

Rules (schematic)
-----------------

1) leq_strict from SubRelOf, its transitive closure, and leq = reflexive ∪ leq_strict.

2) Lifting along inclusion of names:

       holds2(Q,x,y) :- holds2(P,x,y), leq_strict(P,Q).

3) Union populates the target:

       holds2(R,x,y) :- Union(P,Q,R), holds2(P,x,y).
       holds2(R,x,y) :- Union(P,Q,R), holds2(Q,x,y).

4) Composition populates its target:

       holds2(R,x,z) :- Comp(P,Q,R), holds2(P,x,y), holds2(Q,y,z).

5) Star (right-recursive, non-reflexive):

       holds2(R,x,y) :- Star(P,R), holds2(P,x,y).
       holds2(R,x,z) :- Star(P,R), holds2(P,x,y), holds2(R,y,z).

Why this case?
--------------

It stresses the engine on *several* higher-order constructors over relation
names, requires propagation through multiple meta-predicates, and mixes
top-down/tabled and bottom-up reasoning. We also quantify over relation
names in the queries.

How to run
----------

    python relational_algebra_social.py
"""

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Set, Tuple, Union
from collections import defaultdict, deque
import itertools
import inspect

# ╔══════════════════════════════════════════════════════════════════════╗
# ║ Embedded tiny logic engine                                           ║
# ╚══════════════════════════════════════════════════════════════════════╝

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


def fmt_pairs(pairs: Iterable[Tuple[str, str]]) -> str:
    seq = sorted(pairs)
    return "∅" if not seq else "{" + ", ".join(f"⟨{a},{b}⟩" for (a, b) in seq) + "}"


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


# ╔══════════════════════════════════════════════════════════════════════╗
# ║ Case: Relational algebra over social links                           ║
# ╚══════════════════════════════════════════════════════════════════════╝

from typing import List as _ListAlias, Tuple as _TupleAlias, Set as _SetAlias  # just to mirror original typings

# -------------------------
# Domain (individuals)
# -------------------------

D: _TupleAlias[str, ...] = (
    "Alice",
    "Bob",
    "Carol",
    "Dave",
    "Erin",
    "Frank",
)

# -------------------------
# Relation names (intensions)
# -------------------------

EX = "ex:"

Follows      = EX + "Follows"
Mentors      = EX + "Mentors"
Collaborates = EX + "Collaborates"
Knows        = EX + "Knows"      # intended: Follows ∪ Mentors ∪ Collaborates
TwoHop       = EX + "TwoHop"     # intended: Knows ∘ Knows
ReachK       = EX + "ReachK"     # intended: Knows⁺ (length ≥ 1)

# meta over names
SubRelOf  = EX + "SubRelOf"
Union     = EX + "Union"
Comp      = EX + "Comp"
Star      = EX + "Star"
LeqStrict = EX + "leq_strict"
Leq       = EX + "leq"

Holds2    = EX + "holds2"

# -------------------------------
# Predicate signature (NAME/IND)
# -------------------------------

SIGNATURE: Signature = {
    Holds2:    (NAME, IND, IND),
    SubRelOf:  (NAME, NAME),
    Union:     (NAME, NAME, NAME),
    Comp:      (NAME, NAME, NAME),
    Star:      (NAME, NAME),
    LeqStrict: (NAME, NAME),
    Leq:       (NAME, NAME),
}

# -----------------------------
# PROGRAM (facts + rules)
# -----------------------------

PROGRAM: List[Clause] = []

# >>> USER SECTION: FACTS over holds2 (base edges)

for a, b in [
    # social links (no cycles to keep ReachK non-reflexive unless via longer loops)
    ("Alice", "Bob"),
    ("Bob", "Carol"),
    ("Carol", "Dave"),
    ("Bob", "Dave"),
    ("Erin", "Frank"),
]:
    PROGRAM.append(fact(Holds2, Follows, a, b))

for a, b in [
    ("Alice", "Carol"),
    ("Dave", "Erin"),
]:
    PROGRAM.append(fact(Holds2, Mentors, a, b))

for a, b in [
    ("Carol", "Erin"),
    ("Bob", "Frank"),
]:
    PROGRAM.append(fact(Holds2, Collaborates, a, b))

# Inclusion hints (not strictly needed if Union is used, but good for leq-tests)
PROGRAM += [
    fact(SubRelOf, Follows, Knows),
    fact(SubRelOf, Mentors, Knows),
    fact(SubRelOf, Collaborates, Knows),
]

# Union and constructors over names
PROGRAM += [
    fact(Union, Follows, Mentors, Knows),     # Knows gets Follows ∪ Mentors
    fact(Union, Knows, Collaborates, Knows),  # Knows also absorbs Collaborates
    fact(Comp, Knows, Knows, TwoHop),         # TwoHop = Knows ∘ Knows
    fact(Star, Knows, ReachK),                # ReachK = Knows⁺
]

# >>> USER SECTION: RULES over names and application

# (1) Inclusion closure and leq

P, Q, R = Var("P"), Var("Q"), Var("R")
PROGRAM.append(Clause(atom(LeqStrict, P, Q), [atom(SubRelOf, P, Q)]))

P, Q, R = Var("P"), Var("Q"), Var("R")
PROGRAM.append(
    Clause(
        atom(LeqStrict, P, Q),
        [atom(SubRelOf, P, R), atom(LeqStrict, R, Q)],
    )
)

# leq reflexive (unsafe head; engine grounds NAME-domain)
P = Var("P")
PROGRAM.append(Clause(atom(Leq, P, P), []))

# leq includes leq_strict
P, Q = Var("P"), Var("Q")
PROGRAM.append(Clause(atom(Leq, P, Q), [atom(LeqStrict, P, Q)]))

# (2) Lifting along inclusion:
# Put data-producing goal first (bind P), then check inclusion to Q (goal-directed).
P, Q, X, Y = Var("P"), Var("Q"), Var("X"), Var("Y")
PROGRAM.append(
    Clause(
        atom(Holds2, Q, X, Y),
        [
            atom(Holds2, P, X, Y),
            atom(LeqStrict, P, Q),
        ],
    )
)

# (3) Union: both sides inject into R
P, Q, R, X, Y = Var("P"), Var("Q"), Var("R"), Var("X"), Var("Y")
PROGRAM.append(
    Clause(
        atom(Holds2, R, X, Y),
        [
            atom(Union, P, Q, R),
            atom(Holds2, P, X, Y),
        ],
    )
)

P, Q, R, X, Y = Var("P"), Var("Q"), Var("R"), Var("X"), Var("Y")
PROGRAM.append(
    Clause(
        atom(Holds2, R, X, Y),
        [
            atom(Union, P, Q, R),
            atom(Holds2, Q, X, Y),
        ],
    )
)

# (4) Composition: R = P ∘ Q
P, Q, R, X, Y, Z = Var("P"), Var("Q"), Var("R"), Var("X"), Var("Y"), Var("Z")
PROGRAM.append(
    Clause(
        atom(Holds2, R, X, Z),
        [
            atom(Comp, P, Q, R),
            atom(Holds2, P, X, Y),
            atom(Holds2, Q, Y, Z),
        ],
    )
)

# (5) Star (non-reflexive, right-recursive)
P, R, X, Y, Z = Var("P"), Var("R"), Var("X"), Var("Y"), Var("Z")
PROGRAM.append(
    Clause(
        atom(Holds2, R, X, Y),
        [
            atom(Star, P, R),
            atom(Holds2, P, X, Y),
        ],
    )
)

P, R, X, Y, Z = Var("P"), Var("R"), Var("X"), Var("Y"), Var("Z")
PROGRAM.append(
    Clause(
        atom(Holds2, R, X, Z),
        [
            atom(Star, P, R),
            atom(Holds2, P, X, Y),
            atom(Holds2, R, Y, Z),
        ],
    )
)

# -------------------------
# Case-specific engine glue
# -------------------------

def _is_var(t) -> bool:
    return isinstance(t, Var)


def choose_engine(goals: List[Atom]) -> str:
    """
    Heuristic:
      - Enumerations over TwoHop/ReachK → bottom-up
      - Fully unbound conjuncts        → bottom-up
      - Otherwise                      → top-down (tabled)
    """
    for g in goals:
        if (
            g.pred == Holds2
            and len(g.args) == 3
            and g.args[0] in (TwoHop, ReachK)
            and (_is_var(g.args[1]) or _is_var(g.args[2]))
        ):
            return "bottomup"
        if all(_is_var(t) for t in g.args):
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


# -------------------------
# Presentation (printing)
# -------------------------

def print_model() -> None:
    print("Model")
    print("=====")
    print(f"Individuals D = {list(D)}\n")

    print("Fixed predicates (signature)")
    print("----------------------------")
    print("• ex:holds2(R,x,y) — application (⟨x,y⟩ ∈ ext(R)); sorts: (NAME, IND, IND)")
    print("• ex:SubRelOf(P,Q), ex:Union(P,Q,R), ex:Comp(P,Q,R), ex:Star(P,R)")
    print("• ex:leq_strict / ex:leq — ⊆* with/without reflex on names; sorts: (NAME, NAME)\n")

    print("Named relations (with facts)")
    print("----------------------------")
    print("Follows      =",
          fmt_pairs([("Alice", "Bob"),
                     ("Bob", "Carol"),
                     ("Carol", "Dave"),
                     ("Bob", "Dave"),
                     ("Erin", "Frank")]))
    print("Mentors      =",
          fmt_pairs([("Alice", "Carol"),
                     ("Dave", "Erin")]))
    print("Collaborates =",
          fmt_pairs([("Carol", "Erin"),
                     ("Bob", "Frank")]))
    print("Knows   = derived; intended Follows ∪ Mentors ∪ Collaborates")
    print("TwoHop  = derived; intended Knows ∘ Knows")
    print("ReachK  = derived; intended Knows⁺ (length ≥ 1)\n")

    print("Inclusions over names:")
    print("  Follows ⊆ Knows, Mentors ⊆ Knows, Collaborates ⊆ Knows")
    print("Constructors over names:")
    print("  Union(Follows,Mentors,Knows), Union(Knows,Collaborates,Knows),")
    print("  Comp(Knows,Knows,TwoHop), Star(Knows,ReachK)\n")


def print_question() -> None:
    print("Question")
    print("========")
    print("Q1) List all (X,Y) with holds2(TwoHop,X,Y). [auto engine]")
    print("Q2) ∃R: Comp(Knows,Knows,R) ∧ holds2(R,Alice,Dave) ? "
          "(witness relation-names) [auto engine]")
    print("Q3) ∀R,y: (leq(R,Knows) ∧ holds2(R,Alice,y)) → holds2(ReachK,Alice,y) ? "
          "[auto engine]")
    print()


def run_queries():
    # Q1: enumerate TwoHop pairs
    Xv, Yv = Var("X"), Var("Y")
    eng1, sols1, m1 = ask([atom(Holds2, TwoHop, Xv, Yv)])
    pairs = sorted({(deref(Xv, s), deref(Yv, s)) for s in sols1})  # type: ignore

    # Q2: witness relation-names R for (Alice, Dave) under Comp(Knows,Knows,R)
    Rv = Var("R")
    eng2, sols2, m2 = ask([
        atom(Comp, Knows, Knows, Rv),
        atom(Holds2, Rv, "Alice", "Dave"),
    ])
    witnesses = sorted({
        deref(Rv, s) for s in sols2
        if isinstance(deref(Rv, s), str)
    })

    # Q3: universal property
    ok = True
    for R in [Follows, Mentors, Collaborates, Knows, TwoHop]:
        for y in D:
            cond = ask([
                atom(Leq, R, Knows),
                atom(Holds2, R, "Alice", y),
            ])[1]
            if cond and not ask([atom(Holds2, ReachK, "Alice", y)])[1]:
                ok = False
                break
        if not ok:
            break

    return (
        ("Q1", eng1, pairs, m1),
        ("Q2", eng2, witnesses, m2),
        ("Q3", "mixed", ok, 0),
    )


def print_answer(res1, res2, res3) -> None:
    print("Answer")
    print("======")
    tag1, eng1, pairs, _ = res1
    tag2, eng2, wits, _ = res2
    tag3, eng3, ok, _ = res3

    print(f"{tag1}) Engine: {eng1} → TwoHop = {fmt_pairs(pairs)}")
    print(f"{tag2}) Engine: {eng2} → Witness relation-names R = "
          + (fmt_set(wits) if wits else "∅"))
    print(f"{tag3}) Engine: {eng3} → Universal statement holds: "
          f"{'Yes' if ok else 'No'}\n")


def print_reason(eng1, eng2) -> None:
    print("Reason why")
    print("==========")
    print("• Knows is both the union of base links and a superrelation via SubRelOf;")
    print("  lifting moves base facts upward. Comp(Knows,Knows,TwoHop) materializes")
    print("  2-hop links.")
    print("• Star(Knows,ReachK) closes paths of length ≥ 1 (non-reflexive).")
    print("• Queries quantify over relation names (e.g., ∃R with Comp(Knows,Knows,R)).")
    print("• Auto-chooser: big TwoHop/ReachK enumerations → bottom-up; targeted ground")
    print("  checks → tabled top-down.\n")


# -------------------
# Check (12 tests)
# -------------------

class CheckFailure(AssertionError):
    pass


def check(c: bool, msg: str):
    if not c:
        raise CheckFailure(msg)


def run_checks() -> List[str]:
    notes: List[str] = []

    # Expected TwoHop (compute procedurally for the small model)
    base = {
        (Follows, "Alice", "Bob"),
        (Follows, "Bob", "Carol"),
        (Follows, "Carol", "Dave"),
        (Follows, "Bob", "Dave"),
        (Follows, "Erin", "Frank"),
        (Mentors, "Alice", "Carol"),
        (Mentors, "Dave", "Erin"),
        (Collaborates, "Carol", "Erin"),
        (Collaborates, "Bob", "Frank"),
    }

    knows = {(x, y) for (r, x, y) in base
             if r in (Follows, Mentors, Collaborates)}

    # Build TwoHop procedurally from Knows ∘ Knows
    def comp2(pairs):
        idx = {}
        for (x, y) in pairs:
            idx.setdefault(x, set()).add(y)
        out = set()
        for (x, y) in pairs:
            for z in idx.get(y, ()):
                out.add((x, z))
        return out

    exp_twohop = comp2(knows)

    # 1) Bottom-up TwoHop
    facts, _ = solve_bottomup(PROGRAM, SIGNATURE)
    X, Y = Var("X"), Var("Y")
    bu = match_against_facts([atom(Holds2, TwoHop, X, Y)], facts)
    twohop_bu = {(deref(X, s), deref(Y, s)) for s in bu}
    check(twohop_bu == exp_twohop, "Bottom-up TwoHop enumeration mismatch.")
    notes.append("PASS 1: Bottom-up TwoHop enumeration is correct.")

    # 2) Tabled top-down TwoHop
    td, _ = solve_topdown(PROGRAM, [atom(Holds2, TwoHop, X, Y)])
    twohop_td = {(deref(X, s), deref(Y, s)) for s in td}
    check(twohop_td == exp_twohop, "Top-down TwoHop enumeration mismatch.")
    notes.append("PASS 2: Tabled top-down TwoHop enumeration is correct.")

    # 3) ∃R witness for Alice→Dave under Comp(Knows,Knows,R) is exactly {TwoHop}
    R = Var("R")
    bu_w = match_against_facts(
        [atom(Comp, Knows, Knows, R),
         atom(Holds2, R, "Alice", "Dave")],
        facts,
    )
    td_w, _ = solve_topdown(
        PROGRAM,
        [atom(Comp, Knows, Knows, R),
         atom(Holds2, R, "Alice", "Dave")],
    )
    w1 = {deref(R, s) for s in bu_w}
    w2 = {deref(R, s) for s in td_w}
    check(w1 == w2 == {TwoHop},
          f"Witness set mismatch: {w1} vs {w2}")
    notes.append(
        "PASS 3: Witness set for Alice→Dave under composition is {TwoHop}."
    )

    # 4) Universal: if R ≤ Knows and R(Alice,y) then ReachK(Alice,y)
    ok = True
    for r in [Follows, Mentors, Collaborates, Knows, TwoHop]:
        for y in D:
            cond = ask([
                atom(Leq, r, Knows),
                atom(Holds2, r, "Alice", y),
            ])[1]
            if cond and not ask([atom(Holds2, ReachK, "Alice", y)])[1]:
                ok = False
                break
        if not ok:
            break
    check(ok, "Universal property failed.")
    notes.append("PASS 4: Universal property holds.")

    # 5) TwoHop has no reflexives in this acyclic dataset
    for v in D:
        check(
            not ask([atom(Holds2, TwoHop, v, v)])[1],
            f"Unexpected TwoHop reflexive at {v}.",
        )
    notes.append("PASS 5: TwoHop is non-reflexive here.")

    # 6) ReachK non-reflexive unless cycles exist (none here)
    for v in D:
        check(
            not ask([atom(Holds2, ReachK, v, v)])[1],
            f"Unexpected ReachK reflexive at {v}.",
        )
    notes.append("PASS 6: ReachK is non-reflexive here.")

    # 7) Engine chooser behavior
    e1, _, _ = ask([atom(Holds2, TwoHop, Var("X"), Var("Y"))])          # big enumeration
    e2, _, _ = ask([atom(Holds2, TwoHop, "Alice", "Dave")])            # ground check
    check(e1 == "bottomup" and e2 == "topdown", "Engine chooser mismatch.")
    notes.append("PASS 7: Engine chooser behaves as intended.")

    # 8) leq reflexive on names
    for r in [Follows, Mentors, Collaborates, Knows, TwoHop, ReachK]:
        check(
            ask([atom(Leq, r, r)])[1],
            f"Reflexivity of leq failed for {local(r)}.",
        )
    notes.append("PASS 8: leq reflexivity holds for all relation names.")

    # 9) Inclusion basics: base relations are ≤ Knows
    for r in [Follows, Mentors, Collaborates]:
        check(
            ask([atom(LeqStrict, r, Knows)])[1],
            f"leq_strict {local(r)} ⊆ Knows failed.",
        )
    notes.append("PASS 9: leq_strict inclusions hold.")

    # 10) Composition really yields a 2-hop edge: Alice→Dave ∈ TwoHop
    check(
        ask([atom(Holds2, TwoHop, "Alice", "Dave")])[1],
        "Expected Alice→Dave in TwoHop.",
    )
    notes.append("PASS 10: TwoHop contains Alice→Dave.")

    # 11) Bottom-up closure idempotence
    f1, _ = solve_bottomup(PROGRAM, SIGNATURE)
    f2, _ = solve_bottomup(PROGRAM, SIGNATURE)
    check(
        f1[Holds2] == f2[Holds2],
        "Bottom-up closure not idempotent.",
    )
    notes.append("PASS 11: Bottom-up closure is stable.")

    # 12) Deterministic printing
    s1 = fmt_pairs(sorted(exp_twohop))
    s2 = fmt_pairs(sorted(list(exp_twohop)))
    check(s1 == s2, "Pretty-printer determinism failed.")
    notes.append("PASS 12: Pretty printing deterministic.")

    return notes


# -------------------
# Standalone runner
# -------------------

def main():
    print_model()
    print_question()
    res1, res2, res3 = run_queries()
    print_answer(res1, res2, res3)
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

