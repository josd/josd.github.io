% Generating deep taxonomy

:- use_module(library(format)).
:- use_module(library(between)).

run :-
    open('dt.solidarity',write,Out),
    format(Out,"% Deep taxonomy~n",[]),
    format(Out,"% See http://ruleml.org/WellnessRules/files/WellnessRulesN3-2009-11-10.pdf~n",[]),
    format(Out,"~n",[]),
    format(Out,"'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'('https://josd.github.io/ns#z','https://josd.github.io/ns#N0').~n",[]),
    format(Out,"~n",[]),
    (   between(0,9999,I),
        J is I+1,
        format(Out,"'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'https://josd.github.io/ns#N~d') <= 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'https://josd.github.io/ns#N~d').~n",[J,I]),
        format(Out,"'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'https://josd.github.io/ns#I~d') <= 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'https://josd.github.io/ns#N~d').~n",[J,I]),
        format(Out,"'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'https://josd.github.io/ns#J~d') <= 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(X,'https://josd.github.io/ns#N~d').~n",[J,I]),
        fail
    ;   true
    ),
    format(Out,"~n",[]),
    format(Out,"% query~n",[]),
    format(Out,"'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(_ELEMENT,'https://josd.github.io/ns#N1') => true.~n",[]),
    format(Out,"'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(_ELEMENT,'https://josd.github.io/ns#N10') => true.~n",[]),
    format(Out,"'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(_ELEMENT,'https://josd.github.io/ns#N100') => true.~n",[]),
    format(Out,"'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(_ELEMENT,'https://josd.github.io/ns#N1000') => true.~n",[]),
    format(Out,"'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'(_ELEMENT,'https://josd.github.io/ns#N10000') => true.~n",[]),
    close(Out).
