-- Definición inicial de tablas SQLite

CREATE TABLE IF NOT EXISTS compras (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TEXT,
    proveedor TEXT,
    descripcion TEXT,
    monto REAL
);
