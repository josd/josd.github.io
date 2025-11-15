# Branches of Insights – brains

In `Branches of Insights – brains`, [each case](https://github.com/josd/josd.github.io/tree/master/brains/cases) is a small, carefully constructed program developed using the **ARC (Answer • Reason • Check)** methodology. The goal is to produce compact and verifiable programs that read like short scientific abstracts.

Each case is not just a black box that produces an outcome. Instead, it functions as a self-contained, end-to-end account of a computation, explicitly showing:

* what question is being answered,
* why the answer is justified, and
* how that justification has been tested.

---

## The ARC Methodology: Answer • Reason • Check

ARC is a lightweight methodology for designing small, trustworthy computational artifacts. Each case is built to deliver a “triad of trust”:

1. **Answer**
   The program computes a clear answer to a well-specified question.

2. **Reason Why**
   The program produces a structured explanation—expressed in ordinary language and grounded in explicit rules, assumptions, or domain knowledge—explaining *why* the answer follows from the inputs.

3. **Check**
   The program runs explicit checks designed to detect violations of assumptions, boundary conditions, or edge cases. When these checks fail, they do so in a visible and traceable way.

The result is a computation with a complete, auditable trace. A reader can see exactly what was done, under which assumptions it was done, and how the program evaluates the reliability of its own output.

---

## P3: Prompt → Program → Proof

The discipline underlying these ARC cases is referred to as **P3**: a pragmatic **Prompt → Program → Proof** workflow. It starts from three basic ingredients:

* **Data**: the facts, measurements, or inputs,
* **Logic**: the rules, models, or constraints, and
* **Question**: the clearly defined problem to be answered.

In this setting, “proof” is understood in a practical, engineering sense rather than as an abstract mathematical derivation. It emerges from combining:

* a narrative explanation of why the result is valid, and
* the verification code embedded in the program.

Formally:

> **Proof = Reason Why + Check**

### A Triad of Trust

Transforming raw data into reliable, actionable insight is a central challenge in modern analytic workflows. The P3 method addresses this by using a large language model (LLM) only at **design time**, to assist with **question-directed program synthesis**.

The process is:

1. Formulate a prompt that specifies what kind of program is needed.
2. State the question precisely.
3. Provide the relevant data, rules, and assumptions.
4. Use the LLM to synthesize a self-contained program that:

   * ingests these inputs,
   * computes the **answer**,
   * generates the **reason** (the structured explanation), and
   * implements the **check** (the verification procedure).

### From Synthesis to Runtime

This method combines the flexibility of generative AI with the rigor of symbolic systems:

* **At design time**, the LLM is used to generate or refine the program based on the prompt, data, and logic.
* **At runtime**, only the synthesized program is executed. The LLM is no longer involved.

During execution, the program:

* produces the answer,
* emits the explanation of why that answer is correct under the specified assumptions, and
* runs its own checks.

Every output is therefore **verifiable by design**. Each case is a self-contained artifact with an internal test harness. It can be:

* integrated into automated pipelines,
* inspected by auditors or peers, and
* deployed operationally with a clear account of its behavior and limitations.

---

## How to Read a Case

Each branch (case) is designed to be self-contained, readable, and reproducible. It is intended to be accessible to a broad audience:

* If you are a **student**, you should be able to follow the logical progression from inputs and assumptions to answer and checks.
* If you are a **practitioner**, you should find the code and checks straightforward to audit and adapt.
* If you are simply **curious**, you should be able to modify parameters, rerun the program, and directly observe how the outputs change.

A practical way to read a case is:

1. Identify the **question** being asked and the final **answer** reported.
2. Examine the **reason** to see how the premises and rules support that answer.
3. Inspect the **check** to understand what is being verified—for example:

   * whether a known identity holds,
   * whether a conservation law is respected, or
   * whether an error remains within a specified bound.

If a check fails, the program reports a specific violation. That failure is treated as a valuable signal for refinement and learning, rather than something to hide.

---

## The Tree of Insights

As these cases accumulate, they form a growing “tree of insights.”

* **Answers** from earlier cases can serve as inputs or assumptions in later cases.
* **Reasons and checks** maintain a consistent level of rigor, helping ensure that the overall structure remains coherent and trustworthy.

In this way, `Branches of Insights – brains` supports the gradual construction of a transparent, testable network of computational insights, where each branch documents not only what is concluded, but also why and how it has been verified.

