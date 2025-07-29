import sys
import os
import logging

# Add src directory to path
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

# Set up logging
logging.basicConfig(stream=sys.stderr)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

try:
    from main import app as application
    logger.debug("Successfully imported Flask application")
except Exception as e:
    logger.error(f"Failed to import Flask application: {str(e)}")
    raise