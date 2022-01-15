% Generating deep taxonomy

:- use_module(library(between)).
:- use_module(library(format)).

run :-
    open('dt.pl',write,Out),
    write(Out,'% Deep taxonomy\n'),
    write(Out,'% See http://ruleml.org/WellnessRules/files/WellnessRulesN3-2009-11-10.pdf\n'),
    write(Out,'\n'),
    write(Out,'\'http://example.org/etc#n0\'(\'http://example.org/etc#z\').\n'),
    write(Out,'\n'),
    (   between(0,999,I),
        J is I+1,
        format(Out,"'http://example.org/etc#n~d'(X) :- 'http://example.org/etc#n~d'(X).~n",[J,I]),
        format(Out,"'http://example.org/etc#i~d'(X) :- 'http://example.org/etc#n~d'(X).~n",[J,I]),
        format(Out,"'http://example.org/etc#j~d'(X) :- 'http://example.org/etc#n~d'(X).~n",[J,I]),
        fail
    ;   true
    ),
    write(Out,'\n'),
    write(Out,'% query implies goal\n'),
    write(Out,'\'http://example.org/etc#n1\'(_ELEMENT) => goal.\n'),
    write(Out,'\'http://example.org/etc#n10\'(_ELEMENT) => goal.\n'),
    write(Out,'\'http://example.org/etc#n100\'(_ELEMENT) => goal.\n'),
    write(Out,'\'http://example.org/etc#n1000\'(_ELEMENT) => goal.\n'),
    close(Out).
