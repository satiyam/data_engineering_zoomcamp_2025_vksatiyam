:WHILE_LOOP
FOR /F "delims=" %%i IN ('powershell -Command "(docker ps -q).Count"') DO SET COUNT=%%i
echo Current Container Count: %COUNT%

IF "%COUNT%"=="0" GOTO END_LOOP

timeout /t 5 /nobreak > NUL

GOTO WHILE_LOOP

:END_LOOP
echo No Containers Running. Monitoring finished.