@echo off

@echo +++++++++++++++
@echo W3C slide maker
@echo +++++++++++++++

set PERL=..\Tools\perl.exe
set BURST=..\Tools\w3cburst.pl
set ARCH="PC"

del slide*
del Overview*

%PERL% %BURST% cssStandardFiles=%STYLE_SHEET% talkTitle=%TITLE% author=%AUTHOR% authorUrl=%AUTHOR_URL% author2=%AUTHOR2% authorUrl2=%AUTHOR_URL2% logoFile=%LOGO% arch=%ARCH%

set STYLE_SHEET=
set TITLE=
set AUTHOR=
set AUTHOR_URL=
set AUTHOR2=
set AUTHOR_URL2=
set LOGO=
