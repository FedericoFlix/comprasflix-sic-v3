import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import scrolledtext
from tkcalendar import DateEntry
import sqlite3
from datetime import datetime

import os

# Calcula la ruta absoluta del archivo de base de datos
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../database/database.db"))



# ---- Funciones auxiliares ----
def generar_numero_sic():
    hoy = datetime.now().strftime("%Y%m%d")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT numero_sic FROM solicitudes WHERE numero_sic LIKE ?", (f"{hoy}%",))
    existentes = cursor.fetchall()
    conn.close()

    siguiente = len(existentes) + 1
    return f"{hoy}{siguiente:04d}"


def obtener_usuarios():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre FROM usuarios")
    usuarios = cursor.fetchall()
    conn.close()
    return usuarios


def cargar_sic():
    solicitante = combo_solicitante.get()
    fecha_necesidad = date_necesidad.get_date()
    texto_datos = text_datos.get("1.0", tk.END).strip()

    if not solicitante or not texto_datos:
        messagebox.showwarning("Atención", "Debe completar todos los campos obligatorios.")
        return

    # Obtener ID del solicitante
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM usuarios WHERE nombre = ?", (solicitante,))
    solicitante_id = cursor.fetchone()
    if not solicitante_id:
        messagebox.showerror("Error", "Solicitante no encontrado en la base de datos.")
        conn.close()
        return

    numero_sic = entry_numero_sic.get()
    fecha_solicitud = datetime.now().strftime("%Y-%m-%d")

    lineas = texto_datos.splitlines()
    for linea in lineas:
        partes = linea.split("\t")
        if len(partes) != 5:
            messagebox.showerror("Error", f"Línea inválida:\n{linea}")
            continue
        oc, planta, material, cantidad, unidad = partes
        cursor.execute("""
            INSERT INTO solicitudes (
                numero_sic, fecha_solicitud, oc, planta, material,
                cantidad, unidad, estado, solicitante_id, fecha_necesidad
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 'Solicitado', ?, ?)
        """, (numero_sic, fecha_solicitud, oc, planta, material, cantidad, unidad, solicitante_id[0], fecha_necesidad))

    conn.commit()
    conn.close()

    messagebox.showinfo("Éxito", f"SIC {numero_sic} cargado correctamente.")
    text_datos.delete("1.0", tk.END)
    entry_numero_sic.config(state="normal")
    entry_numero_sic.delete(0, tk.END)
    entry_numero_sic.insert(0, generar_numero_sic())
    entry_numero_sic.config(state="readonly")


# ---- Ventana principal ----
root = tk.Tk()
root.title("Carga de SIC")
root.geometry("600x500")

# Fecha actual
fecha_actual = datetime.now().strftime("%d/%m/%Y")
tk.Label(root, text=f"Fecha actual: {fecha_actual}", font=("Arial", 10)).pack(pady=5)

# Número de SIC
frame_numero = tk.Frame(root)
frame_numero.pack(pady=5)
tk.Label(frame_numero, text="Número de SIC:").pack(side=tk.LEFT, padx=5)
entry_numero_sic = tk.Entry(frame_numero, width=20)
entry_numero_sic.insert(0, generar_numero_sic())
entry_numero_sic.config(state="readonly")
entry_numero_sic.pack(side=tk.LEFT)

# Solicitante
frame_solicitante = tk.Frame(root)
frame_solicitante.pack(pady=5)
tk.Label(frame_solicitante, text="Solicitante:").pack(side=tk.LEFT, padx=5)
usuarios = [u[1] for u in obtener_usuarios()]
combo_solicitante = ttk.Combobox(frame_solicitante, values=usuarios, state="readonly", width=30)
combo_solicitante.pack(side=tk.LEFT)

# Fecha de necesidad
frame_fecha = tk.Frame(root)
frame_fecha.pack(pady=5)
tk.Label(frame_fecha, text="Fecha de necesidad:").pack(side=tk.LEFT, padx=5)
date_necesidad = DateEntry(frame_fecha, date_pattern="yyyy-mm-dd", width=12)
date_necesidad.pack(side=tk.LEFT)

# Área de texto
tk.Label(root, text="Datos (OC, Planta, Material, Cantidad, Unidad):").pack(pady=5)
text_datos = scrolledtext.ScrolledText(root, width=70, height=10)
text_datos.pack(padx=10, pady=5)

# Botón de carga
btn_cargar = tk.Button(root, text="Cargar SIC", command=cargar_sic, bg="#4CAF50", fg="white", font=("Arial", 11))
btn_cargar.pack(pady=10)

root.mainloop()
