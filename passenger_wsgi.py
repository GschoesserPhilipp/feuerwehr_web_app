import sys
import os
import logging

# Logging konfigurieren
logging.basicConfig(stream=sys.stderr)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Pfade hinzufügen
APP_DIR = '/home/feuerwehr-app/www/feuerwehr_web_app'
sys.path.insert(0, APP_DIR)
sys.path.insert(0, os.path.join(APP_DIR, 'src'))

try:
    from src.main import app as application

    logger.info("Application successfully loaded")

    # Konfiguration testen
    if not application.config['JWT_SECRET_KEY']:
        logger.error("JWT_SECRET_KEY not configured!")

except Exception as e:
    logger.error(f"Failed to load application: {str(e)}")
    raise