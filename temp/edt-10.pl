% Extended deep taxonomy
% See http://ruleml.org/WellnessRules/files/WellnessRulesN3-2009-11-10.pdf

:- dynamic('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'/2).

'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'('http://example.org/ns#i0','http://example.org/ns#N0').
'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'('http://example.org/ns#i1','http://example.org/ns#N0').
'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'('http://example.org/ns#i2','http://example.org/ns#N0').
'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'('http://example.org/ns#i3','http://example.org/ns#N0').
'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'('http://example.org/ns#i4','http://example.org/ns#N0').
'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'('http://example.org/ns#i5','http://example.org/ns#N0').
'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'('http://example.org/ns#i6','http://example.org/ns#N0').
'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'('http://example.org/ns#i7','http://example.org/ns#N0').
'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'('http://example.org/ns#i8','http://example.org/ns#N0').
'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'('http://example.org/ns#i9','http://example.org/ns#N0').
'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'('http://example.org/ns#i10','http://example.org/ns#N0').

'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'http://example.org/ns#N1') :- 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'http://example.org/ns#N0').
'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'http://example.org/ns#I1') :- 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'http://example.org/ns#N0').
'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'http://example.org/ns#J1') :- 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'http://example.org/ns#N0').
'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'http://example.org/ns#N2') :- 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'http://example.org/ns#N1').
'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'http://example.org/ns#I2') :- 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'http://example.org/ns#N1').
'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'http://example.org/ns#J2') :- 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'http://example.org/ns#N1').
'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'http://example.org/ns#N3') :- 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'http://example.org/ns#N2').
'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'http://example.org/ns#I3') :- 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'http://example.org/ns#N2').
'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'http://example.org/ns#J3') :- 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'http://example.org/ns#N2').
'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'http://example.org/ns#N4') :- 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'http://example.org/ns#N3').
'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'http://example.org/ns#I4') :- 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'http://example.org/ns#N3').
'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'http://example.org/ns#J4') :- 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'http://example.org/ns#N3').
'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'http://example.org/ns#N5') :- 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'http://example.org/ns#N4').
'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'http://example.org/ns#I5') :- 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'http://example.org/ns#N4').
'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'http://example.org/ns#J5') :- 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'http://example.org/ns#N4').
'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'http://example.org/ns#N6') :- 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'http://example.org/ns#N5').
'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'http://example.org/ns#I6') :- 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'http://example.org/ns#N5').
'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'http://example.org/ns#J6') :- 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'http://example.org/ns#N5').
'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'http://example.org/ns#N7') :- 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'http://example.org/ns#N6').
'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'http://example.org/ns#I7') :- 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'http://example.org/ns#N6').
'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'http://example.org/ns#J7') :- 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'http://example.org/ns#N6').
'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'http://example.org/ns#N8') :- 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'http://example.org/ns#N7').
'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'http://example.org/ns#I8') :- 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'http://example.org/ns#N7').
'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'http://example.org/ns#J8') :- 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'http://example.org/ns#N7').
'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'http://example.org/ns#N9') :- 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'http://example.org/ns#N8').
'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'http://example.org/ns#I9') :- 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'http://example.org/ns#N8').
'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'http://example.org/ns#J9') :- 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'http://example.org/ns#N8').
'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'http://example.org/ns#N10') :- 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'http://example.org/ns#N9').
'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'http://example.org/ns#I10') :- 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'http://example.org/ns#N9').
'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'http://example.org/ns#J10') :- 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'http://example.org/ns#N9').

% query
query('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'('http://example.org/ns#i10','http://example.org/ns#N10')).

run :- forall(query(X),(X,writeq(X),write('.\n'))).
