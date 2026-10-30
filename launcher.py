"""Inicio gráfico del programa portátil: navegador + servidor local Flask."""
from __future__ import annotations

import os
import sys
import threading
import tkinter as tk
import webbrowser
from tkinter import messagebox

from werkzeug.serving import make_server

import app as image_app


def main() -> None:
    if sys.platform != "win32":
        raise RuntimeError("Esta distribución está destinada a Windows.")

    root = tk.Tk()
    root.title("ImagenesGPT")
    root.geometry("410x265")
    root.resizable(False, False)

    try:
        server = make_server("127.0.0.1", 0, image_app.app, threaded=True)
    except OSError as exc:
        root.withdraw()
        messagebox.showerror("ImagenesGPT", f"No se pudo iniciar el servidor local:\n{exc}")
        root.destroy()
        return

    thread = threading.Thread(target=server.serve_forever, daemon=True, name="ImagenesGPT")
    thread.start()
    url = f"http://127.0.0.1:{server.server_port}"

    frame = tk.Frame(root, padx=22, pady=16)
    frame.pack(fill="both", expand=True)
    tk.Label(frame, text="Imágenes GPT", font=("Segoe UI", 17, "bold")).pack(anchor="w")
    tk.Label(
        frame,
        text="La aplicación se está ejecutando en tu PC.\n"
             "Utiliza la ventana del navegador para crear imágenes.",
        justify="left", font=("Segoe UI", 10)
    ).pack(anchor="w", pady=(6, 16))
    tk.Button(
        frame, text="Abrir ImagenesGPT en el navegador",
        command=lambda: webbrowser.open(url), width=40
    ).pack(pady=2)
    tk.Button(
        frame, text="Abrir carpeta de imágenes",
        command=lambda: os.startfile(str(image_app.OUTPUT_DIR)), width=40
    ).pack(pady=2)

    def close() -> None:
        if image_app.request_lock.locked() and not messagebox.askyesno(
            "Generación en curso",
            "Hay una generación en curso y podría interrumpirse.\n"
            "¿Quieres cerrar de todos modos?", parent=root
        ):
            return
        server.shutdown()
        server.server_close()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", close)
    tk.Button(frame, text="Cerrar aplicación", command=close, width=40).pack(pady=(9, 0))
    root.after(300, lambda: webbrowser.open(url))
    root.mainloop()


if __name__ == "__main__":
    main()
