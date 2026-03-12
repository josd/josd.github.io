# Higher-order Look, First-order Core

## Intuition

* **Intension** = the *named* property/relation (e.g., a URI like `ex:likes`).
* **Extension** = the *set of tuples* that satisfy it.
* The Hayes–Menzel move: treat relation *names* as ordinary **first-order objects**, and mediate application with fixed **first-order predicates** `Holdsₙ` (and `Appₙ` for function application). This yields a **truth-preserving translation** of the higher-order-looking syntax into orthodox FOL. 
* On the Web this fits naturally: **URIs are logical constants** (intensions); **property extensions** are given by an interpretation map `IEXT` from property-resources to sets of pairs (their extensions). ([W3C][1])

---

## Signature (pure FOL)

For each arity `n ≥ 1`, add a predicate:

* `Holdsₙ(r, x₁, …, xₙ)` (“the relation named by `r` holds of those args”).
  Everything you “apply” (predicates, classes, properties) is just a *term* naming an intension; `Holdsₙ` links that name to its extension. 

Optional but common:

* `ExtEqₙ(r, s) := ∀x₁…xₙ( Holdsₙ(r,x₁,…,xₙ) ↔ Holdsₙ(s,x₁,…,xₙ) )` for **extensional equality** (distinct from intensional identity `r = s`). This intension/extension separation is emphasized by Menzel. ([jfsowa.com][2])

---

## Translation schema (HO → FO)

* **Predicate application**
  `P(t₁,…,tₙ)`  ↦  `Holdsₙ(P, T(t₁), …, T(tₙ))`. 
* **Quantification over predicates**
  `∀P φ`  ↦  `∀p T(φ)` (now `p` ranges over *objects* naming relations). 
* **Predicate equality**
  intensional `P = Q` stays `p = q`; extensional equality becomes `ExtEqₙ(p,q)`. ([jfsowa.com][2])

*A concise third-party summary of the same “Holdsₙ” trick appears in Horrocks et al., describing Hayes–Menzel’s translation explicitly.* 

---

## Micro-examples

### RDF intuition → FOL core

RDF triple

```
ex:Alice ex:likes ex:Bob .
```

reads as

```
Holds2(likes, Alice, Bob)
```

since URIs are **constants** and **property extensions** are given by `IEXT`. ([W3C][1])

---

## What you *can* do (cleanly) in FOL

* **Quantify over “predicates”** (really: over **names** of predicates).
* Define meta-properties (reflexive, transitive, functional, …) using only `Holdsₙ`.
* Keep Web-style naming (URIs/IRIs) first-class while retaining a **first-order model theory** (as in Common Logic). 

---

## Pitfalls & notes

* You need one `Holdsₙ` **per arity** you use (a schema; any given theory uses finitely many). 
* **Row/sequence variables** (variably-polyadic tricks) *do* push you beyond FOL; the FO story here is the `Holdsₙ` part. 
* **Comprehension/λ** (creating new relation-names from formulas) isn’t automatic in FOL; CL handles this conservatively while **including full FOL with equality** and supporting **IRIs as names** for open networks. 

---

## References

* **Hayes & Menzel (2001), “A Semantics for the Knowledge Interchange Format (SKIF)”** — proves that **quantification over relations is possible in FOL** and gives the explicit **`Holdsₙ`/`Appₙ` translation**. See “Mapping SKIF into conventional logic.” 
* **Menzel (2011), “Knowledge representation, the Web, and the evolution of logic,” Synthese** — explains the **type-free, name-centric** approach; separates **denotation vs relation-extension** (e.g., `rext('Married')`) and motivates the Web’s reliance on **URIs as names**. ([jfsowa.com][2])
* **W3C RDF Semantics (2004)** — treats **URI references as logical constants** and models **properties as first-class objects** with extensions via `IEXT` (the intension/extension split for Web vocabularies). ([W3C][1])
* **ISO/IEC 24707:2018 — Common Logic** — **includes full FOL with equality**, permits Web-friendly naming (**IRIs as names**), and supports open networks, while allowing “higher-order-looking” surface features without abandoning a **first-order model theory**. 
* **Horrocks et al., “Three Theses of Representation in the Semantic Web” (2003)** — independent summary of the **Hayes–Menzel `Holdsₙ` translation** (how HO-looking syntax is embedded in FOL). 

[1]: https://www.w3.org/TR/rdf-mt/ "RDF Semantics"
[2]: https://www.jfsowa.com/ikl/Menzel11.pdf "Synthese-CL"

