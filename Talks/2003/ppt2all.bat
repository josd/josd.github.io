@echo off
rem # Quick Hack to try to convert
rem # the outlinee.htm file generated
rem # from powerpoint (frame option)
rem # to the all.htm used by the slidemaker

set PPT_HTM="./ppt/outlinee.htm"

rem do not edit under this line
rem ===========================
..\Tools\perl.exe ..\Tools\ppt2all.pl ppt_htm=%PPT_HTM%
