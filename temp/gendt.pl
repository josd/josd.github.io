% Generating deep taxonomy

run :-
    open('dt.sense',write,Out),
    write(Out,'% Deep taxonomy\n'),
    write(Out,'% See http://ruleml.org/WellnessRules/files/WellnessRulesN3-2009-11-10.pdf\n'),
    write(Out,'\n'),
    write(Out,'\'rdf:type\'(\'eg:z\',\'eg:N0\').\n'),
    write(Out,'\n'),
    (   between(0,9999,I),
        J is I+1,
        format(Out,"'rdf:type'(X,'eg:N~d') => 'rdf:type'(X,'eg:N~d').~n",[I,J]),
        format(Out,"'rdf:type'(X,'eg:N~d') => 'rdf:type'(X,'eg:I~d').~n",[I,J]),
        format(Out,"'rdf:type'(X,'eg:N~d') => 'rdf:type'(X,'eg:J~d').~n",[I,J]),
        fail
    ;   true
    ),
    write(Out,'\n'),
    write(Out,'% query\n'),
    write(Out,'\'rdf:type\'(_ELEMENT,\'eg:N1\') => true.\n'),
    write(Out,'\'rdf:type\'(_ELEMENT,\'eg:N10\') => true.\n'),
    write(Out,'\'rdf:type\'(_ELEMENT,\'eg:N100\') => true.\n'),
    write(Out,'\'rdf:type\'(_ELEMENT,\'eg:N1000\') => true.\n'),
    write(Out,'\'rdf:type\'(_ELEMENT,\'eg:N10000\') => true.\n'),
    close(Out).
