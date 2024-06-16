flag('quantify', 'https://eyereasoner.github.io/.well-known/genid/f5187504-bb2b-4bcf-875a-ca02dfd7b7dd#').
scope('<file:///home/jdroo/github.com/josd/josd.github.io/temp/sample.ttl>').
pfx(:, '<urn:example:>').
:- dynamic('<urn:example:b>'/2).
'<urn:example:b>'('<urn:example:a>', '<urn:example:c>').
:- dynamic('<https://eyereasoner.github.io/.well-known/genid/f5187504-bb2b-4bcf-875a-ca02dfd7b7dd#e_e_1>'/2).
'<https://eyereasoner.github.io/.well-known/genid/f5187504-bb2b-4bcf-875a-ca02dfd7b7dd#e_e_1>'('<https://eyereasoner.github.io/.well-known/genid/f5187504-bb2b-4bcf-875a-ca02dfd7b7dd#e_d_1>', 6).
scount(2).
end_of_file.
