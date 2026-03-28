# arclight

This repository contains eleven small, fast Rust ARC programs.

ARC stands for **Answer • Reason • Check**. An ARC program does more than emit a result. It gives:

- **Answer** — the result itself
- **Reason Why** — a short witness, derivation, or explanation of why the result follows
- **Check** — one or more concrete validations that fail loudly if an assumption is wrong, an edge case bites, or the answer contradicts an independent test

A useful way to read this repository is as **teaching material for an LLM acting as a student programmer**. The target is not a mysterious giant system that emits polished text. The target is a small program that can be written, inspected, rerun, criticized, and improved. In that teaching setup, the student should learn to produce code that answers a precise question, explains its reasoning in a compact witness, and then verifies the result with explicit checks instead of asking for trust.

That teaching angle matters because it pushes toward the right habits: keep the data explicit, keep the logic local, keep the question precise, and make correctness visible in the running artifact. The goal is not just to compute, but to compute in a way that stays easy to inspect, explain, and challenge. That is the practical value of the ARC approach: each run leaves an auditable trail instead of a black box. This follows the core ARC idea that trustworthy computation should be self-contained, repeatable, and verifiable at runtime.

## ARC principles used here

These examples are organized around a few simple ARC principles:

- **Data + Logic + Question** — each case starts from explicit input data, explicit rules or algorithms, and a precise question to answer
- **P3: Prompt → Program → Proof** — in the broader ARC workflow, the important deliverable is not only an answer but a portable program whose output can be checked again and again
- **Proof = Reason Why + Check** — the explanation and the executable validation work together; either one alone is weaker than both together
- **Runtime verification is mandatory** — every case should validate key invariants during execution rather than relying on trust in the code or in the author
- **Portable artifacts beat opaque sessions** — a small standalone program is easier to benchmark, automate, audit, archive, and compare across implementations

In this repository, the programs are handwritten and specialized for speed, but they still follow the same ARC discipline: answer the question, explain the answer, and verify the answer. That also makes them good exemplars for teaching or evaluating an LLM as a student programmer: the deliverable is not merely source code, but a runnable artifact whose reasoning and checks are visible at the interface.

## Why this style is useful

That structure has practical benefits:

- it makes each run easier to audit
- it keeps examples readable instead of opaque
- it teaches a student programmer, human or LLM, to separate result, explanation, and verification
- it encourages independent cross-checks rather than self-certification
- it makes benchmark cases useful as demonstrations, not just speed tests
- it gives each example a stable textual interface that is easy to compare across implementations
- it makes the output easier to reuse in automation, compliance-style review, and reproducible experiments

## What counts as a good Check

A good ARC check is not a decorative success message. It should be a concrete test that can actually fail.

In this repository, good checks try to have one or more of these properties:

- they recompute a quantity from a different angle
- they validate a witness example separately from the summary statistic
- they test algebraic identities, conservation laws, or structural invariants
- they verify boundary cases and representative hard cases
- they stop the program with a clear error when the contract is broken

That means the `Check` section is meant to resist self-certification. The best cases do not merely restate the main computation path; they challenge it.

## Included cases


### `collatz-1000`

A computational check of the Collatz conjecture in `src/collatz_1000.rs`.

For CLI compatibility, the case name remains `collatz-1000`, while this version exhaustively verifies all starts from `1` through `10000`.

It models:

- the standard Collatz step `n -> n / 2` for even `n`
- the standard Collatz step `n -> 3n + 1` for odd `n`
- exhaustive verification over all starts from `1` through `10000`
- the longest stopping time within that range
- the highest peak value reached within that range
- a classic witness trace summary for `27`

### `control-system`

A small rule-based control example in `src/control_system.rs`.

It models:

- the source measurements, observations, and targets as typed Rust enums
- the derived helper rule `measurement10/2`
- the two `control1/2` rules for `actuator1` and `actuator2`
- the final existential query `true :+ control1(_, _)` as `query satisfied`

### `deep-taxonomy-100000`

A specialized forward-chaining taxonomy benchmark in `src/deep_taxonomy_100000.rs`.

It models:

- one seed fact: `Ind has class N(0)`
- 100,000 chain rules: `N(i) -> N(i+1), I(i+1), J(i+1)`
- one final class rule: `N(100000) -> A2`
- one goal rule: `A2 -> goal reached`

This version is specialized for speed and does not use a slower generic triple engine.

### `delfour`

A Rust translation of the browser-side Delfour Insight Economy phone/scanner demo in `src/delfour.rs`.

It models:

- desensitizing a household condition into a neutral low-sugar need
- deriving a scoped, expiring insight envelope for shopping assistance
- signing that envelope with HMAC-SHA256 over canonical JSON
- authorizing scanner use under a purpose-limited ODRL-style policy
- suggesting a lower-sugar alternative for the scanned product
- verifying minimization, authorization, and duty-timing checks

### `euler-identity`

An exact arithmetic version of Euler's identity in `src/euler_identity.rs`.

This version uses direct integer arithmetic over a small `ExactComplex` type.

It mirrors the mathematical structure:

- construct `exp(i*pi)` exactly as `(-1, 0)`
- add `(1, 0)` to obtain `(0, 0)`
- verify the phase modulus squared is `1`
- certify that the identity holds exactly

### `fibonacci`

A direct Fibonacci computation in `src/fibonacci.rs`.

This version computes the requested values with iterative Rust and `BigUint`.

It prints:

