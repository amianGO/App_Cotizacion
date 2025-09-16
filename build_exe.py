#!/usr/bin/env python3
"""
Script para crear el ejecutable (.exe) de la aplicación
"""

import subprocess
import sys
import os
from pathlib import Path

def build_executable():
    """Construye el ejecutable usando PyInstaller"""
    
    print("🔨 Iniciando construcción del ejecutable...")
    
    # Verificar que PyInstaller esté instalado
    try:
        import PyInstaller
        print(" PyInstaller encontrado")
    except ImportError:
        print(" PyInstaller no está instalado. Instalando...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Configuración de PyInstaller
    app_name = "CotizacionesApp"
    main_script = "app.py"
    
    # Comando de PyInstaller
    cmd = [
        "pyinstaller",
        "--onefile",                    # Un solo archivo ejecutable
        "--windowed",                   # Sin consola (GUI)
        "--name", app_name,             # Nombre del ejecutable
        "--add-data", "data;data",      # Incluir carpeta data
        "--add-data", "logic;logic",    # Incluir carpeta logic
        "--add-data", "ui;ui",          # Incluir carpeta ui
        "--hidden-import", "win32com.client",  # Importaciones ocultas
        "--hidden-import", "pandas",
        "--hidden-import", "sqlite3",
        "--hidden-import", "tkinter",
        "--clean",                      # Limpiar archivos temporales
        main_script
    ]
    
    print(f"📦 Construyendo {app_name}.exe...")
    print("⏳ Esto puede tomar varios minutos...")
    
    try:
        # Ejecutar PyInstaller
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        print("✅ ¡Ejecutable creado exitosamente!")
        print(f"📁 Ubicación: {Path.cwd() / 'dist' / f'{app_name}.exe'}")
        print(f"📊 Tamaño aproximado: {get_file_size(Path.cwd() / 'dist' / f'{app_name}.exe')}")
        
        # Limpiar archivos temporales
        print("🧹 Limpiando archivos temporales...")
        import shutil
        if (Path.cwd() / "build").exists():
            shutil.rmtree(Path.cwd() / "build")
        if (Path.cwd() / f"{app_name}.spec").exists():
            (Path.cwd() / f"{app_name}.spec").unlink()
        
        print(" ¡Proceso completado!")
        
    except subprocess.CalledProcessError as e:
        print(f" Error al crear el ejecutable: {e}")
        print(f" Salida de error: {e.stderr}")
        return False
    
    return True

def get_file_size(file_path):
    """Obtiene el tamaño del archivo en formato legible"""
    try:
        size = file_path.stat().st_size
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / (1024 * 1024):.1f} MB"
    except:
        return "Desconocido"

def check_dependencies():
    """Verifica que todas las dependencias estén instaladas"""
    print("🔍 Verificando dependencias...")
    
    required_packages = [
        "pandas",
        "pywin32", 
        "pyinstaller"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f" {package}")
        except ImportError:
            print(f" {package} - No instalado")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n Instalando paquetes faltantes: {', '.join(missing_packages)}")
        for package in missing_packages:
            subprocess.run([sys.executable, "-m", "pip", "install", package])
    
    return len(missing_packages) == 0

if __name__ == "__main__":
    print(" Constructor de Ejecutable - Cotizaciones App")
    print("=" * 50)
    
    # Verificar dependencias
    if not check_dependencies():
        print(" No se pudieron instalar todas las dependencias")
        sys.exit(1)
    
    # Construir ejecutable
    if build_executable():
        print("\n ¡Ejecutable creado exitosamente!")
        print(" Busca el archivo en la carpeta 'dist'")
        print(" Puedes distribuir el .exe sin necesidad de instalar Python")
    else:
        print("\n Error al crear el ejecutable")
        sys.exit(1)
