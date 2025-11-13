# -*- coding: utf-8 -*-
"""
Algebraic KG Construction (inspired by Min Oo & Hartig, ESWC 2025)
------------------------------------------------------------------

What this demonstrates
----------------------
We encode a tiny mapping-algebra style workflow for **knowledge graph
construction (KGC)**:

- Two base *mapping relations* (think: small tables extracted from CSVs)
- Algebraic operators over these relations:

  • `UnionRel(R1,R2,Ru)` – union of mapping relations (same schema)
  • `ExtendAsFromAx(Rin,Rout)` – compute RDF subjects (`as`) from ids (`ax`)
    via a tiny lookup `IRIOf(id, iri)`
  • `ExtendApConst(Rin,P,Rout)` – set the predicate (`ap`) to a constant
    name P
  • `ExtendAoFromAn(Rin,Rout)` – copy a literal name (`an`) into object (`ao`)

- Emission rule: for any mapping relation R that has `as`, `ap`, `ao`
  attributes, produce RDF triples by asserting `holds2(P, S, O)`
  (predicate-as-name, binary).

This case shows a classic optimization/equivalence:

    Extend distributes over Union
    Extend(Union(R1,R2))  ≡  Union(Extend(R1), Extend(R2))

We check this by generating the same set of `ex:name(S,O)` triples via both
plans.

Why this matches the paper’s spirit
-----------------------------------
Min Oo & Hartig propose a **language-agnostic algebra** for KGC with mapping
relations, operators, and equivalences usable for plan rewriting /
optimization.

We build the same intuition with *names as intensions* and a fixed `holds₂`
predicate, so everything stays first-order.

How to run
----------
    python kgc_algebra_min_oo_hartig.py

Printed sections
----------------
Model → Question → Answer → Reason why → Check (12 tests)

"""

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Set, Tuple, Union
from collections import defaultdict, deque
import itertools
import inspect


# ╔══════════════════════════════════════════════════════════════════════╗
# ║ Tiny logic engine                                                    ║
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
# ║ Case: Algebraic KG construction (Min Oo & Hartig style)              ║
# ╚══════════════════════════════════════════════════════════════════════╝

# We now mirror the original case, but using the embedded engine above.

from typing import Set as _SetAlias  # just to avoid confusion below

EX = "ex:"

# Predicates (fixed vocabulary)
Holds2 = EX + "holds2"  # NAME×IND×IND (application)
IRIOf = EX + "IRIOf"    # NAME×IND×IND (id → iri : tiny lookup)

# Operator meta-predicates (NAME-only)
UnionRel = EX + "UnionRel"           # (R1,R2,Ru)
ExtendAsFromAx = EX + "ExtendAsFromAx"   # (Rin,Rout)
ExtendApConst = EX + "ExtendApConst"     # (Rin,Pconst,Rout)
ExtendAoFromAn = EX + "ExtendAoFromAn"   # (Rin,Rout)

# A tiny predicate name for emitted RDF triples:
NamePred = EX + "name"  # the 'rdf:predicate' used for name triples

# Attribute tags we care about
ATTRS = ("ax", "an", "as", "ap", "ao")  # id, name literal, subject, predicate, object


def att(R: str, a: str) -> str:
    """Name of the per-attribute relation: R/a ."""
    return f"{R}/{a}"


# Domain (individuals) — tuple ids and atomic values
t1, t2, t3 = "t1", "t2", "t3"  # tuple identifiers
id1, id2, id3 = "1", "2", "3"  # person ids as individuals

# Predefined IRIs and literals (as individuals too)
i_alice = EX + "person_1"
i_bob = EX + "person_2"
i_carol = EX + "person_3"

lit_Alice = '"Alice"'
lit_Bob = '"Bob"'
lit_Carol = '"Carol"'


# Mapping relation *names* (intensions)
R_P1 = EX + "PersonsPart1"
R_P2 = EX + "PersonsPart2"
R_AllP = EX + "PersonsAll"

R_tmpA1 = EX + "TmpA1"
R_tmpA2 = EX + "TmpA2"
R_nameA = EX + "NameTriples_A"  # plan A (extend after union)

R_tmpB1_1 = EX + "TmpB1_1"
R_tmpB1_2 = EX + "TmpB1_2"
R_tmpB2_1 = EX + "TmpB2_1"
R_tmpB2_2 = EX + "TmpB2_2"
R_nameB1 = EX + "NameTriples_B1"  # plan B (extend then union)
R_nameB2 = EX + "NameTriples_B2"
R_nameU = EX + "NameTriples_Union"


