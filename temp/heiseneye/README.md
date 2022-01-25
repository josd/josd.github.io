# Heiseneye

### Reasoning

Heiseneye performs backward chaining for rules like `HEAD :- BODY` and  
forward chaining for rules like `PREM => CONC` where `CONC` is a conjunction.  
There is no principle to tell whether to use backward or forward chaining.  

Queries are posed and answered as `PREM => yes` so the answers are also  
queries be it with some parts substituted and eventually containing more  
variables than in the original query.  

Run the [examples and test cases](./etc) via
```
$ ./test [scryer-prolog|tpl]
```
giving [result for scryer](./result-scryer-prolog.pl) and [result for tpl](./result-tpl.pl).

### Webizing

Heiseneye is using [ISO Prolog notation](https://en.wikipedia.org/wiki/Prolog#ISO_Prolog):

- Uniform resource identifiers are atoms like `'http://example.org/etc#socrates'`
- Literals are strings like `"Hello world!"`, numbers like `1.52` and booleans like `true`
- Typed literals are predicates like `'http://www.w3.org/2001/XMLSchema#date'("2022-01-15")`
- Blank nodes are Skolem functions like `'https://josd.github.io/heiseneye/etc/likes#sk1'(A,B,C)`
- Triples are predicates like `'http://example.org/etc#location'('http://example.org/etc#i1','http://example.org/etc#gent').`

### Background

- Book of Markus Triska: [The Power of Prolog](https://www.metalevel.at/prolog)
