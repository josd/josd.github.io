n_tosx(N1,s(X)) :- N1 > 0, !, N2 is N1-1, n_tosx(N2,X).
n_tosx(0,0).
