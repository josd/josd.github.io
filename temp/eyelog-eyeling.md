I would **not put literally all effort into one**, but I would make **Eyelog the main R&D line** and keep **Eyeling as an interop/conformance layer**.

My recommendation:

**80% Eyelog, 20% Eyeling.**

Eyelog should become the core symbolic reasoning kernel. Eyeling should remain the N3/RDF bridge, compatibility layer, and benchmark/reference system.

The reason is strategic: the next opportunity is not “Semantic Web adoption” but **symbolic reasoning as a tool inside AI systems**. In that setting, the winning artifact is likely to be small, embeddable, explainable, callable by LLMs, easy to generate, easy to verify, and not culturally tied to RDF/N3 adoption. Eyelog fits that better.

Eyelog is already framed as a compact Prolog-like definite-clause language over ordinary terms, lists, arithmetic, strings, formula data, and finite search, with goal-directed execution and least-Herbrand-model semantics for the pure Horn fragment. That is exactly the kind of clean symbolic substrate that can sit behind LLMs, agents, RAG systems, planners, verifiers, and scientific calculators. ([GitHub][1])

Eyeling is technically valuable, but it is more bound to the N3/RDF world: facts are RDF-like triples, rules are N3 implications, and its strength is Notation3 reasoning with forward/backward chaining, formulas, built-ins, dereferencing, and web-like semantics. ([GitHub][2]) N3 itself is a superset of RDF, so Eyeling inherits both the strengths and the adoption friction of the Semantic Web stack. ([W3C GitHub][3])

The Semantic Web story is nuanced: semantic technologies and knowledge graphs are still used in search, data integration, enterprise systems, and machine learning. ([arXiv][4]) But the public “Semantic Web as a new web of linked machine-readable data” did not really happen at web scale; even RDF/SPARQL advocates increasingly describe the success as enterprise knowledge graphs and RDF technologies rather than “the Semantic Web” vision itself. ([bobdc.com][5]) That makes Eyeling important, but not the best center of gravity.

For neuro-symbolic work, the direction of travel favors **modular symbolic engines** that complement neural models. The MRKL paper explicitly argues for systems with neural models plus external knowledge and discrete reasoning modules. ([arXiv][6]) A 2025 systematic review also reports rapid growth in neuro-symbolic AI since 2020, with major research effort in learning/inference, logic/reasoning, and knowledge representation. ([arXiv][7]) Eyelog is closer to that modular “reasoning module” shape.

So the bet I would make is:

**Eyelog becomes the research platform. Eyeling becomes one important frontend/backend adapter.**

Concretely:

1. **Put new reasoning research in Eyelog**
   Focus on proof explanation, proof certificates, memoization/tabling, bounded search, constraints, aggregation, negation disciplines, probabilistic annotations, LLM-generated rules, and verifiable agent workflows.

2. **Make Eyelog AI-native**
   Provide APIs where an LLM can generate facts/rules, run queries, inspect failures, get proof traces, and repair programs. The surface syntax `ancestor(pat, X)` or `status(case1, accepted)` is easier for models and humans than N3 triples in many applied settings.

3. **Keep Eyeling as N3/RDF compatibility**
   Do not abandon it. It preserves your EYE/N3 heritage, reaches the Semantic Web community, and gives you conformance and provenance credibility. But it should increasingly compile to or interoperate with the Eyelog kernel where possible.

4. **Build translators both ways**
   N3/RDF → Eyelog for reasoning. Eyelog → N3/RDF for publication, linked-data exchange, provenance, and compatibility.

5. **Treat Semantic Web as a data/interchange layer, not the main research thesis**
   The thesis should be: “small symbolic reasoners as trustworthy tools for subsymbolic AI.” RDF/N3 is one supported serialization and ecosystem, not the core identity.

My blunt answer: **bet the future on Eyelog**.

But preserve Eyeling as the bridge to EYE, N3, RDF Surfaces, Semantic Web standards, and historical continuity. The mistake would be killing Eyeling; the bigger mistake would be making Eyeling the place where all new ideas must pass through N3/RDF syntax and culture.

[1]: https://raw.githubusercontent.com/eyereasoner/eyelog/main/SPEC.md "raw.githubusercontent.com"
[2]: https://raw.githubusercontent.com/eyereasoner/eyeling/main/README.md "raw.githubusercontent.com"
[3]: https://w3c.github.io/N3/spec/?utm_source=chatgpt.com "Notation3 Language"
[4]: https://arxiv.org/abs/2412.17159 "[2412.17159] Semantic Web: Past, Present, and Future (with Machine Learning on Knowledge Graphs and Language Models on Knowledge Graphs)"
[5]: https://www.bobdc.com/blog/stopsemanticweb/ "Let's stop saying 'semantic web'"
[6]: https://arxiv.org/abs/2205.00445 "[2205.00445] MRKL Systems: A modular, neuro-symbolic architecture that combines large language models, external knowledge sources and discrete reasoning"
[7]: https://arxiv.org/abs/2501.05435 "[2501.05435] Neuro-Symbolic AI in 2024: A Systematic Review"