- `F(0)`
- `F(1)`
- `F(10)`
- `F(100)`
- `F(1000)`

### `goldbach-1000`

A computational check of Goldbach's conjecture in `src/goldbach_1000.rs`.

It models:

- prime generation up to `1000` with a sieve
- exhaustive verification for every even target from `4` through `1000`
- enumeration of unordered prime-pair decompositions `n = p + q`
- the hardest targets with the fewest decompositions
- the richest target with the most decompositions
- a balanced witness pair for `1000`

### `gps`

A route-planning example in `src/gps.rs`.

It models:

- four route descriptions
- recursive path chaining
- duration and cost summation
- belief and comfort multiplication
- route filtering against goal constraints
- human-readable route output

The translation uses Rust concepts like `City`, `Action`, `Stage`, `Description`, and `Route`.

### `kaprekar-6174`

A computational proof of Kaprekar's constant in `src/kaprekar_6174.rs`.

It models:

- the four-digit Kaprekar routine with leading zeros preserved
- the exclusion of repdigits such as `1111` and `0000`
- exhaustive verification over all remaining four-digit starts
- proof that every valid start reaches `6174`
- verification of the standard `<= 7` iteration bound
- readable witness traces, including the leading-zero case `2111 -> 0999 -> ... -> 6174`

### `polynomial`

A quartic polynomial consistency check in `src/polynomial.rs`.

It models the two quartic outputs shown in the original example material and verifies:

- the exact source coefficients for each reported polynomial
- the exact roots for the real and complex quartics
- polynomial reconstruction from those roots
- direct zero-evaluation of each root against its source polynomial
- that every reported example is internally consistent

### `path-discovery`

A path-finding example in `src/path_discovery.rs`.

It models:

- the full airport graph from the source data
- airport labels as Rust lookup data
- direct flights as `(from, to)` edges
- adjacency-map construction for traversal
- depth-limited DFS over simple paths
- a query for all routes from Ostend-Bruges International Airport to Václav Havel Airport Prague with at most 2 stopovers

## Files

- `src/main.rs` — CLI dispatcher
- `src/report.rs` — structured ARC report model used for JSON output
- `src/collatz_1000.rs` — Collatz conjecture benchmark translation
- `src/control_system.rs` — control system benchmark translation
- `src/deep_taxonomy_100000.rs` — specialized taxonomy benchmark
- `src/delfour.rs` — Delfour phone/scanner insight example
- `src/euler_identity.rs` — Euler identity benchmark translation
- `src/fibonacci.rs` — Fibonacci benchmark translation
- `src/goldbach_1000.rs` — Goldbach conjecture benchmark translation
- `src/gps.rs` — GPS benchmark translation
- `src/kaprekar_6174.rs` — Kaprekar 6174 proof example
- `src/path_discovery.rs` — path discovery benchmark translation plus generated airport and flight data
- `src/polynomial.rs` — polynomial benchmark translation
- `pilot.sh` — build, refresh, and check snapshot files

## Run

The package name is `arclight`, so a release build produces `target/release/arclight`.

Default case:

```bash
cargo run --release
```

Explicit cases:

```bash
cargo run --release -- collatz-1000
cargo run --release -- control-system
cargo run --release -- deep-taxonomy-100000
cargo run --release -- delfour
cargo run --release -- euler-identity
cargo run --release -- fibonacci
cargo run --release -- goldbach-1000
cargo run --release -- gps
cargo run --release -- kaprekar-6174
cargo run --release -- path-discovery
cargo run --release -- polynomial
```

Structured JSON output for one case:

```bash
cargo run --release -- collatz-1000 --format json
```

Structured JSON output for the whole suite:

```bash
cargo run --release -- --all --format json
```

## Stable output and snapshots

Arclight supports two stable output forms:

- the normal human-readable ARC text output
- a structured JSON report produced with `--format json`

The recommended workflow is:

1. keep the human-readable text output for people
2. keep JSON as the canonical machine-checkable form
3. store checked-in snapshots for both
4. refresh snapshots only when a case intentionally changes

The root `pilot.sh` script is the main driver for this:

Because snapshots are regular files in the repository, intentional output changes show up as normal diffs in version control. If you add or grow a case, run `./pilot.sh refresh`, review the snapshot diff, and commit it together with the code change.


```bash
./pilot.sh refresh
./pilot.sh check
```

What it does:

- builds the release binary
- writes per-case text snapshots under `snapshots/text/`
- writes per-case JSON snapshots under `snapshots/json/`
- writes `all.txt`, `all.json`, and `list.txt`
- diffs fresh output against the checked-in snapshots during `check`

That gives a practical separation between:

- **computation** — the Rust code that derives the answer and checks it
- **rendering** — the human-facing text output
- **regression control** — snapshot files that show when a case changed

This is especially useful for ARC programs because the output is part of the artifact: the answer, the reason why, and the executable checks are all meant to stay auditable and reproducible.

## Snapshot layout

```text
snapshots/
  text/
    <case>.txt
    all.txt
    list.txt
  json/
    <case>.json
    all.json
```

List available cases:

```bash
cargo run --release -- --list
```

Run all cases in sequence:

```bash
cargo run --release -- --all
```

## ARC output style

Each case prints a short three-part story:

- **Answer** — the result in a compact, human-readable form
- **Reason Why** — the main witness, derivation, or explanation
- **Check** — concrete validations and cross-checks that fail loudly on contradiction

Where possible, the check section uses more than one line of evidence, so the program does not rely on a single computation path to certify its own output.
