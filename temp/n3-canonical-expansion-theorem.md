---
title: "A Canonical-Expansion Theorem for Basic N3 Entailment"
description: "A theorem and proof for simple/basic entailment in Notation3, related to interpolation."
layout: default
---

<!--
This Markdown file is intended to render well both on GitHub and as a GitHub Pages/Jekyll page.
If your GitHub Pages theme does not render TeX math automatically, add MathJax to the page
or replace the display equations with preformatted blocks.
-->

# A Canonical-Expansion Theorem for Basic N3 Entailment

**Draft status.** Candidate text for a note.  
**Scope.** Basic N3 entailment only; this does not cover the additional semantics of `log:` built-ins such as `log:implies`.

## Abstract

We give a syntactic characterisation of basic entailment for finite, closed, normalised abstract N3 graphs. The result is an N3 analogue of the RDF simple-entailment interpolation lemma. Because N3 includes explicit universal variables and quoted graph terms, the appropriate object is not the premise graph itself but its **canonical expansion**: the union of all ground universal instances of the premise, with fresh witnesses for existential variables. Basic N3 entailment is then equivalent to containment of every universal instance of the conclusion, after a suitable existential instantiation, in this canonical expansion.

## Background and notation

The N3 semantics defines an abstract graph as a triple

\[
G=(U,E,F),
\]

where:

- \(U\) is the set of universally scoped variables;
- \(E\) is the set of existentially scoped variables;
- \(F\) is a finite set of N3 triples.

N3 terms include IRIs, literals, variables, lists, and graph terms. Ground graph terms are compared modulo the N3 graph-term isomorphism relation.

The semantics of variables uses assignments that provide both:

1. a denotation in the semantic domain; and
2. a ground term representation.

This second component is essential because variables may occur freely inside quoted graph terms. The semantic operation of **total application** grounds such occurrences recursively, while respecting variable scope inside nested graph terms.

Throughout this section, entailment means **basic N3 entailment**.

## Normalisation assumptions

Let

\[
G=(U_G,E_G,F_G)
\qquad\text{and}\qquad
H=(U_H,E_H,F_H)
\]

be finite, closed, normalised abstract N3 graphs.

We assume:

1. variables of \(G\) and \(H\) have been renamed apart;
2. free variables, if any occur in a concrete syntax presentation, have first been added to the appropriate universal-variable set;
3. graph terms are considered modulo graph-term isomorphism;
4. equality of triples containing graph terms is taken modulo that isomorphism.

These assumptions are standard hygiene conditions and do not affect entailment.

## Ground terms with witnesses

Let

\[
\mathsf{GT}^{\ast}
\]

be the set of ground N3 terms over the language, extended with a countably infinite supply of fresh witness names.

These witness names play the same role as labelled nulls in canonical-model constructions.

## Ground instances

For a graph

\[
K=(U_K,E_K,F_K)
\]

and a map

\[
\mu:U_K\cup E_K\to\mathsf{GT}^{\ast},
\]

write

\[
\mu[K]
\]

for the ground instance of \(K\) obtained by applying \(\mu\) to \(F_K\).

The application is total:

- direct occurrences of variables in \(U_K\cup E_K\) are replaced by their \(\mu\)-images;
- lists are instantiated componentwise;
- graph terms are instantiated recursively;
- variables scoped inside nested graph terms are not replaced by an outer substitution.

Equivalently, if \(\langle L\rangle\) is a graph term, then its instance is

\[
\langle \mu^t(L)\rangle,
\]

where \(\mu^t\) denotes total application.

## Canonical expansion

For every assignment

\[
\sigma:U_G\to\mathsf{GT}^{\ast},
\]

choose fresh witness names

\[
w_{e,\sigma}
\]

for every

\[
e\in E_G.
\]

Define

\[
\widehat{\sigma}
=
\sigma
\cup
\{\,e\mapsto w_{e,\sigma}\mid e\in E_G\,\}.
\]

The **canonical expansion** of \(G\), written \(\mathcal C(G)\), is

\[
\mathcal C(G)
=
\bigcup_{\sigma:U_G\to\mathsf{GT}^{\ast}}
\widehat{\sigma}[F_G].
\]