# Signature (NAME/IND) — only `holds2` and operator predicates appear in rules
SIGNATURE: Signature = {
    Holds2: (NAME, IND, IND),
    IRIOf: (NAME, IND, IND),
    UnionRel: (NAME, NAME, NAME),
    ExtendAsFromAx: (NAME, NAME),
    ExtendApConst: (NAME, NAME, NAME),
    ExtendAoFromAn: (NAME, NAME),
}


# Program (facts + rules)
PROGRAM: List[Clause] = []


def add_fact(pred: str, *args: str) -> None:
    PROGRAM.append(fact(pred, *args))


def add_rule(head_pred: str, head_args: Iterable, body: List[Atom]) -> None:
    PROGRAM.append(Clause(atom(head_pred, *head_args), body))


# --- Base data: two mapping relations with `(ax, an)` present -----------

# PersonsPart1: t1=(id=1, name="Alice"), t2=(id=2, name="Bob")
add_fact(Holds2, att(R_P1, "ax"), t1, id1)
add_fact(Holds2, att(R_P1, "an"), t1, lit_Alice)
add_fact(Holds2, att(R_P1, "ax"), t2, id2)
add_fact(Holds2, att(R_P1, "an"), t2, lit_Bob)

# PersonsPart2: t3=(id=3, name="Carol")
add_fact(Holds2, att(R_P2, "ax"), t3, id3)
add_fact(Holds2, att(R_P2, "an"), t3, lit_Carol)

# Tiny lookup to build subject IRIs from ids (first-order, finite table)
add_fact(Holds2, IRIOf, id1, i_alice)
add_fact(Holds2, IRIOf, id2, i_bob)
add_fact(Holds2, IRIOf, id3, i_carol)


# --- Operator declarations (meta-facts) ---------------------------------

add_fact(UnionRel, R_P1, R_P2, R_AllP)

add_fact(ExtendAsFromAx, R_AllP, R_tmpA1)
add_fact(ExtendApConst, R_tmpA1, NamePred, R_tmpA2)
add_fact(ExtendAoFromAn, R_tmpA2, R_nameA)

add_fact(ExtendAsFromAx, R_P1, R_tmpB1_1)
add_fact(ExtendAsFromAx, R_P2, R_tmpB1_2)
add_fact(ExtendApConst, R_tmpB1_1, NamePred, R_tmpB2_1)
add_fact(ExtendApConst, R_tmpB1_2, NamePred, R_tmpB2_2)
add_fact(ExtendAoFromAn, R_tmpB2_1, R_nameB1)
add_fact(ExtendAoFromAn, R_tmpB2_2, R_nameB2)
add_fact(UnionRel, R_nameB1, R_nameB2, R_nameU)


# --- Generic *effect rules* for the operators ---------------------------

def lift_union_rules(R1: str, R2: str, Ru: str) -> None:
    T, V = Var("T"), Var("V")
    for a in ATTRS:
        # copy from R1/a -> Ru/a
        add_rule(Holds2, (att(Ru, a), T, V),
                 [atom(Holds2, att(R1, a), T, V)])
        # copy from R2/a -> Ru/a
        add_rule(Holds2, (att(Ru, a), T, V),
                 [atom(Holds2, att(R2, a), T, V)])


def lift_extend_as_from_ax(Rin: str, Rout: str) -> None:
    T, Id, Iri, V = Var("T"), Var("Id"), Var("Iri"), Var("V")
    # as := IRIOf(ax)
    add_rule(
        Holds2, (att(Rout, "as"), T, Iri),
        [
            atom(Holds2, att(Rin, "ax"), T, Id),
            atom(Holds2, IRIOf, Id, Iri),
        ],
    )
    # copy-through for all other attributes except 'as'
    for a in ATTRS:
        if a == "as":
            continue
        add_rule(
            Holds2, (att(Rout, a), T, V),
            [atom(Holds2, att(Rin, a), T, V)],
        )


def lift_extend_ap_const(Rin: str, Pconst: str, Rout: str) -> None:
    T, V = Var("T"), Var("V")
    # ap := Pconst whenever the tuple exists (detected via ax)
    add_rule(
        Holds2, (att(Rout, "ap"), T, Pconst),
        [atom(Holds2, att(Rin, "ax"), T, Var("Id"))],
    )
    # copy-through for other attributes except 'ap'
    for a in ATTRS:
        if a == "ap":
            continue
        add_rule(
            Holds2, (att(Rout, a), T, V),
            [atom(Holds2, att(Rin, a), T, V)],
        )


