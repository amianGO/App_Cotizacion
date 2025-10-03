from colorsys import ONE_SIXTH
import tkinter as tk
from tkinter import messagebox, filedialog
from pathlib import Path
from logic import data_manager

class CreateProductDialog(tk.Toplevel):
    
    def __init__(self, parent, on_success):
        super().__init__(parent)
        self.title("Crear Producto")
        self.geometry("400x350")
        self.on_success = on_success
        self.image_path = None
        
        # Frame principal
        main_frame = tk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Nombre
        tk.Label(main_frame, text="Nombre:").pack(pady=5)
        self.entry_name = tk.Entry(main_frame)
        self.entry_name.pack(pady=5, fill="x")
        
        # Descripción
        tk.Label(main_frame, text="Descripción").pack(pady=5)
        self.entry_desc = tk.Text(main_frame, height=4, wrap=tk.WORD)
        self.entry_desc.pack(pady=5, fill="x")
        
        # Frame para imagen
        image_frame = tk.LabelFrame(main_frame, text="Imagen del producto (Opcional)")
        image_frame.pack(fill="x", pady=10)
        
        # Label para mostrar la imagen seleccionada
        self.image_label = tk.Label(image_frame, text="No se ha seleccionado imagen")
        self.image_label.pack(pady=5)
        
        # Botones para imagen
        btn_frame = tk.Frame(image_frame)
        btn_frame.pack(fill="x", pady=5)
        
        tk.Button(btn_frame, text="Seleccionar imagen", 
                 command=self.select_image).pack(side="left", padx=5)
        self.remove_img_btn = tk.Button(btn_frame, text="Quitar imagen", 
                                      command=self.remove_image, state="disabled")
        self.remove_img_btn.pack(side="left", padx=5)
        
        # Separador
        tk.Frame(main_frame, height=2, bd=1, relief="sunken").pack(fill="x", pady=10)
        
        # Botón guardar
        tk.Button(main_frame, text="Guardar", command=self.save).pack(pady=10)

    def select_image(self):
        file_types = [
            ("Imágenes", "*.png *.jpg *.jpeg *.gif *.bmp"),
            ("Todos los archivos", "*.*")
        ]
        image_path = filedialog.askopenfilename(
            title="Seleccionar imagen del producto",
            filetypes=file_types
        )
        if image_path:
            self.image_path = image_path
            self.image_label.config(text=f"Imagen seleccionada: {Path(image_path).name}")
            self.remove_img_btn.config(state="normal")
            
    def remove_image(self):
        self.image_path = None
        self.image_label.config(text="No se ha seleccionado imagen")
        self.remove_img_btn.config(state="disabled")

    def save(self):
        nombre = self.entry_name.get().strip()
        descripcion = self.entry_desc.get("1.0", "end-1c").strip()
        
        try:
            data_manager.add_product(nombre, descripcion, self.image_path)
            messagebox.showinfo("Éxito", f"Producto '{nombre}' agregado")
            self.on_success()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
class CreateSupplierDialog(tk.Toplevel):
    def __init__(self, parent, on_success):
        super().__init__(parent)
        self.title("Crear Proveedor")
        self.geometry("300x200")
        self.on_success = on_success
        
        tk.Label(self, text="Nombre:").pack(pady=5)
        self.entry_name = tk.Entry(self)
        self.entry_name.pack(pady=5, fill="x", padx=10)
        
        tk.Label(self, text="Correo:").pack(pady=5)
        self.entry_mail = tk.Entry(self)
        self.entry_mail.pack(pady=5, fill="x", padx=10)
        
        tk.Button(self, text="Guardar", command=self.save).pack(pady=10)
        
    
    def save(self):
        nombre = self.entry_name.get().strip()
        correo = self.entry_mail.get().strip()
        
        try:
            data_manager.add_supplier(nombre, correo)
            messagebox.showinfo("Exito", f"El Proveedor {nombre} ha sido guardado")
            self.on_success()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))

