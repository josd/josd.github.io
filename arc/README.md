![ARC — Ask better questions. Get answers you can check.](arc.svg)

# ARC — Verifiable answers from better questions

**ARC = Answer · Reason · Check**

ARC turns a precise question into a portable, executable artifact that answers it, explains the derivation, and checks the result through a route capable of finding errors.

> **Ask the right question. Get the answer. Understand the reason. Run the check.**

## Why ARC?

AI has made answers abundant. Trustworthy answers are still scarce.

A plausible response can be useful, but plausibility is not evidence. In most AI-assisted workflows, verification remains a manual afterthought: inspect the result, redo the calculation, search for another source, write a test, or ask an expert.

ARC moves verification into the artifact itself:

```text
Typical AI workflow
question → AI → answer → manual verification

ARC workflow
question + data + logic → executable artifact → Answer + Reason + Check
```

This moves the most valuable human work upstream: **frame the right question, identify the relevant facts and rules, and decide what would count as a convincing check**. AI can then do more of the mechanical work without asking us to accept an opaque result.

ARC does not make an answer trustworthy by sounding confident. It makes the answer **inspectable, repeatable, and able to prove itself wrong**.

## How an ARC works

Every ARC starts with three explicit inputs:

- **Question** — what do we actually want to know or decide?
- **Data** — which facts, measurements, observations, or inputs are relevant?
- **Logic** — which equations, constraints, policies, algorithms, or definitions govern the result?

From those inputs, an ARC produces three outputs:

1. **Answer** — the direct result to the question.
2. **Reason** — a clear account of how the result follows from the inputs and rules.
3. **Check** — an independent verification that confirms the result or fails visibly.

```text
INPUT                         OUTPUT
Question ─┐                   ┌─ Answer
Data ─────┼─→ compute ────────┼─ Reason
Logic ────┘                   └─ Check
```

A good ARC question is more than a prompt; it is part of the specification. It should be precise enough to distinguish a correct answer, an incorrect answer, and a correct answer to the wrong question.

The result is not trapped in a chat window. It is a self-contained program that can be run again, inspected, shared, tested, and incorporated into an automated workflow.

## The Check is the trust contract

An explanation is not verification. A model can produce a convincing explanation for a wrong result, so the Check must be capable of **disagreeing** with the Answer.

Where possible, it should take a genuinely different route from the primary computation:

- a second formula or algorithm;
- an invariant or conservation law;
- a reverse calculation;
- exhaustive comparison over a bounded domain;
- a known identity, boundary condition, or dimensional constraint;
- an independent data source;
- another domain-appropriate validation.

> **A check that cannot fail is not much of a check.**

Because the Check is executable, it can run automatically whenever the question, data, logic, or implementation changes. A passing check is visible evidence. A failing check is useful information, not something to hide.

## Small arcs compose into larger arcs

An ARC does not have to remain an isolated calculation. Its inputs and outputs form an explicit contract, so the checked Answer from one arc can become Data for another. Several focused arcs can compose into a larger arc with its own question, reasoning, and end-to-end check.

```text
ARC A ──┐
ARC B ──┼──→ larger ARC ──→ Answer + Reason + Check
ARC C ──┘
```

The larger ARC does not merely collect results. It checks whether those results compose into a correct answer to the larger question.

| Quality | What composition provides |
| --- | --- |
| **Reliable** | Each arc checks its own result; the larger arc checks the composition end to end. Failures remain visible and traceable to bounded components. |
| **Scalable** | Independent arcs can run separately or in parallel. Larger workflows grow by composition instead of becoming one monolithic program. |
| **Performant** | Each arc uses only the data and logic its question requires. Unchanged results can be reused, and only affected arcs need to run again. |
| **Evolvable** | An arc can be improved, replaced, or split behind the same contract. New arcs can be added without rewriting the whole system. |

The discipline is recursive: at every level, make the question explicit, expose the reasoning, and include a check capable of catching a wrong result. **Small checked arcs become the building blocks of larger checked arcs.**

## What ARC can—and cannot—guarantee

ARC makes trust testable; it does not make computation infallible.

- A check is only as strong as its independence and coverage. Two implementations can share the same mistaken assumption.
- Correct computation cannot repair incorrect, incomplete, or stale data.
- Explicit logic can still encode the wrong policy or model of the world.
- Some questions involve uncertainty or judgment rather than a single provably correct answer. Their checks should validate evidence, constraints, calibration, or process instead.

That is why ARC keeps the Question, Data, Logic, Reason, and Check visible together. It makes assumptions reviewable and failures diagnosable. Human judgment remains essential—especially in choosing the question and deciding what evidence is sufficient.

## Where ARC works especially well

