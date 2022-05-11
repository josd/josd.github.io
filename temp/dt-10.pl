% Deep taxonomy
% See http://ruleml.org/WellnessRules/files/WellnessRulesN3-2009-11-10.pdf

'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'('https://josd.github.io/ns#z','https://josd.github.io/ns#N0').
'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(A,C) :- 'http://www.w3.org/2000/01/rdf-schema#subClassOf'(B,C),'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(A,B).

'http://www.w3.org/2000/01/rdf-schema#subClassOf'('https://josd.github.io/ns#N0','https://josd.github.io/ns#N1').
'http://www.w3.org/2000/01/rdf-schema#subClassOf'('https://josd.github.io/ns#N0','https://josd.github.io/ns#I1').
'http://www.w3.org/2000/01/rdf-schema#subClassOf'('https://josd.github.io/ns#N0','https://josd.github.io/ns#J1').
'http://www.w3.org/2000/01/rdf-schema#subClassOf'('https://josd.github.io/ns#N1','https://josd.github.io/ns#N2').
'http://www.w3.org/2000/01/rdf-schema#subClassOf'('https://josd.github.io/ns#N1','https://josd.github.io/ns#I2').
'http://www.w3.org/2000/01/rdf-schema#subClassOf'('https://josd.github.io/ns#N1','https://josd.github.io/ns#J2').
'http://www.w3.org/2000/01/rdf-schema#subClassOf'('https://josd.github.io/ns#N2','https://josd.github.io/ns#N3').
'http://www.w3.org/2000/01/rdf-schema#subClassOf'('https://josd.github.io/ns#N2','https://josd.github.io/ns#I3').
'http://www.w3.org/2000/01/rdf-schema#subClassOf'('https://josd.github.io/ns#N2','https://josd.github.io/ns#J3').
'http://www.w3.org/2000/01/rdf-schema#subClassOf'('https://josd.github.io/ns#N3','https://josd.github.io/ns#N4').
'http://www.w3.org/2000/01/rdf-schema#subClassOf'('https://josd.github.io/ns#N3','https://josd.github.io/ns#I4').
'http://www.w3.org/2000/01/rdf-schema#subClassOf'('https://josd.github.io/ns#N3','https://josd.github.io/ns#J4').
'http://www.w3.org/2000/01/rdf-schema#subClassOf'('https://josd.github.io/ns#N4','https://josd.github.io/ns#N5').
'http://www.w3.org/2000/01/rdf-schema#subClassOf'('https://josd.github.io/ns#N4','https://josd.github.io/ns#I5').
'http://www.w3.org/2000/01/rdf-schema#subClassOf'('https://josd.github.io/ns#N4','https://josd.github.io/ns#J5').
'http://www.w3.org/2000/01/rdf-schema#subClassOf'('https://josd.github.io/ns#N5','https://josd.github.io/ns#N6').
'http://www.w3.org/2000/01/rdf-schema#subClassOf'('https://josd.github.io/ns#N5','https://josd.github.io/ns#I6').
'http://www.w3.org/2000/01/rdf-schema#subClassOf'('https://josd.github.io/ns#N5','https://josd.github.io/ns#J6').
'http://www.w3.org/2000/01/rdf-schema#subClassOf'('https://josd.github.io/ns#N6','https://josd.github.io/ns#N7').
'http://www.w3.org/2000/01/rdf-schema#subClassOf'('https://josd.github.io/ns#N6','https://josd.github.io/ns#I7').
'http://www.w3.org/2000/01/rdf-schema#subClassOf'('https://josd.github.io/ns#N6','https://josd.github.io/ns#J7').
'http://www.w3.org/2000/01/rdf-schema#subClassOf'('https://josd.github.io/ns#N7','https://josd.github.io/ns#N8').
'http://www.w3.org/2000/01/rdf-schema#subClassOf'('https://josd.github.io/ns#N7','https://josd.github.io/ns#I8').
'http://www.w3.org/2000/01/rdf-schema#subClassOf'('https://josd.github.io/ns#N7','https://josd.github.io/ns#J8').
'http://www.w3.org/2000/01/rdf-schema#subClassOf'('https://josd.github.io/ns#N8','https://josd.github.io/ns#N9').
'http://www.w3.org/2000/01/rdf-schema#subClassOf'('https://josd.github.io/ns#N8','https://josd.github.io/ns#I9').
'http://www.w3.org/2000/01/rdf-schema#subClassOf'('https://josd.github.io/ns#N8','https://josd.github.io/ns#J9').
'http://www.w3.org/2000/01/rdf-schema#subClassOf'('https://josd.github.io/ns#N9','https://josd.github.io/ns#N10').
'http://www.w3.org/2000/01/rdf-schema#subClassOf'('https://josd.github.io/ns#N9','https://josd.github.io/ns#I10').
'http://www.w3.org/2000/01/rdf-schema#subClassOf'('https://josd.github.io/ns#N9','https://josd.github.io/ns#J10').

run :- 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'('https://josd.github.io/ns#z','https://josd.github.io/ns#N10'),write(true),nl.
