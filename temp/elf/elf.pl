:- op(1150,xfx,=>).
:- op(1175,xfx,<=).

term_expansion((Head <= Body),(Head :- Body)).
term_expansion(('elf:directive'(Term,-)),(:- Term)).

goal_expansion('elf:control'(Goal,-),Goal).
goal_expansion('elf:builtin'(Goal,-),Goal).
