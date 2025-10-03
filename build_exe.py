import subprocess
import sys
import os
from pathlib import Path

def check_dependencies():
    """Verificar que todas las dependencias estén instaladas"""
    print("Verificando dependencias...")
    
    required_packages = [
        "pyinstaller",
        "pandas",
        "tkinter"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            if package != "tkinter":  # tkinter viene con Python
                __import__(package)
            print(f" {package} instalado")
        except ImportError:
            print(f" {package} no instalado")
            missing_packages.append(package)
    
    if missing_packages:
        print("\nInstalando paquetes faltantes...")
        for package in missing_packages:
            subprocess.run([sys.executable, "-m", "pip", "install", package])
        print(" Dependencias instaladas")

def build_executable():
    """Construir el ejecutable usando PyInstaller"""
    print("\n Construyendo el ejecutable...")
    
    # Configuración de PyInstaller
    app_name = "CotizacionesApp"
    main_script = "app.py"
    
    # Comando de PyInstaller con todas las opciones necesarias
    temp_dir = os.path.join(os.environ.get('TEMP', os.getcwd()), 'pyinstaller_build')
    os.makedirs(temp_dir, exist_ok=True)
    
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",                # Un solo archivo ejecutable
        "--windowed",               # Sin consola (GUI)
        "--name", app_name,         # Nombre del ejecutable
        "--add-data", "data;data",  # Incluir carpeta data
        "--add-data", "logic;logic",# Incluir carpeta logic
        "--add-data", "ui;ui",      # Incluir carpeta ui
        "--clean",                  # Limpiar archivos temporales
        "--workpath", temp_dir,     # Directorio temporal para la construcción
        "--distpath", "dist",       # Directorio de salida
        main_script
    ]
    
    try:
        # Ejecutar PyInstaller
        subprocess.run(cmd, check=True)
        
        exe_path = Path("dist") / f"{app_name}.exe"
        if exe_path.exists():
            print(f"\n Ejecutable creado exitosamente en: {exe_path.absolute()}")
            print(f" Tamaño: {exe_path.stat().st_size / (1024*1024):.1f} MB")
        else:
            print("\n Error: No se pudo encontrar el ejecutable generado")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"\n Error al crear el ejecutable: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print(" Creando ejecutable de CotizacionesApp")
    print("=" * 50)
    
    # Verificar e instalar dependencias
    check_dependencies()
    
    # Construir el ejecutable
    if build_executable():
        print("\n✨ ¡Proceso completado!")
        print(" Puedes encontrar tu ejecutable en la carpeta 'dist'")
    else:
        print("\n El proceso falló")