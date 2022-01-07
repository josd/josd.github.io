% Generating deep taxonomy

run :-
    open('dt.pl',write,Out),
    write(Out,'% Deep taxonomy\n'),
    write(Out,'% See http://ruleml.org/WellnessRules/files/WellnessRulesN3-2009-11-10.pdf\n'),
    write(Out,'\n'),
    write(Out,'n0(z).\n'),
    write(Out,'\n'),
    (   between(0,9999,I),
        J is I+1,
        format(Out,"n~d(X) :- n~d(X).~n",[J,I]),
        format(Out,"i~d(X) :- n~d(X).~n",[J,I]),
        format(Out,"j~d(X) :- n~d(X).~n",[J,I]),
        fail
    ;   true
    ),
    write(Out,'\n'),
    write(Out,'% query implies goal\n'),
    write(Out,'n1(_ELEMENT) -: goal.\n'),
    write(Out,'n10(_ELEMENT) -: goal.\n'),
    write(Out,'n100(_ELEMENT) -: goal.\n'),
    write(Out,'n1000(_ELEMENT) -: goal.\n'),
    write(Out,'n10000(_ELEMENT) -: goal.\n'),
    close(Out).
