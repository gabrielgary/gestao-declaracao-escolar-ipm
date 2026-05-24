@echo off
echo ==========================================
echo Corrigindo conflito de bibliotecas Python...
echo ==========================================
echo 1. Desinstalando versoes atuais...
pip uninstall -y xhtml2pdf html5lib reportlab
echo.
echo 2. Instalando versoes compativeis (Python 3.13+)...
pip install html5lib==1.0.1
pip install "reportlab>=4.0"
pip install "xhtml2pdf>=0.2.17"
echo.
echo ==========================================
echo Corrections Applied. Please restart your Django server.
echo ==========================================
pause
