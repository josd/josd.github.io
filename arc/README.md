# The ARC Book
by [Jos De Roo](https://josd.github.io/)

<p align="center">
  <img src="./arc.svg" alt="" width="960">
</p>

[ARC](https://josd.github.io/arc/)—short for Answer • Reason • Check—takes
a question-first view of computation. Start with Data, add Logic, and pose
a precise Question; the result is a self-contained program that does three
things every time it runs: it produces an answer, it explains why that answer
follows, and it checks itself. The method behind ARC is deliberately simple
to remember—[P3: Prompt → Program → Proof](https://josd.github.io/arc/p3.html).
In practice, the “proof” is not a theorem in a textbook sense but an obligation
the program carries with it: Proof = Reason Why + Check. The aim is to make
every run auditable, reproducible, and friendly to continuous integration.

The pages that follow present ARC in small, runnable pieces. Each case is 
compact—often “JS-only”—and renders the ARC triad in place: an Answer, 
the Reason Why, and a Check that can fail loudly when something is off. The 
subjects range widely, from mathematics and formal logic to routing problems, 
clinical policy, and classic puzzles. A Sudoku or a Pythagorean-theorem 
demonstration, for instance, appears not as a black-box result but as a
traceable procedure with its own built-in harness for verification.

If you are reading this for the first time, the best way in is straightforward: 
pick a case, run it, read the Reason Why, and then study the Check. That 
rhythm—the ARC triad—is the point.

### Examples and Test Cases
- [A₂ (Ackermann via hyper-operations)](https://josd.github.io/arc/etc/ackermann.html) — Compute A₂ with exact hyper-ops; print small, expand huge safely.
- [Apollonian gasket](https://josd.github.io/arc/etc/apollonian_gasket.html) — Exact tangent-circle packing via Descartes’ theorem and complex centers.
- [Barbara](https://josd.github.io/arc/etc/barbara.html) — Barbara Term Logic example proved using Resolution.
- [Bike Trip Planning](https://josd.github.io/arc/etc/bike_trip.html) — Route priorities from hazards, preferences, and declarative JSON rules.
- [Binomial Theorem](https://josd.github.io/arc/etc/binomial_theorem.html) — Sum of all binomial coefficients.
- [BMI](https://josd.github.io/arc/etc/bmi.html) — Compute BMI categories with explainable thresholds and sanity checks.
- [Building Performance](https://josd.github.io/arc/etc/building_performance.html) — Reason about energy/comfort metrics and verify rule-based outcomes.
- [Cauchy-Schwarz inequality](https://josd.github.io/arc/etc/cauchy_schwarz.html) — The Cauchy-Schwarz inequality — Computing inner products and norms for two vectors.
- [Chinese Remainder Theorem](https://josd.github.io/arc/etc/chinese_remainder_theorem.html) — CRT: unique solution mod product of coprime moduli.
- [Clinical Care Planning](https://josd.github.io/arc/etc/clinical_care.html) — Derive care plans from observations, guidelines, and policy constraints.
- [Collatz (3n+1)](https://josd.github.io/arc/etc/collatz.html) — Generate trajectories and check invariants for the Collatz map.
- [Combinatorics](https://josd.github.io/arc/etc/combinatorics.html) — Count, choose, and permute with proofs of identities where feasible.
- [Complex identities — explanatory proofs](https://josd.github.io/arc/etc/complex.html) — Symbolic steps for complex-number equalities with auditable reasoning.
- [Control System](https://josd.github.io/arc/etc/control_system.html) — Model simple feedback loops and verify stability/response conditions.
- [Cryptarithm](https://josd.github.io/arc/etc/cryptarithm.html) — Solve letter-to-digit puzzles with constraint checks on carry/uniqueness.
- [Descartes’ circle theorem](https://josd.github.io/arc/etc/descartes_circles.html) — Compute the fourth tangent circle from three using curvature relations.
- [Easter (Computus)](https://josd.github.io/arc/etc/easter.html) — Derive Easter dates from calendrical rules with verifiable steps.
- [Eco-Route](https://josd.github.io/arc/etc/eco_route.html) — Pick lower-emission routes by fusing traffic, grade, and policy goals.
- [Euclid’s Infinitude of Primes](https://josd.github.io/arc/etc/euclid_infinitude.html) — Restate the theorem, explain Euclid’s one‑line proof, and run computational checks.
- [Euler’s characteristic](https://josd.github.io/arc/etc/euler_characteristic.html) — Compute χ = V−E+F for meshes; sanity-check against topology rules.
- [Euler’s identity](https://josd.github.io/arc/etc/euler_identity.html) — Euler's identity, the most beautiful equation in mathematics.
- [Family logic](https://josd.github.io/arc/etc/family.html) — Infer kinship from base relations (parent, spouse) with consistency checks.
- [Fermat’s Little Theorem](https://josd.github.io/arc/etc/fermat_little_theorem.html) — Fermat's Little Theorem about prime numbers.
- [Fibonacci golden spiral](https://josd.github.io/arc/etc/fibonacci_golden_spiral.html) — Draw the spiral from Fibonacci rectangles and verify ratios.
- [Fibonacci via Fast Doubling](https://josd.github.io/arc/etc/fibonacci.html) — Compute big Fₙ with fast-doubling recurrences and proof-style checks.
- [Ford circles](https://josd.github.io/arc/etc/ford_circles.html) — Place circles at rationals; verify tangency and Farey-sequence links.
- [Fundamental Theorem of Arithmetic](https://josd.github.io/arc/etc/fundamental_theorem_arithmetic.html) — Every integer factors as a product of primes.
- [Gödel Numbering](https://josd.github.io/arc/etc/godel_numbering.html) — This page demonstrates a classic Gödel numbering.
- [Gödel Undecidable](https://josd.github.io/arc/etc/godel_undecidable.html) — Gödel — On Formally Undecidable Propositions.
- [GPS Bike](https://josd.github.io/arc/etc/gps_bike.html) — GPS Bike — Gent → Maasmechelen.
- [GPS Clinical Bench](https://josd.github.io/arc/etc/gps_clinical_bench.html) — Benchmark clinical decisions with transparent rules and audit trails.
- [Graph — French cities](https://josd.github.io/arc/etc/graph_french.html) — Shortest paths and connectivity over a city graph with proofs.
- [Grass seed — molecular germination](https://josd.github.io/arc/etc/grass_molecular.html) — Model germination states and transitions with rule checks.
- [Group Theory](https://josd.github.io/arc/etc/group_theory.html) — Verify closure, identity, inverses, and associativity on examples.
- [Health Information Processing](https://josd.github.io/arc/etc/health_info.html) — Transform clinical payloads with typed rules and validation.
- [Hertog Hawking](https://josd.github.io/arc/etc/hertog_hawking.html) — On the Origin of Time.
- [Infinite Game Math](https://josd.github.io/arc/etc/infinite_game_math.html) — The Infinite Game — Math-Centric Book Brief.
- [Kakuro (Cross Sums)](https://josd.github.io/arc/etc/kakuro.html) — Fill grid sums with unique digits using constraint propagation.
- [Kaprekar’s Constant](https://josd.github.io/arc/etc/kaprekar_constant.html) — An exhaustive sweep of every 4‑digit state that runs Kaprekar’s routine.
- [KenKen](https://josd.github.io/arc/etc/kenken.html) — Latin-square + cage arithmetic solved with explainable deductions.
- [Lee](https://josd.github.io/arc/etc/lee.html) — Maze routing with Lee’s algorithm; trace optimal wavefront paths.
- [Leg Length Discrepancy Measurement](https://josd.github.io/arc/etc/lldm.html) — Leg Length Discrepancy Measurement from four landmarks.
- [Library & Path](https://josd.github.io/arc/etc/library_and_path.html) — Toggle “laws,” search a minimal path to a target observation set.
- [Light Eaters](https://josd.github.io/arc/etc/light_eaters.html) — A comprehensive, self-contained book brief for The Light Eaters by Zoë Schlanger.
- [Linked Lists](https://josd.github.io/arc/etc/linked_lists.html) — Linked Lists Term Logic example proved using Resolution.
- [Matrix basics](https://josd.github.io/arc/etc/matrix.html) — Do matrix ops (add/mul/inv) with dimension and property checks.
- [Matrix Determinant](https://josd.github.io/arc/etc/matrix_determinant.html) — Matrix Determinant • det(AB) = det(A)·det(B).
- [Matrix Multiplication](https://josd.github.io/arc/etc/matrix_multiplication.html) — Matrix Multiplication • Not Commutative (AB ≠ BA).
- [N-Queens](https://josd.github.io/arc/etc/n_queens.html) — Place N queens without attacks; verify constraints per row/diag.
- [Newton-Raphson method](https://josd.github.io/arc/etc/newton_raphson.html) — Newton-Raphson root-finding algorithm.
- [Nonogram (Picross)](https://josd.github.io/arc/etc/nonogram.html) — Fill grid cells to match run hints using logical deductions.
- [Peano Addition](https://josd.github.io/arc/etc/peano_addition.html) — Peano Addition • 1+1=2 proved via Resolution.
- [Peano Factorial](https://josd.github.io/arc/etc/peano_factorial.html) — Peano Factorial • 5! = 120 proved via Resolution.
- [Pentagon & pentagram — golden ratio](https://josd.github.io/arc/etc/pentagon_pentagram.html) — Construct φ-relations in pentagons and star polygons with proofs.
- [π (Chudnovsky)](https://josd.github.io/arc/etc/pi.html) — High-precision π via Chudnovsky series with error-bound checks.
- [Pick’s Theorem](https://josd.github.io/arc/etc/picks_theorem.html) — Area = I + B/2 − 1 for lattice polygons; verify interior/boundary counts.
- [Poincaré Rotation on the Circle](https://josd.github.io/arc/etc/poincare.html) — An irrational circle rotation is non-repeating and uniform.
- [Polynomial roots (Durand–Kerner)](https://josd.github.io/arc/etc/polynomial.html) — Find all roots simultaneously; prove convergence on typical cases.
- [Primes](https://josd.github.io/arc/etc/prime.html) — Generate/test primes; log certs (e.g., trial factors or proofs) as checks.
- [Pythagorean Theorem](https://josd.github.io/arc/etc/pythagorean_theorem.html) — Compute legs/hypotenuse and confirm with algebraic or area proofs.
- [REST-path](https://josd.github.io/arc/etc/rest_path.html) — Explain link-following over REST resources; verify pre/post conditions.
- [Roots of Unity](https://josd.github.io/arc/etc/roots_of_unity.html) — Place complex n-th roots on the unit circle; check equal spacing and sums/products.
- [Skyscrapers](https://josd.github.io/arc/etc/skyscrapers.html) — Deduce building heights from sightlines with constraint logic.
- [Socrates](https://josd.github.io/arc/etc/socrates.html) — Classic syllogisms with explicit inference traces.
- [Square tiled by 17 right triangles](https://josd.github.io/arc/etc/square_triangles.html) — Dissect a square into 17 right triangles; verify tiling constraints.
- [Sudoku](https://josd.github.io/arc/etc/sudoku.html) — Explain each step of solving a 9×9 with row/col/box checks.
- [Turing Machine](https://josd.github.io/arc/etc/turing.html) — Run tapes with explicit transitions; verify halting and tape contents.
- [Vandermonde’s identity](https://josd.github.io/arc/etc/vandermonde_identity.html) — Vandermonde’s identity — binomial-convolution equals a single binomial.
- [Wilson's Theorem](https://josd.github.io/arc/etc/wilson_theorem.html) — Wilson's theorem about prime numbers.
- [Wind-Turbine Maintenance](https://josd.github.io/arc/etc/wind_turbines.html) — Plan maintenance from telemetry and policies with auditable outcomes.

