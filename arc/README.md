![ARC — Ask better questions. Get answers you can check.](arc.svg)

# ARC — Verifiable answers from better questions

**ARC = Answer · Reason · Check**

In the AI era, answers are becoming abundant. The scarcer human skill is knowing **what to ask**: framing a question that is precise enough to be useful, bounded enough to be answerable, and concrete enough to be checked.

ARC is a pragmatic way to turn those questions into **trustworthy, executable answers**.

Instead of asking an AI for an answer and then manually trying to verify it, ARC asks for a self-contained program that produces three things:

1. **Answer** — the result to the question.
2. **Reason** — a clear explanation of how the result follows from the data, rules, identities, or assumptions.
3. **Check** — a separate verification that can independently confirm the result or fail when something is wrong.

The goal is not to make AI sound more confident. The goal is to make its work **inspectable, repeatable, and checkable**.

> **Ask the right question. Get the answer. Understand the reason. Run the check.**

## Why ARC now?

Generative AI is very good at producing plausible answers and synthesizing code. But in most real workflows, verification is still surprisingly manual: inspect the result, redo the calculation, search for another source, write a test, ask another model, or have an expert check the work.

ARC makes verification part of the artifact from the beginning.

A useful way to think about the shift is:

```text
Traditional AI workflow
question → AI → answer → human manually checks

ARC workflow
question + data + logic → AI → executable artifact → Answer + Reason + Check
```

This changes the role of the person using AI. The highest-value work moves upstream: **choosing the right question, defining the relevant facts and constraints, and deciding what would count as a convincing check**.

The AI can do more of the mechanical work. Trust still has to be earned.

## The question comes first

ARC starts with three inputs:

```text
Question + Data + Logic
```

The **Question** defines what we actually want to know or decide.

The **Data** provides the relevant facts, measurements, observations, or inputs.

The **Logic** provides the rules of the domain: equations, constraints, policies, algorithms, definitions, or other knowledge needed to derive the answer.

From those inputs, an AI can synthesize a small, self-contained program that makes the path from question to result explicit.

A good ARC question is not merely a prompt. It is part of the specification. It should be specific enough that we can tell the difference between a correct answer, an incorrect answer, and an answer to the wrong question.

## What makes the Check different?

The **Check** is the most important part of the trust contract.

An explanation alone is not verification. A model can generate a convincing explanation for a wrong result. ARC therefore asks for a check that is capable of disagreeing with the answer.

Where possible, the check should use a **different route** from the primary computation: a second formula, an invariant, a reverse calculation, an exhaustive test, a known identity, a boundary condition, an independent data source, or another domain-appropriate validation.

> **A check that cannot fail is not much of a check.**

This makes ARC practical. The verification is executable, so it can be rerun automatically whenever the data, logic, or question changes.

## Built for STEM

ARC is especially well suited to **STEM** because STEM questions often have explicit structure and testable correctness conditions.

Typical ARC checks include:

- recomputing a mathematical result by a second method;
- checking an algebraic identity or invariant;
- testing conservation, dimensional, range, or boundary constraints;
- validating an algorithm against known or exhaustive cases;
- checking engineering outputs against system constraints;
- tracing a rule-based decision back to its inputs and policy rules;
- comparing a numerical result with an analytical or independently computed result.

That makes ARC useful for mathematics, science, engineering, computer science, and other rule-driven technical domains where an answer should be more than plausible.

## From raw data to useful insight

ARC also fits naturally with Professor Ruben Verborgh's vision in [**Inside the Insight Economy**](https://ruben.verborgh.org/blog/2025/08/12/inside-the-insight-economy/).

Verborgh argues for moving beyond indiscriminate raw-data exchange toward **purpose-specific insights**: derive what is useful for a particular recipient, context, and moment instead of moving or accumulating more raw data than necessary.

