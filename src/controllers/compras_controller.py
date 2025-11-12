from src.database.db_manager import conectar, crear_tablas
from src.models.compra import Compra

crear_tablas()  # Asegura que las tablas existan al importar

def agregar_compra(compra: Compra):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO compras (fecha, proveedor, detalle, monto, estado)
        VALUES (?, ?, ?, ?, ?)
    """, (compra.fecha, compra.proveedor, compra.detalle, compra.monto, compra.estado))
    conn.commit()
    conn.close()

def listar_compras():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM compras ORDER BY fecha DESC")
    rows = cur.fetchall()
    conn.close()
    return [Compra(*row) for row in rows]

def eliminar_compra(compra_id: int):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("DELETE FROM compras WHERE id = ?", (compra_id,))
    conn.commit()
    conn.close()

def actualizar_compra(compra: Compra):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        UPDATE compras
        SET fecha=?, proveedor=?, detalle=?, monto=?, estado=?
        WHERE id=?
    """, (compra.fecha, compra.proveedor, compra.detalle, compra.monto, compra.estado, compra.id))
    conn.commit()
    conn.close()
