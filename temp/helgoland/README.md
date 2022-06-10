# helgoland

## Reasoning on Web scale

Helgoland is expressed in [ISO Prolog](https://en.wikipedia.org/wiki/Prolog#ISO_Prolog)

TERM            | Examples
----------------|---------
IRI             | `'http://example.org/etc#Socrates'`
LITERAL         | `"abc"` `"chat"-fr` `"2022-01-15"-'http://www.w3.org/2001/XMLSchema#date'` `1.52` `1e-19` `pi`
VARIABLE        | `X` `_abc` `_`
LIST            | `[TERM,...]` `[TERM,...`\|`LIST]` `[]`
TRIPLE          | `IRI(TERM,TERM)`
GRAPH           | `TRIPLE,...`

CLAUSE          | Examples
----------------|---------
FACT            | `TRIPLE.`
RULE            | `TRIPLE :- GRAPH,`[`PROLOG`](https://github.com/trealla-prolog/trealla)`.`


## Installation and test

Install [Trealla Prolog](https://github.com/trealla-prolog/trealla#building) and then run

```
./test
```

## Background

- Personal notes by Tim Berners-Lee: [Design Issues](https://www.w3.org/DesignIssues/)
- Book of Markus Triska: [The Power of Prolog](https://www.metalevel.at/prolog)
