import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import scrolledtext
from tkcalendar import DateEntry
import sqlite3
from datetime import datetime
import os
from src.drive.drive_sync import subir_base


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
    try:
          
        # solicitante = combo_solicitante.get()
        solicitante = solicitante_fijo
        fecha_necesidad = date_necesidad.get_date()
        datos_texto = text_datos.get("1.0", tk.END).strip()

        if not datos_texto:
            messagebox.showwarning("Advertencia", "Debe ingresar datos.")
            return

        # Separar líneas y columnas
        lineas = [l.strip() for l in datos_texto.splitlines() if l.strip()]
        registros = [l.split("\t") for l in lineas]

        # Validar formato mínimo (OC, Planta, Material, Cantidad, Unidad)
        for r in registros:
            if len(r) < 5:
                messagebox.showerror("Error", "Formato inválido en alguna línea.")
                return

        # Validar que todas las OCs sean iguales
        oc_set = {r[0] for r in registros}
        if len(oc_set) > 1:
            messagebox.showerror("Error", "Todas las líneas deben tener la misma OC.")
            return

        numero_sic = generar_numero_sic()
        fecha_solicitud = datetime.now().strftime("%Y-%m-%d")

        # Conectar a base e insertar todas las líneas
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        for r in registros:
            oc, planta, material, cantidad, unidad = r[:5]
            cursor.execute("""
            INSERT INTO Solicitudes (numero_sic, fecha_solicitud, fecha_necesidad, OC, Planta, Material, Cantidad, Unidad, Estado)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
             """, (numero_sic, fecha_solicitud, fecha_necesidad, oc, planta, material, cantidad, unidad, "Solicitado"))


        conn.commit()
        conn.close()

        messagebox.showinfo("Éxito", f"SIC {numero_sic} cargada correctamente con {len(registros)} ítems.")

        # Limpiar área de texto y actualizar número de SIC
        text_datos.delete("1.0", tk.END)
        entry_numero_sic.config(state="normal")
        entry_numero_sic.delete(0, tk.END)
        entry_numero_sic.insert(0, generar_numero_sic())
        entry_numero_sic.config(state="readonly")

        # Sincroniza con Drive automáticamente
        try:
            from src.drive.drive_sync import subir_base
            subir_base()
        except Exception as e:
            print(f"⚠️ No se pudo sincronizar con Drive: {e}")

    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error al cargar la SIC: {e}")



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
        #frame_solicitante = tk.Frame(root)
        #frame_solicitante.pack(pady=5)
        #tk.Label(frame_solicitante, text="Solicitante:").pack(side=tk.LEFT, padx=5)
        #usuarios = [u[1] for u in obtener_usuarios()]
        #combo_solicitante = ttk.Combobox(frame_solicitante, values=usuarios, state="readonly", width=30)
        #combo_solicitante.pack(side=tk.LEFT)

# Solicitante fijo
frame_solicitante = tk.Frame(root)
frame_solicitante.pack(pady=5)
tk.Label(frame_solicitante, text="Solicitante:").pack(side=tk.LEFT, padx=5)

solicitante_fijo = "Federico"
entry_solicitante = tk.Entry(frame_solicitante, width=30)
entry_solicitante.insert(0, solicitante_fijo)
entry_solicitante.config(state="readonly")  # No editable
entry_solicitante.pack(side=tk.LEFT)

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
