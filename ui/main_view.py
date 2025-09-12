import tkinter as tk
from tkinter import ttk, messagebox

from logic import data_manager
from ui.dialogs import (
    CreateProductDialog, DeleteProductDialog,
    CreateSupplierDialog, DeleteSupplierDialog
)

from logic import data_manager, email_sender

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Cotizaciones Automaticas")
        self.geometry("800x600") #Tamaño de la  ventana
        self.configure(padx = 10, pady = 10) #Margenes
        
        #Estado de seleccion
        self.selected_products = set()
        self.selected_suppliers = set()
        
        # ------ Titulo ------
        tittle = tk.Label(self, text = "Cotizaciones Automaticas", font = ("Arial", 16, "bold")) #Titulo de la ventana
        tittle.pack(pady = 10) #Posicion del titulo
        
        # ------ Botones CRUD ------
        crud_frame = tk.Frame(self)
        crud_frame.pack(pady = 5)
        
        tk.Button(crud_frame, text = "Agregar Producto", command = self.create_product).pack(side = tk.LEFT, padx = 5)
        tk.Button(crud_frame, text = "Eliminar Producto", command = self.delete_product).pack(side = tk.LEFT, padx = 5)
        tk.Button(crud_frame, text = "Agregar Proveedor", command = self.create_supplier).pack(side = tk.LEFT, padx = 5)
        tk.Button(crud_frame, text = "Eliminar Proveedor", command = self.delete_supplier).pack(side = tk.LEFT, padx = 5)
        
        # ------ Frame Central ------
        central_frame = tk.Frame(self)
        central_frame.pack(expand = True, fill = "both", pady = 10)
        
        # ------ Columnas ------
        self.product_frame = self.create_list_panel(central_frame, "Buscador de Productos")
        self.product_frame.pack(side = "left",expand = True, fill = "both", padx = 10)
        
        self.supplier_frame = self.create_list_panel(central_frame, "Buscador de Proveedores")
        self.supplier_frame.pack(side = "left",expand = True, fill = "both", padx = 10)
        
        # ------ Boton Enviar Cotizaciones ------
        send_btn = tk.Button(self, text = "Enviar Cotizaciones", command = self.send_action)
        send_btn.pack(pady = 10)
        
        # ------ Inicializacion de listas ------
        self.refresh_products()
        self.refresh_suppliers()
        
    # ========= PANEL LISTAS (REUTILIZABLE) =========
    
    def create_list_panel(self,parent, title):
        """Crea un panel con un Buscador y lista con checkboxes"""

        frame = tk.Frame(parent, relief = "solid", bd = 1, padx = 5, pady = 5)
        
        # Titulo
        tk.Label(frame, text = title, font = ("Arial", 12, "bold")).pack(pady = 5)
        
        # Buscador
        search_var = tk.StringVar()
        entry = tk.Entry(frame, textvariable = search_var, width = 30)
        entry.pack(fill = "x", padx = 5)
        entry.bind("<KeyRelease>", lambda e, var = search_var, t = title: self.on_search(var.get(), t))
        
        # Canva + Scrollbar para la lista
        
        canvas = tk.Canvas(frame) #Canvas es el contenedor de la lista
        secrollbar = ttk.Scrollbar(frame, orient = "vertical", command = canvas.yview)
        list_frame = tk.Frame(canvas) #El Frame significa que sirve para contener checkbox
        
        list_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion = canvas.bbox("all"))
        )
        
        canvas.create_window((0,0), window = list_frame, anchor = "nw")
        canvas.configure(yscrollcommand = secrollbar.set)
        
        # Empaquetar canvas y scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        secrollbar.pack(side="right", fill="y")
        
        # Guardar Referencias
        frame.search_var = search_var
        frame.list_frame = list_frame
        frame.title = title
        
        return frame
    
    # ========= RENDER DE LISTAS =========
    
    def refresh_products(self, query = ""):
        
        for widget in self.product_frame.list_frame.winfo_children(): # Elimna widgets anteriores
            widget.destroy()
            
        df = data_manager.search_products(query) #df es el dataframe de productos y busqueda
        
        for _, row in df.iterrows():
            name = row["Nombre"]
            var = tk.BooleanVar(value = (name in self.selected_products))
            cb = tk.Checkbutton(
                self.product_frame.list_frame,
                text = name,
                variable = var,
                command = lambda n = name, v = var: self.toggle_selection(n, v, "products"),
                anchor = "w"
            )
            cb.pack(fill = "x", padx = 5, pady = 2)
        
    def refresh_suppliers(self, query = ""):
        
        for widget in self.supplier_frame.list_frame.winfo_children():
            widget.destroy()
            
        df = data_manager.search_suppliers(query)
        
        for _, row in df.iterrows():
            name = row["Nombre"]
            var = tk.BooleanVar(value = (name in self.selected_suppliers))
            cb = tk.Checkbutton(
                self.supplier_frame.list_frame,
                text = name,
                variable = var,
                command = lambda n = name, v = var: self.toggle_selection(n, v, "suppliers"),
                anchor = "w"
            )
            cb.pack(fill = "x", padx = 5, pady = 2)
            

    # ========== EVENTOS ==========
    
    def on_search(self, query, tittle):
        """ Llama al refresco segun el panel """
        if "Producto" in tittle:
            self.refresh_products(query)
        else:
            self.refresh_suppliers(query)
    
    def toggle_selection(self, name, var, kind):
        """ Agregar o quitar de sets de seleccionados """
        if kind == "products":
            (self.selected_products.add(name) if var.get() else self.selected_products.discard(name))
        else:
            (self.selected_suppliers.add(name) if var.get() else self.selected_suppliers.discard(name))
    
    def send_action(self):
        """ Enviar los correos a los proveedores seleccionado """
        products = data_manager.get_products_by_names(self.selected_products)
        suppliers = data_manager.get_suppliers_by_names(self.selected_suppliers)
        
        if not products or not suppliers:
            messagebox.showwarning("Advertencia", "Selecciona almenos un Producto y un Proveedor")
            return
        
        try:
            cc_email = "damiangaviria@gmail.com"
            email_sender.send_bulk_emails(suppliers, products, cc_email)
            messagebox.showinfo("Exito", "Correos enviados correctamente.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        
    
    # ========== CRUD (Solo prints por ahora) ==========
    
    def create_product(self):
        CreateProductDialog(self, self.refresh_products)
    
    def delete_product(self):
        DeleteProductDialog(self, self.refresh_products)
        
    def create_supplier(self):
        CreateSupplierDialog(self, self.refresh_suppliers)
    
    def delete_supplier(self):
        DeleteSupplierDialog(self,self.refresh_suppliers)

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
        