---
title: "A Canonical-Expansion Theorem for Basic N3 Entailment"
description: "A publication-style candidate theorem and proof for simple/basic entailment in Notation3, related to interpolation."
layout: default
---

<style>
  .n3-note {
    border-left: 4px solid #999;
    padding: 0.8rem 1rem;
    margin: 1.2rem 0;
    background: #f7f7f7;
  }

  .n3-theorem {
    border: 1px solid #ddd;
    border-radius: 0.5rem;
    padding: 1rem 1.2rem;
    margin: 1.5rem 0;
    background: #fcfcfc;
  }

  .n3-equation {
    display: block;
    overflow-x: auto;
    margin: 1rem 0;
    padding: 0.85rem 1rem;
    border-radius: 0.45rem;
    background: #f6f8fa;
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace;
    font-size: 0.96rem;
    line-height: 1.6;
    white-space: nowrap;
  }

  .n3-symbol {
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace;
    white-space: nowrap;
  }

  .n3-small {
    font-size: 0.95rem;
  }
</style>

# A Canonical-Expansion Theorem for Basic N3 Entailment

<div class="n3-note">
<strong>Draft status.</strong> Candidate text for a publication section.<br>
<strong>Scope.</strong> Basic N3 entailment only. This does not cover the additional semantics of
<code>log:</code> built-ins such as <code>log:implies</code>.
</div>

## Abstract

We give a syntactic characterisation of basic entailment for finite, closed, normalised abstract N3 graphs. The result is an N3 analogue of the RDF simple-entailment interpolation lemma. Because N3 includes explicit universal variables and quoted graph terms, the appropriate object is not the premise graph itself but its **canonical expansion**: the union of all ground universal instances of the premise, with fresh witnesses for existential variables. Basic N3 entailment is then equivalent to containment of every universal instance of the conclusion, after a suitable existential instantiation, in this canonical expansion.

## Background and notation

The N3 semantics defines an abstract graph as a triple:

<div class="n3-equation">
G = (U, E, F)
</div>

where:

- <span class="n3-symbol">U</span> is the set of universally scoped variables;
- <span class="n3-symbol">E</span> is the set of existentially scoped variables;
- <span class="n3-symbol">F</span> is a finite set of N3 triples.

N3 terms include IRIs, literals, variables, lists, and graph terms. Ground graph terms are compared modulo the N3 graph-term isomorphism relation.

The semantics of variables uses assignments that provide both:

1. a denotation in the semantic domain; and
2. a ground term representation.

This second component is essential because variables may occur freely inside quoted graph terms. The semantic operation of **total application** grounds such occurrences recursively, while respecting variable scope inside nested graph terms.

Throughout this section, entailment means **basic N3 entailment**.

## Normalisation assumptions

Let

<div class="n3-equation">
G = (U<sub>G</sub>, E<sub>G</sub>, F<sub>G</sub>) &nbsp;&nbsp; and &nbsp;&nbsp;
H = (U<sub>H</sub>, E<sub>H</sub>, F<sub>H</sub>)
</div>

be finite, closed, normalised abstract N3 graphs.

We assume:

1. variables of <span class="n3-symbol">G</span> and <span class="n3-symbol">H</span> have been renamed apart;
2. free variables, if any occur in a concrete syntax presentation, have first been added to the appropriate universal-variable set;
3. graph terms are considered modulo graph-term isomorphism;
4. equality of triples containing graph terms is taken modulo that isomorphism.

These assumptions are standard hygiene conditions and do not affect entailment.

## Ground terms with witnesses

Let

<div class="n3-equation">
GT*
</div>

be the set of ground N3 terms over the language, extended with a countably infinite supply of fresh witness names.

These witness names play the same role as labelled nulls in canonical-model constructions.

## Ground instances

For a graph

<div class="n3-equation">
K = (U<sub>K</sub>, E<sub>K</sub>, F<sub>K</sub>)
</div>

and a map

<div class="n3-equation">
μ : U<sub>K</sub> ∪ E<sub>K</sub> → GT*
</div>

write

<div class="n3-equation">
μ[K]
</div>

for the ground instance of <span class="n3-symbol">K</span> obtained by applying <span class="n3-symbol">μ</span> to <span class="n3-symbol">F<sub>K</sub></span>.

The application is total:

