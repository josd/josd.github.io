import { SWIPL, loadEye, queryOnce } from 'eyereasoner';

const data = `
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>.
@prefix : <http://example.org/socrates#>.
@prefix log: <http://www.w3.org/2000/10/swap/log#> .

:Socrates a :Human.
:Human rdfs:subClassOf :Mortal.

(_:A _:B _:S) log:onNegativeSurface {
    _:S a _:A .
    _:A rdfs:subClassOf _:B .
    () log:onNegativeSurface {
        _:S a _:B .
    } .
} .

(_:S _:O) log:onQuerySurface {
  _:S a _:O .
} .
`

async function main() {
  const Module = await SWIPL({ print: (str: string) => { console.log(str) }, arguments: ['-q'] });
  loadEye(Module)
  Module.FS.writeFile('data.n3', data);
  queryOnce(Module, 'main', ['--blogic','--quiet', './data.n3']);
}

main();
