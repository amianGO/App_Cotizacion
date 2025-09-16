#!/usr/bin/env python3
"""
Script de migración de Excel a SQLite
Migra los datos existentes del archivo Excel a la nueva base de datos SQLite
"""

import sys
import os
from pathlib import Path

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from logic.data_manager import _init_database, _get_connection
import pandas as pd

def migrate_from_excel():
    """Migra datos desde Excel a SQLite"""
    
    BASE_DIR = Path(__file__).resolve().parent
    excel_path = BASE_DIR / "data" / "database.xlsx"
    
    if not excel_path.exists():
        print(f" Archivo Excel no encontrado: {excel_path}")
        print("ℹ La aplicación creará automáticamente la base de datos SQLite cuando se ejecute por primera vez.")
        return
    
    print(" Iniciando migración desde Excel a SQLite...")
    
    try:
        # Leer datos de Excel
        print(" Leyendo datos de Excel...")
        products_df = pd.read_excel(excel_path, sheet_name="Productos", dtype=str)
        suppliers_df = pd.read_excel(excel_path, sheet_name="Proveedores", dtype=str)
        
        # Limpiar datos
        products_df = products_df.fillna("").astype(str)
        suppliers_df = suppliers_df.fillna("").astype(str)
        
        print(f" Productos encontrados: {len(products_df)}")
        print(f" Proveedores encontrados: {len(suppliers_df)}")
        
        # Inicializar base de datos SQLite
        print(" Inicializando base de datos SQLite...")
        _init_database()
        
        conn = _get_connection()
        try:
            # Migrar productos
            print(" Migrando productos...")
            products_migrated = 0
            for _, row in products_df.iterrows():
                nombre = str(row.get("Nombre", "")).strip()
                descripcion = str(row.get("Descripcion", "")).strip()
                if nombre:
                    try:
                        conn.execute(
                            "INSERT OR IGNORE INTO productos (nombre, descripcion) VALUES (?, ?)",
                            (nombre, descripcion)
                        )
                        products_migrated += 1
                    except Exception as e:
                        print(f"⚠️ Error migrando producto '{nombre}': {e}")
            
            # Migrar proveedores
            print(" Migrando proveedores...")
            suppliers_migrated = 0
            for _, row in suppliers_df.iterrows():
                nombre = str(row.get("Nombre", "")).strip()
                correo = str(row.get("Correo", "")).strip()
                if nombre and correo and "@" in correo:
                    try:
                        conn.execute(
                            "INSERT OR IGNORE INTO proveedores (nombre, correo) VALUES (?, ?)",
                            (nombre, correo)
                        )
                        suppliers_migrated += 1
                    except Exception as e:
                        print(f"⚠️ Error migrando proveedor '{nombre}': {e}")
            
            conn.commit()
            
            print(f" Migración completada exitosamente!")
            print(f" Productos migrados: {products_migrated}")
            print(f" Proveedores migrados: {suppliers_migrated}")
            print(f" Base de datos SQLite creada en: {BASE_DIR / 'data' / 'database.db'}")
            
        finally:
            conn.close()
            
    except Exception as e:
        print(f" Error durante la migración: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print(" Iniciando migración de Excel a SQLite...")
    success = migrate_from_excel()
    
    if success:
        print("\n ¡Migración completada! Ahora puedes crear el .exe sin problemas.")
        print(" El archivo Excel original se mantiene como respaldo.")
    else:
        print("\n La migración falló. La aplicación creará automáticamente la base de datos SQLite.")