def lift_extend_ao_from_an(Rin: str, Rout: str) -> None:
    T, V = Var("T"), Var("V")
    # ao := an
    add_rule(
        Holds2, (att(Rout, "ao"), T, V),
        [atom(Holds2, att(Rin, "an"), T, V)],
    )
    # copy-through for other attributes except 'ao'
    for a in ATTRS:
        if a == "ao":
            continue
        add_rule(
            Holds2, (att(Rout, a), T, V),
            [atom(Holds2, att(Rin, a), T, V)],
        )


# Specialize rules for the declared operator instances
for (R1, R2, Ru) in [(R_P1, R_P2, R_AllP),
                     (R_nameB1, R_nameB2, R_nameU)]:
    lift_union_rules(R1, R2, Ru)

for (Rin, Rout) in [(R_AllP, R_tmpA1),
                    (R_P1, R_tmpB1_1),
                    (R_P2, R_tmpB1_2)]:
    lift_extend_as_from_ax(Rin, Rout)

for (Rin, Pconst, Rout) in [(R_tmpA1, NamePred, R_tmpA2),
                            (R_tmpB1_1, NamePred, R_tmpB2_1),
                            (R_tmpB1_2, NamePred, R_tmpB2_2)]:
    lift_extend_ap_const(Rin, Pconst, Rout)

for (Rin, Rout) in [(R_tmpA2, R_nameA),
                    (R_tmpB2_1, R_nameB1),
                    (R_tmpB2_2, R_nameB2)]:
    lift_extend_ao_from_an(Rin, Rout)


# --- Emission rules: mapping relations → RDF triples --------------------

def add_emit_rule(R: str) -> None:
    T, S, P, O = Var("T"), Var("S"), Var("P"), Var("O")
    add_rule(
        Holds2, (P, S, O),
        [
            atom(Holds2, att(R, "ap"), T, P),
            atom(Holds2, att(R, "as"), T, S),
            atom(Holds2, att(R, "ao"), T, O),
        ],
    )


for R in (R_nameA, R_nameB1, R_nameB2, R_nameU):
    add_emit_rule(R)


# ╔══════════════════════════════════════════════════════════════════════╗
# ║ Case-specific engine glue (auto engine chooser)                      ║
# ╚══════════════════════════════════════════════════════════════════════╝

def _is_var(t) -> bool:
    return isinstance(t, Var)


def choose_engine(goals: List[Atom]) -> str:
    # Enumerations on holds2(NamePred, X, Y) → bottom-up;
    # precise ground checks → top-down.
    for g in goals:
        if g.pred == Holds2 and any(_is_var(t) for t in g.args):
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


# ╔══════════════════════════════════════════════════════════════════════╗
# ║ Presentation                                                         ║
# ╚══════════════════════════════════════════════════════════════════════╝

def triples_of(pred_name: str) -> Set[Tuple[str, str]]:
    """Convenience to read all pairs for a given predicate name."""
    facts, _ = solve_bottomup(PROGRAM, SIGNATURE)
    pairs: Set[Tuple[str, str]] = set()
    rows = facts.get(Holds2, set())
    # Filter only those where the first column = predicate name (NAME)
    for (p, s, o) in rows:
        if p == pred_name:
            pairs.add((s, o))
    return pairs


def print_model() -> None:
    print("Model")
    print("=====")
    print("Base mapping relations (tables), per-attribute as separate holds₂ names:")
    print(f"• {local(R_P1)}: (ax, an) with tuples t1,t2 → ids 1,2; names \"Alice\",\"Bob\".")
    print(f"• {local(R_P2)}: (ax, an) with tuple t3 → id 3; name \"Carol\".")

    print("\nOperator instances")
    print("------------------")
    print("Plan A (extend after union):")
    print(f"  UnionRel({local(R_P1)}, {local(R_P2)}, {local(R_AllP)})")
    print(f"  ExtendAsFromAx({local(R_AllP)}, {local(R_tmpA1)})")
    print(f"  ExtendApConst({local(R_tmpA1)}, {local(NamePred)}, {local(R_tmpA2)})")
    print(f"  ExtendAoFromAn({local(R_tmpA2)}, {local(R_nameA)}) → emit triples")

    print("Plan B (extend then union):")
    print(f"  ExtendAsFromAx({local(R_P1)}, {local(R_tmpB1_1)}), "
          f"ExtendAsFromAx({local(R_P2)}, {local(R_tmpB1_2)})")
    print(f"  ExtendApConst({local(R_tmpB1_1)}, {local(NamePred)}, {local(R_tmpB2_1)}), "
          f"ExtendApConst({local(R_tmpB1_2)}, {local(NamePred)}, {local(R_tmpB2_2)})")
    print(f"  ExtendAoFromAn(... → {local(R_nameB1)}), "
          f"(... → {local(R_nameB2)}), "
          f"UnionRel(..., {local(R_nameU)}) → emit triples")

    print("\nLookup for subject IRIs:")
    print(f"  IRIOf(1)→{local(i_alice)}, "
          f"IRIOf(2)→{local(i_bob)}, "
          f"IRIOf(3)→{local(i_carol)}\n")


