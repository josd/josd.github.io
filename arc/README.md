<p align="center">
  <img src="arc.svg" alt="The ARC Book logo" width=512 />
</p>

# The ARC Book

**Answer • Reason • Check.** ARC is a simple methodology for crafting small, trustworthy programs. Each case presented in this book is far more than a black box that spits out a result; it's a concise story told in three parts. First comes the **answer** to a specific question. This is followed by the **reason why** that answer is correct, articulated in everyday language and supported by the relevant identities, rules, or ideas. Finally, every case includes a **check**—a concrete test designed to fail loudly if an assumption doesn't hold or an edge case bites. The result is a computation with a complete, auditable trail: you can see precisely what was done, why it was valid, and how the page verifies its own work.

This ARC approach starts from three fundamental ingredients we can all recognize: **Data**, **Logic**, and a **Question**. From these, we compose a tiny, end-to-end accountable program. We summarize this habit as **P3**—**Prompt → Program → Proof**. Here, the “proof” isn't merely ceremonial; it's a practical validation formed by the union of the narrative explanation and the verification code the page carries with it. In short:

> **Proof = Reason Why + Check**

This book aims to be welcoming. If you are a student, you should be able to follow the line of thought. If you are a practitioner, you should find the steps easy to audit. If you are simply curious, you should be able to tinker, change a value, and immediately watch the consequences unfold. Each page is self-contained, and every run is intended to be repeatable.

## Why JavaScript (pure, in the browser)

We use **plain JavaScript** so that every case can run instantly in any modern browser, requiring no installation or complex build steps. JavaScript provides essential tools like exact arithmetic via `BigInt`, convenient arrays and data views for efficient iteration, and first-class access to the DOM for creating simple, interactive visuals. By keeping the mathematics and the interface within the same file, we make it easy to learn from the code, profile performance using DevTools, and modify the inputs directly on the page. Using a single language across all cases also ensures a uniform style; what varies is the core idea, not the underlying plumbing.

## How to read a case

When approaching a new case, begin by skimming the page: What is the question, and what does the output look like? Next, read the **Reason Why**. This is the heart of the ARC method—the place where the steps are explained in clear sentences. Finally, examine the **Check**. What exactly does the page verify? A conservation law? A known identity? A bound on error? If this check fails, the page will explicitly state so. Treat these checks as an integral part of the learning experience; they exist to make all expectations explicit.

If you teach, consider assigning a case as a lab. The combination of code, commentary, and checks naturally invites exploration and discussion. Students can experiment safely, knowing the page will complain if something important goes wrong.

## P3