ARC is a natural fit for STEM and other rule-driven domains with explicit structure and testable correctness conditions. Typical uses include:

- recomputing a mathematical result by a second method;
- checking algebraic identities, invariants, and error bounds;
- validating conservation, dimensional, range, or boundary constraints;
- testing an algorithm against known or exhaustive cases;
- checking engineering outputs against system constraints;
- tracing a rule-based decision back to its inputs and policy rules;
- comparing numerical results with analytical or independently computed results.

The pattern also applies beyond questions with one exact answer. A planning or policy ARC can show which evidence and constraints drove a decision, test whether required rules were respected, and fail visibly when its assumptions no longer hold.

## Design principles

- **Question first** — make the real information need explicit.
- **Answer directly** — do not bury the result in generated prose.
- **Explain the derivation** — expose the relevant rules, assumptions, and steps.
- **Check independently** — use a path that can catch errors in the primary computation.
- **Fail visibly** — never let broken assumptions or edge cases disappear silently.
- **Prefer executable verification** — make checking automatic and repeatable.
- **Keep artifacts self-contained** — preserve the complete case for inspection and reruns.
- **Use only what the question needs** — minimize irrelevant data and unnecessary inference.
- **Compose through explicit contracts** — connect checked outputs to defined inputs so larger arcs remain inspectable.

## Explore ARC

Each example is a self-contained page with the **Answer · Reason · Check** triad presented in place.

