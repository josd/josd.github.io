:- dynamic(path/3).

oneway(france,paris,orleans).
oneway(france,paris,chartres).
oneway(france,paris,amiens).
oneway(france,orleans,blois).
oneway(france,orleans,bourges).
oneway(france,blois,tours).
oneway(france,chartres,lemans).
oneway(france,lemans,angers).
oneway(france,lemans,tours).
oneway(france,angers,nantes).

implies(oneway(A,B,C),path(A,B,C)).
implies((path(A,B,C),path(A,C,D)),path(A,B,D)).

run :-
    implies(Prem,Conc),
    Prem,
    \+Conc,
    assertz(Conc),
    write(implies(Prem,Conc)),
    nl,
    run.
run.
