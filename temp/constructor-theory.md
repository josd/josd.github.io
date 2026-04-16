# Constructor Theory

Constructor theory is a proposal for how to formulate fundamental physics in a way that makes *possible* and *impossible* transformations primary. In the usual presentation of physics, one specifies dynamical laws together with initial conditions, and then computes what state a system will evolve into. Constructor theory asks a different kind of question: given a physical substrate, which transformations can in principle be performed on it, which cannot, and what laws explain that division? In that sense it is not primarily a replacement for quantum theory or thermodynamics, but a higher-level framework for expressing physical laws as constraints on tasks.

The basic motivation is that many central scientific statements are naturally phrased in this language already. The second law of thermodynamics says that some transformations are impossible. Quantum theory says that an arbitrary unknown quantum state cannot be cloned. Information theory distinguishes what can be copied, distinguished, compressed, or transmitted from what cannot. Biology, at a more abstract level, is full of questions about whether accurate replication, self-reproduction, and natural selection are physically possible under generic laws. Constructor theory tries to make that mode of explanation fundamental rather than derivative.

A useful intuition is to compare a trajectory with a machine. Ordinary dynamics tells us what trajectory a system follows. Constructor theory focuses instead on what kinds of machines, devices, catalysts, agents, or processes could repeatedly bring about a given transformation. A heat engine, a catalyst, a programmable computer controlling a robot arm, and a copying device are all examples of things that behave as constructors for suitable tasks. What matters is not their detailed microphysics in the first instance, but the fact that they can cause a transformation while retaining the ability to do so again.

## Why the framework is distinctive

The key conceptual move is that constructor theory puts *counterfactuals* into physics. Information is not just about what state a system actually has; it is also about which alternative states it could have had and which transformations between them are permitted. A bit is meaningful because two alternatives are available and can be acted on reliably. A law forbidding perpetual motion matters because it rules out a transformation that could otherwise have been attempted. Constructor theory therefore aims to express laws not merely as summaries of actual evolutions but as precise statements about the space of achievable tasks.

This is why it is often described as a **theory of principles**. It seeks principles from which subsidiary theories can be expressed in a common language: quantum information, thermodynamics, computation, and even some foundational features of biology. It remains a research programme rather than a finished, universally adopted formalism, but its vocabulary is precise enough to support nontrivial reformulations.

## The basic objects

The theory begins with a few primitive notions.

A **substrate** is any physical system that can undergo transformations. A qubit, a molecule, a gas in a box, a memory register, or a living cell can all serve as substrates.

An **attribute** is a set of physical states of a substrate that are regarded as equivalent for the purpose at hand. One may denote attributes by symbols such as `x`, `y`, or `z`. For example, the attribute `x` might mean “the spin is up along `z`,” or more coarsely “the gas occupies the left half of the box.” An attribute is therefore not necessarily a single microstate; it is a property.

A **variable** is a set of pairwise disjoint attributes of the same substrate:

```text
X = {x1, x2, ..., xn}
```

The intended interpretation is that the substrate can have one value of the variable at a time. A classical bit may be represented by a variable `X = {0, 1}`; a trit by `X = {0, 1, 2}`.

A **task** is an abstract specification of allowed input-output pairs on attributes. In the simplest notation,

```text
A = {x1 -> y1, x2 -> y2, ...}
```

One should read this as: whenever the substrate has attribute `xi`, the task requires the output to have attribute `yi`. A NOT operation on a bit is the task

```text
N = {0 -> 1, 1 -> 0}
```

A resetting operation is the task

```text
R0 = {0 -> 0, 1 -> 0}
```

A **constructor** for a task `A` is a physical system that, when presented with substrates in the allowed input attributes, brings about the corresponding output attributes and retains the ability to do so again. This “again” condition is essential. A constructor need not remain literally unchanged in every microscopic detail; it need only preserve its ability to keep performing the task to arbitrary accuracy.

## Possible and impossible tasks

The central distinction is between tasks that are **possible** and tasks that are **impossible**.

A task `A` is written as possible,

```text
A✓
```

when the laws of physics permit arbitrarily accurate and reliable approximations to a constructor for `A`. A task is written as impossible,

```text
A×
```

when no such arbitrarily accurate constructor can exist under the laws of physics.

This notation is deliberately stronger than saying that a task happens spontaneously or that it is easy to implement in practice. A possible task may require energy, error correction, catalysts, ancillas, a complex machine, or a long time. It is possible in principle, not necessarily cheap. Conversely, an impossible task is not merely technologically out of reach; it is forbidden by physical law.