- direct occurrences of variables in <span class="n3-symbol">U<sub>K</sub> ∪ E<sub>K</sub></span> are replaced by their <span class="n3-symbol">μ</span>-images;
- lists are instantiated componentwise;
- graph terms are instantiated recursively;
- variables scoped inside nested graph terms are not replaced by an outer substitution.

Equivalently, if <span class="n3-symbol">⟨L⟩</span> is a graph term, then its instance is:

<div class="n3-equation">
⟨ μ<sup>t</sup>(L) ⟩
</div>

where <span class="n3-symbol">μ<sup>t</sup></span> denotes total application.

## Canonical expansion

For every assignment

<div class="n3-equation">
σ : U<sub>G</sub> → GT*
</div>

choose fresh witness names

<div class="n3-equation">
w<sub>e,σ</sub>
</div>

for every

<div class="n3-equation">
e ∈ E<sub>G</sub>.
</div>

Define

<div class="n3-equation">
σ̂ = σ ∪ { e ↦ w<sub>e,σ</sub> | e ∈ E<sub>G</sub> }.
</div>

The **canonical expansion** of <span class="n3-symbol">G</span>, written <span class="n3-symbol">C(G)</span>, is:

<div class="n3-equation">
C(G) = ⋃<sub>σ : U<sub>G</sub> → GT*</sub> σ̂[F<sub>G</sub>].
</div>

Membership in <span class="n3-symbol">C(G)</span> is taken modulo graph-term isomorphism.

Intuitively, <span class="n3-symbol">C(G)</span> contains every ground universal instance of <span class="n3-symbol">G</span>, with fresh witnesses for the existential variables of each such instance.

---

## Theorem

<div class="n3-theorem">
<strong>Canonical expansion characterisation of basic N3 entailment.</strong>

Let

<div class="n3-equation">
G = (U<sub>G</sub>, E<sub>G</sub>, F<sub>G</sub>) &nbsp;&nbsp; and &nbsp;&nbsp;
H = (U<sub>H</sub>, E<sub>H</sub>, F<sub>H</sub>)
</div>

be finite, closed, normalised abstract N3 graphs.

Then

<div class="n3-equation">
G ⊨ H
</div>

if and only if, for every assignment

<div class="n3-equation">
α : U<sub>H</sub> → GT*
</div>

there exists an assignment

<div class="n3-equation">
β : E<sub>H</sub> → GT*
</div>

such that

<div class="n3-equation">
(α ∪ β)[F<sub>H</sub>] ⊆ C(G).
</div>

In words: <strong><span class="n3-symbol">G</span> basic-entails <span class="n3-symbol">H</span> exactly when every universal instance of <span class="n3-symbol">H</span> has an existential instance contained in the canonical expansion of <span class="n3-symbol">G</span>.</strong>
</div>

---

## Proof

### Soundness

Assume that for every assignment

<div class="n3-equation">
α : U<sub>H</sub> → GT*
</div>

there exists

<div class="n3-equation">
β : E<sub>H</sub> → GT*
</div>

such that

<div class="n3-equation">
(α ∪ β)[F<sub>H</sub>] ⊆ C(G).
</div>

We prove that

<div class="n3-equation">
G ⊨ H.
</div>

Let <span class="n3-symbol">I</span> be an arbitrary basic interpretation such that

<div class="n3-equation">
I ⊨ G.
</div>

We must show that

<div class="n3-equation">
I ⊨ H.
</div>

Let <span class="n3-symbol">A</span> be an arbitrary assignment for the universal variables <span class="n3-symbol">U<sub>H</sub></span>. For each <span class="n3-symbol">u ∈ U<sub>H</sub></span>, write

<div class="n3-equation">
A(u) = (A<sub>1</sub>(u), A<sub>2</sub>(u)),
</div>

where <span class="n3-symbol">A<sub>1</sub>(u)</span> is the denotation and <span class="n3-symbol">A<sub>2</sub>(u)</span> is a ground term representation satisfying

<div class="n3-equation">
I(A<sub>2</sub>(u)) = A<sub>1</sub>(u).
</div>

Define

<div class="n3-equation">
α(u) = A<sub>2</sub>(u).
</div>

By the syntactic assumption, there exists

<div class="n3-equation">
β : E<sub>H</sub> → GT*
</div>

such that

<div class="n3-equation">
(α ∪ β)[F<sub>H</sub>] ⊆ C(G).
</div>

