fibonacci(A, B) :-
    fib(A, 0, 1, B).

fib(0, A, _, A) :-
    !.
fib(1, _, A, A) :-
    !.
fib(A, B, C, D) :-
    A > 1,
    E is A-1,
    F is B+C,
    fib(E, C, F, D).
