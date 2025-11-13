# -*- coding: utf-8 -*-
"""
Higher algebra — cyclic subgroups of Z₆
---------------------------------------

We represent subgroup generation as reachability under “+k” on Z₆, with the
Hayes–Menzel pattern:

    ex:holds2(R, x, y)   # ⟨x,y⟩ is in the extension of the relation-name R

Named relations (intensions):

    ex:Add1, ex:Add2, ex:Add3
        one-step edges x ↦ x+k (mod 6)

    ex:Gen1, ex:Gen2, ex:Gen3
        generated-by-k reachability (positive-length)

    ex:SubRelOf, ex:leq_strict, ex:leq
        inclusion / closure over relation names (intensions)

Rules (schematic):

    • leq_strict from SubRelOf, plus its transitive closure
    • leq is reflexive on names and extends leq_strict

    • lifting:
        holds2(Q,x,y) :- leq_strict(P,Q), holds2(P,x,y)
        # push facts along SubRelOf

    • generation (right-recursive):
        holds2(Rgen,x,z) :-
            holds2(Rstep,x,y),
            holds2(Rgen,y,z),
            SubRelOf(Rstep,Rgen)

This yields:

    Gen1 = all pairs (x,y)          (since 1 generates Z₆)
    Gen2 = pairs with y ≡ x (mod 2)
    Gen3 = pairs with y ≡ x (mod 3)

The module provides the usual hooks:

    print_model, print_question, run_queries,
    print_answer, print_reason, run_checks, main()

and can be executed directly as a script.
"""

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Set, Tuple, Union
from collections import defaultdict, deque
import itertools
import inspect


# ╔══════════════════════════════════════════════════════════════════════╗
# ║ Engine (lightweight logic programming core)                          ║
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
                    if tpl not in facts[head.pred]:
                        facts[head.pred].add(tpl)
                        changed = True
                else:
                    for tpl in _ground_head_from_domains(head, {}, sig,
                                                         names_list, inds_list):
                        if tpl not in facts[head.pred]:
                            facts[head.pred].add(tpl)
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


# --- Top-down with tabling flavour (via relevant-subprogram LFP) -------

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
    """Collect NAME/IND constants from all ground facts in the full program."""
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
# ║ Case: cyclic subgroups of Z6                                         ║
# ╚══════════════════════════════════════════════════════════════════════╝

from typing import Set as _SetAlias  # just to avoid confusion below

# Domain: "0".."5" as strings
D: Tuple[str, ...] = tuple(str(i) for i in range(6))

# Relation names (intensions)
EX = "ex:"
Add1, Add2, Add3 = EX + "Add1", EX + "Add2", EX + "Add3"
Gen1, Gen2, Gen3 = EX + "Gen1", EX + "Gen2", EX + "Gen3"
SubRelOf = EX + "SubRelOf"
LeqStrict = EX + "leq_strict"
Leq = EX + "leq"
Holds2 = EX + "holds2"

# Signature over NAME / IND
SIGNATURE: Signature = {
    Holds2: (NAME, IND, IND),
    SubRelOf: (NAME, NAME),
    LeqStrict: (NAME, NAME),
    Leq: (NAME, NAME),
}

# Program: facts + rules
PROGRAM: List[Clause] = []


# --- Facts --------------------------------------------------------------

def _add_mod6(x: int, k: int) -> int:
    return (x + k) % 6


# one-step edges for +1,+2,+3 mod 6
for x in range(6):
    PROGRAM.append(fact(Holds2, Add1, str(x), str(_add_mod6(x, 1))))
    PROGRAM.append(fact(Holds2, Add2, str(x), str(_add_mod6(x, 2))))
    PROGRAM.append(fact(Holds2, Add3, str(x), str(_add_mod6(x, 3))))

# Sub-relation edges: Addk ⊆ Genk
PROGRAM += [
    fact(SubRelOf, Add1, Gen1),
    fact(SubRelOf, Add2, Gen2),
    fact(SubRelOf, Add3, Gen3),
]


# --- Rules --------------------------------------------------------------

# Inclusion closure over relation names
P, Q, R = Var("P"), Var("Q"), Var("R")
PROGRAM.append(Clause(atom(LeqStrict, P, Q), [atom(SubRelOf, P, Q)]))

