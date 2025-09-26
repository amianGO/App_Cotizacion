from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Dict, Optional
import re
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox

# --- Configuracion de rutas y Base de Datos ---

BASE_DIR = Path(__file__).resolve().parents[1]
EXCEL_PATH = None  # Se establecerá cuando se cargue un archivo

# Columnas esperadas
COLUMNS_PRODUCTS = ["Nombre", "Descripcion"]
COLUMNS_SUPPLIERS = ["Nombre", "Correo"]

# -------------------- Utilidades internas --------------------

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

# -------------------- Funciones de Excel --------------------

def _load_excel_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Carga datos desde Excel"""
    if EXCEL_PATH is None or not EXCEL_PATH.exists():
        return pd.DataFrame(), pd.DataFrame()
    
    try:
        products_df = pd.read_excel(EXCEL_PATH, sheet_name="Productos", dtype=str)
        suppliers_df = pd.read_excel(EXCEL_PATH, sheet_name="Proveedores", dtype=str)
        
        # Limpiar datos
        products_df = products_df.fillna("").astype(str)
        suppliers_df = suppliers_df.fillna("").astype(str)
        
        return products_df, suppliers_df
    except Exception as e:
        print(f"Error cargando Excel: {e}")
        return pd.DataFrame(), pd.DataFrame()

def _create_empty_excel() -> None:
    """Crea un archivo Excel vacío con las hojas necesarias"""
    try:
        with pd.ExcelWriter(EXCEL_PATH, engine='openpyxl') as writer:
            # Crear hoja de productos vacía
            products_df = pd.DataFrame(columns=COLUMNS_PRODUCTS)
            products_df.to_excel(writer, sheet_name='Productos', index=False)
            
            # Crear hoja de proveedores vacía
            suppliers_df = pd.DataFrame(columns=COLUMNS_SUPPLIERS)
            suppliers_df.to_excel(writer, sheet_name='Proveedores', index=False)
        
        print(f"Archivo Excel creado: {EXCEL_PATH}")
    except Exception as e:
        print(f"Error creando Excel: {e}")

def _save_excel_data(products_df: pd.DataFrame, suppliers_df: pd.DataFrame) -> None:
    """Guarda datos en Excel"""
    try:
        with pd.ExcelWriter(EXCEL_PATH, engine='openpyxl') as writer:
            products_df.to_excel(writer, sheet_name='Productos', index=False)
            suppliers_df.to_excel(writer, sheet_name='Proveedores', index=False)
        print("Datos guardados en Excel exitosamente")
    except Exception as e:
        print(f"Error guardando Excel: {e}")
        raise

# -------------------- API publica: Lectura --------------------

def load_products() -> pd.DataFrame:
    """Devuelve Dataframe de productos (Nombre, Descripcion)."""
    products_df, _ = _load_excel_data()
    if products_df.empty:
        return pd.DataFrame(columns=COLUMNS_PRODUCTS)
    return products_df

def load_supplier() -> pd.DataFrame:
    """Devuelve el Dataframe de Proveedores (Nombre, Correo)"""
    _, suppliers_df = _load_excel_data()
    if suppliers_df.empty:
        return pd.DataFrame(columns=COLUMNS_SUPPLIERS)
    return suppliers_df

# -------------------- API publica: Escritura CRUD --------------------

def add_product(nombre: str, descripcion: str = "") -> None:
    """Agrega un producto si no existe (comparacion case-insentive)"""
    nombre = _normalize_text(nombre)
    descripcion = _normalize_text(descripcion)
    
    if not nombre:
        raise ValueError("El nombre del producto no puede estar vacio")
    
    products_df, suppliers_df = _load_excel_data()
    
    # Verificar si ya existe (case-insensitive)
    existing_products = products_df[products_df['Nombre'].str.lower() == nombre.lower()]
    if not existing_products.empty:
        raise ValueError(f"Ya existe un producto con el nombre '{nombre}'.")
    
    # Agregar nuevo producto
    new_product = pd.DataFrame({
        'Nombre': [nombre],
        'Descripcion': [descripcion]
    })
    products_df = pd.concat([products_df, new_product], ignore_index=True)
    _save_excel_data(products_df, suppliers_df)

def delete_product(nombre: str) -> int:
    """Elimina productos cuyo nombre coincida (case-insensitve). Retorna cuantos elimino"""
    nombre = _normalize_text(nombre)
    
    if not nombre:
        return 0
    
    products_df, suppliers_df = _load_excel_data()
    original_count = len(products_df)
    products_df = products_df[products_df['Nombre'].str.lower() != nombre.lower()]
    deleted_count = original_count - len(products_df)
    
    if deleted_count > 0:
        _save_excel_data(products_df, suppliers_df)
    
    return deleted_count

def add_supplier(nombre: str, correo: str) -> None:
    """Agrega proveedor validando correo y duplicados por nombre (case-insensitive)"""
    nombre = _normalize_text(nombre)
    correo = _normalize_text(correo)
    
    if not nombre:
        raise ValueError("El nombre del proveedor no puede estar vacio")
    
    if not _is_valid_email(correo):
        raise ValueError(f"El correo '{correo}' no es valido.")
    
    products_df, suppliers_df = _load_excel_data()
    
    # Verificar si ya existe (case-insensitive)
    existing_suppliers = suppliers_df[suppliers_df['Nombre'].str.lower() == nombre.lower()]
    if not existing_suppliers.empty:
        raise ValueError(f"Ya existe un proveedor con el nombre '{nombre}'.")
    
    # Agregar nuevo proveedor
    new_supplier = pd.DataFrame({
        'Nombre': [nombre],
        'Correo': [correo]
    })
    suppliers_df = pd.concat([suppliers_df, new_supplier], ignore_index=True)
    _save_excel_data(products_df, suppliers_df)

def delete_supplier(nombre: str) -> int:
    """Elimina proveedores por nombre (case-insensitive). Retorna cuantos eliminó"""
    nombre = _normalize_text(nombre)
    if not nombre:
        return 0
    
    products_df, suppliers_df = _load_excel_data()
    original_count = len(suppliers_df)
    suppliers_df = suppliers_df[suppliers_df['Nombre'].str.lower() != nombre.lower()]
    deleted_count = original_count - len(suppliers_df)
    
    if deleted_count > 0:
        _save_excel_data(products_df, suppliers_df)
    
    return deleted_count

# -------------------- Utilidades para la UI --------------------

def search_products(query: str) -> pd.DataFrame:
    """Filtro por substring case-insensitive en Nombre o Descripcion"""
    q = _casefold(query)
    
    products_df, _ = _load_excel_data()
    if products_df.empty:
        return pd.DataFrame(columns=COLUMNS_PRODUCTS)
    
    if not q:
        return products_df
    else:
        mask = (products_df['Nombre'].str.lower().str.contains(q, na=False) |
               products_df['Descripcion'].str.lower().str.contains(q, na=False))
        return products_df[mask]

def search_suppliers(query: str) -> pd.DataFrame:
    """Filtro por substring case-insensitive en Nombre o Correo"""
    q = _casefold(query)
    
    _, suppliers_df = _load_excel_data()
    if suppliers_df.empty:
        return pd.DataFrame(columns=COLUMNS_SUPPLIERS)
    
    if not q:
        return suppliers_df
    else:
        mask = (suppliers_df['Nombre'].str.lower().str.contains(q, na=False) |
               suppliers_df['Correo'].str.lower().str.contains(q, na=False))
        return suppliers_df[mask]

def get_products_by_names(names: Iterable[str]) -> List[Dict[str, str]]:
    """Devuelve lista de dicts de productos {Nombre, Descripcion} para los nombres dados"""
    wanted = {_casefold(n) for n in names if _normalize_text(n)}
    
    if not wanted:
        return []
    
    products_df, _ = _load_excel_data()
    if products_df.empty:
        return []
    
    # Filtrar productos por nombres
    mask = products_df['Nombre'].str.lower().isin(wanted)
    filtered_df = products_df[mask]
    return filtered_df.to_dict(orient="records")

def get_suppliers_by_names(names: Iterable[str]) -> List[Dict[str, str]]:
    """Devuelve lista de dicts de proveedores {Nombre, Correo} para los nombres dados"""
    wanted = {_casefold(n) for n in names if _normalize_text(n)}
    
    if not wanted:
        return []
    
    _, suppliers_df = _load_excel_data()
    if suppliers_df.empty:
        return []
    
    # Filtrar proveedores por nombres
    mask = suppliers_df['Nombre'].str.lower().isin(wanted)
    filtered_df = suppliers_df[mask]
    return filtered_df.to_dict(orient="records")

def force_save():
    """Fuerza el guardado de todos los cambios pendientes"""
    # En Excel, los datos se guardan automáticamente en cada operación
    print("Datos guardados en Excel")

def get_database_status():
    """Obtiene el estado de la base de datos"""
    products_df, suppliers_df = _load_excel_data()
    return {
        "products": len(products_df),
        "suppliers": len(suppliers_df),
        "database_path": str(EXCEL_PATH),
        "mode": "Excel"
    }

# -------------------- Funciones de carga de Excel --------------------

def load_excel_file(file_path: Optional[str] = None) -> bool:
    """Carga un archivo Excel y establece la ruta global"""
    global EXCEL_PATH
    
    if file_path is None:
        # Abrir diálogo para seleccionar archivo
        root = tk.Tk()
        root.withdraw()  # Ocultar ventana principal
        
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo Excel",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        
        root.destroy()
        
        if not file_path:
            return False
    
    file_path = Path(file_path)
    if not file_path.exists():
        messagebox.showerror("Error", f"El archivo {file_path} no existe")
        return False
    
    try:
        # Leer datos del Excel
        products_df = pd.read_excel(file_path, sheet_name="Productos", dtype=str)
        suppliers_df = pd.read_excel(file_path, sheet_name="Proveedores", dtype=str)
        
        # Limpiar datos
        products_df = products_df.fillna("").astype(str)
        suppliers_df = suppliers_df.fillna("").astype(str)
        
        # Validar estructura
        if 'Nombre' not in products_df.columns:
            messagebox.showerror("Error", "El archivo Excel debe tener una columna 'Nombre' en la hoja 'Productos'")
            return False
        
        if 'Nombre' not in suppliers_df.columns or 'Correo' not in suppliers_df.columns:
            messagebox.showerror("Error", "El archivo Excel debe tener columnas 'Nombre' y 'Correo' en la hoja 'Proveedores'")
            return False
        
        # Establecer la ruta global
        EXCEL_PATH = file_path
        
        # Mostrar resumen
        products_count = len(products_df[products_df['Nombre'].str.strip() != ''])
        suppliers_count = len(suppliers_df[suppliers_df['Nombre'].str.strip() != ''])
        
        messagebox.showinfo("Éxito", 
            f"Archivo Excel cargado exitosamente!\n\n"
            f"Productos cargados: {products_count}\n"
            f"Proveedores cargados: {suppliers_count}\n"
            f"Archivo: {file_path.name}"
        )
        
        return True
        
    except Exception as e:
        messagebox.showerror("Error", f"Error al cargar el archivo Excel: {str(e)}")
        return False

def get_current_mode() -> str:
    """Retorna el modo actual de la base de datos"""
    return "Excel"

def set_mode(mode: str) -> None:
    """Establece el modo de la base de datos (solo Excel)"""
    pass  # Solo soportamos Excel