@echo off
echo =========================================
echo   M-Motors — Setup Django (Windows)
echo =========================================
echo.

:: Créer l'environnement virtuel
echo [1/5] Creation de l'environnement virtuel...
python -m venv venv
if errorlevel 1 (echo ERREUR : Python non trouve. Installez Python 3.10+ & pause & exit /b 1)

:: Activer l'env
echo [2/5] Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

:: Installer les dépendances
echo [3/5] Installation des dependances...
pip install -r requirements.txt

:: Migrations
echo [4/5] Creation de la base de donnees...
python manage.py makemigrations accounts vehicles dossiers
python manage.py migrate

:: Seed
echo [5/5] Initialisation des donnees de test...
python seed.py

echo.
echo =========================================
echo   SETUP TERMINE !
echo =========================================
echo.
echo Lancer le serveur :
echo   venv\Scripts\activate.bat
echo   python manage.py runserver
echo.
echo URLs :
echo   Site front-end : ouvrir m-motors-app\index.html
echo   Admin Django   : http://127.0.0.1:8000/admin/
echo   API vehicules  : http://127.0.0.1:8000/api/vehicles/
echo   API dossiers   : http://127.0.0.1:8000/api/dossiers/
echo.
pause