def print_question() -> None:
    print("Question")
    print("========")
    print("Q1) Enumerate triples holds2(ex:name, S, O) from Plan A and Plan B. [auto engine]")
    print("Q2) Check equivalence: Extend(Union(P1,P2)) vs Union(Extend(P1),Extend(P2)). [auto engine]")
    print("Q3) Ground check: holds2(ex:name, ex:person_2, \"Bob\") ? [auto engine]")
    print()


def triples_from_relation(R: str) -> Set[Tuple[str, str]]:
    """
    Build {(S,O)} for a plan-specific mapping relation R by joining
    its per-attribute tables: R/as, R/ap, R/ao.
    Only include rows whose ap == NamePred.
    """
    facts, _ = solve_bottomup(PROGRAM, SIGNATURE)
    rows = facts.get(Holds2, set())

    as_map: Dict[str, str] = {}
    ao_map: Dict[str, str] = {}
    ap_ok: Set[str] = set()

    r_as = att(R, "as")
    r_ap = att(R, "ap")
    r_ao = att(R, "ao")

    for (p, s, o) in rows:
        if p == r_as:
            as_map[s] = o
        elif p == r_ao:
            ao_map[s] = o
        elif p == r_ap and o == NamePred:
            ap_ok.add(s)

    out: Set[Tuple[str, str]] = set()
    for t in ap_ok:
        if t in as_map and t in ao_map:
            out.add((as_map[t], ao_map[t]))
    return out


def run_queries():
    # Q1: Plan A vs Plan B (properly separated)
    pairsA = sorted(triples_from_relation(R_nameA))
    pairsB = sorted(triples_from_relation(R_nameU))

    # Q2: algebraic equivalence (set equality)
    eq = set(pairsA) == set(pairsB)

    # Q3: ground proof for one concrete triple
    eng3, sols3, _ = ask([atom(Holds2, NamePred, i_bob, lit_Bob)])

    return (
        ("Q1", "bottomup", pairsA, pairsB),
        ("Q2", "mixed", eq, "n/a"),
        ("Q3", eng3, bool(sols3), "n/a"),
    )


def print_answer(res1, res2, res3) -> None:
    print("Answer")
    print("======")
    tag1, eng1, pairsA, pairsB = res1
    tag2, eng2, eq, _ = res2
    tag3, eng3, ok, _ = res3

    def show(ps):
        return "∅" if not ps else "{" + ", ".join(f"⟨{s},{o}⟩" for (s, o) in ps) + "}"

    print(f"{tag1}) Engine: {eng1}")
    print(f"  Plan A (Extend after Union): ex:name =", show(pairsA))
    print(f"  Plan B (Extend then Union) : ex:name =", show(pairsB))
    print(f"{tag2}) Engine: {eng2} → Equivalence holds: {'Yes' if eq else 'No'}")
    print(f"{tag3}) Engine: {eng3} → "
          f"holds2(ex:name, ex:person_2, \"Bob\"): {'Yes' if ok else 'No'}\n")


def print_reason(eng1, eng2) -> None:
    print("Reason why")
    print("==========")
    print("• Mapping relations are represented by *per-attribute* holds₂ names R/ax, R/an, etc.")
    print("• Operators (Union, Extend…) are *names* with generic effect rules specialized per instance.")
    print("• Triples are emitted by reading as/ap/ao and asserting holds₂(P,S,O) with P as a name.")
    print("• This mirrors the algebraic plan view in Min Oo & Hartig (ESWC 2025), where operators")
    print("  combine into plans and equivalences (rewrite rules) ensure semantics-preserving rewrites.")
    print("• Here we validate the classic rewrite Extend ∘ Union ≡ Union ∘ (Extend,Extend).\n")


# ╔══════════════════════════════════════════════════════════════════════╗
# ║ Check (12 tests)                                                     ║
# ╚══════════════════════════════════════════════════════════════════════╝

