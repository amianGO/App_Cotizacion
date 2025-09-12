from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Dict
import re

import pandas as pd


# --- Configuracion de rutas y Hojas ---

BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "data" / "database.xlsx"

SHEET_PRODUCTS = "Productos"
SHEET_SUPPLIERS = "Proveedores"

# Columnas esperadas en cada hoja

COLUMNS_PRODUCTS = ["Nombre", "Descripcion"]
COLUMNS_SUPPLIERS = ["Nombre", "Correo"]

# -------------------- Utilidades internas --------------------

def _require_db_exists() -> None:
    """ Verifica que la base de datos exista; si no, lanza un error claro."""
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"No se encontro la base de datos en {DB_PATH}"
            "Crea el archivo 'database.xlsx' en /data con las hojas "
            f" '{SHEET_PRODUCTS}' ({', '.join(COLUMNS_PRODUCTS)}) y "
            f" '{SHEET_SUPPLIERS}' ({', '.join(COLUMNS_SUPPLIERS)})- "
        )

def _read_sheet(sheet_name: str, expected_cols: List[str]) -> pd.DataFrame:
    """Lee una hoja garantizando columnas y tipos como texto."""
    _require_db_exists()
    try:
        df = pd.read_excel(DB_PATH, sheet_name = sheet_name, engine="openpyxl", dtype=str)
    except ValueError as exc: # Hoja no encontrada
        raise ValueError(
            f"La Hoja '{sheet_name}' No existe en {DB_PATH}. "
            "Verifica el nombre de la hoja."
        ) from exc
    
    # Normalizamos: todo texto, sin NaN y columnas en el orden esperado
    df = df.fillna("").astype(str)
    
    # Si faltan columnas obligatorias, error explicito
    missing = [c for c in expected_cols if c not in df.columns]
    if missing:
        raise ValueError(
            f"En la hoja '{sheet_name}' faltan columnas obligatorias: {missing}. "
            f"Se esperaban: {expected_cols}"
        )
    
    # Reordenamos y nos quedamos solo con las esperadas
    df = df[expected_cols].copy()
    return df


def _write_sheet(df: pd.DataFrame, sheet_name: str) -> None:
    """Escribre solo la hoja indicada y remplazamos la hoja especifica"""
    _require_db_exists
    #Escribimos en modo append y remplazamos la hoja especifica
    
    with pd.ExcelWriter(
        DB_PATH, engine="openpyxl", mode="a", if_sheet_exists = "replace"
    ) as writer:
        df.to_excel(writer, index= False, sheet_name = sheet_name)

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
    """Devuelve Dataframe de productos (Nombre, Descripcion)."""
    return _read_sheet(SHEET_PRODUCTS, COLUMNS_PRODUCTS)

def load_supplier() -> pd.DataFrame:
    """Devuelve el Dataframe de Proveedores (Nombre, Correo)"""
    return _read_sheet(SHEET_SUPPLIERS, COLUMNS_SUPPLIERS)


# -------------------- API publica: Escritura CRUD --------------------

def add_product(nombre: str, descripcion: str = "") -> None:
    """Agrega un producto si no existe (comparacion case-insentive)"""
    nombre = _normalize_text(nombre)
    descripcion = _normalize_text(descripcion)
    
    if not nombre:
        raise ValueError("El nombre del producto no puede estar vacio")
    
    df = load_products()
    if any(_casefold(x) == _casefold(nombre) for x in df["Nombre"]):
        raise ValueError(f"Ya existe un producto con el nombre '{nombre}'. ")
    
    df = pd.concat(
        [df, pd.DataFrame([{"Nombre":nombre, "Descripcion":descripcion}])],
        ignore_index=True
    )
    
    _write_sheet(df, SHEET_PRODUCTS)
    
    
def delete_product(nombre: str) -> int:
    """Elimina productos cuyo nombre coincida (case-insensitve). Retorna cuantos elimino"""
    nombre = _normalize_text(nombre)
    
    if not nombre:
        return 0
    
    df = load_products()
    mask = df["Nombre"].apply(_casefold) != _casefold(nombre)
    removed = len(df) - mask.sum()
    
    if removed > 0:
        _write_sheet(df[mask].reset_index(drop=True),SHEET_PRODUCTS)
        
    return removed


def add_supplier(nombre: str, correo: str) -> None:
    """Agrega proveedor validando correo y duplicados por nombre (case-insensitive)"""
    nombre = _normalize_text(nombre)
    correo = _normalize_text(correo)
    
    if not nombre:
        raise ValueError("El nombre del proveedor no puede estar vacio")
    
    if not _is_valid_email(correo):
        raise ValueError(f"El correo '{correo}' no es valido. ")
    
    df = load_supplier()
    if any(_casefold(x) == _casefold(nombre) for x in df["Nombre"]):
        raise ValueError(f"Ya existe un proveedor con el nombre '{nombre}.'")
    
    df = pd.concat(
        [df, pd.DataFrame([{"Nombre":nombre, "Correo": correo}])],
        ignore_index= True
    )
    
    _write_sheet(df, SHEET_SUPPLIERS)


def delete_supplier(nombre: str) -> int:
    """Elimina proveedores por nombre (case-insensitive). Retorna cuantos eliminó"""
    nombre = _normalize_text(nombre)
    if not nombre:
        return 0
    
    df = load_supplier()
    mask = df["Nombre"].apply(_casefold) != _casefold(nombre)
    removed = len(df) - mask.sum()
    
    if removed > 0:
        _write_sheet(df[mask].reset_index(drop= True), SHEET_SUPPLIERS)
    
    return removed

# -------------------- Utilidades para la UI --------------------

def search_products(query: str) -> pd.DataFrame:
    """Filtro por substring case-insensitive en Nombre o Descripcion"""
    q = _casefold(query)
    df = load_products()
    
    if not q:
        return df
    
    return df[
        df["Nombre"].str.casefold().str.contains(q) | df["Descripcion"].str.casefold().str.contains(q)
    ].reset_index(drop = True)
    
def search_suppliers(query: str) -> pd.DataFrame:
    """Filtro por substring case-insensitive en Nombre o Correo"""
    q = _casefold(query)
    df = load_supplier()
    
    if not q:
        return df
    
    return df[
        df["Nombre"].str.casefold().str.contains(q) | df["Correo"].str.casefold().str.contains(q)
    ].reset_index(drop = True)


def get_products_by_names(names: Iterable[str]) -> List[Dict[str, str]]:
    """Devuelve lista de dicts de productos {Nombre, Descripcion} para los nombres dados"""
    wanted = {_casefold(n) for n in names if _normalize_text(n)}
    
    if not wanted:
        return[]
    
    df = load_products()
    df = df[df["Nombre"].apply(_casefold).isin(wanted)]
    return df.to_dict(orient="records")

def get_suppliers_by_names(names: Iterable[str]) -> List[Dict[str, str]]:
    """Devuelve lista de dicts de proveeodres {Nombre, Correo} para los nombres dados"""
    wanted = {_casefold(n) for n in names if _normalize_text(n)}
    
    if not wanted:
        return[]
    
    df = load_supplier()
    df = df[df["Nombre"].apply(_casefold).isin(wanted)]
    return df.to_dict(orient="records")