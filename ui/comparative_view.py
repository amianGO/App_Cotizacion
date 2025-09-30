import tkinter as tk
from tkinter import ttk, messagebox
from logic import data_manager

class ComparativeView(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Comparativa de precios")
        self.geometry("800x600")
        tk.Label(self, text="Ventana de Comparativa", font=("Arial", 14)).pack(pady=50)
        
        
        #Cargar los datos desde la base principal (no se recarga el excel)
        self.productos = data_manager.load_products().to_dict(orient="records")
        self.suppliers = data_manager.load_supplier().to_dict(orient="records")
        
        # Seleccion de proveedores y productos
        self.selected_products = []
        self.selected_suppliers = []
        
        # Diccionario para almacenar precios y tiempos : {(proveedor, producto): {"precio":..., "tiempo:..."}}
        self.comparative_data = {}
        
        self.create_widgets()
    
    def create_widgets(self):
        
        """Crea los widgets de seleccion y tabla comparativa"""
        
        #Seleccion de proveedores
        supplier_frame = tk.LabelFrame(self, text= "Seleccionar Proveedores")
        supplier_frame.pack(fill="x", padx=5, pady=5)
        self.supplier_vars = {}
        
        for supplier in self.suppliers:
            var = tk.BooleanVar()
            cb = tk.Checkbutton(supplier_frame, text=supplier["Nombre"], variable=var)
            cb.pack(side="left", padx= 5)
            self.supplier_vars[supplier["Nombre"]] = var
        #------------------------------------------------------------------------------------------#
        
        
        #------------------------------------------------------------------------------------------#
        # Seleccion de Productos
        products_frame = tk.LabelFrame(self, text="Seleccionar Productos")
        products_frame.pack(fill="x", padx= 5, pady= 5)
        self.product_vars = {}
        
        for product in self.productos:
            var = tk.BooleanVar()
            cb = tk.Checkbutton(products_frame, text=product["Nombre"], variable= var)
            cb.pack(side="left", padx= 5)
            self.product_vars[product["Nombre"]] = var
        
        # Boton par generar la tabla de ingreso de precios/tiempos
        
        tk.Button(self, text="Generar Tabla comparativa", command= self.generate_table).pack(pady=10)
        
        # Frame de la tabla
        self.table_frame = tk.Frame(self)
        self.table_frame.pack(fill="both", expand=True, padx= 5, pady= 5)
    
    def generate_table(self):
        """Genera la tabla para ingresar precios y timpos por proveedor / producto"""
        
        #Limpiar tabla anterior
        
        for widget in self.table_frame.winfo_children():
            widget.destroy()
            
        
        # Obtener los seleciconados
        self.selected_suppliers = [name for name, var in self.supplier_vars.items() if var.get()]
        self.selected_products = [name for name, var in self.product_vars.items() if var.get()]
        
        if not self.selected_suppliers or not self.selected_products:
            messagebox.showwarning("Advertencia", "Selecciona al menos un proveedor y un producto")
            return

        #Crear encabezados
        columns = ["Proveedor", "Producto", "Precio", "Tiempo de Entrega (dias)"]
        
        for col, text in enumerate(columns):
            tk.Label(self.table_frame, text= text, font=("Arial",10, "bold")).grid(row=0, column=col, padx=5, pady=5)
        
        # Crear campos de ingreso
        self.entry_vars = {}
        row = 1
        
        for supplier in self.selected_suppliers:
            for product in self.selected_products:
                tk.Label(self.table_frame, text=supplier).grid(row=row, column=0, padx=5)
                tk.Label(self.table_frame, text=product).grid(row=row, column=1, padx=5)
                price_var = tk.DoubleVar()
                time_var = tk.IntVar()
                tk.Entry(self.table_frame, textvariable=price_var, width=10).grid(row=row, column=2, padx=5)
                tk.Entry(self.table_frame, textvariable=time_var, width=10).grid(row=row, column=3, padx=5)
                self.entry_vars[(supplier, product)] = {"precio": price_var, "tiempo": time_var}
                row += 1
        
        # Boton para calcular comparativa
        tk.Button(self.table_frame, text="Calcular mejor opcion", command= self.calculate_comparative).grid(row=row, column=0, columnspan=4, pady=10)
    
    def calculate_comparative(self):
        """Calcula la mejor opcion por producto (menor precio y tiempo de entrega)
        y muestra los resultados en un mensaje
        """
        
        result = []
        for product in self.selected_products:
            best_supplier = None
            best_price = float("inf")
            best_time = float("inf")
            for supplier in self.selected_suppliers:
                entry = self.entry_vars.get((supplier, product))
                if entry:
                    precio = entry["precio"].get()
                    tiempo = entry["tiempo"].get()
                    
                    #Comparar por precio y tiempo
                    if precio < best_price or (precio == best_price and tiempo < best_time):
                        best_price = precio
                        best_time = tiempo
                        best_supplier = supplier
            result.append(f"Producto: {product}\n Mejor Proveedor: {best_supplier} \n Precio: {best_price} \n Tiempo de entrega: {best_time} dias \n")
        
        messagebox.showinfo("Comparativa", "\n".join(result))
        