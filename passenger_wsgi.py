import sys
import os

# Füge den src-Ordner dem Python-Importpfad hinzu
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Importiere die Flask-App aus src/main.py
from main import app as application