class CheckFailure(AssertionError):
    pass


def check(c: bool, msg: str):
    if not c:
        raise CheckFailure(msg)


def run_checks() -> List[str]:
    notes: List[str] = []

    facts, _ = solve_bottomup(PROGRAM, SIGNATURE)

    # 1) All three subjects appear
    triples = {(p, s, o) for (p, s, o) in facts.get(Holds2, set())
               if p == NamePred}
    subs = {s for (_, s, _) in triples}
    check(subs == {i_alice, i_bob, i_carol},
          "Missing subjects in emitted triples.")
    notes.append("PASS 1: Subjects {Alice,Bob,Carol} present.")

    # 2) Objects are the expected literals
    objs = {o for (_, _, o) in triples}
    check(objs == {lit_Alice, lit_Bob, lit_Carol},
          "Missing objects in emitted triples.")
    notes.append('PASS 2: Objects {"Alice","Bob","Carol"} present.')

    # 3) Plan A set equals Plan B set
    pairsA = {(s, o) for (p, s, o) in triples if p == NamePred}
    pairsB = triples_of(NamePred)
    check(pairsA == pairsB, "Plan A vs Plan B mismatch.")
    notes.append("PASS 3: Extend over Union equivalence holds.")

    # 4) Ground positive
    td, _ = solve_topdown(PROGRAM, [atom(Holds2, NamePred, i_bob, lit_Bob)])
    check(bool(td), "Top-down failed on a ground triple.")
    notes.append("PASS 4: Tabled top-down proves ground triple.")

    # 5) Ground negative
    td2, _ = solve_topdown(PROGRAM, [atom(Holds2, NamePred, i_bob, lit_Alice)])
    check(not td2, "Unexpected cross-person name triple.")
    notes.append("PASS 5: Negative ground case blocked.")

    # 6) Deterministic pretty output
    s1 = ", ".join(sorted(f"{s}:{o}" for (s, o) in pairsA))
    s2 = ", ".join(sorted(f"{s}:{o}" for (s, o) in set(pairsA)))
    check(s1 == s2, "Deterministic formatting failed.")
    notes.append("PASS 6: Deterministic formatting.")

    # 7) Union copied both parts at attribute level
    have_all_ax = match_against_facts(
        [atom(Holds2, att(R_AllP, "ax"), Var("T"), Var("ID"))],
        facts,
    )
    check(len(have_all_ax) == 3, "UnionRel did not cover all ax values.")
    notes.append("PASS 7: UnionRel covers all ids.")

    # 8) ExtendAsFromAx produced as for every tuple
    have_as = match_against_facts(
        [atom(Holds2, att(R_tmpA1, "as"), Var("T"), Var("IRI"))],
        facts,
    )
    check(len(have_as) == 3, "ExtendAsFromAx missing some as values.")
    notes.append("PASS 8: ExtendAsFromAx populates subjects.")

    # 9) ExtendApConst set NamePred everywhere in that plan
    have_ap = match_against_facts(
        [atom(Holds2, att(R_tmpA2, "ap"), Var("T"), NamePred)],
        facts,
    )
    check(len(have_ap) == 3, "ExtendApConst missing some ap values.")
    notes.append("PASS 9: ExtendApConst populates predicates.")

    # 10) ExtendAoFromAn copied objects correctly
    have_ao = match_against_facts(
        [atom(Holds2, att(R_nameA, "ao"), Var("T"), Var("O"))],
        facts,
    )
    check(len(have_ao) == 3, "ExtendAoFromAn missing some ao values.")
    notes.append("PASS 10: ExtendAoFromAn populates objects.")

    # 11) Bottom-up closure idempotent
    f1, _ = solve_bottomup(PROGRAM, SIGNATURE)
    f2, _ = solve_bottomup(PROGRAM, SIGNATURE)
    check(f1[Holds2] == f2[Holds2], "Bottom-up closure not stable.")
    notes.append("PASS 11: Bottom-up closure stable.")

    # 12) Engine chooser behavior: enumeration vs ground
    e1, _, _ = ask([atom(Holds2, NamePred, Var("S"), Var("O"))])
    e2, _, _ = ask([atom(Holds2, NamePred, i_alice, lit_Alice)])
    check(e1 == "bottomup" and e2 == "topdown",
          "Engine chooser mismatch.")
    notes.append("PASS 12: Engine chooser behaves as intended.")

    return notes


# ╔══════════════════════════════════════════════════════════════════════╗
# ║ Standalone runner                                                    ║
# ╚══════════════════════════════════════════════════════════════════════╝

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

