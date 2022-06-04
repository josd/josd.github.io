# [eyebrow](https://github.com/josd/josd.github.io/tree/master/temp/eyebrow)

## Reasoning in the browser

Eyebrow is expressed in [ISO Prolog](https://en.wikipedia.org/wiki/Prolog#ISO_Prolog):

TERM            | Examples
----------------|---------
IRI             | `'http://example.org/etc#Socrates'`
LITERAL         | `"abc"` `"chat"-fr` `"2022-01-15"-'http://www.w3.org/2001/XMLSchema#date'` `1.52` `1e-19` `pi`
VARIABLE        | `X` `_abc` `_`
LIST            | `[TERM,...]` `[TERM,...`\|`LIST]` `[]`
LINK            | `IRI(TERM)` `IRI(TERM,TERM)`
GRAPH           | `LINK,...`

CLAUSE          | Examples
----------------|---------
FACT            | `LINK.`
RULE            | `LINK :- GRAPH,`[`PROLOG`](http://tau-prolog.org/documentation#prolog)`.`

Eyebrow is using [modules](https://github.com/josd/josd.github.io/tree/master/temp/eyebrow/modules) from [Tau Prolog](http://tau-prolog.org/).


## Eyebrow examples

- [Complex numbers](https://josd.github.io/temp/eyebrow/examples/complex.html) ([view source](https://github.com/josd/josd.github.io/blob/master/temp/eyebrow/examples/complex.html))
- [Easter date](https://josd.github.io/temp/eyebrow/examples/easter.html) ([view source](https://github.com/josd/josd.github.io/blob/master/temp/eyebrow/examples/easter.html))
- [Extended deep taxonomy](https://josd.github.io/temp/eyebrow/examples/edt.html) ([view source](https://github.com/josd/josd.github.io/blob/master/temp/eyebrow/examples/edt.html))
- [Four color case](https://josd.github.io/temp/eyebrow/examples/fourcolor.html) ([view source](https://github.com/josd/josd.github.io/blob/master/temp/eyebrow/examples/fourcolor.html))
- [GPS](https://josd.github.io/temp/eyebrow/examples/gps.html) ([view source](https://github.com/josd/josd.github.io/blob/master/temp/eyebrow/examples/gps.html))
- [Graph traversal](https://josd.github.io/temp/eyebrow/examples/graph.html) ([view source](https://github.com/josd/josd.github.io/blob/master/temp/eyebrow/examples/graph.html))
- [Lee routing](https://josd.github.io/temp/eyebrow/examples/lee.html) ([view source](https://github.com/josd/josd.github.io/blob/master/temp/eyebrow/examples/lee.html))
- [Meta-interpretation](https://josd.github.io/temp/eyebrow/examples/mi.html) ([view source](https://github.com/josd/josd.github.io/blob/master/temp/eyebrow/examples/mi.html))
- [Socrates is a mortal](https://josd.github.io/temp/eyebrow/examples/socrates.html) ([view source](https://github.com/josd/josd.github.io/blob/master/temp/eyebrow/examples/socrates.html))
- [Superdense coding](https://josd.github.io/temp/eyebrow/examples/sdcoding.html) ([view source](https://github.com/josd/josd.github.io/blob/master/temp/eyebrow/examples/sdcoding.html))
- [Turing machine](https://josd.github.io/temp/eyebrow/examples/turing.html) ([view source](https://github.com/josd/josd.github.io/blob/master/temp/eyebrow/examples/turing.html))


## Background

- Personal notes by Tim Berners-Lee: [Design Issues](https://www.w3.org/DesignIssues/)
- Book of Markus Triska: [The Power of Prolog](https://www.metalevel.at/prolog)
