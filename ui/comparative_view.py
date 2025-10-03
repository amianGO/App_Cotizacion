import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
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
        
        self.supplier_selected_state = {}
        self.product_selected_state = {}
        
        # Diccionario para almacenar precios y tiempos : {(proveedor, producto): {"precio":..., "tiempo:..."}}
        self.comparative_data = {}
        
        self.create_widgets()
    
    def create_widgets(self):
        #Frame de proveedores
        supplier_frame = tk.LabelFrame(self, text= "Seleccionar Proveedores")
        supplier_frame.pack(fill="x", padx= 5, pady= 5)
        
        product_frame = tk.LabelFrame(self, text="Selecciona los Productos")
        product_frame.pack(fill="x", padx= 5, pady= 5)
        
        self.urgency_var = tk.BooleanVar(value= False)
        tk.Checkbutton(self, text="Urgencia", variable=self.urgency_var).pack(pady=5)
        
        #Busqueda de Productos
        self.product_search_var = tk.StringVar()
        product_search_entry = tk.Entry(product_frame, textvariable= self.product_search_var)
        product_search_entry.pack(fill="x", padx=5, pady=2)
        product_search_entry.bind("<KeyRelease>", self.update_product_list)
        
        # Busqueda de Proveedores
        self.supplier_search_var = tk.StringVar()
        supplier_search_entry = tk.Entry(supplier_frame, textvariable= self.supplier_search_var)
        supplier_search_entry.pack(fill="x", padx= 5, pady= 2)
        supplier_search_entry.bind("<KeyRelease>", self.update_supplier_list)
        
        # -------------------------------------------------------------------------------------------------------------#
        # -------------------------------------------------------------------------------------------------------------#
        # Frame para los CheckBoxes de Productos (Forma 1 de hacerlo)
        #self.product_list_frame = tk.Frame(product_frame)
        #self.product_list_frame.pack(fill="x")
        #self.product_vars = {}
        #self.render_product_checkboxes(self.productos)
        
        #Contenedor para los Productos
        self.product_container = tk.Frame(product_frame)
        self.product_container.pack(fill="x", padx=5, pady=5)
        
        # Canvas para productos
        self.product_canva = tk.Canvas(self.product_container, height=50)
        self.product_canva.pack_propagate(False)  # Evita que el canvas se encoja
        
        # Scrollbar horizontal para productos
        self.product_scrollbar = tk.Scrollbar(self.product_container, orient="horizontal", command=self.product_canva.xview)
        
        # Frame interno para los checkboxes de productos
        self.product_list_frame = tk.Frame(self.product_canva)
        
        # Configurar canvas
        self.product_canva.configure(xscrollcommand=self.product_scrollbar.set)
        
        # Empaquetar en Orden
        self.product_scrollbar.pack(side="bottom", fill="x")
        self.product_canva.pack(side="top", fill="both", expand=True)  # Cambiado a fill="both"
        
        # Crear ventana del canvas
        self.product_canva.create_window((0,0), window=self.product_list_frame, anchor="nw")
        
        # Configurar los eventos
        self.product_list_frame.bind("<Configure>", self.on_product_frame_configure)
        self.product_vars = {}
        self.render_product_checkboxes(self.productos)
        
        
        
        # -------------------------------------------------------------------------------------------------------------#
        # -------------------------------------------------------------------------------------------------------------#
        
        # Contenedor para los checkboxes de proveedores con scroll
        self.supplier_container = tk.Frame(supplier_frame)
        self.supplier_container.pack(fill="x", padx=5, pady=2)
        
        # Canvas para proveedores
        self.supplier_canvas = tk.Canvas(self.supplier_container, height=50)
        self.supplier_canvas.pack_propagate(False)  # Evita que el canvas se encoja
        
        # Scrollbar horizontal para proveedores
        self.supplier_scrollbar = tk.Scrollbar(self.supplier_container, orient="horizontal", command=self.supplier_canvas.xview)
        
        # Frame interno para los checkboxes de proveedores
        self.supplier_list_frame = tk.Frame(self.supplier_canvas)
        
        # Configurar canvas
        self.supplier_canvas.configure(xscrollcommand=self.supplier_scrollbar.set)
        
        # Empaquetar en orden correcto
        self.supplier_scrollbar.pack(side="bottom", fill="x")
        self.supplier_canvas.pack(side="top", fill="both", expand=True)  # Cambiado a fill="both"
        
        # Crear ventana del canvas
        self.supplier_canvas.create_window((0,0), window=self.supplier_list_frame, anchor="nw")
        
        # Configurar eventos
        self.supplier_list_frame.bind("<Configure>", self.on_supplier_frame_configure)
        self.supplier_vars = {}
        self.render_supplier_checkboxes(self.suppliers)

        # -------------------------------------------------------------------------------------------------------------#
        # -------------------------------------------------------------------------------------------------------------#
        
        tk.Button(self, text= "Generar Tabla comparativa", command= self.generate_table).pack(pady=10)
        
        
        # -------------------------------------------------------------------------------------------------------------#
        # -------------------------------------------------------------------------------------------------------------#
        
        # Contenedor principal para la tabla y scrollbars
        self.table_container = tk.Frame(self)
        self.table_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Canvas para la tabla
        self.table_canvas = tk.Canvas(self.table_container)
        
        # Scrollbars
        self.scrollbar_y = tk.Scrollbar(self.table_container, orient="vertical", command=self.table_canvas.yview)
        self.scrollbar_x = tk.Scrollbar(self.table_container, orient="horizontal", command=self.table_canvas.xview)
        
        # Frame interno para la tabla
        self.table_frame = tk.Frame(self.table_canvas)
        
        # Configurar scrollbars
        self.table_canvas.configure(yscrollcommand=self.scrollbar_y.set, xscrollcommand=self.scrollbar_x.set)
        
        # Empaquetar los widgets en el orden correcto
        self.scrollbar_y.pack(side="right", fill="y")
        self.scrollbar_x.pack(side="bottom", fill="x")
        self.table_canvas.pack(side="left", fill="both", expand=True)
        
        # Crear ventana del canvas
        self.table_canvas.create_window((0,0), window=self.table_frame, anchor="nw")
        
        # Vincular eventos de redimensionamiento y configuración
        self.table_frame.bind("<Configure>", self.on_frame_configure)
        self.table_canvas.bind("<Configure>", self.on_canvas_configure)
        
    # -------------------------------------------------------------------------------------------------------------#
    # -------------------------------------------------------------------------------------------------------------#
    
    def update_product_list(self, event = None):
        query = self.product_search_var.get().lower()
        filtered = [s for s in self.productos if query in s["Nombre"].lower()]
        self.render_product_checkboxes(filtered)
    
    def update_supplier_list(self, event=None):
        query = self.supplier_search_var.get().lower()
        filtered = [s for s in self.suppliers if query in s["Nombre"].lower()]
        self.render_supplier_checkboxes(filtered)
    
    def render_product_checkboxes(self, productos):
        # Limpia los CehckBoxes anteriores
        for widget in self.product_list_frame.winfo_children():
            widget.destroy()
        self.product_vars.clear()
        for product in productos:
            name = product["Nombre"]
            # Recupera el estado anterior si existe
            var = tk.BooleanVar(value=self.product_selected_state.get(name, False))
            cb = tk.Checkbutton(self.product_list_frame, text= name, variable= var,
                                command= lambda n=name, v=var: self.update_product_state(n,v))
            cb.pack(side="left", padx=5)
            self.product_vars[name] = var
    
    def render_supplier_checkboxes(self, suppliers):
        #Limpia los checkBoxes anteriores
        for widget in self.supplier_list_frame.winfo_children():
            widget.destroy()
        self.supplier_vars.clear()
        for supplier in suppliers:
            name = supplier["Nombre"]
            # Recupera el estado anterior si existe
            var = tk.BooleanVar(value=self.supplier_selected_state.get(name, False))
            cb = tk.Checkbutton(self.supplier_list_frame, text=name, variable=var,
                                command= lambda n=name, v=var: self.update_supplier_state(n, v))
            cb.pack(side="left", padx=5)
            self.supplier_vars[name] = var
    
    def update_supplier_state(self, name, var):
        # Actualiza el estado en el diccionario
        self.supplier_selected_state[name] = var.get()
    
    def update_product_state(self, name, var):
        self.product_selected_state[name] = var.get()
    
    def on_frame_configure(self, event=None):
        """Actualiza la región de scroll cuando el frame interno cambia de tamaño"""
        self.table_canvas.configure(scrollregion=self.table_canvas.bbox("all"))
    
    def on_canvas_configure(self, event=None):
        """Ajusta el ancho del frame interno cuando el canvas cambia de tamaño"""
        # Asegura que el frame interno tenga al menos el ancho del canvas
        width = event.width if event else self.table_canvas.winfo_width()
        self.table_canvas.itemconfig(self.table_canvas.find_withtag("all")[0], width=width)
    
    def on_supplier_frame_configure(self, event=None):
        """Actualiza la región de scroll del canvas de proveedores"""
        self.supplier_canvas.configure(scrollregion=self.supplier_canvas.bbox("all"))
        # Ajustar la altura del canvas al contenido
        bbox = self.supplier_canvas.bbox("all")
        if bbox:
            _, _, _, height = bbox
            self.supplier_canvas.configure(height=min(50, height))
    
    def on_product_frame_configure(self, event= None):
        """ Actualiza la region de Scroll del canvas de productos"""
        self.product_canva.configure(scrollregion=self.product_canva.bbox("all"))
        # Ajusta la altura del canvas al contenido
        bbox = self.product_canva.bbox("all")
        if bbox:
            _,_,_, height = bbox
            self.product_canva.configure(height=min(50, height))
        
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
        urgente = self.urgency_var.get()
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
                    if urgente:
                        #Si es urgente, Prioriza menor tiempo de entrega
                        if tiempo < best_time or (tiempo == best_time and precio < best_price):
                            best_time = tiempo
                            best_price = precio
                            best_supplier = supplier
                    #Comparar por precio y tiempo
                    else:
                        if precio < best_price or (precio == best_price and tiempo < best_time):
                            best_price = precio
                            best_time = tiempo
                            best_supplier = supplier
            result.append(f"Producto: {product}\n Mejor Proveedor: {best_supplier} \n Precio: {best_price} \n Tiempo de entrega: {best_time} dias \n")
        
        messagebox.showinfo("Comparativa", "\n".join(result))
        
        #Preguntar ruta para guardar el archivo
        ruta =filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Archivo de texto", "*.txt")],
            title="Guardar Comparativa"
        )
        
        if ruta:
            with open(ruta, "w", encoding="utf-8") as f:
                f.write(f"Comparativa realizada el {datetime.now().strftime('%y-%m-%d %H:%M:%S')}\n\n")
                for product in self.selected_products:
                    f.write(f"Producto: {product}\n")
                    for supplier in self.selected_suppliers:
                        entry = self.entry_vars.get((supplier, product))
                        if entry:
                            precio = entry["precio"].get()
                            tiempo = entry["tiempo"].get()
                            f.write(f"  Proveedor: {supplier} | Precio: {precio} | Tiempo de Entrega: {tiempo} dias \n")
                    f.write("\n")
                f.write("Resumen de mejores opciones:\n")
                f.write("\n".join(result))
            messagebox.showinfo("Guardado", f"Comparativa guardada en:\n{ruta}")
                    
        