
UPGRADE PROCEDURE:
*****************
!!Becareful if you copy the .exe and .dll file
under unix shell, they no more work under windows.!!


windows version:
to upgrade the slidemaker.zip, unzip it on a windows box
add your new files:
	w3cburst.pl w3ctalk*.css
	Makefile make.bat infos.txt
zip you local C:\Talks\ on the windows box, and put the new slidemaker.zip
back in  /afs/w3.org/pub/WWW/Talks/Tools

unix version:
to upgrade the slidemaker.tgz, 
AFTER you have updated the files 
in /afs/w3.org/pub/WWW/Talks/Tools (using CVS)
	w3cburst.pl w3ctalk*.css
	Makefile make.bat infos.txt

then do:
cd /tmp
gnutar xvzf /afs/w3.org/pub/WWW/Talks/Tools/slidemaker.tgz
cp /afs/w3.org/pub/WWW/Talks/Tools/Makefile /tmp/Talks/Tools
cp /afs/w3.org/pub/WWW/Talks/Tools/make.bat /tmp/Talks/Tools
cp /afs/w3.org/pub/WWW/Talks/Tools/w3cburst.pl /tmp/Talks/Tools
cp /afs/w3.org/pub/WWW/Talks/Tools/w3ctalk*.css /tmp/Talks/Tools
cp all others files you have modified (new icons in Icons/ for example)
gnutar cvzf sm-unix.tgz Talks/

and put the new slidemaker.tgz 
back in  /afs/w3.org/pub/WWW/Talks/Tools
