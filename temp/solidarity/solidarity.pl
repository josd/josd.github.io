:- op(1150,xfx,=>).
:- op(1175,xfx,<=).

term_expansion((Head <= Body),(Head :- Body)).
term_expansion(('https://josd.github.io/ns#directive'(Term,-)),(:- Term)).

goal_expansion('https://josd.github.io/ns#control'(Goal,-),Goal).
goal_expansion('https://josd.github.io/ns#builtin'(Goal,-),Goal).
