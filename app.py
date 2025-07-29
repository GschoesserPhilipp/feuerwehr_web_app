import sys
import os
from flask import Flask

# Pfade korrekt einrichten
BASE_DIR = '/home/feuerwehr-app/www/feuerwehr_web_app'
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, 'src'))

# Jetzt erst die App importieren
from src.main import app as application

if __name__ == "__main__":
    application.run()