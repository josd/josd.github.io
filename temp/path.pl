:- dynamic(path/2).

oneway(paris,orleans).
oneway(paris,chartres).
oneway(paris,amiens).
oneway(orleans,blois).
oneway(orleans,bourges).
oneway(blois,tours).
oneway(chartres,lemans).
oneway(lemans,angers).
oneway(lemans,tours).
oneway(angers,nantes).

implies(oneway(A,B),path(A,B)).
implies((path(A,B),path(B,C)),path(A,C)).

run :-
    implies(Prem,Conc),
    Prem,
    \+Conc,
    assertz(Conc),
    write(implies(Prem,Conc)),
    nl,
    fail.
run.
