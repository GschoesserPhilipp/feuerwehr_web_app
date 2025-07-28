import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.main import app as application

if __name__ == "__main__":
    application.run()