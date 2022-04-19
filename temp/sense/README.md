# sense

## sense notation

The sense notation is stemming from [EYE Notation3 P-code](https://josd.github.io/eye/).
It is expressed in [Prolog](https://en.wikipedia.org/wiki/Prolog) syntax and
has the following __terms__ and __clauses__:

TERM            | Examples
----------------|---------
QNAME           | `'eg:Socrates'`
LITERAL         | `"abc"` `"chat"-fr` `"2022-01-15"-'xsd:date'` `-` `1.52` `1e-19` `pi`
VARIABLE        | `X` `_abc` `_`
LIST            | `[TERM,...]` `[TERM,...`\|`LIST]` `[]`
TRIPLE          | `QNAME(TERM,TERM)`
GRAPH           | `TRIPLE,...` `true`

CLAUSE          | Examples
----------------|---------
ASSERTION       | `TRIPLE.`
FORWARD_RULE    | `GRAPH => GRAPH.`
QUERY           | `GRAPH => true.`
ANSWER          | `GRAPH => true.`
INFERENCE_FUSE  | `GRAPH => false.`
BACKWARD_RULE   | `TRIPLE <= GRAPH.`

## sense engine

The [sense engine](./sense.sense) is written in the sense notation.
It performs forward chaining for a `FORWARD_RULE` and backward chaining for a `BACKWARD_RULE`.

Queries are posed and answered as `GRAPH => true.` so the answers are also queries be it with
some parts substituted and eventually containing more variables than in the original query.
This forms a dialogue leading to necessary and sufficient answers so that action can take place.

The builtin triples are:

`'sense:builtin'(`[`Builtin`](https://www.swi-prolog.org/pldoc/man?section=builtin)`,-)`

The domain predicates are available via `'sense:domain_predicate'(Predicate,-)`
so quantifying over predicates could be done as follows:
```
'sense:domain_predicate'(P,-),
'sense:builtin'(Triple =.. [P,_S,_O],-),
Triple
    => true.
```

The witness count is available via `'sense:witness_count'(Count,-)`
so one could use the following to terminate an infinite inference process with existential rules:
```
'sense:witness_count'(Count,-),
'sense:builtin'(Count > 25,-),
'sense:builtin'(halt,-)
    => true.
```

## sense installation and test

Install [swipl](https://www.swi-prolog.org/Download.html) and run [./test](./test) to get
[result.sense](./result.sense).
