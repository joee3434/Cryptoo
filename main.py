import time
import tkinter as tk
from tkinter import messagebox, filedialog

import customtkinter as ctk

from crypto_engine import encrypt_text, decrypt_text, default_key_hint
from database import init_db, add_record, get_history, clear_history

APP_NAME = "CRYPTOO"
BG = "#070B14"
SIDEBAR = "#0A1020"
PANEL = "#10192B"
PANEL_ALT = "#0C1424"
BORDER = "#253451"
CYAN = "#29D9F5"
PURPLE = "#A78BFA"
TEXT = "#EAF2FF"
MUTED = "#8EA2C7"
GREEN = "#43E6A2"
RED = "#FF6489"


class CryptooApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("CRYPTOO // Cryptography Workstation")
        self.geometry("1380x900")
        self.minsize(1120, 760)
        self.configure(fg_color=BG)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        init_db()

        self.algorithm = tk.StringVar(value="Caesar Cipher")
        self.operation = tk.StringVar(value="Encrypt")
        self.key_var = tk.StringVar(value="3")
        self.status_var = tk.StringVar(value="SYSTEM ONLINE  /  LOCAL DATABASE CONNECTED")
        self.active_section = "workspace"
        self._build_ui()
        self._update_key_hint()
        self._refresh_history()

    def _label(self, parent, text, **kwargs):
        return ctk.CTkLabel(parent, text=text, **kwargs)

    def _build_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Left navigation
        side = ctk.CTkFrame(self, width=242, corner_radius=0, fg_color=SIDEBAR)
        side.grid(row=0, column=0, sticky="nsew")
        side.grid_propagate(False)

        logo = ctk.CTkFrame(side, fg_color="transparent")
        logo.pack(fill="x", padx=22, pady=(28, 24))
        self._label(logo, "◈", font=ctk.CTkFont(size=39, weight="bold"), text_color=CYAN).pack(side="left", padx=(0, 10))
        titlebox = ctk.CTkFrame(logo, fg_color="transparent")
        titlebox.pack(side="left")
        self._label(titlebox, "CRYPTOO", font=ctk.CTkFont(size=27, weight="bold"), text_color=TEXT).pack(anchor="w")
        self._label(titlebox, "CRYPTOGRAPHY LAB", font=ctk.CTkFont(size=13, weight="bold"), text_color=CYAN).pack(anchor="w", pady=(1, 0))

        self._label(side, "WORKSPACE", font=ctk.CTkFont(size=14, weight="bold"), text_color="#617494").pack(anchor="w", padx=24, pady=(8, 9))
        self._nav_item(side, "⌘", "Encryption Studio", True, self._show_workspace)
        self._nav_item(side, "◷", "Operation History", False, self._show_history_section)
        self._nav_item(side, "⛨", "Cipher Library", False, self._show_cipher_library)
        self._nav_item(side, "⚙", "Key & Parameters", False, self._show_key_help)

        ctk.CTkFrame(side, height=1, fg_color=BORDER).pack(fill="x", padx=20, pady=22)
        self._label(side, "AVAILABLE CIPHERS", font=ctk.CTkFont(size=14, weight="bold"), text_color="#617494").pack(anchor="w", padx=24, pady=(0, 12))
        for icon, name, desc, color in [
            ("↻", "Caesar", "Shift substitution", CYAN),
            ("⌁", "Vigenère", "Keyword polyalphabetic", PURPLE),
            ("▦", "Playfair", "Digraph substitution", "#FBBF24"),
            ("▤", "Hill", "Matrix-based cipher", GREEN),
        ]:
            row = ctk.CTkFrame(side, fg_color="transparent")
            row.pack(fill="x", padx=24, pady=5)
            self._label(row, icon, font=ctk.CTkFont(size=23, weight="bold"), text_color=color, width=26).pack(side="left")
            textbox = ctk.CTkFrame(row, fg_color="transparent")
            textbox.pack(side="left", padx=8)
            self._label(textbox, name, font=ctk.CTkFont(size=16, weight="bold"), text_color=TEXT).pack(anchor="w")
            self._label(textbox, desc, font=ctk.CTkFont(size=13), text_color=MUTED).pack(anchor="w")

        ctk.CTkFrame(side, height=1, fg_color=BORDER).pack(fill="x", padx=20, pady=22)
        status_card = ctk.CTkFrame(side, fg_color="#0F1D2B", corner_radius=12, border_width=1, border_color="#174D54")
        status_card.pack(fill="x", padx=17)
        self._label(status_card, "●  LOCAL SYSTEM ACTIVE", font=ctk.CTkFont(size=14, weight="bold"), text_color=GREEN).pack(anchor="w", padx=12, pady=(12, 5))
        self._label(status_card, "Offline desktop app\nSQLite history enabled", font=ctk.CTkFont(size=14), text_color=MUTED, justify="left").pack(anchor="w", padx=12, pady=(0, 12))
        self._label(side, "BUILD 2.0  •  EDUCATIONAL", font=ctk.CTkFont(size=13), text_color="#526581").pack(side="bottom", pady=18)

        # Main content
        main = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        main.grid(row=0, column=1, sticky="nsew", padx=27, pady=23)
        main.grid_columnconfigure(0, weight=1)
        main.grid_rowconfigure(3, weight=1)

        header = ctk.CTkFrame(main, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        head_left = ctk.CTkFrame(header, fg_color="transparent")
        head_left.pack(side="left")
        self._label(head_left, "Cryptography Workstation", font=ctk.CTkFont(size=33, weight="bold"), text_color=TEXT).pack(anchor="w")
        self._label(head_left, "Encrypt. Decrypt. Understand the algorithm.", font=ctk.CTkFont(size=17), text_color=MUTED).pack(anchor="w", pady=(5, 0))
        ctk.CTkLabel(header, text="●  ALL SYSTEMS NORMAL", text_color=GREEN, font=ctk.CTkFont(size=14, weight="bold"),
                     fg_color="#0D211F", corner_radius=8, padx=12, pady=8).pack(side="right", pady=(7, 0))

        # Metric tiles
        metrics = ctk.CTkFrame(main, fg_color="transparent")
        metrics.grid(row=1, column=0, sticky="ew", pady=(0, 17))
        for i in range(3):
            metrics.grid_columnconfigure(i, weight=1)
        self._metric(metrics, 0, "▦", "04", "CLASSICAL CIPHERS", CYAN)
        self._metric(metrics, 1, "◷", "LIVE", "OPERATION HISTORY", PURPLE)
        self._metric(metrics, 2, "⬡", "LOCAL", "SQLITE STORAGE", GREEN)

        # Settings panel
        settings = ctk.CTkFrame(main, fg_color=PANEL, corner_radius=15, border_width=1, border_color=BORDER)
        settings.grid(row=2, column=0, sticky="ew", pady=(0, 16))
        settings.grid_columnconfigure((0, 1, 2), weight=1)
        self._label(settings, "01  /  CIPHER CONFIGURATION", font=ctk.CTkFont(size=14, weight="bold"), text_color=CYAN).grid(row=0, column=0, columnspan=3, sticky="w", padx=18, pady=(15, 10))
        self._label(settings, "ALGORITHM", font=ctk.CTkFont(size=14, weight="bold"), text_color=MUTED).grid(row=1, column=0, sticky="w", padx=18, pady=(0, 5))
        self.algo_menu = ctk.CTkOptionMenu(settings, variable=self.algorithm,
            values=["Caesar Cipher", "Vigenère Cipher", "Playfair Cipher", "Hill Cipher"],
            command=lambda _: self._update_key_hint(), fg_color="#172844",
            button_color="#087EAB", button_hover_color="#0B6687", dropdown_fg_color=PANEL_ALT,
            text_color=TEXT, font=ctk.CTkFont(size=22, weight="bold"),
            dropdown_font=ctk.CTkFont(size=24, weight="bold"), height=64)
        self.algo_menu.grid(row=2, column=0, sticky="ew", padx=18, pady=(0, 16))
        self._label(settings, "OPERATION", font=ctk.CTkFont(size=14, weight="bold"), text_color=MUTED).grid(row=1, column=1, sticky="w", padx=18, pady=(0, 5))
        self.op_menu = ctk.CTkSegmentedButton(settings, variable=self.operation, values=["Encrypt", "Decrypt"],
            selected_color="#6D28D9", selected_hover_color="#5B21B6", unselected_color="#172844",
            command=lambda _: self._update_key_hint(), height=54, font=ctk.CTkFont(size=18, weight="bold"))
        self.op_menu.grid(row=2, column=1, sticky="ew", padx=18, pady=(0, 16))
        self._label(settings, "KEY / PARAMETERS", font=ctk.CTkFont(size=14, weight="bold"), text_color=MUTED).grid(row=1, column=2, sticky="w", padx=18, pady=(0, 5))
        self.key_entry = ctk.CTkEntry(settings, textvariable=self.key_var, placeholder_text="Enter cipher key",
            fg_color="#080E1A", border_color="#30405D", text_color=TEXT, height=52)
        self.key_entry.grid(row=2, column=2, sticky="ew", padx=18, pady=(0, 4))
        self.key_hint = self._label(settings, "", font=ctk.CTkFont(size=14), text_color=MUTED)
        self.key_hint.grid(row=3, column=2, sticky="w", padx=18, pady=(0, 13))

        # Input/output
        panels = ctk.CTkFrame(main, fg_color="transparent")
        panels.grid(row=3, column=0, sticky="nsew", pady=(0, 15))
        panels.grid_columnconfigure((0, 1), weight=1)
        panels.grid_rowconfigure(1, weight=1)
        self._label(panels, "02  /  INPUT PAYLOAD", font=ctk.CTkFont(size=15, weight="bold"), text_color=CYAN).grid(row=0, column=0, sticky="w", padx=(0, 8), pady=(0, 8))
        self._label(panels, "03  /  OUTPUT PAYLOAD", font=ctk.CTkFont(size=15, weight="bold"), text_color=PURPLE).grid(row=0, column=1, sticky="w", padx=(8, 0), pady=(0, 8))
        self.input_box = ctk.CTkTextbox(panels, fg_color=PANEL_ALT, border_width=1, border_color="#24506A",
            text_color=TEXT, corner_radius=12, wrap="word", font=ctk.CTkFont(family="DejaVu Sans Mono", size=20))
        self.input_box.grid(row=1, column=0, sticky="nsew", padx=(0, 8))
        self.input_box.insert("1.0", "Enter your message here...")
        self.output_box = ctk.CTkTextbox(panels, fg_color=PANEL_ALT, border_width=1, border_color="#4C3C7B",
            text_color=TEXT, corner_radius=12, wrap="word", font=ctk.CTkFont(family="DejaVu Sans Mono", size=20))
        self.output_box.grid(row=1, column=1, sticky="nsew", padx=(8, 0))
        self.output_box.configure(state="disabled")

        # Action bar and history
        bottom = ctk.CTkFrame(main, fg_color="transparent")
        bottom.grid(row=4, column=0, sticky="nsew")
        bottom.grid_columnconfigure(0, weight=1)
        actions = ctk.CTkFrame(bottom, fg_color="transparent")
        actions.grid(row=0, column=0, sticky="ew", pady=(0, 13))
        ctk.CTkButton(actions, text="⚡  EXECUTE", command=self._run_operation, height=42, width=145,
            fg_color="#0788A9", hover_color="#066A85", font=ctk.CTkFont(size=16, weight="bold")).pack(side="left", padx=(0, 8))
        ctk.CTkButton(actions, text="▣  COPY OUTPUT", command=self._copy_output, height=42, width=135,
            fg_color="#202B43", hover_color="#2C3B5C").pack(side="left", padx=(0, 8))
        ctk.CTkButton(actions, text="⇩  EXPORT", command=self._export_output, height=42, width=105,
            fg_color="#202B43", hover_color="#2C3B5C").pack(side="left", padx=(0, 8))
        ctk.CTkButton(actions, text="⌫  CLEAR", command=self._clear, height=42, width=95,
            fg_color="#422033", hover_color="#6B2947").pack(side="left")
        ctk.CTkButton(actions, text="CLEAR HISTORY", command=self._clear_history, height=42, width=125,
            fg_color="#202B43", hover_color="#2C3B5C").pack(side="right")

        history = ctk.CTkFrame(bottom, fg_color=PANEL, corner_radius=14, border_width=1, border_color=BORDER)
        history.grid(row=1, column=0, sticky="nsew")
        history.grid_columnconfigure(0, weight=1)
        self._label(history, "◷  RECENT OPERATIONS", font=ctk.CTkFont(size=15, weight="bold"), text_color=TEXT).pack(anchor="w", padx=15, pady=(12, 3))
        self.history_list = ctk.CTkScrollableFrame(history, fg_color="transparent", height=110)
        self.history_list.pack(fill="both", expand=True, padx=9, pady=(0, 8))

        self._label(main, "", text_color=MUTED).grid(row=5, column=0)
        ctk.CTkLabel(main, textvariable=self.status_var, text_color="#617594", font=ctk.CTkFont(size=14)).grid(row=6, column=0, sticky="w", pady=(8, 0))

    def _metric(self, parent, col, icon, value, caption, color):
        card = ctk.CTkFrame(parent, fg_color=PANEL, corner_radius=12, border_width=1, border_color=BORDER)
        card.grid(row=0, column=col, sticky="ew", padx=(0 if col == 0 else 7, 7 if col < 2 else 0))
        ctk.CTkLabel(card, text=icon, text_color=color, font=ctk.CTkFont(size=27, weight="bold")).pack(side="left", padx=15, pady=12)
        box = ctk.CTkFrame(card, fg_color="transparent")
        box.pack(side="left", pady=10)
        ctk.CTkLabel(box, text=value, text_color=TEXT, font=ctk.CTkFont(size=21, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(box, text=caption, text_color=MUTED, font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w")

    def _nav_item(self, parent, icon, label, active, command):
        frame = ctk.CTkFrame(parent, fg_color="#12263C" if active else "transparent", corner_radius=9)
        frame.pack(fill="x", padx=14, pady=3)
        btn = ctk.CTkButton(
            frame, text=f"{icon}   {label}", command=command,
            anchor="w", height=56, corner_radius=8,
            fg_color="#12263C" if active else "transparent",
            hover_color="#1B3150", text_color=CYAN if active else TEXT,
            font=ctk.CTkFont(size=20, weight="bold" if active else "normal"),
            border_spacing=10
        )
        btn.pack(fill="x", padx=0, pady=0)

    def _show_workspace(self):
        self.status_var.set("WORKSPACE ACTIVE  /  SELECT A CIPHER AND RUN AN OPERATION")
        self.input_box.focus_set()

    def _show_history_section(self):
        self.status_var.set("OPERATION HISTORY  /  RECENT DATABASE RECORDS")
        self._refresh_history()
        self.history_list.focus_set()

    def _show_cipher_library(self):
        details = (
            "CIPHER LIBRARY\\n\\n"
            "CAESAR CIPHER\\nShift each English letter by a fixed integer. Educational only.\\n\\n"
            "VIGENERE CIPHER\\nUses a repeating alphabetic keyword to shift letters.\\n\\n"
            "PLAYFAIR CIPHER\\nEncrypts letter pairs using a 5x5 keyword square. I and J share a cell.\\n\\n"
            "HILL CIPHER\\nUses a 2x2 matrix modulo 26; the matrix must have an invertible determinant.\\n\\n"
            "These classical ciphers are for learning and must not protect confidential data."
        )
        from tkinter import messagebox
        messagebox.showinfo("Cryptoo | Cipher Library", details)
        self.status_var.set("CIPHER LIBRARY OPENED")

    def _show_key_help(self):
        details = (
            "KEY & PARAMETERS\\n\\n"
            "CAESAR: integer shift, for example 3.\\n"
            "VIGENERE: English-letter keyword, for example LEMON.\\n"
            "PLAYFAIR: keyword, for example MONARCHY.\\n"
            "HILL: four comma-separated integers, for example 3,3,2,5.\\n\\n"
            "Use the same key and algorithm for decryption. Playfair and Hill may add padding letters."
        )
        from tkinter import messagebox
        messagebox.showinfo("Cryptoo | Key & Parameters", details)
        self.status_var.set("KEY AND PARAMETER GUIDE OPENED")

    def _update_key_hint(self):
        algo = self.algorithm.get()
        hints = {
            "Caesar Cipher": "Integer shift, e.g. 3. Default is 3.",
            "Vigenère Cipher": "English letters only, e.g. LEMON.",
            "Playfair Cipher": "Keyword, e.g. MONARCHY. I/J are combined; output uses letter pairs.",
            "Hill Cipher": "2×2 matrix as a,b,c,d e.g. 3,3,2,5 (determinant must be invertible mod 26)."
        }
        self.key_hint.configure(text=hints[algo])
        if algo == "Caesar Cipher" and not self.key_var.get().strip():
            self.key_var.set("3")
        elif algo == "Vigenère Cipher" and self.key_var.get().strip() == "3":
            self.key_var.set("")
        elif algo in ("Playfair Cipher", "Hill Cipher") and self.key_var.get().strip() == "3":
            self.key_var.set("")

    def _set_output(self, value):
        self.output_box.configure(state="normal")
        self.output_box.delete("1.0", "end")
        self.output_box.insert("1.0", value)
        self.output_box.configure(state="disabled")

    def _run_operation(self):
        raw = self.input_box.get("1.0", "end").strip()
        if raw == "Enter your message here...":
            raw = ""
        if not raw:
            messagebox.showwarning("Missing input", "Enter a message or ciphertext first.")
            return
        algo, op, key = self.algorithm.get(), self.operation.get(), self.key_var.get().strip()
        try:
            start = time.perf_counter()
            result = encrypt_text(algo, raw, key) if op == "Encrypt" else decrypt_text(algo, raw, key)
            elapsed = (time.perf_counter() - start) * 1000
            self._set_output(result)
            add_record(algo, op, raw, result, elapsed)
            self._refresh_history()
            self.status_var.set(f"SUCCESS  /  {algo.upper()}  /  {elapsed:.3f} ms")
        except Exception as exc:
            messagebox.showerror("Operation failed", str(exc))
            self.status_var.set("OPERATION FAILED  /  CHECK INPUT AND KEY")

    def _copy_output(self):
        text = self.output_box.get("1.0", "end").strip()
        if not text:
            messagebox.showinfo("No output", "Run an operation first.")
            return
        self.clipboard_clear()
        self.clipboard_append(text)
        self.status_var.set("OUTPUT COPIED TO CLIPBOARD")

    def _export_output(self):
        text = self.output_box.get("1.0", "end").strip()
        if not text:
            messagebox.showinfo("No output", "Run an operation first.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text file", "*.txt")])
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
            self.status_var.set("OUTPUT EXPORTED")

    def _clear(self):
        self.input_box.delete("1.0", "end")
        self._set_output("")
        self.status_var.set("WORKSPACE CLEARED")

    def _refresh_history(self):
        if not hasattr(self, "history_list"):
            return
        for child in self.history_list.winfo_children():
            child.destroy()
        rows = get_history(8)
        if not rows:
            ctk.CTkLabel(self.history_list, text="No records yet — run a cipher operation to populate history.",
                         text_color=MUTED).pack(anchor="w", padx=8, pady=8)
            return
        for rid, algo, op, inp, out, stamp, ms in rows:
            item = ctk.CTkFrame(self.history_list, fg_color="#0B1322", corner_radius=8)
            item.pack(fill="x", padx=2, pady=3)
            color = CYAN if op == "Encrypt" else PURPLE
            ctk.CTkLabel(item, text=f"◈  {algo}     /     {op.upper()}     /     {stamp}     /     {ms:.3f} ms",
                         text_color=color, font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=10, pady=(7, 2))
            ctk.CTkLabel(item, text=f"IN:  {inp[:100]}", text_color=TEXT,
                         font=ctk.CTkFont(size=14)).pack(anchor="w", padx=10)
            ctk.CTkLabel(item, text=f"OUT: {out[:100]}", text_color=MUTED,
                         font=ctk.CTkFont(size=14)).pack(anchor="w", padx=10, pady=(0, 7))

    def _clear_history(self):
        if messagebox.askyesno("Clear history", "Permanently delete all local operation history?"):
            clear_history()
            self._refresh_history()
            self.status_var.set("HISTORY CLEARED")


if __name__ == "__main__":
    app = CryptooApp()
    app.mainloop()
