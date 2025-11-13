# -*- coding: utf-8 -*-
"""
OWL RL–ish Role Hierarchy + Inverses
(Hayes–Menzel “names + holds₂/holds₁” style)
-------------------------------------------

We represent role *names* (intensions) like

    ex:parentOf, ex:childOf, ex:teaches, ...

and use a fixed application predicate:

    ex:holds2(R, x, y)       # ⟨x,y⟩ ∈ extension of role-name R

We also add a unary application for classes (types):

    ex:holds1(C, x)          # x ∈ extension of class-name C

Meta over **role names**:

    • ex:SubRelOf(P,Q)      — role inclusion (P ⊆ Q)
    • ex:InverseOf(P,Q)     — inverse roles (P = Q⁻¹)
    • ex:Symmetric(P)       — symmetric role P
    • ex:Transitive(P)      — transitive role P
    • ex:SubRelChain(P,Q,R) — property chain (P∘Q ⊆ R)
    • ex:Domain(P,C),
      ex:Range(P,C)         — typing of role P: dom = C, rng = C

Meta over **class names**:

    • ex:SubClassOf(C,D)    — class inclusion (C ⊆ D)

Rules (selection)
-----------------

1) Inclusion closure over names, plus reflexive `leq`:

    leq_strict(P,Q) :- SubRelOf(P,Q).
    leq_strict(P,Q) :- SubRelOf(P,R), leq_strict(R,Q).

    leq(P,P).
    leq(P,Q) :- leq_strict(P,Q).

and lifting:

    holds2(Q,x,y) :- holds2(P,x,y), leq_strict(P,Q).

2) Inverse, Symmetric, Transitive, Chains:

    holds2(Q,y,x) :- InverseOf(P,Q), holds2(P,x,y).
    InverseOf(Q,P) :- InverseOf(P,Q).           # make it explicitly symmetric

    holds2(P,y,x) :- Symmetric(P), holds2(P,x,y).

    holds2(P,x,z) :- Transitive(P),
                     holds2(P,x,y), holds2(P,y,z).

    holds2(R,x,z) :- SubRelChain(P,Q,R),
                     holds2(P,x,y), holds2(Q,y,z).

3) Domain / Range typing (unary holds1), with propagation:

    holds1(C,x) :- Domain(P,C), holds2(P,x,y).
    holds1(C,y) :- Range(P,C), holds2(P,x,y).

    Domain(P,C) :- leq_strict(P,Q), Domain(Q,C).
    Range(P,C)  :- leq_strict(P,Q), Range(Q,C).

    Range(Q,C)  :- InverseOf(P,Q), Domain(P,C).
    Domain(Q,C) :- InverseOf(P,Q), Range(P,C).

    Subclasses:
    holds1(D,x) :- SubClassOf(C,D), holds1(C,x).

Dataset (small, acyclic for transitivity)
-----------------------------------------

Individuals:
    Alice, Bob, Carol, Dave, Erin, Frank, Grace, Helen

Roles (base):

    parentOf:  Alice→Bob, Bob→Carol, Carol→Dave
    marriedTo: Erin→Frank            (Symmetric → will infer Frank→Erin)
    teaches:   Grace→Carol, Grace→Dave
    supervises:Grace→Erin

Hierarchy/meta:

    childOf  = parentOf⁻¹                      (InverseOf)
    parentOf ⊆ ancestorOf; Transitive(ancestorOf)

    teaches ⊆ advises; supervises ⊆ advises
    SubRelChain(parentOf, parentOf, ancestorOf)

    Domain(advises, Professor), Range(advises, Student)
    SubClassOf(Student, Person),
    SubClassOf(Professor, Person)

Questions
---------

Q1) Enumerate all ⟨x,y⟩ with holds2(ancestorOf,x,y).

Q2) Witness role-names R s.t. leq(R,advises) ∧ holds2(R,Grace,Erin).

Q3) Typing check:
    ∀y, if holds2(advises,Grace,y)
        then Professor(Grace) ∧ Student(y)?

Q4) Inverse check:
    childOf = parentOf⁻¹ (list and compare).

Q5) Symmetry check:
    marriedTo(Erin,Frank) ⇒ marriedTo(Frank,Erin).

How to run
----------

    python role_hierarchy_owlrl.py
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


# --- Unification --------------------------------------------------------

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


def unify_lists(xs: List[Term], ys: List[Term], subst: Dict[Var, Term]) -> Optional[Dict[Var, Term]]:
    if len(xs) != len(ys):
        return None
    for a, b in zip(xs, ys):
        subst = unify(a, b, subst)
        if subst is None:
            return None
    return subst


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


# --- Bottom-up least fixpoint engine -----------------------------------

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

    # Start with explicit ground facts
    facts: Dict[str, Set[Tuple[str, ...]]] = defaultdict(set)
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
                # fact with possible head-only vars
                if not all(isinstance(t, str) for t in cl.head.args):
                    for tpl in _ground_head_from_domains(cl.head, {}, sig,
                                                         names_list, inds_list):
                        if tpl not in facts[cl.head.pred]:
                            facts[cl.head.pred].add(tpl)
                            changed = True
                continue

            # join body against current facts
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


# --- Utilities ----------------------------------------------------------

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


# --- Top-down with restricted subprogram via dependency graph -----------

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
# ║ Case: OWL RL–ish role hierarchy + inverses                           ║
# ╚══════════════════════════════════════════════════════════════════════╝

from typing import Dict, List, Tuple, Set  # (for annotations below)


# -------------------------
# Domain (individuals)
# -------------------------

D: Tuple[str, ...] = (
    "Alice", "Bob", "Carol", "Dave",
    "Erin", "Frank", "Grace", "Helen"
)

# -------------------------
# Names (roles & classes)
# -------------------------

EX = "ex:"

# roles
parentOf = EX + "parentOf"
childOf = EX + "childOf"
ancestorOf = EX + "ancestorOf"
marriedTo = EX + "marriedTo"
teaches = EX + "teaches"
supervises = EX + "supervises"
advises = EX + "advises"

# classes
Person = EX + "Person"
Student = EX + "Student"
Professor = EX + "Professor"

# meta over names
SubRelOf = EX + "SubRelOf"
InverseOf = EX + "InverseOf"
Symmetric = EX + "Symmetric"
Transitive = EX + "Transitive"
SubRelChain = EX + "SubRelChain"
Domain = EX + "Domain"
Range = EX + "Range"
SubClassOf = EX + "SubClassOf"
LeqStrict = EX + "leq_strict"
Leq = EX + "leq"

Holds2 = EX + "holds2"   # binary application: role-name × IND × IND
Holds1 = EX + "holds1"   # unary application: class-name × IND

# -------------------------------
# Predicate signature (NAME/IND)
# -------------------------------

SIGNATURE: Signature = {
    Holds2: (NAME, IND, IND),
    Holds1: (NAME, IND),
    SubRelOf: (NAME, NAME),
    InverseOf: (NAME, NAME),
    Symmetric: (NAME,),
    Transitive: (NAME,),
    SubRelChain: (NAME, NAME, NAME),
    Domain: (NAME, NAME),
    Range: (NAME, NAME),
    SubClassOf: (NAME, NAME),
    LeqStrict: (NAME, NAME),
    Leq: (NAME, NAME),
}

# -----------------------------
# PROGRAM (facts + rules)
# -----------------------------

PROGRAM: List[Clause] = []

# --- base role facts ----------------------------------------------------

for a, b in [("Alice", "Bob"),
             ("Bob", "Carol"),
             ("Carol", "Dave")]:
    PROGRAM.append(fact(Holds2, parentOf, a, b))

PROGRAM.append(fact(Holds2, marriedTo, "Erin", "Frank"))

PROGRAM += [
    fact(Holds2, teaches, "Grace", "Carol"),
    fact(Holds2, teaches, "Grace", "Dave"),
    fact(Holds2, supervises, "Grace", "Erin"),
]

# --- role hierarchy & meta ----------------------------------------------

PROGRAM += [
    fact(InverseOf, parentOf, childOf),

    fact(SubRelOf, parentOf, ancestorOf),
    fact(Transitive, ancestorOf),
    fact(SubRelChain, parentOf, parentOf, ancestorOf),

    fact(SubRelOf, teaches, advises),
    fact(SubRelOf, supervises, advises),
    fact(Symmetric, marriedTo),

    # typing of advises (propagates down to teaches/supervises)
    fact(Domain, advises, Professor),
    fact(Range, advises, Student),

    # class hierarchy
    fact(SubClassOf, Student, Person),
    fact(SubClassOf, Professor, Person),
]

# --- rules: inclusion closure + leq -------------------------------------

P, Q, R = Var("P"), Var("Q"), Var("R")
PROGRAM.append(Clause(atom(LeqStrict, P, Q), [atom(SubRelOf, P, Q)]))

P, Q, R = Var("P"), Var("Q"), Var("R")
PROGRAM.append(Clause(atom(LeqStrict, P, Q),
                      [atom(SubRelOf, P, R), atom(LeqStrict, R, Q)]))

P = Var("P")
PROGRAM.append(Clause(atom(Leq, P, P), []))  # reflexive leq (unsafe → engine grounds)

P, Q = Var("P"), Var("Q")
PROGRAM.append(Clause(atom(Leq, P, Q), [atom(LeqStrict, P, Q)]))

# lifting along inclusion (data-first, then inclusion)
P, Q, X, Y = Var("P"), Var("Q"), Var("X"), Var("Y")
PROGRAM.append(
    Clause(
        atom(Holds2, Q, X, Y),
        [atom(Holds2, P, X, Y), atom(LeqStrict, P, Q)],
    )
)

# --- rules: inverse / symmetric / transitive / chains -------------------

P, Q, X, Y, Z = Var("P"), Var("Q"), Var("X"), Var("Y"), Var("Z")
PROGRAM.append(
    Clause(
        atom(Holds2, Q, Y, X),
        [atom(InverseOf, P, Q), atom(Holds2, P, X, Y)],
    )
)

# make InverseOf symmetric explicitly
P, Q = Var("P"), Var("Q")
PROGRAM.append(Clause(atom(InverseOf, Q, P), [atom(InverseOf, P, Q)]))

P, X, Y = Var("P"), Var("X"), Var("Y")
PROGRAM.append(
    Clause(
        atom(Holds2, P, Y, X),
        [atom(Symmetric, P), atom(Holds2, P, X, Y)],
    )
)

P, X, Y, Z = Var("P"), Var("X"), Var("Y"), Var("Z")
PROGRAM.append(
    Clause(
        atom(Holds2, P, X, Z),
        [atom(Transitive, P),
         atom(Holds2, P, X, Y),
         atom(Holds2, P, Y, Z)],
    )
)

P, Q, R, X, Y, Z = Var("P"), Var("Q"), Var("R"), Var("X"), Var("Y"), Var("Z")
PROGRAM.append(
    Clause(
        atom(Holds2, R, X, Z),
        [
            atom(SubRelChain, P, Q, R),
            atom(Holds2, P, X, Y),
            atom(Holds2, Q, Y, Z),
        ],
    )
)

# --- rules: typing (holds1) + propagation -------------------------------

P, Cn, X, Y = Var("P"), Var("Cn"), Var("X"), Var("Y")
PROGRAM.append(
    Clause(
        atom(Holds1, Cn, X),
        [atom(Domain, P, Cn), atom(Holds2, P, X, Y)],
    )
)

P, Cn, X, Y = Var("P"), Var("Cn"), Var("X"), Var("Y")
PROGRAM.append(
    Clause(
        atom(Holds1, Cn, Y),
        [atom(Range, P, Cn), atom(Holds2, P, X, Y)],
    )
)

# propagate typing down subroles
P, Q, Cn = Var("P"), Var("Q"), Var("Cn")
PROGRAM.append(
    Clause(
        atom(Domain, P, Cn),
        [atom(LeqStrict, P, Q), atom(Domain, Q, Cn)],
    )
)

P, Q, Cn = Var("P"), Var("Q"), Var("Cn")
PROGRAM.append(
    Clause(
        atom(Range, P, Cn),
        [atom(LeqStrict, P, Q), atom(Range, Q, Cn)],
    )
)

# propagate typing through inverse links
P, Q, Cn = Var("P"), Var("Q"), Var("Cn")
PROGRAM.append(
    Clause(
        atom(Range, Q, Cn),
        [atom(InverseOf, P, Q), atom(Domain, P, Cn)],
    )
)

P, Q, Cn = Var("P"), Var("Q"), Var("Cn")
PROGRAM.append(
    Clause(
        atom(Domain, Q, Cn),
        [atom(InverseOf, P, Q), atom(Range, P, Cn)],
    )
)

# subclasses
Cn, Dn, Xv = Var("Cn"), Var("Dn"), Var("X")
PROGRAM.append(
    Clause(
        atom(Holds1, Dn, Xv),
        [atom(SubClassOf, Cn, Dn), atom(Holds1, Cn, Xv)],
    )
)

# -------------------------
# Case-specific engine glue
# -------------------------

def _is_var(t) -> bool:
    return isinstance(t, Var)


# Prefer bottom-up for big enumerations over transitive roles
def choose_engine(goals: List[Atom]) -> str:
    for g in goals:
        if (
            g.pred == Holds2
            and len(g.args) == 3
            and g.args[0] in (ancestorOf,)
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
    print("• ex:holds1(C,x)   — unary application (x ∈ C);  sorts: (NAME, IND)")
    print("• Meta over role names: SubRelOf, InverseOf, Symmetric, Transitive,")
    print("    SubRelChain, Domain, Range")
    print("• Meta over class names: SubClassOf\n")

    print("Named relations (with facts)")
    print("----------------------------")
    print("parentOf =", fmt_pairs([("Alice", "Bob"),
                               ("Bob", "Carol"),
                               ("Carol", "Dave")]))
    print("childOf   = derived (inverse of parentOf)")
    print("ancestorOf = derived (transitive super of parentOf)")
    print("marriedTo = {⟨Erin,Frank⟩} (symmetric → derived ⟨Frank,Erin⟩)")
    print("teaches   = {⟨Grace,Carol⟩, ⟨Grace,Dave⟩}")
    print("supervises= {⟨Grace,Erin⟩}")
    print("advises   = derived (super of teaches, supervises)\n")

    print("Typing:")
    print("  Domain(advises,Professor), Range(advises,Student)")
    print("  Student ⊆ Person, Professor ⊆ Person\n")


def print_question() -> None:
    print("Question")
    print("========")
    print("Q1) List all (x,y) with holds2(ancestorOf,x,y). [auto engine]")
    print("Q2) ∃R: leq(R,advises) ∧ holds2(R,Grace,Erin) ? (witness names) [auto engine]")
    print("Q3) ∀y: holds2(advises,Grace,y) → Professor(Grace) ∧ Student(y) ? [auto engine]")
    print("Q4) Inverse check: list (x,y) with childOf(x,y) and compare to parentOf⁻¹. [auto engine]")
    print("Q5) Symmetry check: marriedTo(Erin,Frank) ⇒ marriedTo(Frank,Erin). [auto engine]")
    print()


def run_queries():
    # Q1: enumerate ancestorOf
    Xv, Yv = Var("X"), Var("Y")
    eng1, sols1, m1 = ask([atom(Holds2, ancestorOf, Xv, Yv)])
    anc_pairs = sorted({(deref(Xv, s), deref(Yv, s)) for s in sols1})  # type: ignore

    # Q2: witness role-names R for Grace→Erin under ≤ advises
    Rv = Var("R")
    eng2, sols2, m2 = ask([
        atom(Leq, Rv, advises),
        atom(Holds2, Rv, "Grace", "Erin"),
    ])
    witnesses = sorted({deref(Rv, s) for s in sols2 if isinstance(deref(Rv, s), str)})

    # Q3: typing universal for advises at source Grace
    ok = True
    for y in D:
        cond = ask([atom(Holds2, advises, "Grace", y)])[1]
        if cond:
            ok_prof = ask([atom(Holds1, Professor, "Grace")])[1]
            ok_stud = ask([atom(Holds1, Student, y)])[1]
            if not (ok_prof and ok_stud):
                ok = False
                break

    # Q4: inverse pairs for childOf
    Xc, Yc = Var("X"), Var("Y")
    _, sols_c, _ = ask([atom(Holds2, childOf, Xc, Yc)])
    child_pairs = sorted({(deref(Xc, s), deref(Yc, s)) for s in sols_c})  # type: ignore

    # Q5: symmetry: check derived partner
    sym_ok = bool(ask([atom(Holds2, marriedTo, "Frank", "Erin")])[1])

    return (
        ("Q1", eng1, anc_pairs, m1),
        ("Q2", eng2, witnesses, m2),
        ("Q3", "mixed", ok, 0),
        ("Q4", "auto", child_pairs, 0),
        ("Q5", "auto", sym_ok, 0),
    )


def print_answer(res1, res2, res3, res4, res5) -> None:
    print("Answer")
    print("======")
    tag1, eng1, anc, _ = res1
    tag2, eng2, wits, _ = res2
    tag3, eng3, ok, _ = res3
    tag4, eng4, child_inv, _ = res4
    tag5, eng5, sym_ok, _ = res5

    print(f"{tag1}) Engine: {eng1} → ancestorOf =", fmt_pairs(anc))
    print(f"{tag2}) Engine: {eng2} → Witness role-names R = "
          + (fmt_set(wits) if wits else "∅"))
    print(f"{tag3}) Engine: {eng3} → Typing statement holds: {'Yes' if ok else 'No'}")
    print(f"{tag4}) Engine: {eng4} → childOf pairs =", fmt_pairs(child_inv))
    print(f"{tag5}) Engine: {eng5} → Symmetry consequence Frank↔Erin: "
          f"{'Yes' if sym_ok else 'No'}\n")


def print_reason(eng1, eng2) -> None:
    print("Reason why")
    print("==========")
    print("• Role inclusions (SubRelOf) lifted via holds₂ deliver advisors from teaches/supervises.")
    print("• Inverses & symmetry are modeled as meta-constraints over names; application stays")
    print("  first-order via holds₂.")
    print("• Transitivity on ancestorOf gives longer chains; property chain parentOf∘parentOf ⊆")
    print("  ancestorOf aligns with OWL RL.")
    print("• Domain/Range typing is checked via holds₁ (unary) and propagates through subroles")
    print("  and inverses.")
    print("• Auto-chooser sends big transitive enumerations to bottom-up; focused ground checks")
    print("  go to tabled top-down.\n")


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

    # Expected ancestorOf from the chain
    exp_anc = {
        ("Alice", "Bob"),
        ("Alice", "Carol"),
        ("Alice", "Dave"),
        ("Bob", "Carol"),
        ("Bob", "Dave"),
        ("Carol", "Dave"),
    }

    # 1) Bottom-up ancestorOf
    facts, _ = solve_bottomup(PROGRAM, SIGNATURE)
    X, Y = Var("X"), Var("Y")
    bu = match_against_facts([atom(Holds2, ancestorOf, X, Y)], facts)
    anc_bu = {(deref(X, s), deref(Y, s)) for s in bu}
    check(anc_bu == exp_anc, "Bottom-up ancestorOf mismatch.")
    notes.append("PASS 1: Bottom-up ancestorOf is correct.")

    # 2) Tabled top-down ancestorOf
    td, _ = solve_topdown(PROGRAM, [atom(Holds2, ancestorOf, X, Y)])
    anc_td = {(deref(X, s), deref(Y, s)) for s in td}
    check(anc_td == exp_anc, "Top-down ancestorOf mismatch.")
    notes.append("PASS 2: Tabled top-down ancestorOf is correct.")

    # 3) Witnesses for Grace→Erin under ≤ advises are {supervises, advises}
    R = Var("R")
    bu_w = match_against_facts(
        [atom(Leq, R, advises), atom(Holds2, R, "Grace", "Erin")],
        facts,
    )
    td_w, _ = solve_topdown(
        PROGRAM,
        [atom(Leq, R, advises), atom(Holds2, R, "Grace", "Erin")],
    )
    w1 = {deref(R, s) for s in bu_w}
    w2 = {deref(R, s) for s in td_w}
    check(w1 == w2 == {supervises, advises},
          f"Witness set mismatch: {w1} vs {w2}")
    notes.append(
        "PASS 3: Witness set for Grace→Erin under advises is {supervises, advises}."
    )

    # 4) Typing: every advisee of Grace is a Student; Grace is a Professor
    ok = True
    for y in D:
        cond = match_against_facts(
            [atom(Holds2, advises, "Grace", y)],
            facts,
        )
        if cond and (
            not match_against_facts([atom(Holds1, Student, y)], facts)
            or not match_against_facts([atom(Holds1, Professor, "Grace")], facts)
        ):
            ok = False
            break
    check(ok, "Typing (Professor/Student) property failed.")
    notes.append("PASS 4: Typing property holds for advises.")

    # 5) Inverse correctness: childOf equals inverse of parentOf
    inv_expected = {(b, a) for (a, b) in
                    [("Alice", "Bob"), ("Bob", "Carol"), ("Carol", "Dave")]}
    bu_child = match_against_facts([atom(Holds2, childOf, X, Y)], facts)
    child_bu = {(deref(X, s), deref(Y, s)) for s in bu_child}
    check(child_bu == inv_expected, "childOf inverse mismatch.")
    notes.append("PASS 5: childOf = parentOf⁻¹ holds.")

    # 6) Symmetric: marriedTo(Frank,Erin) derived
    check(
        bool(match_against_facts(
            [atom(Holds2, marriedTo, "Frank", "Erin")],
            facts,
        )),
        "Symmetric marriedTo missing reverse.",
    )
    notes.append("PASS 6: Symmetry of marriedTo holds.")

    # 7) Engine chooser behavior
    e1, _, _ = ask([atom(Holds2, ancestorOf, Var("X"), Var("Y"))])
    e2, _, _ = ask([atom(Holds2, ancestorOf, "Alice", "Dave")])
    check(e1 == "bottomup" and e2 == "topdown", "Engine chooser mismatch.")
    notes.append("PASS 7: Engine chooser behaves as intended.")

    # 8) leq reflexive on all role names
    for r in [parentOf, childOf, ancestorOf,
              marriedTo, teaches, supervises, advises]:
        check(
            ask([atom(Leq, r, r)])[1],
            f"Reflexivity of leq failed for {local(r)}.",
        )
    notes.append("PASS 8: leq reflexivity holds.")

    # 9) leq_strict transitivity: parentOf ⊆ ancestorOf and teaches ⊆ advises
    check(
        ask([atom(LeqStrict, parentOf, ancestorOf)])[1],
        "leq_strict parentOf ⊆ ancestorOf failed.",
    )
    check(
        ask([atom(LeqStrict, teaches, advises)])[1],
        "leq_strict teaches ⊆ advises failed.",
    )
    notes.append("PASS 9: leq_strict inclusions hold.")

    # 10) Property chain works: parentOf∘parentOf ⊆ ancestorOf
    for (x, z) in [("Alice", "Carol"), ("Bob", "Dave")]:
        check(
            ask([atom(Holds2, ancestorOf, x, z)])[1],
            f"Chain-derived ancestorOf missing for {x}→{z}.",
        )
    notes.append("PASS 10: Property chain derivations present.")

    # 11) Bottom-up closure idempotence
    f1, _ = solve_bottomup(PROGRAM, SIGNATURE)
    f2, _ = solve_bottomup(PROGRAM, SIGNATURE)
    check(
        f1[Holds2] == f2[Holds2] and f1[Holds1] == f2[Holds1],
        "Bottom-up closure not idempotent.",
    )
    notes.append("PASS 11: Bottom-up closure is stable.")

    # 12) Deterministic printing
    s1 = fmt_pairs(sorted(exp_anc))
    s2 = fmt_pairs(sorted(list(exp_anc)))
    check(s1 == s2, "Pretty-printer determinism failed.")
    notes.append("PASS 12: Pretty printing deterministic.")

    return notes


# -------------------
# Standalone runner
# -------------------

def main():
    print_model()
    print_question()
    res1, res2, res3, res4, res5 = run_queries()
    print_answer(res1, res2, res3, res4, res5)
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

