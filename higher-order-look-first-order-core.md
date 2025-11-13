# Higher-Order Look, First-Order Core

## Abstract

We recall a simple device, due to Hayes and Menzel, for giving a **higher-order look** to a logic whose **semantics remains first-order**. Predicates and relations are treated as first-order objects (intensions), and their application is mediated by a fixed family of predicates (\mathsf{Holds}_n). This yields a straightforward embedding of a higher-order-looking surface language into ordinary first-order logic (FOL), and matches neatly the way RDF and related Web standards treat URIs and properties.

---

## 1 Idea in one paragraph

The key move is to separate **naming a relation** from **applying a relation**.

* Relation names (symbols, URIs) are interpreted as **first-order objects**.
* For each arity (n), a distinguished predicate
  [
  \mathsf{Holds}_n(r,x_1,\dots,x_n)
  ]
  says: “the relation named by (r) holds of (x_1,\dots,x_n).”

Higher-order-looking formulas such as “(\forall P)” or “(P(x,y))” are then understood as **quantifying over names** and using (\mathsf{Holds}_n) for application. The model theory is purely first-order; the “higher-order” aspect is only in the surface syntax.

---

## 2 The first-order core

We fix a standard first-order language with equality and add, for each arity (n \ge 1),

[
\mathsf{Holds}_n(r,x_1,\dots,x_n).
]

Intended reading:

* domain elements include **relation intensions** (e.g., URIs for properties);
* (\mathsf{Holds}_n(r,\vec x)) is true iff the tuple (\vec x) is in the **extension** of the relation named by (r).

We can also define **extensional equality** of (n)-ary relations:

[
\mathsf{ExtEq}_n(r,s) ;;:!!\iff;;
\forall x_1\dots x_n;
\bigl(\mathsf{Holds}_n(r,x_1,\dots,x_n)
\leftrightarrow
\mathsf{Holds}_n(s,x_1,\dots,x_n)\bigr).
]

Thus we distinguish:

* **intensional identity**: (r = s),
* **extensional equality**: (\mathsf{ExtEq}_n(r,s)).

This mirrors, for example, RDF’s `IEXT` mapping from a property-resource to its extension, and more generally the intension/extension split emphasised in [3,4].

---

## 3 The translation (schematic)

Suppose the surface language allows:

* predicate application: (P(t_1,\dots,t_n));
* quantification over predicate variables: (\forall P), (\exists P);
* (optionally) equality between predicates.

We map this into the (\mathsf{Holds}_n)-language as follows.

1. **Application**

   [
   P(t_1,\dots,t_n)
   \quad\mapsto\quad
   \mathsf{Holds}_n(P,T(t_1),\dots,T(t_n)),
   ]
   where (P) is now a *term* (variable or constant) naming a relation, and (T) is the recursive translation on terms.

2. **Quantification over predicates**

   [
   \forall P,\varphi
   \quad\mapsto\quad
   \forall p,T(\varphi),
   ]
   where (p) is an ordinary first-order variable. Inside (\varphi), each (P(\dots)) has already been translated to a (\mathsf{Holds}_n(p,\dots)) atom.

3. **Predicate equality**

   * intensional: (P = Q \mapsto p = q),
   * extensional: (P \equiv Q) (if present) (\mapsto \mathsf{ExtEq}_n(p,q)).

Hayes and Menzel show that such a translation can be made truth-preserving and adequate for KIF-style formalisms [1,2].

---

## 4 Tiny examples

### 4.1 Meta-properties of relations

In a CLIF-style syntax, with `r` ranging over relation names:

```lisp
(def Reflexive (r)
  (forall (x)
    (Holds2 r x x)))
```

This defines “`r` is reflexive” entirely within FOL.

For two binary relation names `likes` and `admires`:

```lisp
(forall (x y)
  (iff (Holds2 likes  x y)
       (Holds2 admires x y)))  ;; extensional equality

(= likes admires)              ;; intensional identity
```

The first states (\mathsf{ExtEq}_2(\text{likes},\text{admires})); the second states that the *names* are identical.

### 4.2 RDF triples

An RDF triple

```turtle
ex:Alice ex:likes ex:Bob .
```

can be read as the FOL atom

[
\mathsf{Holds}_2(\text{likes},\text{Alice},\text{Bob}),
]

with `likes` a first-order object whose extension is given by the usual RDF `IEXT` mapping [5].

---

## 5 Essence and limitations

* We get a **higher-order look** (quantifying over and talking about predicates) on top of a **first-order core**.
* The trick is entirely driven by:

  * first-order objects as intensions,
  * fixed (\mathsf{Holds}_n) predicates for application.

Limitations:

* One (\mathsf{Holds}_n) is needed per arity (n); this is harmless in practice.
* Truly **variadic** predicates (row variables, arbitrary arity) or strong comprehension principles go beyond this simple FOL setting.
* The approach is nevertheless sufficient for most Semantic Web-style reasoning and everyday meta-talk about relations.

---

## References

[1] P. Hayes and C. Menzel, *A Semantics for the Knowledge Interchange Format*, manuscript / technical report, 2001 (and later revisions).

[2] P. Hayes and C. Menzel, “A Logic for Ontologies,” in *Proceedings of IJCAI-01 Workshop on Ontologies and Information Sharing*, 2001.

[3] C. Menzel, “Knowledge Representation, the World Wide Web, and the Evolution of Logic,” *Synthese* 182(2), 2011.

[4] ISO/IEC 24707, *Common Logic (CL): a Framework for a Family of Logic-Based Languages*, 2018.

[5] P. Hayes, *RDF Semantics*, W3C Recommendation, 2004.

