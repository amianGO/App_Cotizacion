from email import message
from pathlib import Path
import platform
from tempfile import template
import time
import subprocess
import urllib.parse

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

def check_outlook_availability() -> bool:
    """ Verifica si Outlook está disponible y configurado """
    if platform.system() != "Windows":
        return False
    
    outlook = None
    try:
        # Intentar diferentes métodos de conexión
        connection_methods = [
            ("GetActiveObject", lambda: win32.GetActiveObject("Outlook.Application")),
            ("Dispatch", lambda: win32.Dispatch("Outlook.Application")),
            ("DispatchEx", lambda: win32.DispatchEx("Outlook.Application"))
        ]
        
        for method_name, method_func in connection_methods:
            try:
                outlook = method_func()
                if outlook:
                    # Verificar que realmente podemos crear un item
                    test_mail = outlook.CreateItem(0)
                    test_mail = None
                    outlook = None
                    return True
            except Exception as e:
                # Si es el error específico de "Cadena clase no válida", continuar con el siguiente método
                if "-2147221005" in str(e) or "Cadena clase no válida" in str(e):
                    continue
                # Para otros errores, también continuar
                pass
                
    except Exception:
        pass
    finally:
        # Limpiar referencias
        if outlook:
            try:
                outlook = None
            except:
                pass
    
    return False

def test_outlook_connection() -> tuple[bool, str]:
    """ Prueba la conexión con Outlook y devuelve (éxito, mensaje) """
    if platform.system() != "Windows":
        return False, "Solo funciona en Windows"
    
    outlook = None
    try:
        # Intentar diferentes métodos de conexión
        connection_methods = [
            ("GetActiveObject", lambda: win32.GetActiveObject("Outlook.Application")),
            ("Dispatch", lambda: win32.Dispatch("Outlook.Application")),
            ("DispatchEx", lambda: win32.DispatchEx("Outlook.Application"))
        ]
        
        for method_name, method_func in connection_methods:
            try:
                outlook = method_func()
                if outlook:
                    # Verificar que realmente podemos crear un item
                    test_mail = outlook.CreateItem(0)
                    test_mail = None
                    
                    # Verificar configuración de cuentas
                    try:
                        accounts = outlook.Session.Accounts
                        account_count = accounts.Count
                        if account_count == 0:
                            outlook = None
                            return False, f"Outlook conectado con {method_name} pero no tiene cuentas de email configuradas"
                        else:
                            outlook = None
                            return True, f"Outlook conectado exitosamente usando {method_name} con {account_count} cuenta(s) configurada(s)"
                    except Exception as e:
                        outlook = None
                        return False, f"Outlook conectado con {method_name} pero hay problemas con la configuración: {str(e)}"
                        
            except Exception as e:
                error_msg = str(e)
                if "-2147221005" in error_msg or "Cadena clase no válida" in error_msg:
                    continue
                # Para otros errores, también continuar
                pass
                
        return False, "No se pudo conectar con Outlook usando ningún método"
                
    except Exception as e:
        return False, f"Error inesperado: {str(e)}"
    finally:
        # Limpiar referencias
        if outlook:
            try:
                outlook = None
            except:
                pass

def diagnose_outlook_issues() -> str:
    """ Diagnostica problemas comunes con Outlook y devuelve recomendaciones """
    diagnosis = []
    
    # Verificar sistema operativo
    if platform.system() != "Windows":
        diagnosis.append("Solo funciona en Windows")
        return "\n".join(diagnosis)
    
    # Verificar conexión básica
    success, message = test_outlook_connection()
    if success:
        diagnosis.append(f" {message}")
    else:
        diagnosis.append(f" {message}")
        
        # Agregar recomendaciones específicas
        if "no tiene cuentas" in message.lower():
            diagnosis.append(" RECOMENDACIÓN: Configura una cuenta de email en Outlook")
            diagnosis.append("   1. Abre Outlook")
            diagnosis.append("   2. Ve a Archivo > Configuración de cuenta > Configuración de cuenta")
            diagnosis.append("   3. Agrega tu cuenta de email")
        elif "no se pudo conectar" in message.lower():
            diagnosis.append(" RECOMENDACIÓN: Outlook no está instalado o no está funcionando")
            diagnosis.append("   1. Verifica que Outlook esté instalado")
            diagnosis.append("   2. Intenta abrir Outlook manualmente")
            diagnosis.append("   3. Si no tienes Outlook, instala Microsoft Outlook")
        elif "cadena clase no válida" in message.lower():
            diagnosis.append(" RECOMENDACIÓN: Problema con la instalación de Outlook")
            diagnosis.append("   1. Repara la instalación de Office/Outlook")
            diagnosis.append("   2. O reinstala Microsoft Office")
    
    return "\n".join(diagnosis)

