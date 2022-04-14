# elf

## elf language

The elf language is stemming from the [EYE](https://josd.github.io/eye/) N3P intermediate language.
It is expressed in [ISO Prolog](https://en.wikipedia.org/wiki/Prolog#ISO_Prolog) syntax and
has the following __terms__ and __clauses__:

TERM            | Examples
----------------|---------
QNAME           | `'eg:Socrates'`
LITERAL         | `"abc"` `"chat"-fr` `"2022-01-15"-'xsd:date'` `-` `1.52` `1e-19` `pi`
VARIABLE        | `X` `_abc` `_`
LIST            | `[TERM,...]` `[TERM,...`\|`LIST]` `[]`
TRIPLE          | `QNAME(TERM,TERM)`
GRAPH           | `TRIPLE,...`

CLAUSE          | Examples
----------------|---------
ASSERTION       | `TRIPLE.` `true => GRAPH.`
FORWARD_RULE    | `GRAPH => GRAPH.`
QUERY           | `GRAPH => true.`
ANSWER          | `GRAPH => true.`
INFERENCE_FUSE  | `GRAPH => false.`
BACKWARD_RULE   | `TRIPLE <= GRAPH.`

## elf engine

The [elf engine](./elf.elf) is written in the elf language.
It performs forward chaining for a `FORWARD_RULE` and backward chaining for a `BACKWARD_RULE`.

Queries are posed and answered as `GRAPH => true.` so the answers are also queries be it with
some parts substituted and eventually containing more variables than in the original query.
This forms a dialogue leading to necessary and sufficient answers so that action can take place.

The builtin triples are:

- `'elf:directive'(`[`Directive`](https://www.deransart.fr/prolog/bips.html#directives)`,-)`
- `'elf:control'(`[`Control`](https://www.deransart.fr/prolog/bips.html#control_constructs)`,-)`
- `'elf:builtin'(`[`Builtin`](https://www.deransart.fr/prolog/bips.html#builtins)`,-)`

The domain predicates are available via `'elf:domain_predicate'(Predicate,-)`
so quantifying over predicates could be done as follows:
```
'elf:domain_predicate'(P,-),
'elf:builtin'(Triple =.. [P,_S,_O],-),
Triple
    => true.
```

The witness count is available via `'elf:witness_count'(Count,-)`
so one could use the following to terminate an infinite inference process with existential rules:
```
'elf:witness_count'(Count,-),
'elf:builtin'(Count > 25,-),
'elf:builtin'(halt,-)
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