This shift from trajectories to tasks is the core mathematical principle of constructor theory. Ordinary physics often answers the question

```text
given s(0), what is s(t)?
```

Constructor theory asks instead:

```text
given a task A, is A✓ or A×?
```

The idea is that much of fundamental physics can be reformulated in this second style.

## Composition principles

A framework about tasks needs rules for building complicated tasks out of simpler ones. Constructor theory therefore relies on composition principles.

If two tasks act on independent substrates, one can form their **parallel composition**:

```text
A ⊗ B
```

If

```text
A = {xi -> yi}
B = {uj -> vj}
```

then their parallel composition acts on the composite substrate and is informally given by

```text
A ⊗ B = {(xi, uj) -> (yi, vj)}
```

If the output attributes of one task match the input attributes of another, one can form a **serial composition**:

```text
B ∘ A
```

If

```text
A = {x -> y}
B = {y -> z}
```

then

```text
B ∘ A = {x -> z}
```

The underlying principle is that if two tasks are possible, then suitably composed networks of them should also be possible, provided the relevant substrates and side conditions are available. Constructor theory sometimes calls these arrangements **regular networks** of tasks. This is one reason it connects naturally to computation: algorithms and circuits are structured compositions of tasks.

## Information-theoretic principles

One of the most developed parts of constructor theory is the **constructor theory of information**. Here the aim is to define information not by Shannon entropy or Hilbert-space axioms at the outset, but in terms of the kinds of transformations that physical substrates permit.

A variable

```text
X = {x1, ..., xn}
```

is an **information variable** if permutations of its attributes are possible and if the variable can be copied in the right sense. The permutation requirement says that for any permutation `pi` on the labels,

```text
Pi_pi(X) = {x -> pi(x) : x in X}✓
```

Informally, the substrate can faithfully support reversible relabellings of the values of `X`.

The copying task for a variable `X` is the task

```text
C(X) = {(x, x0) -> (x, x) : x in X}
```

where `x0` is a receptive blank attribute. If this task is possible, then one can replicate the value of the variable onto another instance of the substrate. A substrate possessing at least one information variable is an **information medium**.

This already captures a large part of what one wants from physical information: a physically instantiated variable whose values can be reliably transformed, copied, and used compositionally. Classical bits are straightforward examples. Quantum systems are subtler: not every set of states forms a clonable variable, and this limitation is precisely the kind of law constructor theory is meant to express.

A variable `X` is **distinguishable** if there is a possible task that maps each attribute in `X` to a distinct value of some information variable. In loose notation,

```text
D(X) = {xi -> i}✓
```

Distinguishability is therefore itself a task-theoretic notion, not an extra primitive imported from elsewhere.

The no-cloning principle in quantum theory appears naturally in this language. For generic quantum states `{psi_i}` that are not mutually orthogonal, the universal cloning task

```text
{(psi_i, psi_0) -> (psi_i, psi_i)}
```

is impossible. Constructor theory treats this not as a quirk of a Hilbert-space proof alone, but as a law about the impossibility of a certain task.

## Thermodynamic principles in constructor-theoretic form

Constructor theory has also been applied to thermodynamics, where the goal is to state the laws as exact statements about tasks rather than as approximate statistical regularities.

The general idea is that one identifies classes of tasks corresponding to work-like transformations, heat-like transformations, and adiabatically possible transformations. Instead of saying only that entropy tends to increase in typical macroscopic evolutions, one says that certain tasks and their transposes do not stand on the same footing. In particular, there can exist tasks `A` such that `A✓` while the transpose or reverse task `A^T` is impossible under the relevant adiabatic conditions.

In schematic form,

```text
A✓ does not imply (A^T)✓
```

That asymmetry is the task-theoretic expression of irreversibility. It is not the whole of thermodynamics, but it shows how the second law can be reformulated as a sharp asymmetry in the space of possible transformations.

The ambition here is significant: if successful, thermodynamic laws can be stated without relying fundamentally on coarse-graining, equilibrium ensembles, or an appeal to “large numbers” as the conceptual starting point. The framework is meant to apply exactly, even when the systems are microscopic.

## Replication, self-reproduction, and life

A different application concerns the physics of life. Constructor theory asks what must be true of physical law for high-fidelity replication and self-reproduction to be possible without embedding biological design directly into the laws.

