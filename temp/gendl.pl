% Generating deep taxonomy

run :-
    open('dl.pl',write,Out),
    format(Out,"% Deep taxonomy~n",[]),
    format(Out,"% See http://ruleml.org/WellnessRules/files/WellnessRulesN3-2009-11-10.pdf~n",[]),
    format(Out,"~n",[]),
    format(Out,"'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'('http://example.org/ns#i1','http://example.org/ns#N0').~n",[]),
    format(Out,"'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X, D) :- 'http://www.w3.org/2000/01/rdf-schema#subClassOf'(C, D), 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X, C).~n",[]),
    format(Out,"~n",[]),    
    (   between(0,1999999,I),
        J is I+1,
        format(Out,"'http://www.w3.org/2000/01/rdf-schema#subClassOf'('http://example.org/ns#N~d', 'http://example.org/ns#N~d').~n",[I,J]),
        format(Out,"'http://www.w3.org/2000/01/rdf-schema#subClassOf'('http://example.org/ns#N~d', 'http://example.org/ns#I~d').~n",[I,J]),
        format(Out,"'http://www.w3.org/2000/01/rdf-schema#subClassOf'('http://example.org/ns#N~d', 'http://example.org/ns#J~d').~n",[I,J]),
        fail
    ;   true
    ),
    format(Out,"~n",[]),
    format(Out,"run :- 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'('http://example.org/ns#i1','http://example.org/ns#N2000000'), write(true), nl.~n",[]),
    close(Out).