Membership in \(\mathcal C(G)\) is taken modulo graph-term isomorphism.

Intuitively, \(\mathcal C(G)\) contains every ground universal instance of \(G\), with fresh witnesses for the existential variables of each such instance.

---

## Theorem

Let

\[
G=(U_G,E_G,F_G)
\qquad\text{and}\qquad
H=(U_H,E_H,F_H)
\]

be finite, closed, normalised abstract N3 graphs.

Then

\[
G\models H
\]

if and only if, for every assignment

\[
\alpha:U_H\to\mathsf{GT}^{\ast},
\]

there exists an assignment

\[
\beta:E_H\to\mathsf{GT}^{\ast}
\]

such that

\[
(\alpha\cup\beta)[F_H]\subseteq\mathcal C(G).
\]

In words:

> \(G\) basic-entails \(H\) exactly when every universal instance of \(H\) has an existential instance contained in the canonical expansion of \(G\).

---

## Proof

### Soundness

Assume that for every assignment

\[
\alpha:U_H\to\mathsf{GT}^{\ast}
\]

there exists

\[
\beta:E_H\to\mathsf{GT}^{\ast}
\]

such that

\[
(\alpha\cup\beta)[F_H]\subseteq\mathcal C(G).
\]

We prove that

\[
G\models H.
\]

Let \(I\) be an arbitrary basic interpretation such that

\[
I\models G.
\]

We must show that

\[
I\models H.
\]

Let \(A\) be an arbitrary assignment for the universal variables \(U_H\). For each \(u\in U_H\), write

\[
A(u)=(A_1(u),A_2(u)),
\]

where \(A_1(u)\) is the denotation and \(A_2(u)\) is a ground term representation satisfying

\[
I(A_2(u))=A_1(u).
\]

Define

\[
\alpha(u)=A_2(u).
\]

By the syntactic assumption, there exists

\[
\beta:E_H\to\mathsf{GT}^{\ast}
\]

such that

\[
(\alpha\cup\beta)[F_H]\subseteq\mathcal C(G).
\]

Only finitely many triples of \(\mathcal C(G)\) are used in this inclusion. Each such triple belongs to some canonical instance of \(G\), generated by some universal assignment

\[
\sigma:U_G\to\mathsf{GT}^{\ast}.
\]

For every such \(\sigma\), define an assignment \(A_\sigma\) for the universal variables of \(G\) in \(I\) by

\[
A_\sigma(u)=(I(\sigma(u)),\sigma(u)).
\]

Since

\[
I\models G,
\]

there exists an assignment \(B_\sigma\) for \(E_G\) such that

\[
I[A_\sigma\bullet B_\sigma](F_G)=\mathrm{true}.
\]

Now replace each canonical witness name

\[
w_{e,\sigma}
\]

occurring in the selected finite fragment by the corresponding ground term representation

\[
B_{\sigma,2}(e).
\]

Call this replacement map \(\rho\), and extend \(\rho\) recursively to lists and graph terms. The replacement preserves sharing: the same witness name is always replaced by the same witness term.

Because each selected triple came from an instance of \(G\) that is true in \(I\), every triple in

\[
\rho((\alpha\cup\beta)[F_H])
\]

is true in \(I\).

Define an existential assignment \(B\) for \(E_H\) by

\[
B(e)=
\bigl(I(\rho(\beta(e))),\rho(\beta(e))\bigr).
\]

Then

\[
I[A\bullet B](F_H)=\mathrm{true}.
\]

Since \(A\) was arbitrary, we have

\[
I\models H.
\]

Since \(I\) was arbitrary among models of \(G\), it follows that

\[
G\models H.
\]

This proves soundness.

---

### Completeness

Assume that the syntactic condition fails.

Then there exists an assignment

\[
\alpha:U_H\to\mathsf{GT}^{\ast}
\]

such that, for every assignment

\[
\beta:E_H\to\mathsf{GT}^{\ast},
\]

we have

\[
(\alpha\cup\beta)[F_H]\nsubseteq\mathcal C(G).
\]

We construct a basic interpretation \(I_G\) such that

\[
I_G\models G
\]

but

\[
I_G\not\models H.
\]

Let the domain of \(I_G\) be