def generate_email_draft(suppliers: list[dict], products: list[dict], cc_email: str = "") -> str:
    """ Genera un archivo de texto con los emails como respaldo """
    
    if not suppliers:
        raise ValueError("No se proporcionaron proveedores")
    
    if not products:
        raise ValueError("No se proporcionaron productos")
    
    template = load_template()
    output_lines = []
    
    for supplier in suppliers:
        supplier_name = supplier.get("Nombre", "").strip()
        supplier_email = supplier.get("Correo", "").strip()
        
        if not supplier_name or not supplier_email:
            continue
        
        body = build_message(template, supplier_name, products)
        
        output_lines.append("=" * 50)
        output_lines.append(f"PARA: {supplier_email}")
        if cc_email:
            output_lines.append(f"CC: {cc_email}")
        output_lines.append(f"ASUNTO: Cotización de elementos")
        output_lines.append("")
        output_lines.append(body)
        output_lines.append("")
    
    return "\n".join(output_lines)


def send_email_via_powershell(supplier_name: str, supplier_email: str, products: list[dict], cc_email: str = "") -> None:
    """ Envía email usando PowerShell y Outlook (envío automático real) """
    
    # Validar que el email del proveedor no esté vacío
    if not supplier_email or not supplier_email.strip():
        raise ValueError(f"Email del proveedor '{supplier_name}' está vacío o es inválido")
    
    # Limpiar y validar datos
    supplier_name = str(supplier_name).strip()
    supplier_email = str(supplier_email).strip()
    
    template = load_template()
    body = build_message(template, supplier_name, products)
    
    # Limpiar el cuerpo del mensaje de caracteres problemáticos
    body = body.replace('\x00', '')  # Remover caracteres nulos
    body = body.replace('"', '""')  # Escapar comillas dobles para PowerShell
    body = body.replace('\n', '\n')  # Mantener saltos de línea normales para PowerShell
    body = body.replace('\r', '')  # Remover retornos de carro
    
    # Preparar el asunto
    subject = "Cotización de elementos"
    subject = subject.replace('"', '""')  # Escapar comillas dobles
    
    # Construir el script de PowerShell con mejor manejo de errores
    ps_script = f'''
try {{
    $outlook = New-Object -ComObject Outlook.Application
    $mail = $outlook.CreateItem(0)
    $mail.To = "{supplier_email}"
    $mail.Subject = "{subject}"
    $mail.Body = @"
{body}
"@
'''
    
    if cc_email and cc_email.strip():
        cc_email = cc_email.strip().replace('"', '""')
        ps_script += f'    $mail.CC = "{cc_email}"\n'
    
    ps_script += '''    $mail.Send()
    Write-Host "Email enviado exitosamente a {supplier_name} ({supplier_email})"
} catch {
    Write-Error "Error al enviar email: $($_.Exception.Message)"
    exit 1
} finally {
    if ($mail) { $mail = $null }
    if ($outlook) { $outlook = $null }
}'''
    
    try:
        # Ejecutar el script de PowerShell
        result = subprocess.run([
            'powershell', '-ExecutionPolicy', 'Bypass', '-Command', ps_script
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            error_msg = result.stderr.strip() if result.stderr else "Error desconocido en PowerShell"
            raise Exception(f"PowerShell error: {error_msg}")
        
        # Verificar que el mensaje de éxito esté en la salida
        if "Email enviado exitosamente" not in result.stdout:
            raise Exception("El email no se envió correctamente según PowerShell")
            
    except subprocess.TimeoutExpired:
        raise Exception("Timeout al enviar email via PowerShell (60 segundos)")
    except Exception as e:
        raise Exception(f"Error al enviar email via PowerShell: {str(e)}")

def build_message(template: str, supplier_name: str, products: list[dict]) -> str:
    """ Rellena la plantilla con datos del proveedor y productos """
    
    if not products:
        product_lines = "No se especificaron productos."
    else:
        product_lines = []
        for p in products:
            nombre = str(p.get('Nombre', 'Sin nombre')).strip()
            descripcion = str(p.get('Descripcion', 'Sin descripción')).strip()
            product_lines.append(f"- {nombre}: {descripcion}")
        product_lines = "\n".join(product_lines)
    
    message = template.format(
        nombre_proveedor = str(supplier_name).strip(),
        lista_productos = product_lines
    )
    
    return message

def send_email(supplier_name: str, supplier_email: str, products: list[dict], cc_email: str = "") -> None:
    """ Envia un solo mensaje a un proveedor via Outlook """
    
    # Validar que el email del proveedor no esté vacío
    if not supplier_email or not supplier_email.strip():
        raise ValueError(f"Email del proveedor '{supplier_name}' está vacío o es inválido")
    
    # Limpiar y validar datos
    supplier_name = str(supplier_name).strip()
    supplier_email = str(supplier_email).strip()
    
    template = load_template()
    body = build_message(template, supplier_name, products)
    
    # Limpiar el cuerpo del mensaje de caracteres problemáticos
    body = body.replace('\x00', '')  # Remover caracteres nulos
    body = body.encode('utf-8', errors='ignore').decode('utf-8')  # Limpiar codificación
    
    outlook = None
    mail = None
    
    try:
        # Intentar conectar con Outlook de manera más robusta
        outlook = None
        
        # Primero intentar con GetActiveObject (si Outlook ya está ejecutándose)
        try:
            outlook = win32.GetActiveObject("Outlook.Application")
        except Exception:
            # Si falla, intentar con Dispatch (crear nueva instancia)
            try:
                outlook = win32.Dispatch("Outlook.Application")
            except Exception as e:
                # Si también falla Dispatch, intentar con DispatchEx
                try:
                    outlook = win32.DispatchEx("Outlook.Application")
                except Exception:
                    raise Exception(f"No se pudo conectar con Outlook. Error: {str(e)}")
        
        # Verificar que Outlook se inicializó correctamente
        if outlook is None:
            raise Exception("No se pudo inicializar Outlook")
        
        # Verificar que Outlook está configurado
        try:
            # Intentar acceder a la configuración de cuentas
            accounts = outlook.Session.Accounts
            if accounts.Count == 0:
                raise Exception("Outlook no tiene cuentas de email configuradas")
        except Exception as e:
            raise Exception(f"Outlook no está configurado correctamente: {str(e)}")
        
        # Crear el mensaje
        mail = outlook.CreateItem(0)  # 0 = olMailItem
        
        # Configurar el mensaje
        mail.To = supplier_email
        
        if cc_email and cc_email.strip():
            mail.CC = cc_email.strip()
        
        mail.Subject = "Cotización de elementos"
        mail.Body = body
        
        # Verificar que el mensaje se configuró correctamente
        if not mail.To or mail.To != supplier_email:
            raise Exception("No se pudo configurar el destinatario del email")
        
        # IMPORTANTE: Enviar el mensaje inmediatamente
        mail.Send()
        
        # Pequeña pausa para asegurar que el envío se procese
        time.sleep(2)
        
        print(f" Email enviado exitosamente a {supplier_name} ({supplier_email})")
        
    except Exception as e:
        error_msg = f"Error al enviar email a {supplier_name} ({supplier_email}): {str(e)}"
        print(f" {error_msg}")
        raise Exception(error_msg)
    
    finally:
        # Limpiar referencias COM de manera más robusta
        try:
            if mail:
                mail = None
        except:
            pass
        try:
            if outlook:
                outlook = None
        except:
            pass

def send_bulk_emails(
    suppliers: list[dict],
    products: list[dict],
    cc_email: str = ""
) -> None:
    """ Envia correos personalizados a cada proveedor individualmente """
    
    if not suppliers:
        raise ValueError("No se proporcionaron proveedores para enviar emails")
    
    if not products:
        raise ValueError("No se proporcionaron productos para cotizar")
    
    # Verificar que Outlook esté disponible antes de empezar
    print("Verificando conexión con Outlook...")
    success, message = test_outlook_connection()
    if not success:
        raise Exception(f"No se puede conectar con Outlook: {message}")
    print(f"{message}")
    
    print(f" Iniciando envío de emails a {len(suppliers)} proveedor(es)...")
    print(f" Productos a cotizar: {len(products)}")
    
    successful_sends = 0
    failed_sends = []
    
    # Enviar individualmente a cada proveedor
    for i, supplier in enumerate(suppliers, 1):
        try:
            # Validar que el proveedor tenga los campos necesarios
            if not isinstance(supplier, dict):
                raise ValueError(f"Proveedor inválido: {supplier}")
            
            supplier_name = supplier.get("Nombre", "").strip()
            supplier_email = supplier.get("Correo", "").strip()
            
            if not supplier_name:
                raise ValueError("Nombre del proveedor está vacío")
            
            if not supplier_email:
                raise ValueError(f"Email del proveedor '{supplier_name}' está vacío")
            
            print(f"Enviando email {i}/{len(suppliers)} a: {supplier_name} ({supplier_email})")
            
            # Intentar primero con COM, si falla usar PowerShell
            try:
                send_email(
                    supplier_email=supplier_email,
                    supplier_name=supplier_name,
                    products=products,
                    cc_email=cc_email
                )
                successful_sends += 1
                print(f" Email {i}/{len(suppliers)} enviado exitosamente a {supplier_name}")
                
            except Exception as com_error:
                print(f"Error COM con {supplier_name}, intentando PowerShell...")
                # Si falla COM, intentar con PowerShell
                try:
                    send_email_via_powershell(
                        supplier_email=supplier_email,
                        supplier_name=supplier_name,
                        products=products,
                        cc_email=cc_email
                    )
                    successful_sends += 1
                    print(f" Email {i}/{len(suppliers)} enviado exitosamente a {supplier_name} (via PowerShell)")
                    
                except Exception as ps_error:
                    # Si ambos fallan, agregar a la lista de errores
                    error_msg = f"{supplier_name}: COM Error: {str(com_error)} | PowerShell Error: {str(ps_error)}"
                    failed_sends.append(error_msg)
                    print(f" Error en email {i}/{len(suppliers)} a {supplier_name}: {error_msg}")
                    continue
            
            # Pequeño retraso entre envíos para evitar problemas de concurrencia
            time.sleep(1)
            
        except Exception as e:
            error_msg = f"{supplier.get('nombre', 'Proveedor desconocido')}: {str(e)}"
            failed_sends.append(error_msg)
            print(f" Error general en email {i}/{len(suppliers)}: {error_msg}")
    
    # Reportar resultados finales
    print(f"\n RESUMEN DE ENVÍO:")
    print(f" Emails enviados exitosamente: {successful_sends}")
    print(f" Emails fallidos: {len(failed_sends)}")
    
    # Si todos fallaron, reportar error
    if successful_sends == 0 and failed_sends:
        error_msg = (
            f"No se pudo enviar ningún email automáticamente.\n\n"
            f"Se intentaron ambos métodos (COM y PowerShell) pero fallaron.\n\n"
            f"Errores encontrados:\n" + "\n".join(failed_sends)
        )
        raise Exception(error_msg)
    
    # Si algunos fallaron, reportar resultados
    elif failed_sends:
        error_msg = f"Se enviaron {successful_sends} emails exitosamente de {len(suppliers)} proveedores.\n\nErrores:\n" + "\n".join(failed_sends)
        raise Exception(error_msg)
    
    # Si todo fue exitoso
    else:
        print(f"¡Todos los emails fueron enviados exitosamente!")