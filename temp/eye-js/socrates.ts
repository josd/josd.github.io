import { SWIPL, loadEye, queryOnce } from 'eyereasoner';

const query = `
@prefix : <http://example.org/socrates#>.

{:Socrates a ?WHAT} => {:Socrates a ?WHAT}.
`

const data = `
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>.
@prefix : <http://example.org/socrates#>.

:Socrates a :Human.
:Human rdfs:subClassOf :Mortal.

{?A rdfs:subClassOf ?B. ?S a ?A} => {?S a ?B}.
`

async function main() {
  // Instantiate a new SWIPL module and log any results it produces to the console
  const Module = await SWIPL({ print: (str: string) => { console.log(str) }, arguments: ['-q'] });

  // Load EYE into the SWIPL Module and run consule("eye.pl").
  loadEye(Module)

  // Load the the strings data and query as files data.n3 and query.n3 into the module
  Module.FS.writeFile('data.n3', data);
  Module.FS.writeFile('query.n3', query);

  // Execute main(['--quiet', './data.n3', '--query', './query.n3']).
  queryOnce(Module, 'main', ['--nope', '--quiet', './data.n3', '--query', './query.n3']);
}

main();
