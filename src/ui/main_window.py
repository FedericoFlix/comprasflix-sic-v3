import tkinter as tk
<<<<<<< HEAD
from tkinter import ttk, messagebox
from tkinter import scrolledtext
=======
from tkinter import ttk, messagebox, scrolledtext
>>>>>>> sic-funcional
from tkcalendar import DateEntry
import sqlite3
from datetime import datetime
import os
from src.drive.drive_sync import subir_base
<<<<<<< HEAD


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
=======
from src.mail.mailer import enviar_correo


# -------------------------------
# Configuración de base de datos
# -------------------------------
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../database/database.db"))

def get_db_connection():
    """Retorna una conexión a la base de datos."""
    return sqlite3.connect(DB_PATH)


# -------------------------------
# Funciones de negocio
# -------------------------------
def generar_numero_sic():
    """Genera el siguiente número de SIC consecutivo."""
    hoy = datetime.now().strftime("%Y%m%d")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT numero_sic FROM solicitudes WHERE numero_sic LIKE ? ORDER BY numero_sic DESC LIMIT 1",
            (f"{hoy}%",)
        )
        ultimo = cursor.fetchone()
        if ultimo:
            secuencia = int(ultimo[0][-4:]) + 1
        else:
            secuencia = 1
    finally:
        conn.close()

    return f"{hoy}{secuencia:04d}"


def obtener_usuarios():
    """Retorna la lista de nombres de usuarios."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT nombre FROM usuarios ORDER BY nombre")
        usuarios = [u[0] for u in cursor.fetchall()]
    finally:
        conn.close()
    return usuarios


def insertar_solicitud(numero_sic, solicitante_id, fecha_necesidad, datos_lineas):
    """Inserta las solicitudes en la base de datos."""
    fecha_solicitud = datetime.now().strftime("%Y-%m-%d")
    errores = []

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        for linea in datos_lineas:
            partes = linea.split("\t")
            if len(partes) != 5:
                errores.append(linea)
                continue
            oc, planta, material, cantidad, unidad = partes
            cursor.execute("""
                INSERT INTO solicitudes (
                    numero_sic, fecha_solicitud, oc, planta, material,
                    cantidad, unidad, estado, solicitante_id, fecha_necesidad
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 'Solicitado', ?, ?)
            """, (numero_sic, fecha_solicitud, oc, planta, material, cantidad, unidad, solicitante_id, fecha_necesidad))
        conn.commit()
    except sqlite3.Error as e:
        messagebox.showerror("Error de base de datos", str(e))
    finally:
        conn.close()

    return errores


# -------------------------------
# Función principal de carga
# -------------------------------
def cargar_sic():
    solicitante = combo_solicitante.get()
    fecha_necesidad = date_necesidad.get_date()
    texto_datos = text_datos.get("1.0", tk.END).strip()

    if not solicitante or not texto_datos:
        messagebox.showwarning("Atención", "Debe completar todos los campos obligatorios.")
        return

    # Obtener ID del solicitante
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM usuarios WHERE nombre = ?", (solicitante,))
        solicitante_id = cursor.fetchone()
        if not solicitante_id:
            messagebox.showerror("Error", "Solicitante no encontrado en la base de datos.")
            return
        solicitante_id = solicitante_id[0]
    finally:
        conn.close()

    # Deshabilitar botón mientras se procesa
    btn_cargar.config(state="disabled")
    numero_sic = entry_numero_sic.get()
    lineas = texto_datos.splitlines()
    errores = insertar_solicitud(numero_sic, solicitante_id, fecha_necesidad, lineas)
    btn_cargar.config(state="normal")

    if errores:
        messagebox.showwarning(
            "Algunas líneas no se cargaron",
            "Las siguientes líneas no tienen el formato correcto (OC, Planta, Material, Cantidad, Unidad):\n" +
            "\n".join(errores)
        )

    messagebox.showinfo("Éxito", f"SIC {numero_sic} cargado correctamente.")
    text_datos.delete("1.0", tk.END)
    entry_numero_sic.config(state="normal")
    entry_numero_sic.delete(0, tk.END)
    entry_numero_sic.insert(0, generar_numero_sic())
    entry_numero_sic.config(state="readonly")
   
    # -------------------------------
    # Envío de correo con los datos
    # -------------------------------
    try:
        materiales = []
        for linea in lineas:
            partes = linea.split("\t")
            if len(partes) == 5:
                _, planta, material, cantidad, unidad = partes
                materiales.append((material, cantidad, unidad))
        
        # Enviar el mail con la info
        enviar_correo(numero_sic, planta, fecha_necesidad, materiales)
    except Exception as e:
        print(f"⚠️ Error al intentar enviar el correo: {e}")


    subir_base()


# -------------------------------
# Interfaz gráfica
# -------------------------------
root = tk.Tk()
root.title("Carga de SIC")
root.geometry("650x520")
>>>>>>> sic-funcional

# Fecha actual
fecha_actual = datetime.now().strftime("%d/%m/%Y")
tk.Label(root, text=f"Fecha actual: {fecha_actual}", font=("Arial", 10)).pack(pady=5)

# Número de SIC
<<<<<<< HEAD
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
=======
frame_numero = ttk.Frame(root)
frame_numero.pack(pady=5, fill="x", padx=10)
ttk.Label(frame_numero, text="Número de SIC:").pack(side=tk.LEFT, padx=5)
entry_numero_sic = ttk.Entry(frame_numero, width=20)
entry_numero_sic.insert(0, generar_numero_sic())
entry_numero_sic.state(["readonly"])
entry_numero_sic.pack(side=tk.LEFT)

# Solicitante
frame_solicitante = ttk.Frame(root)
frame_solicitante.pack(pady=5, fill="x", padx=10)
ttk.Label(frame_solicitante, text="Solicitante:").pack(side=tk.LEFT, padx=5)
usuarios = obtener_usuarios()
combo_solicitante = ttk.Combobox(frame_solicitante, values=usuarios, state="readonly", width=30)
combo_solicitante.pack(side=tk.LEFT)

# Fecha de necesidad
frame_fecha = ttk.Frame(root)
frame_fecha.pack(pady=5, fill="x", padx=10)
ttk.Label(frame_fecha, text="Fecha de necesidad:").pack(side=tk.LEFT, padx=5)
>>>>>>> sic-funcional
date_necesidad = DateEntry(frame_fecha, date_pattern="yyyy-mm-dd", width=12)
date_necesidad.pack(side=tk.LEFT)

# Área de texto
<<<<<<< HEAD
tk.Label(root, text="Datos (OC, Planta, Material, Cantidad, Unidad):").pack(pady=5)
text_datos = scrolledtext.ScrolledText(root, width=70, height=10)
text_datos.pack(padx=10, pady=5)

# Botón de carga
btn_cargar = tk.Button(root, text="Cargar SIC", command=cargar_sic, bg="#4CAF50", fg="white", font=("Arial", 11))
btn_cargar.pack(pady=10)
=======
ttk.Label(root, text="Datos (OC, Planta, Material, Cantidad, Unidad):").pack(pady=5)
text_datos = scrolledtext.ScrolledText(root, width=80, height=12)
text_datos.pack(padx=10, pady=5)

# Botón de carga
btn_cargar = ttk.Button(root, text="Cargar SIC", command=cargar_sic)
btn_cargar.pack(pady=15)
>>>>>>> sic-funcional

root.mainloop()
