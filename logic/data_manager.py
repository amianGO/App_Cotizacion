from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Dict
import re
import sqlite3
import pandas as pd

# --- Configuracion de rutas y Base de Datos ---

BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "data" / "database.db"

# Tablas y columnas
TABLE_PRODUCTS = "productos"
TABLE_SUPPLIERS = "proveedores"

COLUMNS_PRODUCTS = ["id", "nombre", "descripcion"]
COLUMNS_SUPPLIERS = ["id", "nombre", "correo"]

# -------------------- Utilidades internas --------------------

def _get_connection() -> sqlite3.Connection:
    """Obtiene una conexión a la base de datos SQLite"""
    # Crear directorio si no existe
    DB_PATH.parent.mkdir(exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Para acceso por nombre de columna
    return conn

def _init_database() -> None:
    """Inicializa la base de datos con las tablas necesarias"""
    conn = _get_connection()
    try:
        # Crear tabla de productos
        conn.execute(f'''
            CREATE TABLE IF NOT EXISTS {TABLE_PRODUCTS} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL UNIQUE,
                descripcion TEXT DEFAULT ''
            )
        ''')
        
        # Crear tabla de proveedores
        conn.execute(f'''
            CREATE TABLE IF NOT EXISTS {TABLE_SUPPLIERS} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL UNIQUE,
                correo TEXT NOT NULL
            )
        ''')
        
        conn.commit()
    finally:
        conn.close()

def _normalize_text(s: str) -> str:
    return (s or "").strip()

def _casefold(s: str) -> str:
    """Normalizamos para comparaciones insensibles a mayusculas/acentos."""
    return _normalize_text(s).casefold()


def _is_valid_email(email: str) -> bool:
    """Validacion simple de correo (suficiente para la app)"""
    email = _normalize_text(email)
    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    return bool(re.match(pattern, email))

# -------------------- API publica: Lectura --------------------

def load_products() -> pd.DataFrame:
    """Devuelve Dataframe de productos (id, nombre, descripcion)."""
    _init_database()
    conn = _get_connection()
    try:
        df = pd.read_sql_query(f"SELECT * FROM {TABLE_PRODUCTS}", conn)
        return df
    finally:
        conn.close()

def load_supplier() -> pd.DataFrame:
    """Devuelve el Dataframe de Proveedores (id, nombre, correo)"""
    _init_database()
    conn = _get_connection()
    try:
        df = pd.read_sql_query(f"SELECT * FROM {TABLE_SUPPLIERS}", conn)
        return df
    finally:
        conn.close()


# -------------------- API publica: Escritura CRUD --------------------

def add_product(nombre: str, descripcion: str = "") -> None:
    """Agrega un producto si no existe (comparacion case-insentive)"""
    nombre = _normalize_text(nombre)
    descripcion = _normalize_text(descripcion)
    
    if not nombre:
        raise ValueError("El nombre del producto no puede estar vacio")
    
    _init_database()
    conn = _get_connection()
    try:
        # Verificar si ya existe (case-insensitive)
        cursor = conn.execute(
            f"SELECT id FROM {TABLE_PRODUCTS} WHERE LOWER(nombre) = LOWER(?)",
            (nombre,)
        )
        if cursor.fetchone():
            raise ValueError(f"Ya existe un producto con el nombre '{nombre}'.")
        
        # Insertar nuevo producto
        conn.execute(
            f"INSERT INTO {TABLE_PRODUCTS} (nombre, descripcion) VALUES (?, ?)",
            (nombre, descripcion)
        )
        conn.commit()
    finally:
        conn.close()
    
    
def delete_product(nombre: str) -> int:
    """Elimina productos cuyo nombre coincida (case-insensitve). Retorna cuantos elimino"""
    nombre = _normalize_text(nombre)
    
    if not nombre:
        return 0
    
    _init_database()
    conn = _get_connection()
    try:
        cursor = conn.execute(
            f"DELETE FROM {TABLE_PRODUCTS} WHERE LOWER(nombre) = LOWER(?)",
            (nombre,)
        )
        deleted_count = cursor.rowcount
        conn.commit()
        return deleted_count
    finally:
        conn.close()


def add_supplier(nombre: str, correo: str) -> None:
    """Agrega proveedor validando correo y duplicados por nombre (case-insensitive)"""
    nombre = _normalize_text(nombre)
    correo = _normalize_text(correo)
    
    if not nombre:
        raise ValueError("El nombre del proveedor no puede estar vacio")
    
    if not _is_valid_email(correo):
        raise ValueError(f"El correo '{correo}' no es valido.")
    
    _init_database()
    conn = _get_connection()
    try:
        # Verificar si ya existe (case-insensitive)
        cursor = conn.execute(
            f"SELECT id FROM {TABLE_SUPPLIERS} WHERE LOWER(nombre) = LOWER(?)",
            (nombre,)
        )
        if cursor.fetchone():
            raise ValueError(f"Ya existe un proveedor con el nombre '{nombre}'.")
        
        # Insertar nuevo proveedor
        conn.execute(
            f"INSERT INTO {TABLE_SUPPLIERS} (nombre, correo) VALUES (?, ?)",
            (nombre, correo)
        )
        conn.commit()
    finally:
        conn.close()


def delete_supplier(nombre: str) -> int:
    """Elimina proveedores por nombre (case-insensitive). Retorna cuantos eliminó"""
    nombre = _normalize_text(nombre)
    if not nombre:
        return 0
    
    _init_database()
    conn = _get_connection()
    try:
        cursor = conn.execute(
            f"DELETE FROM {TABLE_SUPPLIERS} WHERE LOWER(nombre) = LOWER(?)",
            (nombre,)
        )
        deleted_count = cursor.rowcount
        conn.commit()
        return deleted_count
    finally:
        conn.close()

# -------------------- Utilidades para la UI --------------------

def search_products(query: str) -> pd.DataFrame:
    """Filtro por substring case-insensitive en Nombre o Descripcion"""
    q = _casefold(query)
    _init_database()
    conn = _get_connection()
    try:
        if not q:
            df = pd.read_sql_query(f"SELECT * FROM {TABLE_PRODUCTS}", conn)
        else:
            df = pd.read_sql_query(
                f"SELECT * FROM {TABLE_PRODUCTS} WHERE "
                f"LOWER(nombre) LIKE LOWER(?) OR LOWER(descripcion) LIKE LOWER(?)",
                conn, params=(f"%{q}%", f"%{q}%")
            )
        return df
    finally:
        conn.close()
    
def search_suppliers(query: str) -> pd.DataFrame:
    """Filtro por substring case-insensitive en Nombre o Correo"""
    q = _casefold(query)
    _init_database()
    conn = _get_connection()
    try:
        if not q:
            df = pd.read_sql_query(f"SELECT * FROM {TABLE_SUPPLIERS}", conn)
        else:
            df = pd.read_sql_query(
                f"SELECT * FROM {TABLE_SUPPLIERS} WHERE "
                f"LOWER(nombre) LIKE LOWER(?) OR LOWER(correo) LIKE LOWER(?)",
                conn, params=(f"%{q}%", f"%{q}%")
            )
        return df
    finally:
        conn.close()


def get_products_by_names(names: Iterable[str]) -> List[Dict[str, str]]:
    """Devuelve lista de dicts de productos {nombre, descripcion} para los nombres dados"""
    wanted = {_casefold(n) for n in names if _normalize_text(n)}
    
    if not wanted:
        return []
    
    _init_database()
    conn = _get_connection()
    try:
        # Crear placeholders para la consulta IN
        placeholders = ','.join('?' * len(wanted))
        query = f"SELECT * FROM {TABLE_PRODUCTS} WHERE LOWER(nombre) IN ({placeholders})"
        
        df = pd.read_sql_query(query, conn, params=list(wanted))
        return df.to_dict(orient="records")
    finally:
        conn.close()

def get_suppliers_by_names(names: Iterable[str]) -> List[Dict[str, str]]:
    """Devuelve lista de dicts de proveedores {nombre, correo} para los nombres dados"""
    wanted = {_casefold(n) for n in names if _normalize_text(n)}
    
    if not wanted:
        return []
    
    _init_database()
    conn = _get_connection()
    try:
        # Crear placeholders para la consulta IN
        placeholders = ','.join('?' * len(wanted))
        query = f"SELECT * FROM {TABLE_SUPPLIERS} WHERE LOWER(nombre) IN ({placeholders})"
        
        df = pd.read_sql_query(query, conn, params=list(wanted))
        return df.to_dict(orient="records")
    finally:
        conn.close()