flag('quantify', 'https://eyereasoner.github.io/.well-known/genid/18ed0e3b-7e21-4b82-9834-765af2728b65#').
scope('<file:///home/jdroo/github.com/josd/josd.github.io/temp/sample.ttl>').
pfx(:, '<urn:example:>').
:- dynamic('<urn:example:b>'/2).
'<urn:example:b>'('<urn:example:a>', '<urn:example:c>').
:- dynamic('<urn:example:e>'/2).
'<urn:example:e>'('<https://eyereasoner.github.io/.well-known/genid/18ed0e3b-7e21-4b82-9834-765af2728b65#e_d_1>', 6).
scount(2).
end_of_file.
