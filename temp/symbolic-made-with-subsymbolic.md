# Symbolic AI, Made with Subsymbolic Hands

There is a nice irony in using a language model to help build an RDF Surfaces reasoner.

RDF Surfaces are deeply symbolic: explicit triples, scoped variables, nested negation, codices, and derivations that are either valid or not. A surface is not a suggestion. A rule either matches or it does not. The output is not plausible text; it is a reproducible set of derived statements.

And yet, this symbolic machinery was partly built with a subsymbolic assistant.

That is the interesting part. The language model helped connect examples to implementation, draft tests, update documentation, and debug mistakes. But it did not become the reasoner. Once the feature is implemented, Eyeling derives conclusions because the rules say so, not because a neural model guesses them.

The process also showed why symbolic systems still matter. Small details mattered: whether `_:x` was bound in the right surface, whether `rdf:type` was declared or written as `a`, whether `%not[` was normalized before Turtle parsing, whether a worker regex was escaped correctly. When those details were wrong, the tests failed. The symbolic layer kept the subsymbolic helper honest.

So this is not a story about one AI tradition replacing the other. It is a story about a useful division of labor.

Use subsymbolic AI to help write, search, transform, and explain.

Use symbolic AI to state, derive, verify, and reproduce.

The human keeps the meaning clear, the tests draw the boundary, and the reasoner delivers the exact result.

That makes this a small but lovely case study: symbolic AI made with subsymbolic AI — and then checked by symbolic AI again.
