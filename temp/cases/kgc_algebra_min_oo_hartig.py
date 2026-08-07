# -*- coding: utf-8 -*-
"""
Algebraic KG Construction (inspired by Min Oo & Hartig, ESWC 2025)
------------------------------------------------------------------

What this demonstrates
----------------------
We encode a tiny mapping-algebra style workflow for **knowledge graph construction (KGC)**,
but instead of a generic logic engine we use **specialized Python closures**:

- Two base *mapping relations* (think: small tables extracted from CSVs)
- Algebraic operators over these relations:
    • UnionRel(R1,R2,Ru)
         – union of mapping relations (same schema, disjoint tuple ids here)
    • ExtendAsFromAx(Rin,Rout)
         – compute RDF subjects (`as`) from ids (`ax`) via a tiny lookup IRIOf(id → iri)
    • ExtendApConst(Rin,P,Rout)
         – set the predicate (`ap`) to a constant name P
    • ExtendAoFromAn(Rin,Rout)
         – copy a literal name (`an`) into object (`ao`)

- Emission rule: for any mapping relation R that has `as`, `ap`, `ao` attributes, we
  produce RDF triples by asserting holds₂(P,S,O) at the meta-level as a Python set:
       triple_ext[P] ⊆ IND × IND

This case shows a classic optimization/equivalence:

    Extend distributes over Union

        Extend(Union(R1,R2))  ≡  Union(Extend(R1), Extend(R2))

We check this by generating the same set of ex:name(S,O) triples via **Plan A**
(extend after union) and **Plan B** (extend before union).

How to run
----------
    python kgc_algebra_min_oo_hartig.py

Printed sections
----------------
Model → Question → Answer → Reason why → Check (harness)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Set, Tuple


# ──────────────────────────────────────────────────────────────────────
# Names and small helpers
# ──────────────────────────────────────────────────────────────────────

EX = "ex:"

# Attribute tags we care about
ATTRS = ("ax", "an", "as", "ap", "ao")  # id, name literal, subject, predicate, object

# A tiny predicate name for emitted RDF triples:
NamePred = EX + "name"  # the 'rdf:predicate' used for name triples


def local(name: str) -> str:
    """Strip namespace prefix ex: for nicer printing."""
    return name.split(":", 1)[1] if ":" in name else name


def fmt_pairs(pairs: Iterable[Tuple[str, str]]) -> str:
    seq = sorted(set(pairs))
    if not seq:
        return "∅"
    return "{" + ", ".join(f"⟨{s},{o}⟩" for (s, o) in seq) + "}"


def fmt_set(names: Iterable[str]) -> str:
    s = sorted(set(names))
    if not s:
        return "∅"
    return "{" + ", ".join(local(n) for n in s) + "}"


# ──────────────────────────────────────────────────────────────────────
# Domain (individuals) and mapping relation names
# ──────────────────────────────────────────────────────────────────────

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

INDIVIDUALS: Tuple[str, ...] = (
    t1,
    t2,
    t3,
    id1,
    id2,
    id3,
    i_alice,
    i_bob,
    i_carol,
    lit_Alice,
    lit_Bob,
    lit_Carol,
)

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

RELATIONS: Tuple[str, ...] = (
    R_P1,
    R_P2,
    R_AllP,
    R_tmpA1,
    R_tmpA2,
    R_nameA,
    R_tmpB1_1,
    R_tmpB1_2,
    R_tmpB2_1,
    R_tmpB2_2,
    R_nameB1,
    R_nameB2,
    R_nameU,
)


# ──────────────────────────────────────────────────────────────────────
# Core data structures
# ──────────────────────────────────────────────────────────────────────

# MappingRel: attribute -> (tupleId -> value)
MappingRel = Dict[str, Dict[str, str]]

# All mapping relations: R_name -> MappingRel
MappingStore = Dict[str, MappingRel]

# Emitted RDF triples: predicate name -> {(S,O)}
TripleStore = Dict[str, Set[Tuple[str, str]]]


@dataclass
class KGCModel:
    mappings: MappingStore
    iri_of: Dict[str, str]
    triples: TripleStore


# ──────────────────────────────────────────────────────────────────────
# Specialized algebra operations
# ──────────────────────────────────────────────────────────────────────

def _set_attr(mappings: MappingStore, R: str, a: str, t: str, v: str) -> None:
    mappings.setdefault(R, {}).setdefault(a, {})[t] = v


def union_rel(mappings: MappingStore, R1: str, R2: str, Ru: str) -> None:
    """
    UnionRel(R1,R2,Ru): attribute-wise union R1 ∪ R2 → Ru.

    Here tuple ids are disjoint, so we simply copy all attribute values;
    in the presence of overlaps, R2 values would overwrite R1's (still a valid
    union in this setting).
    """
    mappings.setdefault(Ru, {})
    for a in ATTRS:
        out = mappings[Ru].setdefault(a, {})
        for srcR in (R1, R2):
            src = mappings.get(srcR, {}).get(a, {})
            for t, v in src.items():
                out[t] = v


def extend_as_from_ax(
    mappings: MappingStore, iri_of: Dict[str, str], Rin: str, Rout: str
) -> None:
    """
    ExtendAsFromAx(Rin,Rout):

        Rout/as(t) := IRIOf(Rin/ax(t))
        and copy all other attributes through (ax, an, ap, ao).
    """
    mappings.setdefault(Rout, {})
    rin = mappings.get(Rin, {})

    # Copy-through for all attrs except 'as'
    for a in ATTRS:
        if a == "as":
            continue
        src = rin.get(a, {})
        if src:
            mappings[Rout].setdefault(a, {})
            mappings[Rout][a].update(src)

    # Compute `as` from `ax` via iri_of
    ax = rin.get("ax", {})
    if ax:
        as_map = mappings[Rout].setdefault("as", {})
        for t, idv in ax.items():
            as_map[t] = iri_of[idv]


def extend_ap_const(mappings: MappingStore, Rin: str, Pconst: str, Rout: str) -> None:
    """
    ExtendApConst(Rin,Pconst,Rout):

        Rout/ap(t) := Pconst for every tuple t that exists in Rin
        (we detect existence via Rin/ax), and copy all other attrs.
    """
    mappings.setdefault(Rout, {})
    rin = mappings.get(Rin, {})

    # Copy-through for all attrs except 'ap'
    for a in ATTRS:
        if a == "ap":
            continue
        src = rin.get(a, {})
        if src:
            mappings[Rout].setdefault(a, {})
            mappings[Rout][a].update(src)

    # Set `ap` from presence of `ax`
    ax = rin.get("ax", {})
    if ax:
        ap_map = mappings[Rout].setdefault("ap", {})
        for t in ax.keys():
            ap_map[t] = Pconst


def extend_ao_from_an(mappings: MappingStore, Rin: str, Rout: str) -> None:
    """
    ExtendAoFromAn(Rin,Rout):

        Rout/ao(t) := Rin/an(t)
        and copy all other attrs.
    """
    mappings.setdefault(Rout, {})
    rin = mappings.get(Rin, {})

    # Copy-through for all attrs except 'ao'
    for a in ATTRS:
        if a == "ao":
            continue
        src = rin.get(a, {})
        if src:
            mappings[Rout].setdefault(a, {})
            mappings[Rout][a].update(src)

    # Set `ao` from `an`
    an = rin.get("an", {})
    if an:
        ao_map = mappings[Rout].setdefault("ao", {})
        for t, name in an.items():
            ao_map[t] = name


def emit_triples(mappings: MappingStore, R: str, triples: TripleStore) -> None:
    """
    Emit RDF triples from mapping relation R:

        if R/as(t)=S, R/ap(t)=P, R/ao(t)=O then triple (P,S,O) is added.
    """
    rel = mappings.get(R, {})
    as_map = rel.get("as", {})
    ap_map = rel.get("ap", {})
    ao_map = rel.get("ao", {})

    common_t = set(as_map.keys()) & set(ap_map.keys()) & set(ao_map.keys())
    for t in common_t:
        P = ap_map[t]
        S = as_map[t]
        O = ao_map[t]
        triples.setdefault(P, set()).add((S, O))


def triples_from_relation(m: KGCModel, R: str) -> Set[Tuple[str, str]]:
    """
    Build {(S,O)} for a plan-specific mapping relation R by joining its
    per-attribute tables R/as, R/ap, R/ao, restricted to ap == NamePred.
    """
    rel = m.mappings.get(R, {})
    as_map = rel.get("as", {})
    ap_map = rel.get("ap", {})
    ao_map = rel.get("ao", {})

    out: Set[Tuple[str, str]] = set()
    for t, P in ap_map.items():
        if P != NamePred:
            continue
        if t in as_map and t in ao_map:
            out.add((as_map[t], ao_map[t]))
    return out


def triples_of(m: KGCModel, pred_name: str) -> Set[Tuple[str, str]]:
    """Convenience to read all (S,O) pairs for a given predicate name."""
    return set(m.triples.get(pred_name, set()))


# ──────────────────────────────────────────────────────────────────────
# Model builder
# ──────────────────────────────────────────────────────────────────────

def build_model() -> KGCModel:
    # Initialize mapping store for all known relation names
    mappings: MappingStore = {R: {} for R in RELATIONS}

    # Base data: two mapping relations with (ax, an)
    # PersonsPart1: t1=(id=1, name="Alice"), t2=(id=2, name="Bob")
    _set_attr(mappings, R_P1, "ax", t1, id1)
    _set_attr(mappings, R_P1, "an", t1, lit_Alice)
    _set_attr(mappings, R_P1, "ax", t2, id2)
    _set_attr(mappings, R_P1, "an", t2, lit_Bob)

    # PersonsPart2: t3=(id=3, name="Carol")
    _set_attr(mappings, R_P2, "ax", t3, id3)
    _set_attr(mappings, R_P2, "an", t3, lit_Carol)

    # Tiny lookup to build subject IRIs from ids
    iri_of: Dict[str, str] = {
        id1: i_alice,
        id2: i_bob,
        id3: i_carol,
    }

    # Plan A: Extend after Union
    union_rel(mappings, R_P1, R_P2, R_AllP)
    extend_as_from_ax(mappings, iri_of, R_AllP, R_tmpA1)
    extend_ap_const(mappings, R_tmpA1, NamePred, R_tmpA2)
    extend_ao_from_an(mappings, R_tmpA2, R_nameA)

    # Plan B: Extend then Union
    extend_as_from_ax(mappings, iri_of, R_P1, R_tmpB1_1)
    extend_as_from_ax(mappings, iri_of, R_P2, R_tmpB1_2)

    extend_ap_const(mappings, R_tmpB1_1, NamePred, R_tmpB2_1)
    extend_ap_const(mappings, R_tmpB1_2, NamePred, R_tmpB2_2)

    extend_ao_from_an(mappings, R_tmpB2_1, R_nameB1)
    extend_ao_from_an(mappings, R_tmpB2_2, R_nameB2)

    union_rel(mappings, R_nameB1, R_nameB2, R_nameU)

    # Emission: mapping relations → binary RDF triples
    triples: TripleStore = {}
    for R in (R_nameA, R_nameB1, R_nameB2, R_nameU):
        emit_triples(mappings, R, triples)

    return KGCModel(mappings=mappings, iri_of=iri_of, triples=triples)


# ──────────────────────────────────────────────────────────────────────
# Presentation
# ──────────────────────────────────────────────────────────────────────

def print_model(m: KGCModel) -> None:
    print("Model")
    print("=====")
    print("Base mapping relations (tables), per-attribute:")
    print(f"• {local(R_P1)}: (ax, an) with tuples t1,t2 → ids 1,2; names \"Alice\",\"Bob\".")
    print(f"• {local(R_P2)}: (ax, an) with tuple t3 → id 3; name \"Carol\".\n")

    print("Operator instances")
    print("------------------")
    print("Plan A (extend after union):")
    print(f"  UnionRel({local(R_P1)}, {local(R_P2)}, {local(R_AllP)})")
    print(f"  ExtendAsFromAx({local(R_AllP)}, {local(R_tmpA1)})")
    print(f"  ExtendApConst({local(R_tmpA1)}, {local(NamePred)}, {local(R_tmpA2)})")
    print(f"  ExtendAoFromAn({local(R_tmpA2)}, {local(R_nameA)}) → emit triples\n")

    print("Plan B (extend then union):")
    print(f"  ExtendAsFromAx({local(R_P1)}, {local(R_tmpB1_1)}), "
          f"ExtendAsFromAx({local(R_P2)}, {local(R_tmpB1_2)})")
    print(f"  ExtendApConst({local(R_tmpB1_1)}, {local(NamePred)}, {local(R_tmpB2_1)}), "
          f"ExtendApConst({local(R_tmpB1_2)}, {local(NamePred)}, {local(R_tmpB2_2)})")
    print(f"  ExtendAoFromAn(... → {local(R_nameB1)}), (... → {local(R_nameB2)}), "
          f"UnionRel(..., {local(R_nameU)}) → emit triples\n")

    print("Lookup for subject IRIs:")
    print(f"  IRIOf(1)→{local(i_alice)}, IRIOf(2)→{local(i_bob)}, IRIOf(3)→{local(i_carol)}\n")


def print_question() -> None:
    print("Question")
    print("========")
    print("Q1) Enumerate triples ex:name(S,O) from Plan A and from Plan B.")
    print("Q2) Check equivalence: Extend(Union(P1,P2)) vs Union(Extend(P1),Extend(P2)).")
    print("Q3) Ground check: ex:name(ex:person_2, \"Bob\") ?")
    print()


def run_queries(m: KGCModel):
    # Q1: Plan A vs Plan B (properly separated)
    pairsA = sorted(triples_from_relation(m, R_nameA))
    pairsB = sorted(triples_from_relation(m, R_nameU))

    # Q2: algebraic equivalence (set equality)
    eq = set(pairsA) == set(pairsB)

    # Q3: ground membership for one concrete triple
    triples_name = triples_of(m, NamePred)
    ok = (i_bob, lit_Bob) in triples_name

    return (
        ("Q1", pairsA, pairsB),
        ("Q2", eq),
        ("Q3", ok),
    )


def print_answer(res1, res2, res3) -> None:
    print("Answer")
    print("======")

    tag1, pairsA, pairsB = res1
    tag2, eq = res2
    tag3, ok = res3

    def show(ps):
        return "∅" if not ps else "{" + ", ".join(f"⟨{s},{o}⟩" for (s, o) in ps) + "}"

    print(f"{tag1})")
    print(f"  Plan A (Extend after Union): ex:name =", show(pairsA))
    print(f"  Plan B (Extend then Union) : ex:name =", show(pairsB))
    print(f"{tag2}) Equivalence holds (sets equal): {'Yes' if eq else 'No'}")
    print(f"{tag3}) holds2(ex:name, ex:person_2, \"Bob\"): {'Yes' if ok else 'No'}\n")


def print_reason() -> None:
    print("Reason why")
    print("==========")
    print("• Mapping relations are represented by per-attribute tables R/ax, R/an, R/as, R/ap, R/ao.")
    print("• Algebra operators (Union, ExtendAsFromAx, ExtendApConst, ExtendAoFromAn) are implemented")
    print("  as specialized Python functions over these tables.")
    print("• Triples are emitted by reading as/ap/ao and adding triples (P,S,O) to a TripleStore.")
    print("• This mirrors the algebraic plan view in Min Oo & Hartig (ESWC 2025), where operators")
    print("  compose into plans and equivalences (rewrite rules) ensure semantics-preserving rewrites.")
    print("• Here we validate the classic rewrite Extend ∘ Union  ≡  Union ∘ (Extend, Extend).\n")


# ──────────────────────────────────────────────────────────────────────
# Check (harness)
# ──────────────────────────────────────────────────────────────────────

class CheckFailure(AssertionError):
    pass


def check(c: bool, msg: str):
    if not c:
        raise CheckFailure(msg)


def run_checks(m: KGCModel) -> List[str]:
    notes: List[str] = []

    triples_name = triples_of(m, NamePred)

    # 1) All three subjects appear
    subs = {s for (s, _) in triples_name}
    check(
        subs == {i_alice, i_bob, i_carol},
        f"Missing subjects in emitted triples: {subs}",
    )
    notes.append("PASS 1: Subjects {Alice,Bob,Carol} present.")

    # 2) Objects are the expected literals
    objs = {o for (_, o) in triples_name}
    check(
        objs == {lit_Alice, lit_Bob, lit_Carol},
        f"Missing objects in emitted triples: {objs}",
    )
    notes.append("PASS 2: Objects {\"Alice\",\"Bob\",\"Carol\"} present.")

    # 3) Plan A set equals Plan B set and both match global ex:name
    pairsA = triples_from_relation(m, R_nameA)
    pairsB = triples_from_relation(m, R_nameU)
    check(
        pairsA == pairsB == triples_name,
        "Plan A vs Plan B vs global ex:name mismatch.",
    )
    notes.append("PASS 3: Extend over Union equivalence holds (A == B == global).")

    # 4) Ground positive: (person_2, \"Bob\") present
    check((i_bob, lit_Bob) in triples_name, "Expected (Bob) triple missing.")
    notes.append("PASS 4: Ground positive triple for Bob present.")

    # 5) Ground negative: (person_2, \"Alice\") absent
    check((i_bob, lit_Alice) not in triples_name, "Unexpected cross-person triple present.")
    notes.append("PASS 5: Negative ground case (Bob,Alice) is blocked.")

    # 6) UnionRel copied both parts at attribute level (ids)
    ax_all = m.mappings[R_AllP].get("ax", {})
    check(
        set(ax_all.values()) == {id1, id2, id3}
        and set(ax_all.keys()) == {t1, t2, t3},
        "UnionRel did not cover all ax values.",
    )
    notes.append("PASS 6: UnionRel covers all ids {1,2,3} with tuples {t1,t2,t3}.")

    # 7) ExtendAsFromAx produced `as` for every tuple in AllP
    as_tmpA1 = m.mappings[R_tmpA1].get("as", {})
    check(len(as_tmpA1) == 3 and set(as_tmpA1.values()) == {i_alice, i_bob, i_carol},
          "ExtendAsFromAx missing some as values.")
    notes.append("PASS 7: ExtendAsFromAx populates subjects ex:person_1/2/3.")

    # 8) ExtendApConst set NamePred everywhere in plan A
    ap_tmpA2 = m.mappings[R_tmpA2].get("ap", {})
    check(
        len(ap_tmpA2) == 3 and all(p == NamePred for p in ap_tmpA2.values()),
        "ExtendApConst missing some ap values in plan A.",
    )
    notes.append("PASS 8: ExtendApConst populates predicates ex:name in plan A.")

    # 9) ExtendAoFromAn copied objects correctly in plan A
    ao_nameA = m.mappings[R_nameA].get("ao", {})
    check(
        len(ao_nameA) == 3 and set(ao_nameA.values()) == {lit_Alice, lit_Bob, lit_Carol},
        "ExtendAoFromAn missing some ao values in plan A.",
    )
    notes.append("PASS 9: ExtendAoFromAn populates objects \"Alice\",\"Bob\",\"Carol\" in plan A.")

    # 10) Plan B: NameTriples_B1 and _B2 partition into two+one and union to B-Union
    pairsB1 = triples_from_relation(m, R_nameB1)
    pairsB2 = triples_from_relation(m, R_nameB2)
    pairsBU = triples_from_relation(m, R_nameU)
    check(
        pairsB1 | pairsB2 == pairsBU and pairsB1 & pairsB2 == set(),
        "Plan B partition/union mismatch.",
    )
    notes.append("PASS 10: Plan B parts (B1,B2) partition and union correctly.")

    # 11) Building the model twice yields the same triple set
    m2 = build_model()
    check(
        triples_of(m2, NamePred) == triples_name,
        "Rebuilt model has different ex:name triples.",
    )
    notes.append("PASS 11: Model rebuilding is stable (idempotent wrt ex:name).")

    # 12) Deterministic formatting of pairs
    s1 = ", ".join(sorted(f"{s}:{o}" for (s, o) in triples_name))
    s2 = ", ".join(sorted(f"{s}:{o}" for (s, o) in set(triples_name)))
    check(s1 == s2, "Deterministic formatting of pairs failed.")
    notes.append("PASS 12: Pretty-printing of triples is deterministic.")

    return notes


# ──────────────────────────────────────────────────────────────────────
# Standalone runner
# ──────────────────────────────────────────────────────────────────────

def main():
    m = build_model()

    print_model(m)
    print_question()
    res1, res2, res3 = run_queries(m)
    print_answer(res1, res2, res3)
    print_reason()

    print("Check (harness)")
    print("===============")
    try:
        for note in run_checks(m):
            print(note)
    except CheckFailure as e:
        print("FAIL:", e)
        raise


if __name__ == "__main__":
    main()

