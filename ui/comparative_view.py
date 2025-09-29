import tkinter as tk
from turtle import title

class ComparativeView(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Comparativa")
        self.geometry("800x600")
        self.configure(padx= 10, pady= 10)
        
        self.selected_suppliers = set()
        
        tittle = tk.Label(self, text="Comparativa de Precios", font= ("Arial", 16, "bold"))
        tittle.pack(pady = 10)
        
        action_frame = tk.Frame(self)
        action_frame.pack(pady= 5)
        
        tk.Button(action_frame, text="Cerrar", command= self.destroy).pack(side= tk.LEFT, padx= 5)
        
        central_frame = tk.Frame(self)
        central_frame.pack(expand= True, fill= "both", pady= 10)
        
        # Columnas
        