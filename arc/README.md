<p align="center">
  <img src="arc.svg" alt="The ARC Book logo" width=512 />
</p>

# The ARC Book

**Answer • Reason • Check.** ARC is a simple way to write small, trustworthy programs. Each case in this book is more than a black box that spits out a result: it is a short story with three parts. First comes the **answer** to a clear question. Next comes the **reason why** that answer follows—written in everyday language and supported by the relevant identities, rules, or ideas. Finally comes a **check**, a concrete test that can fail loudly if an assumption does not hold or an edge case bites. The result is computation with an auditable trail: you can see what was done, why it was valid, and how the page verifies itself.

ARC starts from three ingredients we can all recognize: **Data**, **Logic**, and **Question**. From these we compose a tiny program that is accountable end‑to‑end. We summarize this habit as **P3**—**Prompt → Program → Proof**—where the “proof” is practical rather than ceremonial: it is the union of the narrative explanation and the verification the page carries with it. In short:

> **Proof = Reason Why + Check**

This book aims to be welcoming. If you are a student, you should be able to follow the line of thought. If you are a practitioner, you should be able to audit the steps. If you are simply curious, you should be able to tinker, change a value, and watch the consequences unfold. Each page is self‑contained, and each run is meant to be repeatable.

## Why JavaScript (pure, in the browser)

We use **plain JavaScript** so that every case runs instantly in any modern browser with no installation and no build steps. JavaScript gives us exact arithmetic through `BigInt`, convenient arrays and data views for efficient iteration, and first‑class access to the DOM for simple, interactive visuals. By keeping the math and the interface in the same file, we make it easy to learn from the code, to profile performance with DevTools, and to modify the inputs right on the page. Using one language across all cases also keeps the style uniform; what varies is the idea, not the plumbing.

## How to read a case

Begin by skimming the page: what is the question and what does the output look like? Then read the **Reason Why**; this is the heart of ARC—the place where we explain the steps in sentences. Finally, look at the **Check**. What does the page verify? A conservation law? A known identity? A bound on error? If the check fails, the page will say so. Treat the checks as part of the learning experience: they are there to make expectations explicit.

If you teach, consider assigning one case as a lab. The combination of code, commentary, and checks invites exploration and discussion; students can experiment safely because the page will complain when something important goes wrong.

## P3

ARC’s discipline is easy to remember: **P3 — Prompt → Program → Proof**. Start with a prompt (the question, the data, and the rules you are willing to use). Write a small program that answers that prompt. Then insist on a proof‑like obligation: an explanation in words plus a check that runs. You can read more at the brief note on P3: <https://josd.github.io/arc/p3/>.

## Examples and test cases

The collection ranges from mathematics and formal logic to routing, clinical policy, and classic puzzles. Each link below opens a self‑contained page that presents the ARC triad in place.

