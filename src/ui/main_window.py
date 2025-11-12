import tkinter as tk

def run_app():
    root = tk.Tk()
    root.title("SIC - Sistema de Ingreso de Compras (v3)")
    root.geometry("800x600")
    tk.Label(root, text="Bienvenido a SIC v3", font=("Segoe UI", 16)).pack(pady=50)
    root.mainloop()
