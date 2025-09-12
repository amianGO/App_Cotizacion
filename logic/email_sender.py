from email import message
from pathlib import Path
import platform
from tempfile import template

# Windows-specific import
if platform.system() == "Windows":
    import win32com.client as win32
else:
    win32 = None

BASE_DIR = Path(__file__).resolve().parents[1]
TEMPLATE_PATH = BASE_DIR / "data" / "email_template.txt"

def load_template() -> str:
    """ Carga el contenido de la plantilla del Email """
    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError(
            f"No se encontro la plantilla en {TEMPLATE_PATH}."
            "Crea un archivo 'email_template' en /data "
        )
    
    with open(TEMPLATE_PATH, "r", encoding= "utf-8") as f:
        return f.read()
    

def build_message(template: str, supplier_name: str, products: list[dict]) -> str:
    """ Rellena la plantilla con datos del proveedor y productos """
    
    product_lines = "\n".join([f"- {p['Nombre']}: {p['Descripcion']}" for p in products])
    message = template.format(
        nombre_proveedor = supplier_name,
        lista_productos = product_lines
    )
    
    return message

def send_email(supplier_name: str, supplier_email: str, products: list[dict], cc_email: str = "") -> None:
    
    """ Envia un solo mensaje a un proveedor via Outlook """
    template = load_template()
    body = build_message(template,supplier_name,products)
    
    outlook = win32.Dispatch("Outlook.Application")
    mail = outlook.CreateItem(0)
    mail.To = supplier_email
    
    if cc_email:
        mail.CC = cc_email
        mail.Subject = "Cotizacion de elementos"
        mail.Body = body
        mail.send()

def send_bulk_emails(
    suppliers: list[dict],
    products: list[dict],
    cc_email: str = ""
) -> None:
    """ Envia correos personalizados a cada proveedor """
    for supplier in suppliers:
        send_email(
            supplier_email=supplier["Correo"],
            supplier_name=supplier["Nombre"],
            products = products,
            cc_email = cc_email
        )