\[
\Delta_{I_G}
=
\mathsf{GT}^{\ast}/\!\simeq,
\]

the set of ground N3 terms modulo graph-term isomorphism.

For every IRI or literal \(a\), define

\[
D_{I_G}(a)=[a].
\]

For every ground graph term \(\langle K\rangle\), define

\[
Q_{I_G}(\langle K\rangle)=[\langle K\rangle].
\]

Thus graph terms are interpreted as representatives of their own isomorphism classes, and isomorphic graph terms receive the same value.

Define the extension relation by

\[
EXT_{I_G}
=
\{\,([s],[p],[o])\mid (s,p,o)\in\mathcal C(G)\,\}.
\]

We first show that

\[
I_G\models G.
\]

Let \(A\) be any assignment for \(U_G\). Put

\[
\sigma(u)=A_2(u).
\]

By construction of \(\mathcal C(G)\), the canonical instance of \(G\) corresponding to \(\sigma\) is contained in \(\mathcal C(G)\). For every existential variable \(e\in E_G\), choose the canonical witness

\[
w_{e,\sigma}.
\]

This gives an existential assignment \(B\) such that every triple in

\[
(A\bullet B)[F_G]
\]

belongs to \(EXT_{I_G}\). Hence

\[
I_G[A\bullet B](F_G)=\mathrm{true}.
\]

Since \(A\) was arbitrary,

\[
I_G\models G.
\]

We now show that

\[
I_G\not\models H.
\]

Use the assignment for \(U_H\) determined by the failing \(\alpha\):

\[
A(u)=([\alpha(u)],\alpha(u)).
\]

Suppose, for contradiction, that

\[
I_G\models H.
\]

Then there would exist an existential assignment \(B\) for \(E_H\). Define

\[
\beta(e)=B_2(e).
\]

Since truth in \(I_G\) is exactly membership in \(\mathcal C(G)\), this would imply

\[
(\alpha\cup\beta)[F_H]\subseteq\mathcal C(G),
\]

contradicting the choice of \(\alpha\).

Therefore

\[
I_G\not\models H.
\]

Thus there exists a model of \(G\) that is not a model of \(H\), so

\[
G\not\models H.
\]

This proves completeness.

---

## Relation with the RDF interpolation lemma

The RDF interpolation lemma states that, for simple RDF entailment, a graph \(S\) entails a graph \(E\) exactly when some subgraph of \(S\) is an instance of \(E\).

The theorem above is the corresponding statement for basic N3 entailment.

In the RDF fragment:

- there are no graph terms;
- there are no N3 lists as first-class terms;
- there are no universal variables;
- existential variables correspond to RDF blank nodes;
- the canonical expansion \(\mathcal C(G)\) is just \(G\), up to renaming of existential witnesses.

The condition

\[
\exists\beta:E_H\to\mathsf{GT}^{\ast}
\quad
\beta[F_H]\subseteq\mathcal C(G)
\]

then says precisely that an instance of \(H\) is contained in \(G\). Thus the N3 theorem conservatively generalises the RDF interpolation lemma.

The essential extra feature in N3 is the presence of explicit universal variables. Because of them, a conclusion may be supported by several different universal instances of the premise.

For example, the graph

\[
(\{x\},\emptyset,\{P(x),Q(x)\})
\]

entails

\[
(\{u,v\},\emptyset,\{P(u),Q(v)\}).
\]

However, the two triples in the conclusion may come from two different instances of the premise. This is why a direct “subgraph of \(G\)” formulation is insufficient; the correct object is the canonical expansion

\[
\mathcal C(G).
\]

---

## Scope and limitations

This theorem concerns **basic N3 entailment** only.

It does not cover the additional semantics of predicates such as `log:implies`. The N3 draft treats log interpretation separately from basic interpretation, adding special semantic conditions for predicates in the `log:` namespace.

Thus the theorem should be read as the N3 analogue of simple RDF entailment, not as a completeness theorem for full N3 reasoning with logical built-ins.

## References

- [Notation3 Language: Semantics](https://w3c-cg.github.io/N3/spec/semantics.html)
- [RDF Semantics: Interpolation lemma for simple entailment](https://www.w3.org/TR/rdf-mt/)
