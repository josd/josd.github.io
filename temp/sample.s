flag('quantify', 'https://eyereasoner.github.io/.well-known/genid/7542bd82-27e1-4c20-bfac-f3d99de353f9#').
scope('<file:///home/jdroo/github.com/josd/josd.github.io/temp/sample.ttl>').
pfx(:, '<urn:example:>').
:- dynamic('<urn:example:b>'/2).
'<urn:example:b>'('<urn:example:a>', '<urn:example:c>').
:- dynamic('<urn:example:e>'/2).
'<urn:example:e>'('<https://eyereasoner.github.io/.well-known/genid/7542bd82-27e1-4c20-bfac-f3d99de353f9#e_d_1>', 6).
scount(2).
end_of_file.