Only finitely many triples of <span class="n3-symbol">C(G)</span> are used in this inclusion. Each such triple belongs to some canonical instance of <span class="n3-symbol">G</span>, generated by some universal assignment

<div class="n3-equation">
σ : U<sub>G</sub> → GT*.
</div>

For every such <span class="n3-symbol">σ</span>, define an assignment <span class="n3-symbol">A<sub>σ</sub></span> for the universal variables of <span class="n3-symbol">G</span> in <span class="n3-symbol">I</span> by

<div class="n3-equation">
A<sub>σ</sub>(u) = (I(σ(u)), σ(u)).
</div>

Since

<div class="n3-equation">
I ⊨ G,
</div>

there exists an assignment <span class="n3-symbol">B<sub>σ</sub></span> for <span class="n3-symbol">E<sub>G</sub></span> such that

<div class="n3-equation">
I[A<sub>σ</sub> • B<sub>σ</sub>](F<sub>G</sub>) = true.
</div>

Now replace each canonical witness name

<div class="n3-equation">
w<sub>e,σ</sub>
</div>

occurring in the selected finite fragment by the corresponding ground term representation

<div class="n3-equation">
B<sub>σ,2</sub>(e).
</div>

Call this replacement map <span class="n3-symbol">ρ</span>, and extend <span class="n3-symbol">ρ</span> recursively to lists and graph terms. The replacement preserves sharing: the same witness name is always replaced by the same witness term.

Because each selected triple came from an instance of <span class="n3-symbol">G</span> that is true in <span class="n3-symbol">I</span>, every triple in

<div class="n3-equation">
ρ((α ∪ β)[F<sub>H</sub>])
</div>

is true in <span class="n3-symbol">I</span>.

Define an existential assignment <span class="n3-symbol">B</span> for <span class="n3-symbol">E<sub>H</sub></span> by

<div class="n3-equation">
B(e) = (I(ρ(β(e))), ρ(β(e))).
</div>

Then

<div class="n3-equation">
I[A • B](F<sub>H</sub>) = true.
</div>

Since <span class="n3-symbol">A</span> was arbitrary, we have

<div class="n3-equation">
I ⊨ H.
</div>

Since <span class="n3-symbol">I</span> was arbitrary among models of <span class="n3-symbol">G</span>, it follows that

<div class="n3-equation">
G ⊨ H.
</div>

This proves soundness.

---

### Completeness

Assume that the syntactic condition fails.

Then there exists an assignment

<div class="n3-equation">
α : U<sub>H</sub> → GT*
</div>

such that, for every assignment

<div class="n3-equation">
β : E<sub>H</sub> → GT*,
</div>

we have

<div class="n3-equation">
(α ∪ β)[F<sub>H</sub>] ⊄ C(G).
</div>

We construct a basic interpretation <span class="n3-symbol">I<sub>G</sub></span> such that

<div class="n3-equation">
I<sub>G</sub> ⊨ G
</div>

but

<div class="n3-equation">
I<sub>G</sub> ⊭ H.
</div>

Let the domain of <span class="n3-symbol">I<sub>G</sub></span> be

<div class="n3-equation">
Δ<sub>I<sub>G</sub></sub> = GT* / ≃,
</div>

the set of ground N3 terms modulo graph-term isomorphism.

For every IRI or literal <span class="n3-symbol">a</span>, define

<div class="n3-equation">
D<sub>I<sub>G</sub></sub>(a) = [a].
</div>

For every ground graph term <span class="n3-symbol">⟨K⟩</span>, define

<div class="n3-equation">
Q<sub>I<sub>G</sub></sub>(⟨K⟩) = [⟨K⟩].
</div>

Thus graph terms are interpreted as representatives of their own isomorphism classes, and isomorphic graph terms receive the same value.

Define the extension relation by

<div class="n3-equation">
EXT<sub>I<sub>G</sub></sub> = { ([s], [p], [o]) | (s, p, o) ∈ C(G) }.
</div>

We first show that

<div class="n3-equation">
I<sub>G</sub> ⊨ G.
</div>

Let <span class="n3-symbol">A</span> be any assignment for <span class="n3-symbol">U<sub>G</sub></span>. Put

<div class="n3-equation">
σ(u) = A<sub>2</sub>(u).
</div>

