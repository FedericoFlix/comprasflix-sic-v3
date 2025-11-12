from src.controllers.compras_controller import agregar_compra, listar_compras
from src.models.compra import Compra

agregar_compra(Compra(None, "2025-11-12", "Proveedor X", "Compra de prueba", 120000.50))
for c in listar_compras():
    print(c)
