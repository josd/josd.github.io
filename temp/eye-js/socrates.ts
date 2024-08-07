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
  console.log('Testing performance of socrates query')

  // Instantiate a new SWIPL module and log any results it produces to the console
  console.time(`Initialise SWIPL and load EYE\t`);
  const Module = await SWIPL({ print: (str: string) => { console.log(str) }, arguments: ['-q'] });
  // Load EYE into the SWIPL Module and run consule("eye.pl").
  loadEye(Module)
  console.timeEnd(`Initialise SWIPL and load EYE\t`);

  // Load the the strings data and query as files data.n3 and query.n3 into the module
  console.time('Load data.n3\t\t');
  Module.FS.writeFile('data.n3', data);
  console.timeEnd('Load data.n3\t\t');

  console.time('Load query.n3\t\t');
  Module.FS.writeFile('query.n3', query);
  console.timeEnd('Load query.n3\t\t');

  console.time('Execute query\t\t');
  queryOnce(Module, 'main', ['--nope', '--quiet', './data.n3', '--query', './query.n3']);
  console.timeEnd('Execute query\t\t');

  console.log()
}

main();
