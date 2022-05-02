# [solidarity](https://github.com/josd/solidarity)

## solidarity language

The solidarity language is stemming from the [EYE](https://josd.github.io/eye/) N3P intermediate language.
It is expressed in [ISO Prolog](https://en.wikipedia.org/wiki/Prolog#ISO_Prolog) syntax and
has the following __terms__ and __clauses__:

TERM            | Examples
----------------|---------
IRI             | `'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'`
LITERAL         | `"abc"` `"chat"-fr` `"2022-01-15"-'http://www.w3.org/2001/XMLSchema#date'` `-` `1.52` `1e-19` `pi`
VARIABLE        | `X` `_abc` `_`
LIST            | `[TERM,...]` `[TERM,...`\|`LIST]` `[]`
TRIPLE          | `IRI(TERM,TERM)`
GRAPH           | `TRIPLE,...`

CLAUSE          | Examples
----------------|---------
ASSERTION       | `TRIPLE.` `true => GRAPH.`
FORWARD_RULE    | `GRAPH => GRAPH.`
QUERY           | `GRAPH => true.`
ANSWER          | `GRAPH => true.`
INFERENCE_FUSE  | `GRAPH => false.`
BACKWARD_RULE   | `TRIPLE <= GRAPH.`

## solidarity engine

The [solidarity engine](./solidarity.solidarity) is written in the solidarity language.
It performs forward chaining for a `FORWARD_RULE` and backward chaining for a `BACKWARD_RULE`.

Queries are posed and answered as `GRAPH => true.` so the answers are also queries be it with
some parts substituted and eventually containing more variables than in the original query.
This forms a dialogue leading to necessary and sufficient answers so that action can take place.

The builtin triples are:

- `'https://josd.github.io/ns#directive'(`[`Directive`](https://www.deransart.fr/prolog/bips.html#directives)`,-)`
- `'https://josd.github.io/ns#control'(`[`Control`](https://www.deransart.fr/prolog/bips.html#control_constructs)`,-)`
- `'https://josd.github.io/ns#builtin'(`[`Builtin`](https://www.deransart.fr/prolog/bips.html#builtins)`,-)`

The domain predicates are available via `'https://josd.github.io/ns#domain_predicate'(Predicate,-)`
so quantifying over predicates could be done as follows:
```
'https://josd.github.io/ns#domain_predicate'(P,-),
'https://josd.github.io/ns#builtin'(Triple =.. [P,_S,_O],-),
Triple
    => true.
```

The witness count is available via `'https://josd.github.io/ns#witness_count'(Count,-)`
so one could use the following to terminate an infinite inference process with existential rules:
```
'https://josd.github.io/ns#witness_count'(Count,-),
'https://josd.github.io/ns#builtin'(Count > 25,-),
'https://josd.github.io/ns#builtin'(halt,-)
    => true.
```

## Installation and test

Install [Rust](https://www.rust-lang.org/tools/install) and [Scryer](https://github.com/mthom/scryer-prolog#installing-scryer-prolog)
and then run the following from the command line:

```
./test
```

## Background

- Personal notes by Tim Berners-Lee: [Design Issues](https://www.w3.org/DesignIssues/)
- Book of Markus Triska: [The Power of Prolog](https://www.metalevel.at/prolog)
