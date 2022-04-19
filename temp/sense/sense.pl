% prolog
:- op(1150,xfx,=>).
:- op(1175,xfx,<=).

term_expansion((Body => Head),((Body => Head) :- true)).
term_expansion((Head <= Body),(Head :- Body)).
term_expansion(('sense:builtin'(Term,-)),(:- Term)).

goal_expansion('sense:builtin'(Goal,-),Goal).

'sense:builtin'(Goal,-) :- Goal.
