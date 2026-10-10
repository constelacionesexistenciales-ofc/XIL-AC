"""Interfaz de escritorio local XIL-AC. No contiene cliente HTTP ni transmite texto."""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from privacy_engine import review_text

APP_TITLE = "XIL-AC · Puerta Local"
WARNING = (
    "MODO LOCAL: la transmisión remota está DESHABILITADA. "
    "Esta versión no se conecta a la API ni envía el texto. "
    "El análisis es heurístico y no garantiza anonimización."
)

class GatewayApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("850x700")
        self.minsize(620, 540)
        self.configure(bg="#f4f5f6")
        self._build()

    def _build(self) -> None:
        root = ttk.Frame(self, padding=18)
        root.pack(fill="both", expand=True)
        ttk.Label(root, text="XIL-AC · Puerta Local", font=("Segoe UI", 19, "bold")).pack(anchor="w")
        ttk.Label(root, text="Revisión de privacidad antes de cualquier operación", font=("Segoe UI", 10)).pack(anchor="w", pady=(2, 12))

        warning = tk.Label(root, text=WARNING, bg="#fff0df", fg="#7c3100",
                           justify="left", anchor="w", wraplength=780,
                           padx=12, pady=10, font=("Segoe UI", 10, "bold"))
        warning.pack(fill="x", pady=(0, 12))

        ttk.Label(root, text="Texto para revisar (el contenido se procesa solo en este equipo):").pack(anchor="w")
        self.input_text = tk.Text(root, height=14, wrap="word", font=("Consolas", 10),
                                  undo=True, borderwidth=1, relief="solid")
        self.input_text.pack(fill="both", expand=True, pady=(5, 10))

        buttons = ttk.Frame(root)
        buttons.pack(fill="x")
        ttk.Button(buttons, text="Revisar localmente", command=self._review).pack(side="left")
        ttk.Button(buttons, text="Borrar contenido", command=self._clear).pack(side="left", padx=(8, 0))

        ttk.Label(root, text="Resultado de la revisión", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(14, 4))
        self.status = tk.Label(root, text="Todavía no se revisó ningún texto.",
                               bg="#ffffff", fg="#202124", justify="left",
                               anchor="nw", wraplength=780, padx=12, pady=12,
                               relief="solid", borderwidth=1)
        self.status.pack(fill="x")
        ttk.Label(root, text="Sin conexión de red · Sin almacenamiento del texto · Sin botón de envío",
                  foreground="#555555").pack(anchor="w", pady=(12, 0))

    def _review(self) -> None:
        content = self.input_text.get("1.0", "end-1c")
        result = review_text(content)
        colors = {"DENY": ("#fff0df", "#7c3100"),
                  "REVIEW_REQUIRED": ("#fff7d6", "#624900")}
        bg, fg = colors.get(result.decision, ("#ffffff", "#202124"))
        details = [
            f"DECISIÓN LOCAL: {result.decision}",
            f"Nivel de señal: {result.risk}",
            result.message,
        ]
        if result.categories:
            details.append("Tipos de señales: " + ", ".join(result.categories))
        details.append("POLÍTICA: el envío remoto está bloqueado en esta versión, incluso si no aparecen señales.")
        self.status.configure(text="\n\n".join(details), bg=bg, fg=fg)

    def _clear(self) -> None:
        self.input_text.delete("1.0", "end")
        self.status.configure(text="Contenido borrado de la interfaz. La transmisión remota sigue deshabilitada.",
                              bg="#ffffff", fg="#202124")

if __name__ == "__main__":
    GatewayApp().mainloop()