The ARC discipline is easy to remember: **P3 — Prompt → Program → Proof**. You start with a prompt (which includes the question, the data, and the rules you are willing to use). You then write a small program that answers that prompt. Finally, you insist on fulfilling a proof-like obligation: providing an explanation in words *plus* a check that actually runs. You can read more at the brief note on P3: [https://josd.github.io/p3/](https://josd.github.io/p3/).

## Examples and test cases

Each link below opens a self-contained page that presents the ARC triad in place.

Part A

  - [**Ackermann**](https://josd.github.io/arc/ackermann.html) — Compute A₂ with exact hyper-ops; print small, expand huge safely.
  - [**Binomial Theorem**](https://josd.github.io/arc/binomial-theorem.html) — Sum of all binomial coefficients.
  - [**Collatz**](https://josd.github.io/arc/collatz.html) — Generate trajectories and check invariants for the Collatz map.
  - [**Complex Identities**](https://josd.github.io/arc/complex.html) — Symbolic steps for complex-number equalities with auditable reasoning.
  - [**Euclid’s Infinitude of Primes**](https://josd.github.io/arc/euclid-infinitude.html) — Restate the theorem, explain Euclid’s one‑line proof, and run computational checks.
  - [**Euler’s Identity**](https://josd.github.io/arc/euler-identity.html) — The most beautiful equation in mathematics.
  - [**Fibonacci**](https://josd.github.io/arc/fibonacci.html) — Compute big Fₙ with fast-doubling recurrences and proof‑style checks.
  - [**Fundamental Theorem of Arithmetic**](https://josd.github.io/arc/fundamental-theorem-arithmetic.html) — Every integer factors as a product of primes.
  - [**Gödel Numbering**](https://josd.github.io/arc/godel-numbering.html) — A classic Gödel numbering demonstrator.
  - [**Group Theory**](https://josd.github.io/arc/group-theory.html) — Verify closure, identity, inverses, and associativity on examples.
  - [**Kaprekar’s Constant**](https://josd.github.io/arc/kaprekar-constant.html) — Exhaustive sweep of every 4‑digit state in Kaprekar’s routine.
  - [**Matrix Basics**](https://josd.github.io/arc/matrix.html) — Add/multiply/invert with dimension/property checks.
  - [**Matrix Multiplication**](https://josd.github.io/arc/matrix-multiplication.html) — Not commutative (AB ≠ BA).
  - [**Peano Factorial**](https://josd.github.io/arc/peano-factorial.html) — 5! = 120 proved via Resolution.
  - [**Pi**](https://josd.github.io/arc/pi.html) — High‑precision π via Chudnovsky series with error‑bound checks.
  - [**Polynomial Roots**](https://josd.github.io/arc/polynomial.html) — Find all roots simultaneously; prove convergence on typical cases.
  - [**Primes**](https://josd.github.io/arc/prime.html) — Generate/test primes; log certs (trial factors or proofs) as checks.
  - [**Pythagorean Theorem**](https://josd.github.io/arc/pythagorean-theorem.html) — Compute legs/hypotenuse and confirm with algebraic or area proofs.
  - [**Vandermonde’s Identity**](https://josd.github.io/arc/vandermonde-identity.html) — Binomial‑convolution equals a single binomial.
  - [**Wilson’s Theorem**](https://josd.github.io/arc/wilson-theorem.html) — A property of primes.

Part B

  - [**Barbara**](https://josd.github.io/arc/barbara.html) — Barbara Term Logic example proved using Resolution.
  - [**Bike Trip Planning**](https://josd.github.io/arc/bike-trip.html) — Route priorities from hazards, preferences, and declarative JSON rules.
  - [**Body Mass Index**](https://josd.github.io/arc/bmi.html) — Compute BMI categories with explainable thresholds and sanity checks.
  - [**Building Performance**](https://josd.github.io/arc/building-performance.html) — Reason about energy/comfort metrics and verify rule-based outcomes.
  - [**Clinical Care Planning**](https://josd.github.io/arc/clinical-care.html) — Derive care plans from observations, guidelines, and policy constraints.
  - [**Control System**](https://josd.github.io/arc/control-system.html) — Model simple feedback loops and verify stability/response conditions.
  - [**Easter**](https://josd.github.io/arc/easter.html) — Derive Easter dates from calendrical rules with verifiable steps.
  - [**Eco-Route**](https://josd.github.io/arc/eco-route.html) — Pick lower-emission routes by fusing traffic, grade, and policy goals.
  - [**Family Logic**](https://josd.github.io/arc/family.html) — Infer kinship from base relations (parent, spouse) with consistency checks.
  - [**GPS Bike**](https://josd.github.io/arc/gps-bike.html) — GPS for bike trip Gent → Maasmechelen.
  - [**GPS Clinical Bench**](https://josd.github.io/arc/gps-clinical-bench.html) — Benchmark clinical decisions with transparent rules and audit trails.
  - [**Graph of French Cities**](https://josd.github.io/arc/graph-french.html) — Shortest paths and connectivity over a city graph with proofs.
  - [**Grass Seed Germination**](https://josd.github.io/arc/grass-molecular.html) — Model germination states and transitions with rule checks.
  - [**Health Information Processing**](https://josd.github.io/arc/health-info.html) — Transform clinical payloads with typed rules and validation.
  - [**Kakuro**](https://josd.github.io/arc/kakuro.html) — Fill grid sums with unique digits using constraint propagation.
  - [**KenKen**](https://josd.github.io/arc/kenken.html) — Latin‑square + cage arithmetic solved with explainable deductions.
  - [**Lee**](https://josd.github.io/arc/lee.html) — Maze routing with Lee’s algorithm; trace optimal wavefront paths.
  - [**Leg Length Discrepancy Measurement**](https://josd.github.io/arc/lldm.html) — Leg Length Discrepancy Measurement from four landmarks.
  - [**Linked Lists**](https://josd.github.io/arc/linked-lists.html) — Term logic example proved using Resolution.
  - [**N‑Queens**](https://josd.github.io/arc/n-queens.html) — Place N queens without attacks; verify constraints per row/diag.
  - [**Newton–Raphson**](https://josd.github.io/arc/newton-raphson.html) — Newton–Raphson method for root‑finding.
  - [**Nonogram**](https://josd.github.io/arc/nonogram.html) — Fill grid cells to match run hints using logical deductions.
  - [**REST‑Path**](https://josd.github.io/arc/rest-path.html) — Explain link‑following over REST resources; verify pre/post conditions.
  - [**Roots of Unity**](https://josd.github.io/arc/roots-of-unity.html) — Place complex n‑th roots on the unit circle; check spacing and sums/products.
  - [**Skyscrapers**](https://josd.github.io/arc/skyscrapers.html) — Deduce building heights from sightlines with constraint logic.
  - [**Socrates**](https://josd.github.io/arc/socrates.html) — Classic syllogisms with explicit inference traces.
  - [**Square Tiled by Right Triangles**](https://josd.github.io/arc/square-triangles.html) — Dissect a square into 17 right triangles; verify tiling constraints.
  - [**Sudoku**](https://josd.github.io/arc/sudoku.html) — Explain each step of solving a 9×9 with row/col/box checks.
  - [**Turing Machine**](https://josd.github.io/arc/turing.html) — Run tapes with explicit transitions; verify halting and tape contents.
  - [**Wind‑Turbine Maintenance**](https://josd.github.io/arc/wind-turbines.html) — Plan maintenance from telemetry and policies with auditable outcomes.

-----

If you spot an error, have a clearer sentence, or can propose a better check, please contribute. Small improvements accumulate quickly in a format like this. The only house rule is to keep all examples self-contained and written in plain JavaScript, so anyone can open them in a browser and learn from them.
