from dataclasses import dataclass

@dataclass
class Compra:
    id: int | None
    fecha: str
    proveedor: str
    detalle: str
    monto: float
    estado: str = "pendiente"