The rough picture is that a self-reproducer can be analysed as a network of constructors and information-bearing components. A replicator stores digital information; a vehicle uses that information to build or maintain structures, including copies of the replicator itself. The conceptual claim is that life does not require special “vital” laws. What is required is that physics permit suitable information variables, copying tasks, and controlled construction tasks. In this way Darwinian evolution can be analysed as a pattern of possible tasks supported by generic no-design laws.

## The core mathematical attitude

Constructor theory is mathematical in a somewhat unusual way. Its primitive mathematics is not an equation of motion but a logic of tasks. The objects are substrates, attributes, variables, and tasks; the central predicates are possibility and impossibility; and the important algebraic structure comes from composition, interoperability, and constraints on copying, distinguishing, and transforming variables.

One can summarize the core formal attitude as follows.

1. **Represent physical capabilities as tasks.** A law is fundamentally about whether tasks are admitted or forbidden.
2. **Use attributes rather than exact microstates where appropriate.** This makes the framework naturally suited to information and thermodynamics.
3. **Treat possibility as an exact notion.** “Possible” means achievable to arbitrary accuracy by some constructor allowed by the laws.
4. **Demand closure under composition.** Complex constructions should arise from networks of simpler possible tasks.
5. **Recover familiar theories as subsidiary theories.** Quantum information, thermodynamics, and computation should be expressible in this language.

The result is a framework that sits somewhere between operational physics, computer science, and the logic of physical law.

## What constructor theory is good for

The most successful use of constructor theory so far is conceptual clarification. It gives a unified language for talking about information, computation, thermodynamic irreversibility, and biological replication. It is especially strong wherever impossibility statements matter: no-cloning, no perpetual motion, no exact reversal under certain constraints, and no generic self-reproduction without the appropriate information-bearing structure.

It is less useful, at least at present, as a day-to-day calculational tool. One would not ordinarily use constructor theory to compute a scattering amplitude, design a transistor layout, or solve fluid equations. Its role is more foundational. It aims to say what those calculations are *about* at the deepest level: which transformations are available in our universe and why.

That makes it best understood not as a competitor to ordinary mathematical physics but as an attempt to provide a more general explanatory vocabulary. Whether it will become a standard part of physics remains open. But even in its current form, it offers a powerful lens for seeing a common structure behind information, thermodynamics, computation, and life.

## A compact formal summary

For reference, the minimal mathematical skeleton can be collected in one place.

A substrate `S` has attributes `x, y, ...` and variables `X = {xi}`.

A task is a relation on attributes,

```text
A = {xi -> yi}
```

A constructor for `A` is a system that performs `A` while retaining the ability to do so again.

A task is possible if arbitrarily accurate constructors are allowed by physical law,

```text
A✓
```

and impossible otherwise,

```text
A×
```

Tasks compose in parallel and series,

```text
A ⊗ B
B ∘ A
```

An information variable `X` supports all permutations,

```text
{x -> pi(x) : x in X}✓
```

and supports copying,

```text
{(x, x0) -> (x, x) : x in X}✓
```

Distinguishability is the possibility of mapping distinct attributes to distinct information values,

```text
{xi -> i}✓
```

Many important laws then take the form of impossibility statements about classes of tasks.

## Notes on notation and portability

This version avoids LaTeX delimiters such as `$...$`, `$$...$$`, `\(...\)`, and `\[...\]` so that it renders cleanly in plain GitHub Markdown, GitHub Pages setups without math support, static-site generators, and Markdown previewers that do not load MathJax or KaTeX. The notation is therefore written in plain text and code blocks rather than in TeX.

## References

1. David Deutsch, “Constructor Theory,” *Synthese* (2013), preprint: [arXiv:1210.7439](https://arxiv.org/abs/1210.7439).
2. Chiara Marletto, “Constructor Theory of Information,” *Proceedings of the Royal Society A* 471 (2015): [paper](https://royalsocietypublishing.org/rspa/article/471/2174/20140540/100308/Constructor-theory-of-informationConstructor).
3. Chiara Marletto, “Constructor Theory of Life,” *Journal of The Royal Society Interface* 12 (2015): [paper](https://royalsocietypublishing.org/rsif/article/12/104/20141226/35617/Constructor-theory-of-lifeConstructor-theory-of).
4. Chiara Marletto, “Constructor Theory of Thermodynamics,” preprint: [arXiv:1608.02625](https://arxiv.org/abs/1608.02625).
5. Constructor Theory project overview and FAQs: [constructortheory.org](https://www.constructortheory.org/).
