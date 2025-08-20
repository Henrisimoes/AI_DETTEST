@echo off
ECHO.
ECHO    ================================================
ECHO      INICIANDO PORTAL GERADOR DE DOCUMENTOS DETRAN-MT
ECHO    ================================================
ECHO.

ECHO    (1/4) Iniciando o servidor de BACK-END (controlador.py)...
REM Inicia o nosso controlador na porta 5000.
start "Controlador Backend" cmd /c "python controlador.py"

ECHO    (2/4) Iniciando o servidor de FRONT-END (http.server)...
REM Inicia o servidor HTTP do Python na pasta atual (porta 8000 por padrao).
REM Este eh o nosso substituto para o Live Server.
start "Servidor Frontend" cmd /c "python -m http.server 8000"

ECHO    (3/4) Aguardando 3 segundos para os servidores ligarem...
timeout /t 3 >nul

ECHO    (4/4) Abrindo a interface no seu navegador...
REM Agora abrimos a URL correta do nosso servidor de front-end.
start "" "http://localhost:8000/index.html"

ECHO.
ECHO    Pronto! O sistema esta no ar.
ECHO.

REM Esta janela fechara em 5 segundos.
timeout /t 5 >nul
exit