| Start here | What it demonstrates |
| --- | --- |
| [**Euler's Identity**](https://josd.github.io/arc/euler-identity.html) | A classic symbolic result with an independent numerical check. |
| [**Pi**](https://josd.github.io/arc/pi.html) | High-precision computation with explicit error bounds. |
| [**Bike Trip Planning**](https://josd.github.io/arc/bike-trip.html) | A practical decision derived from hazards, preferences, and declarative rules. |
| [**Wind-Turbine Maintenance**](https://josd.github.io/arc/wind-turbines.html) | Engineering decisions checked against telemetry and policy constraints. |
| [**Delfour**](https://josd.github.io/arc/delfour.html) | A purpose-specific insight derived without exposing sensitive source data. |
| [**Flandor**](https://josd.github.io/arc/flandor.html) | Several local signals composed into a checked regional decision. |

<details>
<summary><strong>Browse the full example catalogue</strong></summary>

### Science

- [**Body Mass Index**](https://josd.github.io/arc/bmi.html) — Compute BMI categories with explainable thresholds and sanity checks.
- [**Grass Seed Germination**](https://josd.github.io/arc/grass-molecular.html) — Model germination states and transitions with rule checks.
- [**Leg Length Discrepancy Measurement**](https://josd.github.io/arc/lldm.html) — Derive a measurement from four landmarks with explicit calculation steps.

### Economics / Insight Economy

- [**Delfour — microeconomics**](https://josd.github.io/arc/delfour.html) — Turn sensitive local household data into a purpose-specific shopping insight without exposing the underlying condition.
- [**Flandor — macroeconomics**](https://josd.github.io/arc/flandor.html) — Combine privacy-preserving regional signals into a checked stabilization decision and select the lowest-cost eligible retooling package.

### Technology

- [**Auroracare**](https://josd.github.io/arc/auroracare.html) — Purpose-based medical data exchange.
- [**Clinical Care Planning**](https://josd.github.io/arc/clinical-care.html) — Derive care plans from observations, guidelines, and policy constraints.
- [**GPS Clinical Bench**](https://josd.github.io/arc/gps-clinical-bench.html) — Benchmark rule-based clinical decisions with transparent audit trails.
- [**Graph of French Cities**](https://josd.github.io/arc/graph-french.html) — Compute shortest paths and verify graph connectivity.
- [**Health Information Processing**](https://josd.github.io/arc/health-info.html) — Transform clinical payloads with typed rules and validation.
- [**Linked Lists**](https://josd.github.io/arc/linked-lists.html) — Term-logic example checked using Resolution.
- [**REST-Path**](https://josd.github.io/arc/rest-path.html) — Explain link-following over REST resources and verify pre/post conditions.
- [**Turing Machine**](https://josd.github.io/arc/turing.html) — Run tapes with explicit transitions and verify halting and tape contents.

### Engineering

- [**Bike Trip Planning**](https://josd.github.io/arc/bike-trip.html) — Route priorities from hazards, preferences, and declarative JSON rules.
- [**Building Performance**](https://josd.github.io/arc/building-performance.html) — Reason about energy and comfort metrics and verify rule-based outcomes.
- [**Control System**](https://josd.github.io/arc/control-system.html) — Model feedback loops and verify stability and response conditions.
- [**Eco-Route**](https://josd.github.io/arc/eco-route.html) — Select lower-emission routes from traffic, grade, and policy goals.
- [**GPS Bike**](https://josd.github.io/arc/gps-bike.html) — Plan a bicycle route from Gent to Maasmechelen.
- [**Lee Algorithm**](https://josd.github.io/arc/lee.html) — Find a maze route and trace the optimal wavefront path.
- [**Wind-Turbine Maintenance**](https://josd.github.io/arc/wind-turbines.html) — Plan maintenance from telemetry and policy rules with auditable outcomes.

### Mathematics

- [**Ackermann**](https://josd.github.io/arc/ackermann.html) — Compute A₂ with exact hyper-operations and safe handling of huge values.
- [**Binomial Theorem**](https://josd.github.io/arc/binomial-theorem.html) — Verify the sum of all binomial coefficients.
- [**Collatz**](https://josd.github.io/arc/collatz.html) — Generate trajectories and check invariants for the Collatz map.
- [**Complex Identities**](https://josd.github.io/arc/complex.html) — Show symbolic steps for complex-number equalities with auditable reasoning.
- [**Euclid's Infinitude of Primes**](https://josd.github.io/arc/euclid-infinitude.html) — Explain Euclid's proof and run computational checks.
- [**Euler's Identity**](https://josd.github.io/arc/euler-identity.html) — Derive and numerically check a classic identity.
- [**Fibonacci**](https://josd.github.io/arc/fibonacci.html) — Compute large Fibonacci numbers with fast doubling and proof-style checks.
- [**Fundamental Theorem of Arithmetic**](https://josd.github.io/arc/fundamental-theorem-arithmetic.html) — Explore unique prime factorization.
- [**Gödel Numbering**](https://josd.github.io/arc/godel-numbering.html) — Demonstrate a classic Gödel numbering construction.
- [**Group Theory**](https://josd.github.io/arc/group-theory.html) — Verify closure, identity, inverses, and associativity on examples.
- [**Kaprekar's Constant**](https://josd.github.io/arc/kaprekar-constant.html) — Exhaustively test every four-digit state in Kaprekar's routine.
- [**Matrix Basics**](https://josd.github.io/arc/matrix.html) — Add, multiply, and invert matrices with dimension and property checks.
- [**Matrix Multiplication**](https://josd.github.io/arc/matrix-multiplication.html) — Demonstrate and check that matrix multiplication is not commutative in general.
- [**Newton–Raphson**](https://josd.github.io/arc/newton-raphson.html) — Find roots numerically and check residual error.
- [**Peano Factorial**](https://josd.github.io/arc/peano-factorial.html) — Show that 5! = 120 using Resolution.
- [**Pi**](https://josd.github.io/arc/pi.html) — Compute high-precision π with the Chudnovsky series and error-bound checks.
- [**Polynomial Roots**](https://josd.github.io/arc/polynomial.html) — Find roots simultaneously and verify convergence on representative cases.
- [**Primes**](https://josd.github.io/arc/prime.html) — Generate and test primes with explicit certificates or factor checks.
- [**Pythagorean Theorem**](https://josd.github.io/arc/pythagorean-theorem.html) — Compute triangle sides and confirm the result algebraically.
- [**Roots of Unity**](https://josd.github.io/arc/roots-of-unity.html) — Place complex roots on the unit circle and check spacing, sums, and products.

</details>

## ARC and the Insight Economy

ARC fits naturally with Professor Ruben Verborgh's vision in [**Inside the Insight Economy**](https://ruben.verborgh.org/blog/2025/08/12/inside-the-insight-economy/): derive a purpose-specific insight for a particular recipient, context, and moment instead of moving or accumulating more raw data than necessary.

A well-formed question expresses that purpose. It lets a system focus on the data and logic the question actually needs, derive an actionable answer, explain the derivation, and verify the result.

- [**Delfour**](https://josd.github.io/arc/delfour.html) shows the micro-economic case: sensitive household information stays local while a narrowly scoped shopping insight is derived for one retailer context, with explicit policy and checks.
- [**Flandor**](https://josd.github.io/arc/flandor.html) shows the macro-economic case: exporters, labour-market actors, and grid operators keep detailed evidence local while a regional ARC composes their signals into a time-bounded stabilization decision.

Together, they illustrate the principle: **move the minimum useful insight, not the maximum available data**.

ARC does not replace the Insight Economy architecture. It complements it with a pragmatic discipline for **question-directed, explainable, verifiable computation**.

## What ARC is trying to make normal

AI should not force us to choose between **speed** and **trust**.

The practical ambition of ARC is simple: formulate a precise question, answer it directly, show how the result was derived, and perform a meaningful check without requiring a person to rebuild the entire solution by hand.

> **Better questions → explicit reasoning → independently checked answers.**
