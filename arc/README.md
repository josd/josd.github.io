<p align="center">
  <img src="arc.svg" alt="The ARC Book logo" width=512 />
</p>

# The ARC Book

**Answer • Reason • Check.** ARC is a simple methodology for crafting small, trustworthy programs. Each case presented in this book is far more than a black box that spits out a result; it's a concise story told in three parts. First comes the **Answer** to a specific question. This is followed by the **Reason Why** that answer is correct, articulated in everyday language and supported by the relevant identities, rules, or ideas. Finally, every case includes a **Check**—a concrete test designed to fail loudly if an assumption doesn't hold or an edge case bites. The result is a computation with a complete, auditable trail: you can see precisely what was done, why it was valid, and how the page verifies its own work.

This ARC approach starts from three fundamental ingredients we can all recognize: **Data**, **Logic**, and a **Question**. From these, we compose a tiny, end-to-end accountable program. We summarize this habit as **P3**—**Prompt → Program → Proof**. Here, the “proof” isn't merely ceremonial; it's a practical validation formed by the union of the narrative explanation and the verification code the page carries with it. In short:

> **Proof = Reason Why + Check**

This book aims to be welcoming. If you are a student, you should be able to follow the line of thought. If you are a practitioner, you should find the steps easy to audit. If you are simply curious, you should be able to tinker, change a value, and immediately watch the consequences unfold. Each page is self-contained, and every run is intended to be repeatable.

## P3: Prompt → Program → Proof

Translating raw data into trusted, actionable insight remains a major hurdle. It can be difficult to be sure an AI model's answer is correct, to audit its reasoning, or to automate processes with confidence. A method called P3 addresses this challenge by teaching a large language model to perform a specific, rigorous task. It transforms raw inputs, such as data, logic, and a specific question, into a single, self-contained program. This program is fully autonomous and, most importantly, is required to deliver a "triad of trust": the final answer, a clear explanation of the reason why, and an independent check that validates the result, guarding against errors and hallucinations. In this system, the proof consists of both the explanation and the verification.

At its core, P3 is a pattern for question-directed program synthesis. You can think of it as giving a brilliant but literal programmer a complete lesson plan. You provide the task, all necessary materials, and a precise specification for the deliverable. The process involves formulating a prompt that instructs the model on what kind of program to write, declaring a precise question within that prompt, and providing the necessary facts and rules that govern the domain. The model is then instructed to write a self-contained program that ingests these inputs and produces the complete "answer, reason, check" output. The final deliverable isn't just a code snippet; it's a trustworthy and auditable artifact that can be executed in an automated pipeline, shared with auditors, and deployed with confidence.

This method stands out by blending the flexibility of generative AI with the rigor of symbolic systems. Every output is verifiable by design because it is a self-contained program with its own built-in test harness. Each execution produces both a result and an independent verification, moving beyond the "black box" paradigm. It uses the language model for what it does best—understanding intent and synthesizing code structure—while relying on formal logic to ensure the reasoning is explicit and explainable. The generated program is explicitly required to explain its reasoning, so you don't just know what the answer is; you know why it's the answer and have the means to prove it. By starting with a precise question, the model creates a concrete, repeatable procedure, turning the resulting program into a durable asset perfect for automation, compliance, and reproducible research.

The architecture is straightforward: inputs flow into the AI synthesizer, which emits a single program. Executing that program produces the three artifacts. This system rests on the principles that runtime verification is mandatory and that the primary output is a portable program. For performance-critical applications, an advanced "mixed computation" pattern can be used. This approach teaches the model to separate stable logic from dynamic data. The AI-guided synthesis acts as a "specializer," converting declarative logic into a compact, highly efficient driver function. At runtime, this specialized driver is extremely fast, consuming only new facts (like a new user transaction) and applying the pre-compiled logic to emit the standard "answer, reason, check" triad. This preserves the core trust contract while dramatically improving speed, determinism, and auditability. The logic stays declarative, while the execution becomes small, fast, and predictable.

Adopting this workflow is an iterative process. It begins by clearly defining the question you need to answer. Next, you assemble the relevant data files, the logic that defines your operational rules, and a prompt that explains the task to the model. You then use the prompt to guide the AI in generating the self-contained program. After running the program, you confirm that the answer, reason, and check are all correct. As your data and logic evolve, you simply refine your inputs and re-run the synthesis step to create an updated, validated artifact. The practical benefits include building unprecedented trust, as the "answer, reason, check" triad makes every output verifiable. This is essential for regulatory and compliance-driven environments. It also enables extreme automation by producing executables that integrate seamlessly into modern development pipelines. Furthermore, it lowers maintenance overhead because policies are maintained as declarative logic, not complex code. Subject matter experts can define operational logic in a high-level format, while the AI handles the complex task of translating it into efficient, verifiable code.

## Examples and test cases

Each link below opens a self-contained page that presents the ARC triad in place.

Part A

  - [**Auroracare**](https://josd.github.io/arc/auroracare.html) — AuroraCare Purpose-based Medical Data Exchange.
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
  - [**Nonogram**](https://josd.github.io/arc/nonogram.html) — Fill grid cells to match run hints using logical deductions.
  - [**REST‑Path**](https://josd.github.io/arc/rest-path.html) — Explain link‑following over REST resources; verify pre/post conditions.
  - [**Roots of Unity**](https://josd.github.io/arc/roots-of-unity.html) — Place complex n‑th roots on the unit circle; check spacing and sums/products.
  - [**Skyscrapers**](https://josd.github.io/arc/skyscrapers.html) — Deduce building heights from sightlines with constraint logic.
  - [**Socrates**](https://josd.github.io/arc/socrates.html) — Classic syllogisms with explicit inference traces.
  - [**Square Tiled by Right Triangles**](https://josd.github.io/arc/square-triangles.html) — Dissect a square into 17 right triangles; verify tiling constraints.
  - [**Sudoku**](https://josd.github.io/arc/sudoku.html) — Explain each step of solving a 9×9 with row/col/box checks.
  - [**Turing Machine**](https://josd.github.io/arc/turing.html) — Run tapes with explicit transitions; verify halting and tape contents.
  - [**Wind‑Turbine Maintenance**](https://josd.github.io/arc/wind-turbines.html) — Plan maintenance from telemetry and policies with auditable outcomes.

Part B

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
  - [**Newton–Raphson**](https://josd.github.io/arc/newton-raphson.html) — Newton–Raphson method for root‑finding.
  - [**Peano Factorial**](https://josd.github.io/arc/peano-factorial.html) — 5! = 120 proved via Resolution.
  - [**Pi**](https://josd.github.io/arc/pi.html) — High‑precision π via Chudnovsky series with error‑bound checks.
  - [**Polynomial Roots**](https://josd.github.io/arc/polynomial.html) — Find all roots simultaneously; prove convergence on typical cases.
  - [**Primes**](https://josd.github.io/arc/prime.html) — Generate/test primes; log certs (trial factors or proofs) as checks.
  - [**Pythagorean Theorem**](https://josd.github.io/arc/pythagorean-theorem.html) — Compute legs/hypotenuse and confirm with algebraic or area proofs.
  - [**Vandermonde’s Identity**](https://josd.github.io/arc/vandermonde-identity.html) — Binomial‑convolution equals a single binomial.
  - [**Wilson’s Theorem**](https://josd.github.io/arc/wilson-theorem.html) — A property of primes.

Part C

  - [**Python cases**](https://github.com/josd/josd.github.io/tree/master/arc/cases/) — Self-contained Python cases that chain together over a bus.