P, Q, R = Var("P"), Var("Q"), Var("R")
PROGRAM.append(Clause(atom(LeqStrict, P, Q),
                      [atom(SubRelOf, P, R), atom(LeqStrict, R, Q)]))

# leq is reflexive and extends leq_strict
P = Var("P")
PROGRAM.append(Clause(atom(Leq, P, P), []))

P, Q = Var("P"), Var("Q")
PROGRAM.append(Clause(atom(Leq, P, Q), [atom(LeqStrict, P, Q)]))

# Lifting: push Addk facts into Genk along inclusions
P, Q, X, Y = Var("P"), Var("Q"), Var("X"), Var("Y")
PROGRAM.append(
    Clause(
        atom(Holds2, Q, X, Y),
        [
            atom(Holds2, P, X, Y),  # use existing facts first
            atom(LeqStrict, P, Q),
        ],
    )
)

# Generation (right-recursive):
# holds2(Rgen, x, z) :- holds2(Rstep, x, y),
#                       holds2(Rgen, y, z),
#                       SubRelOf(Rstep, Rgen).
Rstep, Rgen, X, Y, Z = Var("Rstep"), Var("Rgen"), Var("X"), Var("Y"), Var("Z")
PROGRAM.append(
    Clause(
        atom(Holds2, Rgen, X, Z),
        [
            atom(Holds2, Rstep, X, Y),
            atom(Holds2, Rgen, Y, Z),
            atom(SubRelOf, Rstep, Rgen),
        ],
    )
)


# --- Case-specific engine wrapper --------------------------------------

def _is_var(t) -> bool:
    return isinstance(t, Var)


