from colorsys import ONE_SIXTH
import tkinter as tk
from tkinter import messagebox
from logic import data_manager

class CreateProductDialog(tk.Toplevel):
    
    def __init__(self, parent, on_success):
        super().__init__(parent)
        self.title("Crear Producto")
        self.geometry("300x200")
        self.on_success = on_success
        
        tk.Label(self, text="Nombre:").pack(pady=5)
        self.entry_name = tk.Entry(self)
        self.entry_name.pack(pady=5, fill="x", padx=10)
        
        
        tk.Label(self, text="Descripcion").pack(pady=5)
        self.entry_desc = tk.Entry(self)
        self.entry_desc.pack(pady=5, fill="x", padx=10)
        
        tk.Button(self, text="Guardar", command=self.save).pack(pady=10)

    def save(self):
        nombre = self.entry_name.get().strip()
        descripcion = self.entry_desc.get().strip()
        
        try:
            data_manager.add_product(nombre, descripcion)
            messagebox.showinfo("Exito", f"Producto '{nombre}' agregado")
            self.on_success()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
class DeleteProductDialog(tk.Toplevel):
    def __init__(self, parent, on_success):
        super().__init__(parent)
        self.title("Borrar Producto")
        self.geometry("300x150")
        self.on_success = on_success
        
        
        tk.Label(self, text="Nombre del producto a borrar:").pack(pady=5)
        self.entry_name = tk.Entry(self)
        self.entry_name.pack(pady=5, fill="x", padx=10)
        
        tk.Button(self, text="Borrar", command= self.delete).pack(pady=10)
        
    def delete(self):
        nombre = self.entry_name.get().strip()
        try:
            removed = data_manager.delete_product(nombre)
            if removed > 0:
                messagebox.showinfo("Exito", f"El producto {nombre} ha sido eliminado")
                self.on_success()
                self.destroy()
            else:
                messagebox.showwarning("No encontrado", f"No se encontro el producto {nombre}")
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

class DeleteSupplierDialog(tk.Toplevel):
    def __init__(self, parent, on_success):
        super().__init__(parent)
        self.title("Eliminar un Proveedor")
        self.geometry("300x200")
        self.on_success = on_success
        
        tk.Label(self, text="Nombre del proveedor a eliminar").pack(pady=5)
        self.entry_name = tk.Entry(self)
        self.entry_name.pack(pady=5, fill="x", padx=10)
        
        tk.Button(self, text="Borrar", command=self.delete).pack(pady=10)
        
    def delete(self):
        nombre = self.entry_name.get().strip()
        
        try:
            removed = data_manager.delete_supplier(nombre)
            if removed > 0:
                messagebox.showinfo("Exito", f"El Proveedor {nombre} se ha eliminado")
                self.on_success()
                self.destroy()
            else:
                messagebox.showwarning("No encontrado", f"El proveedor {nombre} no fue encontrado")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            