- [**A₂ (Ackermann via hyper-operations)**](https://josd.github.io/arc/ackermann.html) — Compute A₂ with exact hyper-ops; print small, expand huge safely.
- [**Apollonian gasket**](https://josd.github.io/arc/apollonian-gasket.html) — Exact tangent-circle packing via Descartes’ theorem and complex centers.
- [**Barbara**](https://josd.github.io/arc/barbara.html) — Barbara Term Logic example proved using Resolution.
- [**Best of All Possible Worlds**](https://josd.github.io/arc/eloquent-leibniz-kempe.html) — A self‑contained research brief for *The Best of All Possible Worlds*.
- [**Bike Trip Planning**](https://josd.github.io/arc/bike-trip.html) — Route priorities from hazards, preferences, and declarative JSON rules.
- [**Binomial Theorem**](https://josd.github.io/arc/binomial-theorem.html) — Sum of all binomial coefficients.
- [**BMI**](https://josd.github.io/arc/bmi.html) — Compute BMI categories with explainable thresholds and sanity checks.
- [**Building Performance**](https://josd.github.io/arc/building-performance.html) — Reason about energy/comfort metrics and verify rule-based outcomes.
- [**Cauchy–Schwarz inequality**](https://josd.github.io/arc/cauchy-schwarz.html) — Computing inner products and norms for two vectors.
- [**Chinese Remainder Theorem**](https://josd.github.io/arc/chinese-remainder-theorem.html) — CRT: unique solution mod product of coprime moduli.
- [**Clinical Care Planning**](https://josd.github.io/arc/clinical-care.html) — Derive care plans from observations, guidelines, and policy constraints.
- [**Collatz (3n+1)**](https://josd.github.io/arc/collatz.html) — Generate trajectories and check invariants for the Collatz map.
- [**Combinatorics**](https://josd.github.io/arc/combinatorics.html) — Count, choose, and permute with proofs of identities where feasible.
- [**Complex identities — explanatory proofs**](https://josd.github.io/arc/complex.html) — Symbolic steps for complex-number equalities with auditable reasoning.
- [**Control System**](https://josd.github.io/arc/control-system.html) — Model simple feedback loops and verify stability/response conditions.
- [**Cryptarithm**](https://josd.github.io/arc/cryptarithm.html) — Solve letter-to-digit puzzles with constraint checks on carry/uniqueness.
- [**Descartes’ circle theorem**](https://josd.github.io/arc/descartes-circles.html) — Compute the fourth tangent circle from three using curvature relations.
- [**Easter (Computus)**](https://josd.github.io/arc/easter.html) — Derive Easter dates from calendrical rules with verifiable steps.
- [**Eco-Route**](https://josd.github.io/arc/eco-route.html) — Pick lower-emission routes by fusing traffic, grade, and policy goals.
- [**Eloquent JavaScript**](https://josd.github.io/arc/eloquent-javascript.html) — A self‑contained research brief for *Eloquent JavaScript*.
- [**Euclid’s Infinitude of Primes**](https://josd.github.io/arc/euclid-infinitude.html) — Restate the theorem, explain Euclid’s one‑line proof, and run computational checks.
- [**Euler’s characteristic**](https://josd.github.io/arc/euler-characteristic.html) — Compute χ = V−E+F for meshes; sanity-check against topology rules.
- [**Euler’s identity**](https://josd.github.io/arc/euler-identity.html) — The most beautiful equation in mathematics.
- [**Family logic**](https://josd.github.io/arc/family.html) — Infer kinship from base relations (parent, spouse) with consistency checks.
- [**Fermat’s Little Theorem**](https://josd.github.io/arc/fermat-little-theorem.html) — A classic property of prime numbers.
- [**Fibonacci golden spiral**](https://josd.github.io/arc/fibonacci-golden-spiral.html) — Draw the spiral from Fibonacci rectangles and verify ratios.
- [**Fibonacci via Fast Doubling**](https://josd.github.io/arc/fibonacci.html) — Compute big Fₙ with fast-doubling recurrences and proof‑style checks.
- [**Ford circles**](https://josd.github.io/arc/ford-circles.html) — Place circles at rationals; verify tangency and Farey‑sequence links.
- [**Fundamental Theorem of Arithmetic**](https://josd.github.io/arc/fundamental-theorem-arithmetic.html) — Every integer factors as a product of primes.
- [**Gödel Numbering**](https://josd.github.io/arc/godel-numbering.html) — A classic Gödel numbering demonstrator.
- [**Gödel Undecidable**](https://josd.github.io/arc/godel-undecidable.html) — A self‑contained research brief for *On Formally Undecidable Propositions*.
- [**GPS Bike**](https://josd.github.io/arc/gps-bike.html) — GPS for bike trip Gent → Maasmechelen.
- [**GPS Clinical Bench**](https://josd.github.io/arc/gps-clinical-bench.html) — Benchmark clinical decisions with transparent rules and audit trails.
- [**Graph — French cities**](https://josd.github.io/arc/graph-french.html) — Shortest paths and connectivity over a city graph with proofs.
- [**Grass seed — molecular germination**](https://josd.github.io/arc/grass-molecular.html) — Model germination states and transitions with rule checks.
- [**Group Theory**](https://josd.github.io/arc/group-theory.html) — Verify closure, identity, inverses, and associativity on examples.
- [**Health Information Processing**](https://josd.github.io/arc/health-info.html) — Transform clinical payloads with typed rules and validation.
- [**Hertog Hawking**](https://josd.github.io/arc/hertog-hawking.html) — A self‑contained book brief for *On the Origin of Time*.
- [**Infinite Game Math**](https://josd.github.io/arc/infinite-game-math.html) — A math‑centric book brief for *The Infinite Game*.
- [**Introduction to Logic**](https://josd.github.io/arc/introduction-to-logic.html) — A self‑contained book brief for *Introduction to Logic*.
- [**It All Adds Up**](https://josd.github.io/arc/it-all-adds-up.html) — A self‑contained book brief for *It All Adds Up*.
- [**Kakuro (Cross Sums)**](https://josd.github.io/arc/kakuro.html) — Fill grid sums with unique digits using constraint propagation.
- [**Kaprekar’s Constant**](https://josd.github.io/arc/kaprekar-constant.html) — Exhaustive sweep of every 4‑digit state in Kaprekar’s routine.
- [**KenKen**](https://josd.github.io/arc/kenken.html) — Latin‑square + cage arithmetic solved with explainable deductions.
- [**Lee**](https://josd.github.io/arc/lee.html) — Maze routing with Lee’s algorithm; trace optimal wavefront paths.
- [**Leg Length Discrepancy Measurement**](https://josd.github.io/arc/lldm.html) — Leg Length Discrepancy Measurement from four landmarks.
- [**Leonhard Euler**](https://josd.github.io/arc/leonhard-euler.html) — A self‑contained research brief for *Leonhard Euler*..
- [**Library & Path**](https://josd.github.io/arc/library-and-path.html) — Toggle “laws,” search a minimal path to a target observation set.
- [**Light Eaters**](https://josd.github.io/arc/light-eaters.html) — A self‑contained book brief for *The Light Eaters*.
- [**Linked Lists**](https://josd.github.io/arc/linked-lists.html) — Term logic example proved using Resolution.
- [**Matrix basics**](https://josd.github.io/arc/matrix.html) — Add/multiply/invert with dimension/property checks.
- [**Matrix Determinant**](https://josd.github.io/arc/matrix-determinant.html) — det(AB) = det(A)·det(B).
- [**Matrix Multiplication**](https://josd.github.io/arc/matrix-multiplication.html) — Not commutative (AB ≠ BA).
- [**N‑Queens**](https://josd.github.io/arc/n-queens.html) — Place N queens without attacks; verify constraints per row/diag.
- [**Newton–Raphson method**](https://josd.github.io/arc/newton-raphson.html) — Newton–Raphson method for root‑finding.
- [**Outer Limits of Reason**](https://josd.github.io/arc/newton-raphson.html) — A self‑contained book brief for *The Outer Limits of Reason*.
- [**Nonogram (Picross)**](https://josd.github.io/arc/nonogram.html) — Fill grid cells to match run hints using logical deductions.
- [**Peano Addition**](https://josd.github.io/arc/peano-addition.html) — 1+1=2 proved via Resolution.
- [**Peano Factorial**](https://josd.github.io/arc/peano-factorial.html) — 5! = 120 proved via Resolution.
- [**Pentagon & pentagram — golden ratio**](https://josd.github.io/arc/pentagon-pentagram.html) — Construct φ‑relations in pentagons and star polygons with proofs.
- [**π (Chudnovsky)**](https://josd.github.io/arc/pi.html) — High‑precision π via Chudnovsky series with error‑bound checks.
- [**Pick’s Theorem**](https://josd.github.io/arc/picks-theorem.html) — Area = I + B/2 − 1 for lattice polygons; verify counts.
- [**Poincaré rotation on the circle**](https://josd.github.io/arc/poincare.html) — An irrational circle rotation is non‑repeating and uniform.
- [**Polynomial roots (Durand–Kerner)**](https://josd.github.io/arc/polynomial.html) — Find all roots simultaneously; prove convergence on typical cases.
- [**Primes**](https://josd.github.io/arc/prime.html) — Generate/test primes; log certs (trial factors or proofs) as checks.
- [**Proofs from THE BOOK**](https://josd.github.io/arc/proofs-from-the-book.html) — A self‑contained book brief for *Proofs from THE BOOK*.
- [**Pythagorean Theorem**](https://josd.github.io/arc/pythagorean-theorem.html) — Compute legs/hypotenuse and confirm with algebraic or area proofs.
- [**REST‑path**](https://josd.github.io/arc/rest-path.html) — Explain link‑following over REST resources; verify pre/post conditions.
- [**Roots of Unity**](https://josd.github.io/arc/roots-of-unity.html) — Place complex n‑th roots on the unit circle; check spacing and sums/products.
- [**Skyscrapers**](https://josd.github.io/arc/skyscrapers.html) — Deduce building heights from sightlines with constraint logic.
- [**Socrates**](https://josd.github.io/arc/socrates.html) — Classic syllogisms with explicit inference traces.
- [**Square tiled by 17 right triangles**](https://josd.github.io/arc/square-triangles.html) — Dissect a square into 17 right triangles; verify tiling constraints.
- [**Sudoku**](https://josd.github.io/arc/sudoku.html) — Explain each step of solving a 9×9 with row/col/box checks.
- [**Turing Machine**](https://josd.github.io/arc/turing.html) — Run tapes with explicit transitions; verify halting and tape contents.
- [**Vandermonde’s identity**](https://josd.github.io/arc/vandermonde-identity.html) — Binomial‑convolution equals a single binomial.
- [**Wilson’s Theorem**](https://josd.github.io/arc/wilson-theorem.html) — A property of primes.
- [**Wind‑Turbine Maintenance**](https://josd.github.io/arc/wind-turbines.html) — Plan maintenance from telemetry and policies with auditable outcomes.

---

If you spot an error, have a clearer sentence, or can propose a better check, please do. Small improvements accumulate quickly in a format like this. The only house rule is to keep examples self‑contained and in plain JavaScript so anyone can open them in a browser and learn from them.

