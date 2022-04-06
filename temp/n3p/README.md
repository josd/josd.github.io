# n3p

## Architecture and design

n3p is processing `n3p data` and is itself implemented as [`n3p code`](https://github.com/josd/josd.github.io/temp/n3p/blob/master/n3p.n3p).
It produces `n3p answers` supported by `n3p lemmas`.

It uses [Scryer](https://github.com/mthom/scryer-prolog) and runs on [Rust](https://www.rust-lang.org).

### n3p language

The n3p language is stemming from the [N3](https://w3c.github.io/N3/spec/) compiled prolog code used in the [EYE](https://josd.github.io/eye/) reasoner.
It is expressed in [ISO Prolog](https://en.wikipedia.org/wiki/Prolog#ISO_Prolog) syntax.

It has the following terms and clauses:

TERM            | Examples
----------------|---------
IRI             | `'http://example.org/ns#Socrates'`
LITERAL         | `"abc"` `"chat"-fr` `"2022-01-15"-'http://www.w3.org/2001/XMLSchema#date'` `1.52` `1e-19` `pi`
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

### n3p engine

The n3p engine performs forward chaining for a `FORWARD_RULE` and backward chaining for a `BACKWARD_RULE`.

Queries are posed and answered as `GRAPH => true.` so the answers are also queries be it with
some parts substituted and eventually containing more variables than in the original query.
This forms a dialogue leading to necessary and sufficient answers, supported by lemmas, so that action can take place.

The builtin triples are:

- `'http://josd.github.io/ns#directive'(`[`Directive`](https://www.deransart.fr/prolog/bips.html#directives)`,[])`
- `'http://josd.github.io/ns#control'(`[`Control`](https://www.deransart.fr/prolog/bips.html#control_constructs)`,[])`
- `'http://josd.github.io/ns#builtin'(`[`Builtin`](https://www.deransart.fr/prolog/bips.html#builtins)`,[])`

The domain predicates are available via `'http://josd.github.io/ns#domain_predicate'(Predicate,[])`
so quantifying over predicates could be done as follows:
```
'http://josd.github.io/ns#domain_predicate'(P,[]),
'http://josd.github.io/ns#builtin'(Triple =.. [P,_S,_O],[]),
Triple
    => true.
```

The witness count is available via `'http://josd.github.io/ns#witness_count'(Count,[])`
so one could use the following to terminate an infinite inference process with existential rules:
```
'http://josd.github.io/ns#witness_count'(Count,[]),
'http://josd.github.io/ns#builtin'(Count > 25,[]),
'http://josd.github.io/ns#builtin'(halt,[])
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
