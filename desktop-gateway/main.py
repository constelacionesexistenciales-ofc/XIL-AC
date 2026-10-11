"""Interfaz de escritorio local XIL-AC. No contiene cliente HTTP ni transmite texto."""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from auth_store import authenticate, create_initial_user, has_users
from privacy_engine import review_text

APP_TITLE = "XIL-AC · Puerta Local"
WARNING = (
    "MODO LOCAL: la transmisión remota está DESHABILITADA. "
    "Esta versión no se conecta a la API ni envía el texto. "
    "El análisis es heurístico y no garantiza anonimización."
)


class AccessDialog(tk.Toplevel):
    def __init__(self, master: tk.Tk, setup: bool = False) -> None:
        super().__init__(master)
        self.result = False
        self.setup = setup
        self.title("Configurar acceso inicial" if setup else "Ingresar a XIL-AC")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        body = ttk.Frame(self, padding=20)
        body.pack(fill="both", expand=True)
        ttk.Label(body, text="Crear el acceso personal" if setup else "Acceso personal",
                  font=("Segoe UI", 15, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))
        explanation = ("Configurá usuario, contraseña y PIN. La contraseña debe tener al menos 10 caracteres; "
                       "el PIN debe tener de 4 a 8 dígitos." if setup else
                       "Ingresá tu usuario y elegí contraseña o PIN.")
        ttk.Label(body, text=explanation, wraplength=430).grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 12))
        self.username = tk.StringVar()
        self.credential = tk.StringVar()
        self.method = tk.StringVar(value="password")
        ttk.Label(body, text="Usuario").grid(row=2, column=0, sticky="w", pady=4)
        self.user_entry = ttk.Entry(body, textvariable=self.username, width=34)
        self.user_entry.grid(row=2, column=1, sticky="ew", pady=4)
        self.credential_label = ttk.Label(body, text="Contraseña")
        self.credential_label.grid(row=3, column=0, sticky="w", pady=4)
        self.credential_entry = ttk.Entry(body, textvariable=self.credential, show="•", width=34)
        self.credential_entry.grid(row=3, column=1, sticky="ew", pady=4)
        if setup:
            self.password_confirm = tk.StringVar()
            self.pin = tk.StringVar()
            self.pin_confirm = tk.StringVar()
            ttk.Label(body, text="Repetir contraseña").grid(row=4, column=0, sticky="w", pady=4)
            ttk.Entry(body, textvariable=self.password_confirm, show="•", width=34).grid(row=4, column=1, sticky="ew", pady=4)
            ttk.Label(body, text="PIN (4–8 dígitos)").grid(row=5, column=0, sticky="w", pady=4)
            ttk.Entry(body, textvariable=self.pin, show="•", width=34).grid(row=5, column=1, sticky="ew", pady=4)
            ttk.Label(body, text="Repetir PIN").grid(row=6, column=0, sticky="w", pady=4)
            ttk.Entry(body, textvariable=self.pin_confirm, show="•", width=34).grid(row=6, column=1, sticky="ew", pady=4)
            ttk.Label(body, text="Usá una contraseña nueva que no hayas compartido.",
                      wraplength=430).grid(row=7, column=0, columnspan=2, sticky="w", pady=(8, 4))
            button_row = 8
        else:
            methods = ttk.Frame(body)
            methods.grid(row=4, column=1, sticky="w", pady=4)
            ttk.Label(body, text="Método").grid(row=4, column=0, sticky="w", pady=4)
            ttk.Radiobutton(methods, text="Contraseña", variable=self.method, value="password",
                            command=self._switch_method).pack(side="left")
            ttk.Radiobutton(methods, text="PIN", variable=self.method, value="pin",
                            command=self._switch_method).pack(side="left", padx=(12, 0))
            button_row = 5
        buttons = ttk.Frame(body)
        buttons.grid(row=button_row, column=0, columnspan=2, sticky="e", pady=(14, 0))
        ttk.Button(buttons, text="Cancelar", command=self._cancel).pack(side="left", padx=(0, 8))
        ttk.Button(buttons, text="Configurar" if setup else "Ingresar", command=self._submit).pack(side="left")
        self.bind("<Return>", lambda _event: self._submit())
        self.protocol("WM_DELETE_WINDOW", self._cancel)
        self.user_entry.focus_set()
        self.update_idletasks()
        self.geometry(f"+{master.winfo_rootx()+60}+{master.winfo_rooty()+60}")

    def _switch_method(self) -> None:
        is_password = self.method.get() == "password"
        self.credential_label.configure(text="Contraseña" if is_password else "PIN")
        self.credential_entry.configure(show="•" if is_password else "")
        self.credential.set("")

    def _submit(self) -> None:
        username = self.username.get().strip()
        credential = self.credential.get()
        if self.setup:
            if credential != self.password_confirm.get():
                messagebox.showerror("No coincide", "Las contraseñas no coinciden.", parent=self)
                return
            if self.pin.get() != self.pin_confirm.get():
                messagebox.showerror("No coincide", "Los PIN no coinciden.", parent=self)
                return
            try:
                create_initial_user(username, credential, self.pin.get())
            except (ValueError, RuntimeError, OSError) as exc:
                messagebox.showerror("No se pudo configurar", str(exc), parent=self)
                return
            self.result = True
            self.destroy()
            return
        ok, message = authenticate(username, credential, self.method.get())
        if not ok:
            messagebox.showerror("Acceso denegado", message, parent=self)
            return
        self.result = True
        self.destroy()

    def _cancel(self) -> None:
        self.result = False
        self.destroy()


class GatewayApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.withdraw()
        try:
            dialog = AccessDialog(self, setup=not has_users())
            self.wait_window(dialog)
            if not dialog.result:
                self.destroy()
                return
        except (RuntimeError, OSError) as exc:
            messagebox.showerror("Acceso local", str(exc), parent=self)
            self.destroy()
            return
        self.deiconify()
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
        result = review_text(self.input_text.get("1.0", "end-1c"))
        colors = {"DENY": ("#fff0df", "#7c3100"),
                  "REVIEW_REQUIRED": ("#fff7d6", "#624900")}
        bg, fg = colors.get(result.decision, ("#ffffff", "#202124"))
        details = [f"DECISIÓN LOCAL: {result.decision}", f"Nivel de señal: {result.risk}", result.message]
        if result.categories:
            details.append("Tipos de señales: " + ", ".join(result.categories))
        details.append("POLÍTICA: el envío remoto está bloqueado en esta versión, incluso si no aparecen señales.")
        self.status.configure(text="\n\n".join(details), bg=bg, fg=fg)

    def _clear(self) -> None:
        self.input_text.delete("1.0", "end")
        self.status.configure(text="Contenido borrado de la interfaz. La transmisión remota sigue deshabilitada.",
                              bg="#ffffff", fg="#202124")


if __name__ == "__main__":
    app = GatewayApp()
    if app.winfo_exists():
        app.mainloop()
