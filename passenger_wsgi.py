import sys
import os
import logging

# Logging konfigurieren
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, '/home/feuerwehr-app/www/feuerwehr_web_app')
sys.path.insert(0, '/home/feuerwehr-app/www/feuerwehr_web_app/src')

try:
    # Explizit aus src.main importieren
    from src.main import app as application
    logging.info("Successfully imported application")
except Exception as e:
    logging.error(f"Import failed: {str(e)}")
    raise