By construction of <span class="n3-symbol">C(G)</span>, the canonical instance of <span class="n3-symbol">G</span> corresponding to <span class="n3-symbol">σ</span> is contained in <span class="n3-symbol">C(G)</span>. For every existential variable <span class="n3-symbol">e ∈ E<sub>G</sub></span>, choose the canonical witness

<div class="n3-equation">
w<sub>e,σ</sub>.
</div>

This gives an existential assignment <span class="n3-symbol">B</span> such that every triple in

<div class="n3-equation">
(A • B)[F<sub>G</sub>]
</div>

belongs to <span class="n3-symbol">EXT<sub>I<sub>G</sub></sub></span>. Hence

<div class="n3-equation">
I<sub>G</sub>[A • B](F<sub>G</sub>) = true.
</div>

Since <span class="n3-symbol">A</span> was arbitrary,

<div class="n3-equation">
I<sub>G</sub> ⊨ G.
</div>

We now show that

<div class="n3-equation">
I<sub>G</sub> ⊭ H.
</div>

Use the assignment for <span class="n3-symbol">U<sub>H</sub></span> determined by the failing <span class="n3-symbol">α</span>:

<div class="n3-equation">
A(u) = ([α(u)], α(u)).
</div>

Suppose, for contradiction, that

<div class="n3-equation">
I<sub>G</sub> ⊨ H.
</div>

Then there would exist an existential assignment <span class="n3-symbol">B</span> for <span class="n3-symbol">E<sub>H</sub></span>. Define

<div class="n3-equation">
β(e) = B<sub>2</sub>(e).
</div>

Since truth in <span class="n3-symbol">I<sub>G</sub></span> is exactly membership in <span class="n3-symbol">C(G)</span>, this would imply

<div class="n3-equation">
(α ∪ β)[F<sub>H</sub>] ⊆ C(G),
</div>

contradicting the choice of <span class="n3-symbol">α</span>.

Therefore

<div class="n3-equation">
I<sub>G</sub> ⊭ H.
</div>

Thus there exists a model of <span class="n3-symbol">G</span> that is not a model of <span class="n3-symbol">H</span>, so

<div class="n3-equation">
G ⊭ H.
</div>

This proves completeness.

---

## Relation with the RDF interpolation lemma

The RDF interpolation lemma states that, for simple RDF entailment, a graph <span class="n3-symbol">S</span> entails a graph <span class="n3-symbol">E</span> exactly when some subgraph of <span class="n3-symbol">S</span> is an instance of <span class="n3-symbol">E</span>.

The theorem above is the corresponding statement for basic N3 entailment.

In the RDF fragment:

- there are no graph terms;
- there are no N3 lists as first-class terms;
- there are no universal variables;
- existential variables correspond to RDF blank nodes;
- the canonical expansion <span class="n3-symbol">C(G)</span> is just <span class="n3-symbol">G</span>, up to renaming of existential witnesses.

The condition

<div class="n3-equation">
there exists β : E<sub>H</sub> → GT* such that β[F<sub>H</sub>] ⊆ C(G)
</div>

then says precisely that an instance of <span class="n3-symbol">H</span> is contained in <span class="n3-symbol">G</span>. Thus the N3 theorem conservatively generalises the RDF interpolation lemma.

The essential extra feature in N3 is the presence of explicit universal variables. Because of them, a conclusion may be supported by several different universal instances of the premise.

For example, the graph

<div class="n3-equation">
({x}, ∅, {P(x), Q(x)})
</div>

entails

<div class="n3-equation">
({u, v}, ∅, {P(u), Q(v)}).
</div>

However, the two triples in the conclusion may come from two different instances of the premise. This is why a direct “subgraph of <span class="n3-symbol">G</span>” formulation is insufficient; the correct object is the canonical expansion <span class="n3-symbol">C(G)</span>.

---

## Scope and limitations

This theorem concerns **basic N3 entailment** only.

It does not cover the additional semantics of predicates such as <code>log:implies</code>. The N3 draft treats log interpretation separately from basic interpretation, adding special semantic conditions for predicates in the <code>log:</code> namespace.

Thus the theorem should be read as the N3 analogue of simple RDF entailment, not as a completeness theorem for full N3 reasoning with logical built-ins.

## References

- [Notation3 Language: Semantics](https://w3c-cg.github.io/N3/spec/semantics.html)
- [RDF Semantics: Interpolation lemma for simple entailment](https://www.w3.org/TR/rdf-mt/)
