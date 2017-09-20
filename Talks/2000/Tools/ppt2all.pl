#!/usr/local/bin/perl
#
# Quick Hack to try to convert
# the outlinee.htm file generated
# from powerpoint (frame option)
# to the all.htm used by the slidemaker

$ppt_htm = './ppt/outlinee.htm';
$all = './all.htm';

print "Generating $all ...\n";

# process arguments
foreach (@ARGV) {
    split(/=/);
    $cmd="\$$_[0] = \'$_[1]\';";
    if (length $_[1] !=0) { 
	eval($cmd);
    }
}

# copy file in memory
if (!open(PPT, $ppt_htm)) {
    print "Error: Cannot open file: $all\n";
    exit 0;
}
@table = <PPT>;
close(PPT);


open(ALL, ">$all");

do {
    $_ = $table[0];
    if (/JavaScript:parent.ItemClicked/) {
	s/^.*>(.*)<\/A>.*$/\1/;
	print ALL "<h1>$_</h1>";
    }
    else {
	s/<UL><\/UL>/<P>/g;
	s/<\/UL><UL>/<P>/g;
	s/<UL>//g;
	s/<\/UL>//g;
	s/<LI>//g;
	s/<\/P>//g;
	print ALL $_;
    }
} 
while (shift(@table));

close(ALL);
print "Finished, you can type make now.\n";

