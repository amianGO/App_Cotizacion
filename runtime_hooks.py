import os
import sys
from pathlib import Path

def get_application_path():
    """
    Obtiene la ruta base de la aplicación, funcionando tanto en desarrollo como en el exe
    """
    if getattr(sys, 'frozen', False):
        # Si estamos ejecutando como exe
        return Path(sys._MEIPASS)
    else:
        # Si estamos en desarrollo
        return Path(__file__).resolve().parent

# Establecer la variable de entorno para la ruta base de la aplicación
os.environ['APP_ROOT'] = str(get_application_path())