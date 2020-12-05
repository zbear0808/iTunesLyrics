@ECHO OFF 
TITLE Execute python script on anaconda environment
ECHO Please Wait...
:: Section 1: Activate the environment.
ECHO ============================
ECHO Conda Activate
ECHO ============================
@CALL "C:\Users\Zubair\anaconda3\Scripts\activate.bat" com
:: Section 2: Execute python script.
ECHO ============================
ECHO Python test.py
ECHO ============================
python "C:\Users\Zubair\Documents\SMLoadr-win-x64_v1.9.5\GUI\PLAYLISTS\FormatPlaylists.py"
python "C:\Users\Zubair\Documents\Python Scripts\iTunes.py"

pause
ECHO ============================
ECHO End
ECHO ============================

