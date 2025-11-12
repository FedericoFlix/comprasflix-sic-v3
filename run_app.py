import os
import sys
import subprocess
from src.drive.drive_sync import sincronizar_normalizado as sincronizar

sincronizar()



def main():
    # Ruta absoluta a la carpeta raíz del proyecto
    project_root = os.path.abspath(os.path.dirname(__file__))
    ui_path = os.path.join(project_root, "src", "ui", "main_window.py")

    # Asegura que la raíz esté en el sys.path
    if project_root not in sys.path:
        sys.path.append(project_root)

    # Ejecuta la ventana principal
    try:
        subprocess.run([sys.executable, "-m", "src.ui.main_window"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al ejecutar la aplicación: {e}")
    except KeyboardInterrupt:
        print("\n🟡 Ejecución interrumpida por el usuario.")

if __name__ == "__main__":
    print("🚀 Iniciando SIC App...")
    main()
