% Generating deep taxonomy

run :-
    open('dt.pl',write,Out),
    format(Out,"% Deep taxonomy~n",[]),
    format(Out,"% See http://ruleml.org/WellnessRules/files/WellnessRulesN3-2009-11-10.pdf~n",[]),
    format(Out,"~n",[]),
    format(Out,"'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'('http://example.org/ns#i1','http://example.org/ns#N0').~n",[]),
    format(Out,"~n",[]),
    (   between(0,1999999,I),
        J is I+1,
        format(Out,"'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'http://example.org/ns#N~d') :- 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'http://example.org/ns#N~d').~n",[J,I]),
        format(Out,"'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'http://example.org/ns#I~d') :- 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'http://example.org/ns#N~d').~n",[J,I]),
        format(Out,"'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'http://example.org/ns#J~d') :- 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'http://example.org/ns#N~d').~n",[J,I]),
        fail
    ;   true
    ),
    format(Out,"~n",[]),
    format(Out,"run :- 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'('http://example.org/ns#i1','http://example.org/ns#N2000000'), write(true), nl.~n",[]),
    close(Out).
