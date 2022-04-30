% Generating deep taxonomy

run :-
    open('dt.solidarity',write,Out),
    format(Out,"% Deep taxonomy~n",[]),
    format(Out,"% See http://ruleml.org/WellnessRules/files/WellnessRulesN3-2009-11-10.pdf~n",[]),
    format(Out,"~n",[]),
    format(Out,"'sol:prefix'('rdf:','http://www.w3.org/1999/02/22-rdf-syntax-ns#').~n",[]),
    format(Out,"'sol:prefix'('etc:','https://josd.github.io/etc-ns#').~n",[]),
    format(Out,"~n",[]),
    format(Out,"'sol:directive'(dynamic('rdf:type'/2),-).~n",[]),
    format(Out,"~n",[]),
    format(Out,"'rdf:type'('etc:z','etc:N0').~n",[]),
    format(Out,"~n",[]),
    (   between(0,9999,I),
        J is I+1,
        format(Out,"'rdf:type'(X,'etc:N~d') <= 'rdf:type'(X,'etc:N~d').~n",[J,I]),
        format(Out,"'rdf:type'(X,'etc:I~d') <= 'rdf:type'(X,'etc:N~d').~n",[J,I]),
        format(Out,"'rdf:type'(X,'etc:J~d') <= 'rdf:type'(X,'etc:N~d').~n",[J,I]),
        fail
    ;   true
    ),
    format(Out,"~n",[]),
    format(Out,"% query~n",[]),
    format(Out,"'rdf:type'(_ELEMENT,'etc:N1') => true.~n",[]),
    format(Out,"'rdf:type'(_ELEMENT,'etc:N10') => true.~n",[]),
    format(Out,"'rdf:type'(_ELEMENT,'etc:N100') => true.~n",[]),
    format(Out,"'rdf:type'(_ELEMENT,'etc:N1000') => true.~n",[]),
    format(Out,"'rdf:type'(_ELEMENT,'etc:N10000') => true.~n",[]),
    close(Out).
