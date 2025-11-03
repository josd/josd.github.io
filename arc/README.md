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

ARC’s discipline is easy to remember: **P3 — Prompt → Program → Proof**. Start with a prompt (the question, the data, and the rules you are willing to use). Write a small program that answers that prompt. Then insist on a proof‑like obligation: an explanation in words plus a check that runs. You can read more at the brief note on P3: <https://eyereasoner.github.io/eye/p3/p3>.

## Examples and test cases
Each link below opens a self‑contained page that presents the ARC triad in place.
- [**Ackermann**](https://josd.github.io/arc/ackermann.html) — Compute A₂ with exact hyper-ops; print small, expand huge safely.
- [**Binomial Theorem**](https://josd.github.io/arc/binomial-theorem.html) — Sum of all binomial coefficients.
- [**Collatz**](https://josd.github.io/arc/collatz.html) — Generate trajectories and check invariants for the Collatz map.
- [**Complex identities**](https://josd.github.io/arc/complex.html) — Symbolic steps for complex-number equalities with auditable reasoning.
- [**Euclid’s Infinitude of Primes**](https://josd.github.io/arc/euclid-infinitude.html) — Restate the theorem, explain Euclid’s one‑line proof, and run computational checks.
- [**Euler’s identity**](https://josd.github.io/arc/euler-identity.html) — The most beautiful equation in mathematics.
- [**Fibonacci**](https://josd.github.io/arc/fibonacci.html) — Compute big Fₙ with fast-doubling recurrences and proof‑style checks.
- [**Fundamental Theorem of Arithmetic**](https://josd.github.io/arc/fundamental-theorem-arithmetic.html) — Every integer factors as a product of primes.
- [**Gödel Numbering**](https://josd.github.io/arc/godel-numbering.html) — A classic Gödel numbering demonstrator.
- [**Group Theory**](https://josd.github.io/arc/group-theory.html) — Verify closure, identity, inverses, and associativity on examples.
- [**Kaprekar’s Constant**](https://josd.github.io/arc/kaprekar-constant.html) — Exhaustive sweep of every 4‑digit state in Kaprekar’s routine.
- [**Matrix basics**](https://josd.github.io/arc/matrix.html) — Add/multiply/invert with dimension/property checks.
- [**Peano Factorial**](https://josd.github.io/arc/peano-factorial.html) — 5! = 120 proved via Resolution.
- [**Pi**](https://josd.github.io/arc/pi.html) — High‑precision π via Chudnovsky series with error‑bound checks.
- [**Polynomial roots**](https://josd.github.io/arc/polynomial.html) — Find all roots simultaneously; prove convergence on typical cases.
- [**Primes**](https://josd.github.io/arc/prime.html) — Generate/test primes; log certs (trial factors or proofs) as checks.
- [**Pythagorean Theorem**](https://josd.github.io/arc/pythagorean-theorem.html) — Compute legs/hypotenuse and confirm with algebraic or area proofs.
- [**Turing Machine**](https://josd.github.io/arc/turing.html) — Run tapes with explicit transitions; verify halting and tape contents.
- [**Vandermonde’s identity**](https://josd.github.io/arc/vandermonde-identity.html) — Binomial‑convolution equals a single binomial.
- [**Wilson’s Theorem**](https://josd.github.io/arc/wilson-theorem.html) — A property of primes.

---

If you spot an error, have a clearer sentence, or can propose a better check, please do. Small improvements accumulate quickly in a format like this. The only house rule is to keep examples self‑contained and in plain JavaScript so anyone can open them in a browser and learn from them.

