# Complex Matrix Stability Worlds

## 1. What this case is about

Imagine you build a simple control system, or a digital filter, or some tiny feedback loop in electronics or software. A very common way to model it is with a **discrete-time linear system**:

> next state = (some matrix) × (current state)
>
> written as:
> **x₍k+1₎ = A · x₍k₎**

Here:

* **x₍k₎** is a vector representing the state at step `k` (e.g. position and velocity),
* **A** is a 2×2 matrix (in our case) whose entries may be complex numbers.

The big question engineers ask is:

> If I let this system run on its own, will it blow up, oscillate forever, or settle down?

That’s the notion of **stability**.

Our case is a tiny, [self-contained Python “laboratory”](https://github.com/josd/josd.github.io/blob/master/brains/cases/complex_matrix_stability_worlds.py) for that question. It does three things:

1. It implements the *true* mathematical test for stability of 2×2 complex matrices.
2. It implements **three approximate tests**, each representing a different compromise between accuracy and simplicity.
3. It treats each test as a “world” and asks, in a logical way:

   * “In which worlds are the tests always correct?”
   * “How do these ‘theorems’ about correctness relate to each other?”

The aim is to show, in a very concrete way, how a real-world engineering notion (stability of a system) can be wired into the “higher-order look, first-order core” style: the serious math lives in simple numeric computations, and the talk about “theorems” and “worlds” is handled by a small logical wrapper.

---

## 2. The real stability test (world 0)

For the system

> x₍k+1₎ = A · x₍k₎

the fundamental result is:

* **The system is stable** if all eigenvalues of A have magnitude at most 1.
  (Think: their distance from the origin in the complex plane is ≤ 1.)

* **The system is damped** (strictly stable) if all eigenvalues have magnitude at most 0.9.
  (We choose 0.9 just as a clear “safety margin inside the unit circle”.)

In our code:

* We compute the eigenvalues of a 2×2 matrix analytically from the quadratic formula:

  * For `[[a, b], [c, d]]`, the characteristic polynomial is
    λ² − (a + d) λ + (ad − bc)
  * We solve that exactly using complex arithmetic.

* We define:

  * `stable_true(A)` = “spectral radius ≤ 1”
  * `damped_true(A)` = “spectral radius ≤ 0.9”

This is **world 0**.

You can think of world 0 as the world where we are willing and able to do proper math: we compute the eigenvalues and answer correctly. It’s what you’d do in a serious control or signal processing toolkit.

So in world 0:

* The “stable?” question is answered perfectly.
* The “damped?” question is also answered perfectly.

Later, when we talk about “theorems” like `CorrectStable` and `CorrectDamped`, world 0 will be the only one that passes both.

---

## 3. Why introduce other “worlds” at all?

Because in practice, we often use **shortcuts**.

Maybe you are working with a large system and exact eigenvalues are hard or expensive to get. Or maybe you’re reasoning on a whiteboard and want a quick bound. Or you have legacy code with some old heuristic.

Those shortcuts:

* are *easier* to apply than full eigenvalue calculation,
* but they might occasionally be *wrong*.

So the script introduces three more worlds, each with its own approximate stability test. All of them answer the same two questions (stable? damped?), but by different recipes.

This creates a perfect playground to:

* Compare **accuracy vs simplicity**.
* Turn “this test is correct” into a **logical fact** we can talk about.

---

## 4. World 1: Gershgorin-disc test (conservative)

**Idea:** Use a classical analytic bound from matrix theory: **Gershgorin circles**.

For a 2×2 matrix

> A = [[a₁₁, a₁₂], [a₂₁, a₂₂]]

Gershgorin’s theorem says that all eigenvalues lie in the union of discs:

* Disc 1: center a₁₁, radius |a₁₂|
* Disc 2: center a₂₂, radius |a₂₁|

A very cheap bound on “how far eigenvalues can wander” is then:

> max( |a₁₁| + |a₁₂| , |a₂₂| + |a₂₁| )

If that max is small, we can be sure the eigenvalues are also small. If it’s large, we might still be safe, but we can’t be sure.

In **world 1** we define:

* **“stable in world 1”** if
  max( |a₁₁| + |a₁₂| , |a₂₂| + |a₂₁| ) ≤ 1.0
* **“damped in world 1”** if
  the same max ≤ 0.9

This test is:

* **Sound but incomplete** for stability:

  * If world 1 says “stable”, then the system really is stable.
  * But sometimes the true system is stable, and world 1 says “not sure” (so it outputs unstable).

* For damping, we similarly get a very cautious test.

So world 1 is like a **strict safety inspector**:

* It will never approve a truly unsafe system.
* But it will reject many safe systems as “too risky, I am not sure”.

That’s why, when we check whether world 1’s answers *always* match the true answers, it fails: there are matrices where world 1 says “unstable” even though the true eigenvalue test says “stable”.

---

## 5. World 2: Diagonal-only heuristic (too optimistic)

In **world 2**, we do something even simpler and more naive:

> Look only at the diagonal entries a₁₁ and a₂₂.

We define:

* **“stable in world 2”** if max(|a₁₁|, |a₂₂|) ≤ 1.0
* **“damped in world 2”** if max(|a₁₁|, |a₂₂|) ≤ 0.9

We completely ignore the off-diagonal entries a₁₂ and a₂₁, which encode how state variables influence each other.

This heuristic is:

* Very cheap and very easy to compute.
* Sometimes roughly okay if the off-diagonal terms are very small.
* But in general, **totally unreliable**.

For example, you can have a matrix like:

> [[0, 2], [-2, 0]]

whose diagonal is zero, so world 2 calls it “very stable”, but its eigenvalues lie on the unit circle of radius 2 (actually ±2i), meaning it’s very *unstable* in the true sense.

So world 2 is like the **optimistic engineer** who only looks at “self-effects” (diagonal terms) and ignores couplings. It often declares systems safe that are, in reality, dangerous.

As a result, world 2 fails our correctness tests dramatically.

---

## 6. World 3: Tiny-norm heuristic (overly pessimistic and silly)

In **world 3**, we try a different kind of shortcut:

> If the entire matrix is tiny, the system is probably stable.

We measure “tiny” with the **Frobenius norm**:

> ||A||_F = sqrt(sum of |aᵢⱼ|² over all entries)

Then we define:

* **“stable in world 3”** if ||A||_F ≤ 0.5
* **“damped in world 3”** if ||A||_F ≤ 0.4

This is deliberately absurdly strict. For example, the identity matrix `I` has norm sqrt(2) ≈ 1.41, but its eigenvalues are exactly 1. So in the true sense:

* `I` is stable (on the boundary of the unit circle),
* but world 3 says “no way, the norm is too big”.

So world 3 represents a **crude rule of thumb** that only accepts extremely tiny matrices and rejects almost everything else, including many perfectly acceptable systems.

In real life, such a heuristic might correspond to someone saying “if all gains are below 0.1, I guess we’re safe”, without thinking about the actual eigenvalues.

---

## 7. Two “theorems” we care about

We now shift from the engineering view to a more logical, “meta” view.

Given any world w (0, 1, 2, or 3), we can ask:

1. Does its notion of “stable” always agree with the true matrix stability?
2. Does its notion of “damped” always agree with the true damping notion?

We treat these as **theorem names** (intensions):

* `thm:CorrectStable`
  means: “this world’s stable predicate is always correct.”
* `thm:CorrectDamped`
  means: “this world’s damped predicate is always correct.”

Of course, we can’t test “all matrices”, so in the code we approximate that by:

* Generating a large number of random 2×2 complex matrices with small integer entries.
* For each, compare:

  * world-w “stable?” vs `stable_true`
  * world-w “damped?” vs `damped_true`
* If there are zero mismatches in all the samples, we treat the theorem as holding in that world (empirically).

This is the **first-order core**: concrete matrices, concrete computations.

---

## 8. Turning it into Holds₁ and Holds₂

To connect with the “higher-order look” story, we introduce:

### 8.1 Holds₁: which theorems are true in which worlds?

We define a function (or relation):

> `Holds1(P, w)`  =  “the theorem named by P holds in world w”.

Implementation-wise:

* We build a dictionary `EXT1` that maps each theorem-name to a set of worlds where it holds.
* Then `Holds1(P, w)` is true exactly if `w` is in that set.

So for example:

* After sampling, world 0 will be in `EXT1["thm:CorrectStable"]` and `EXT1["thm:CorrectDamped"]`.
* Worlds 1, 2, 3 will be in neither set, because we explicitly constructed matrices where they misclassify.

Conceptually:

* `Holds1(thm:CorrectStable, 0)` is our way of saying
  “In world 0, the `stable` test is correct for all samples (and we treat that as a theorem).”
* `Holds1(thm:CorrectStable, 1)` is false: world 1 sometimes gets it wrong.

### 8.2 Holds₂: a “stronger than” relation between theorems

We also introduce a binary relation-name:

> `rel:stronger`

and a binary predicate:

> `Holds2(rel:stronger, X, Y)`  =  “the theorem X is stronger than Y”.

In this case, we want to express the idea that:

> If a world is always correct about damping, then it is also always correct about stability.

Why does that make sense?

* Intuitively, getting “damped vs not damped” right is *harder* than getting “stable vs unstable” right, because damping is a stronger requirement (strictly inside the unit circle, not just inside or on).
* So if a world somehow passes the stricter test on all samples, it will automatically pass the weaker one.

We encode this by:

* Putting the single pair `(thm:CorrectDamped, thm:CorrectStable)` into a set `EXT2["rel:stronger"]`.
* Then `Holds2(rel:stronger, X, Y)` is true exactly when `(X, Y)` is in that set.

So:

* `Holds2(rel:stronger, thm:CorrectDamped, thm:CorrectStable)` is true.
* All other pairs with `rel:stronger` are false.

Now the “higher-order” statement:

> “CorrectDamped is stronger than CorrectStable in our tiny universe.”

becomes a simple extensional fact about membership in `EXT2`.

---

## 9. How the script ties it all together

When you run the script, it does roughly this:

1. **Sample matrices** and compute for each world:

   * How many times its “stable?” matches the true test.
   * How many times its “damped?” matches the true test.
   * Store counts and a boolean flag “does this test hold on all samples?”.

2. **Build `EXT1`** from those results:

   * `EXT1["thm:CorrectStable"]` = set of worlds where no stability mismatch occurred.
   * `EXT1["thm:CorrectDamped"]` = set of worlds where no damping mismatch occurred.

3. **Define `EXT2`** with the single pair `(thm:CorrectDamped, thm:CorrectStable)`.

4. **Print the “Answer” section**:

   * A readable explanation of the four worlds.
   * A table showing how many times each world was correct or incorrect.
   * For each world, the truth values of
     `Holds1(thm:CorrectStable, w)` and `Holds1(thm:CorrectDamped, w)`.

5. **Print the “Reason why” section**:

   * A narrative explanation of stability via eigenvalues.
   * How the approximations (Gershgorin, diagonal-only, tiny norm) behave.
   * How the Holds₁ / Holds₂ relations are constructed.

6. **Run the “Check (harness)”**:

   * A bunch of tests making sure:

     * Eigenvalue computations are sane on simple matrices.
     * World 0 agrees with ground truth on some explicit examples.
     * Worlds 1, 2, 3 each have at least one intentional misclassification.
     * The statistics match expectations (only world 0 gets full marks).
     * `Holds1` and `EXT1` are consistent.
     * The “stronger” relation in `Holds2` is respected:
       whenever `Holds1(thm:CorrectDamped, w)` is true,
       `Holds1(thm:CorrectStable, w)` is also true.

---

## 10. Why this might be useful or interesting

This little case is doing two things at once:

1. **Real-world side**
   It really does something meaningful: given a 2×2 complex matrix A, it can
   compute its eigenvalues and tell you whether the associated system is stable
   or damped in the standard control-theory sense. And it demonstrates how
   various common heuristics (norm bounds, Gershgorin discs, ignoring
   off-diagonal terms) can succeed or fail.

2. **Logical / semantic side**
   It shows how you can package *properties of whole tests* as first-class
   objects (“theorems”) and talk about them with predicates like `Holds1` and
   `Holds2`, without ever leaving a simple numeric core. The mathematics of
   eigenvalues, discs, norms, etc. is all first-order and concrete; the
   “higher-order look” comes only from how we choose to represent which
   theorems hold in which worlds.

You can read it as a tiny story:

* There are four “engineers”, each living in their own world and using their
  own stability test.
* We ask: “Are you always right?” (CorrectStable, CorrectDamped).
* Only the engineer with the true eigenvalue calculation (world 0) can say
  “yes” to both questions; the others have shortcuts that sometimes fail.
* And we formalise that story as a little model where Holds₁ and Holds₂
  encode which theorems hold and how they relate.

That combination—real engineering semantics plus a clean logical “meta-view”—
is exactly the sweet spot this case is trying to illustrate.