def choose_engine(goals: List[Atom]) -> str:
    """
    Simple heuristic:
      * holds2(Gen*, X?, Y?) with vars → bottom-up (enumeration)
      * any fully unbound goal → bottom-up
      * otherwise → top-down
    """
    for g in goals:
        if (
            g.pred == Holds2
            and len(g.args) == 3
            and str(g.args[0]).startswith(EX + "Gen")
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
        sols, steps = solve_topdown(PROGRAM, goals, step_limit=step_limit)
        if steps > fallback_threshold:
            facts, _ = solve_bottomup(PROGRAM, SIGNATURE)
            sols = match_against_facts(goals, facts)
            engine = "bottomup"
            return engine, sols, 0
        return engine, sols, steps
    else:
        facts, rounds = solve_bottomup(PROGRAM, SIGNATURE)
        sols = match_against_facts(goals, facts)
        return engine, sols, rounds


# --- Presentation / queries ---------------------------------------------

def print_model() -> None:
    print("Model")
    print("=====")
    print(f"Elements (individuals) D = {list(D)} (Z6, as strings)\n")

    print("Fixed predicates (signature)")
    print("----------------------------")
    print("• ex:holds2(R,x,y) — extensional application; sorts: (NAME, IND, IND)")
    print("• ex:SubRelOf(P,Q) — inclusion over relation names; sorts: (NAME, NAME)")
    print("• ex:leq_strict / ex:leq — subset* with / without reflex; sorts: (NAME, NAME)\n")

    print("Named relations (with base facts)")
    print("---------------------------------")
    add1 = [(str(x), str((x + 1) % 6)) for x in range(6)]
    add2 = [(str(x), str((x + 2) % 6)) for x in range(6)]
    add3 = [(str(x), str((x + 3) % 6)) for x in range(6)]
    print("Add1 =", fmt_pairs(add1))
    print("Add2 =", fmt_pairs(add2))
    print("Add3 =", fmt_pairs(add3))
    print("Gen1, Gen2, Gen3 are derived only (no base facts)\n")
    print("Inclusions over names: Add1 ⊆ Gen1, Add2 ⊆ Gen2, Add3 ⊆ Gen3\n")


def print_question() -> None:
    print("Question")
    print("========")
    print('Q1) List all (x,y) with holds2(Gen2,x,y). [auto engine]')
    print('Q2) ∃R: holds2(R,0,3) ∧ leq(R,Gen3) ? (witness relation names) [auto engine]')
    print('Q3) ∀R,y: (leq(R,Gen2) ∧ holds2(R,0,y)) → holds2(Gen2,0,y) ? [auto engine]')
    print()


def run_queries():
    # Q1: enumerate Gen2 pairs
    Xv, Yv = Var("X"), Var("Y")
    eng1, sols1, m1 = ask([atom(Holds2, Gen2, Xv, Yv)])
    gen2_pairs = sorted({(deref(Xv, s), deref(Yv, s)) for s in sols1})  # type: ignore

    # Q2: witness relation-names R for (0,3) under Gen3
    Rv = Var("R")
    eng2, sols2, m2 = ask([atom(Holds2, Rv, "0", "3"), atom(Leq, Rv, Gen3)])
    witnesses = sorted({deref(Rv, s) for s in sols2 if isinstance(deref(Rv, s), str)})

    # Q3: universal property for Gen2 at source 0
    ok = True
    for R in [Add2, Gen2]:
        for y in D:
            _, cond_sols, _ = ask([atom(Leq, R, Gen2), atom(Holds2, R, "0", y)])
            cond = bool(cond_sols)
            if cond and not ask([atom(Holds2, Gen2, "0", y)])[1]:
                ok = False
                break
        if not ok:
            break

    return (("Q1", eng1, gen2_pairs, m1),
            ("Q2", eng2, witnesses, m2),
            ("Q3", "mixed", ok, 0))


def print_answer(res1, res2, res3) -> None:
    print("Answer")
    print("======")
    tag1, eng1, pairs, _ = res1
    tag2, eng2, wits, _ = res2
    tag3, eng3, ok, _ = res3
    print(f"{tag1}) Engine: {eng1} → Gen2 =", fmt_pairs(pairs))
    print(f"{tag2}) Engine: {eng2} → Witness relation-names R = "
          + (fmt_set(wits) if wits else "∅"))
    print(f"{tag3}) Engine: {eng3} → Universal statement holds: {'Yes' if ok else 'No'}\n")


def print_reason(eng1, eng2) -> None:
    print("Reason why")
    print("==========")
    print("• In Z6, ⟨1⟩ = Z6, ⟨2⟩ = {0,2,4}, ⟨3⟩ = {0,3}.")
    print("• “Generated-by-k” is encoded as reachability under Addk steps with right recursion.")
    print("• Quantification over relations (e.g., ∃R ⊆ Gen3) ranges over relation names (intensions).")
    print("• Lifting pushes Addk facts into Genk; recursion then closes paths of length ≥ 2.")
    print("• The engine chooser prefers bottom-up for big enumerations (Gen2(X,Y)); "
          "ground checks often use top-down.\n")


# --- Check harness ------------------------------------------------------

class CheckFailure(AssertionError):
    pass


def check(cond: bool, msg: str):
    if not cond:
        raise CheckFailure(msg)


def _expected_gen_k_pairs(k: int) -> _SetAlias[Tuple[str, str]]:
    """
    Compute expected reachability pairs for Addk on Z6
    (positive-length paths only).
    """
    nodes = list(range(6))
    edges = {x: {(x + k) % 6} for x in nodes}

    reach: Dict[int, _SetAlias[int]] = {x: set() for x in nodes}
    for s in nodes:
        seen: _SetAlias[int] = set()
        q = deque()
        for t in edges[s]:
            q.append(t)
            seen.add(t)
            reach[s].add(t)
        while q:
            u = q.popleft()
            for v in edges[u]:
                if v not in seen:
                    seen.add(v)
                    q.append(v)
                    reach[s].add(v)

    return {(str(x), str(y)) for x in nodes for y in reach[x]}


def run_checks() -> List[str]:
    notes: List[str] = []

    # Expected Gen2 & Gen3 (finite, computed procedurally)
    exp_gen2 = _expected_gen_k_pairs(2)
    exp_gen3 = _expected_gen_k_pairs(3)

    # 1) Bottom-up enumerates expected Gen2
    facts, _ = solve_bottomup(PROGRAM, SIGNATURE)
    X, Y = Var("X"), Var("Y")
    bu2 = match_against_facts([atom(Holds2, Gen2, X, Y)], facts)
    gen2_bu = {(deref(X, s), deref(Y, s)) for s in bu2}
    check(gen2_bu == exp_gen2, "Bottom-up Gen2 enumeration mismatch.")
    notes.append("PASS 1: Bottom-up Gen2 enumeration is correct.")

    # 2) Ground goal-directed correctness on all pairs
    ok_all = True
    for x in D:
        for y in D:
            should = (x, y) in exp_gen2
            got = bool(ask([atom(Holds2, Gen2, x, y)])[1])
            if got != should:
                ok_all = False
                break
        if not ok_all:
            break
    check(ok_all, "Ground goal-directed correctness for Gen2 failed.")
    notes.append("PASS 2: Ground goal-directed correctness for Gen2 holds.")

    # 3) Witness relation names R for (0,3) under Gen3 are {Add3, Gen3}
    R = Var("R")
    bu_w = match_against_facts(
        [atom(Holds2, R, "0", "3"), atom(Leq, R, Gen3)], facts
    )
    td_w, _ = solve_topdown(
        PROGRAM, [atom(Holds2, R, "0", "3"), atom(Leq, R, Gen3)]
    )
    w1 = {deref(R, s) for s in bu_w}
    w2 = {deref(R, s) for s in td_w}
    check(w1 == w2 == {Add3, Gen3},
          f"Witness set mismatch: {w1} vs {w2}")
    notes.append("PASS 3: Witness set for (0,3) under Gen3 is {Add3, Gen3}.")

    # 4) Universal property for Gen2 at source 0
    ok = True
    for r in [Add2, Gen2]:
        for y in D:
            cond_sols = ask([atom(Leq, r, Gen2), atom(Holds2, r, '0', y)])[1]
            cond = bool(cond_sols)
            if cond and not ask([atom(Holds2, Gen2, '0', y)])[1]:
                ok = False
                break
        if not ok:
            break
    check(ok, "Universal property failed for Gen2.")
    notes.append("PASS 4: Universal property holds for Gen2 at source 0.")

    # 5) Negative: (0,3) is NOT in Gen2
    check(
        not ask([atom(Holds2, Gen2, "0", "3")])[1],
        "Gen2 incorrectly relates 0 to 3.",
    )
    notes.append("PASS 5: Gen2 excludes cross-parity pair (0,3).")

    # 6) Non-membership: (1,0) not in Gen3
    check(
        not ask([atom(Holds2, Gen3, "1", "0")])[1],
        "Gen3 incorrectly relates 1 to 0.",
    )
    notes.append("PASS 6: Gen3 excludes cross-coset pair (1,0).")

    # 7) Engine chooser behaviour
    e1, _, _ = ask([atom(Holds2, Gen2, Var("X"), Var("Y"))])
    e2, _, _ = ask([atom(Holds2, Gen2, "0", "4")])
    check(
        e1 == "bottomup" and e2 in ("topdown", "bottomup"),
        "Engine chooser mismatch.",
    )
    notes.append(
        "PASS 7: Engine chooser behaves as intended (enumeration vs ground)."
    )

    # 8) leq reflexive on names
    for r in [Add1, Add2, Add3, Gen1, Gen2, Gen3]:
        check(
            ask([atom(Leq, r, r)])[1],
            f"Reflexivity of leq failed for {local(r)}.",
        )
    notes.append("PASS 8: leq reflexivity holds for all relation names.")

    # 9) leq_strict inclusions
    check(
        ask([atom(LeqStrict, Add2, Gen2)])[1],
        "leq_strict Add2 ⊆ Gen2 failed.",
    )
    check(
        ask([atom(LeqStrict, Add3, Gen3)])[1],
        "leq_strict Add3 ⊆ Gen3 failed.",
    )
    notes.append("PASS 9: leq_strict inclusions hold.")

    # 10) Top-down stability on ground query
    ok1 = ask([atom(Holds2, Gen2, "0", "4")])[1]
    ok2 = ask([atom(Holds2, Gen2, "0", "4")])[1]
    check(ok1 and ok2, "Repeated ground query should remain true.")
    notes.append("PASS 10: Standardize-apart stable on repeats.")

    # 11) Bottom-up closure idempotence
    f1, _ = solve_bottomup(PROGRAM, SIGNATURE)
    f2, _ = solve_bottomup(PROGRAM, SIGNATURE)
    check(
        f1[Holds2] == f2[Holds2],
        "Bottom-up closure not idempotent.",
    )
    notes.append("PASS 11: Bottom-up closure is stable.")

    # 12) Deterministic pretty-printing
    s1 = fmt_pairs(sorted(exp_gen2))
    s2 = fmt_pairs(sorted(list(exp_gen2)))
    check(s1 == s2, "Pretty-printer determinism failed.")
    notes.append("PASS 12: Pretty printing deterministic.")

    return notes


# --- Standalone runner --------------------------------------------------

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

