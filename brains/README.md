# Branches of Insights - brains

In `Branches of Insights - brains`, [each case](https://github.com/josd/josd.github.io/tree/master/brains/cases) is a small, trustworthy program crafted using the **ARC (Answer • Reason • Check)** methodology.

The aim is to write compact, verifiable programs that read like a short abstract. Each case is far more than a black box that spits out a result; it's a concise, end-to-end story told in three parts.

## 💡 The ARC Methodology: Answer • Reason • Check

ARC is a simple methodology for crafting these small, trustworthy programs. Each case delivers a "triad of trust":

1.  **Answer:** The program computes a clear answer to a specific question.
2.  **Reason Why:** It emits a formally constrained account—articulated in everyday language and supported by the relevant rules or ideas—of *why* the answer is correct.
3.  **Check:** It runs concrete checks designed to fail loudly if an assumption is wrong or an edge case matters.

The result is a computation with a complete, auditable trail. You can see precisely what was done, why it was valid under the declared rules, and how the artifact verifies its own work.

## 🚀 P3: Prompt → Program → Proof

The discipline behind these ARC cases is **P3**—a pragmatic **Prompt → Program → Proof** workflow that starts from three fundamental ingredients: **Data**, **Logic**, and a **Question**.

This "proof" isn't a complex external artifact; it's a practical validation formed by the union of the narrative explanation and the verification code the program carries with it.

> **Proof = Reason Why + Check**

### A Triad of Trust

Translating raw data into trusted, actionable insight is a major hurdle. The P3 method addresses this by using a large language model (LLM) at design time for what it does best: question-directed program synthesis.

The process involves formulating a prompt that instructs the model on what kindof program to write, declaring a precise question, and providing the necessary facts and rules. The model is then instructed to write a self-contained program that ingests these inputs and produces the complete "answer, reason, check" output.

### From Synthesis to Runtime

This method blends the flexibility of generative AI with the rigor of symbolic systems.
* **At design time,** the LLM helps synthesize the program from the prompt.
* **At runtime,** only the program executes. It is fully autonomous and produces the answer, emits the reason, and evaluates the checks.

Every output is verifiable by design because it is a self-contained program with its own built-in test harness. This moves beyond the "black box" paradigm, producing a trustworthy and auditable artifact that can be executed in an automated pipeline, shared with auditors, and deployed with confidence.

## How to Read a Case

Each branch is designed to be self-contained, readable, and repeatable. The aim is to be welcoming:
* If you are a **student**, you should be able to follow the line of thought.
* If you are a **practitioner**, you should find the steps easy to audit.
* If you are simply **curious**, you should be able to tinker, change a value, and immediately watch the consequences unfold.

A sensible way to read one is to locate the **question** and the final **answer**, examine the **reason** to see how the premises support the conclusion, and then look at what the **check** actually enforces—whether that is a known identity, a conservation law, or a bound on error.

If a check fails, the branch reports a precise violation, and that failure becomes part of the learning rather than something to hide.

## 🌳 The Tree of Insights

As these cases accumulate, their answers can feed subsequent programs while their reasons and checks preserve the discipline that keeps the whole tree of insights coherent.