That idea matters for ARC. A well-formed question expresses the purpose of a computation. Once the purpose is explicit, a system can focus on the data and logic needed for that question, derive an actionable answer, explain the derivation, and verify the result.

Two examples make the micro-to-macro progression concrete:

- [**Delfour**](https://josd.github.io/arc/delfour.html) is the micro-economic case: sensitive household information stays local while a narrowly scoped shopping insight is derived for one retailer context, with explicit policy and checks.
- [**Flandor**](https://josd.github.io/arc/flandor.html) is the macro-economic case: exporters, labour-market actors, and grid operators keep detailed evidence local while a regional insight combines the pressures needed for a time-bounded stabilization decision. The board can act without receiving firm-level books, vacancy lists, or grid-control detail.

Together they illustrate a key Insight Economy idea: **move the minimum useful insight, not the maximum available data**. ARC adds a pragmatic Answer · Reason · Check discipline around the resulting decision.

ARC is not a replacement for the Insight Economy architecture. It is a complementary engineering pattern: **question-directed, explainable, verifiable computation** that can help turn data into trusted insight.

## The ARC pattern

For each case, ARC aims to produce a portable artifact with a simple contract:

```text
INPUT
  question
  data
  logic / constraints

COMPUTE
  derive the result
  record the reasoning
  run an independent check

OUTPUT
  Answer
  Reason
  Check
```

The result is not just a response in a chat window. It is something that can be executed again, inspected, shared, tested, and incorporated into an automated workflow.

## Design principles

- **Question first** — make the actual information need explicit.
- **Answer directly** — do not bury the result in generated prose.
- **Explain the derivation** — expose the relevant rules, assumptions, and steps.
- **Check independently** — validate through a path that can catch errors.
- **Fail visibly** — assumptions and edge cases should not disappear silently.
- **Prefer executable verification** — turn checking from a manual activity into a repeatable one.
- **Keep artifacts self-contained** — make it possible to inspect and rerun the complete case.
- **Use only what the question needs** — minimize irrelevant data and unnecessary inference.

## Examples and test cases

Each link below opens a self-contained ARC page. The examples focus on STEM and technical reasoning, with the **Answer · Reason · Check** triad presented in place.

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
- [**Kaprekar's Constant**](https://josd.github.io/arc/kaprekar-constant.html) — Exhaustively test every 4-digit state in Kaprekar's routine.
- [**Matrix Basics**](https://josd.github.io/arc/matrix.html) — Add, multiply, and invert matrices with dimension and property checks.
- [**Matrix Multiplication**](https://josd.github.io/arc/matrix-multiplication.html) — Demonstrate and check that matrix multiplication is not commutative in general.
- [**Newton–Raphson**](https://josd.github.io/arc/newton-raphson.html) — Find roots numerically and check residual error.
- [**Peano Factorial**](https://josd.github.io/arc/peano-factorial.html) — Show that 5! = 120 using Resolution.
- [**Pi**](https://josd.github.io/arc/pi.html) — Compute high-precision π with the Chudnovsky series and error-bound checks.
- [**Polynomial Roots**](https://josd.github.io/arc/polynomial.html) — Find roots simultaneously and verify convergence on representative cases.
- [**Primes**](https://josd.github.io/arc/prime.html) — Generate and test primes with explicit certificates or factor checks.
- [**Pythagorean Theorem**](https://josd.github.io/arc/pythagorean-theorem.html) — Compute triangle sides and confirm the result algebraically.
- [**Roots of Unity**](https://josd.github.io/arc/roots-of-unity.html) — Place complex roots on the unit circle and check spacing, sums, and products.

## What ARC is trying to make normal

AI should not force us to choose between **speed** and **trust**.

A useful AI system should be able to help us formulate and answer precise questions, show how it reached the result, and perform meaningful checks without requiring a human to rebuild the entire solution by hand.

That is the practical ambition of ARC:

> **better questions → explicit reasoning → independently checked answers**

