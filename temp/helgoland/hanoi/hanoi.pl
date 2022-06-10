% Towers of Hanoi

'https://josd.github.io/helgoland#move'(0,[_,_,_]) :-
    !.
'https://josd.github.io/helgoland#move'(N,[A,B,C]) :-
    M is N-1,
    'https://josd.github.io/helgoland#move'(M,[A,C,B]),
    'https://josd.github.io/helgoland#move'(M,[C,B,A]).

% query
query('https://josd.github.io/helgoland#move'(14,[left,centre,right])).

run :-
    query(Q),
    Q,
    writeq(Q),
    write('.\n'),
    fail;
    true.
