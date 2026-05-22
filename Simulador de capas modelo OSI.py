# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import messagebox, font as tkfont
import random
import base64

# ── COLORES DE ACENTO ──
ACCENT_GOLD  = "#f59e0b"   
ACCENT_GREEN = "#10b981"   
ACCENT_BLUE  = "#0ea5e9"   
LAYER_ACTIVE = "#fde047"   
LAYER_DONE_A = "#a7f3d0"   
LAYER_DONE_B = "#bae6fd"   

# ── DICCIONARIO DE TEMAS MEJORADO ──
TEMAS = {
    "claro": {
        "bg_main": "#f8fafc",      
        "bg_panel": "#ffffff",     
        "header_fg": "#0f172a",    
        "header_sub": "#64748b",   
        "text_main": "#0f172a",    
        "text_dim": "#64748b",     
        "nota_bg": "#ffffff",
        "nota_border": "#cbd5e1",
        "console_bg": "#f1f5f9",   
        "console_fg_a": "#059669", 
        "console_fg_b": "#0284c7", 
        "layer_idle": "#e2e8f0",   
        "btn_tema_bg": "#e2e8f0",
        "btn_tema_fg": "#0f172a",
        "canvas_flecha": "#94a3b8"
    },
    "oscuro": {
        "bg_main": "#121212",      
        "bg_panel": "#1e1e1e",     
        "header_fg": "#ffffff",    
        "header_sub": "#a1a1aa",   
        "text_main": "#ffffff",    
        "text_dim": "#a1a1aa",     
        "nota_bg": "#1e1e1e",
        "nota_border": "#333333",  
        "console_bg": "#000000",   
        "console_fg_a": "#10b981", 
        "console_fg_b": "#38bdf8", 
        "layer_idle": "#2d2d2d",   
        "btn_tema_bg": "#333333",
        "btn_tema_fg": "#ffffff",
        "canvas_flecha": "#71717a"
    }
}

CAPAS = [
    ("7", "APL", "Aplicación"),
    ("6", "PRE", "Presentación"),
    ("5", "SES", "Sesión"),
    ("4", "TRA", "Transporte"),
    ("3", "RED", "Red"),
    ("2", "ENL", "Enlace"),
    ("1", "FIS", "Física"),
]

PDU_NOMBRES = ["Datos", "Datos cifrados", "SPDU", "Segmento", "Paquete", "Trama", "Bits"]


class SimuladorOSI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Simulador de Capas del Modelo OSI — UNEMI 2026")
        self.root.geometry("1150x760")
        self.root.resizable(True, True)

        self._en_ejecucion = False
        self._cola_pasos   = []
        self.tema_actual   = "oscuro" 

        self._construir_ui()

    def _boton_redondo(self, parent, texto, comando, color_bg, color_fg, ancho=120, alto=34, radio=10):
        cv = tk.Canvas(parent, width=ancho, height=alto, bg=parent["bg"], highlightthickness=0, cursor="hand2")

        def _dibujar(bg):
            cv.delete("all")
            r = radio
            cv.create_arc(0, 0, 2*r, 2*r, start=90, extent=90, fill=bg, outline=bg)
            cv.create_arc(ancho-2*r, 0, ancho, 2*r, start=0, extent=90, fill=bg, outline=bg)
            cv.create_arc(0, alto-2*r, 2*r, alto, start=180, extent=90, fill=bg, outline=bg)
            cv.create_arc(ancho-2*r, alto-2*r, ancho, alto, start=270, extent=90, fill=bg, outline=bg)
            cv.create_rectangle(r, 0, ancho-r, alto, fill=bg, outline=bg)
            cv.create_rectangle(0, r, ancho, alto-r, fill=bg, outline=bg)
            cv.create_text(ancho//2, alto//2, text=texto, font=("Times New Roman", 11, "bold"), fill=color_fg)

        _dibujar(color_bg)

        def _on_enter(e):
            if not cv._habilitado: return
            r, g, b = parent.winfo_rgb(color_bg)
            r2 = min(65535, int(r * 0.85))
            g2 = min(65535, int(g * 0.85))
            b2 = min(65535, int(b * 0.85))
            _dibujar(f"#{r2>>8:02x}{g2>>8:02x}{b2>>8:02x}")

        def _on_leave(e):
            if not cv._habilitado: return
            _dibujar(color_bg)

        def _on_click(e):
            if cv._habilitado: comando()
                
        def _set_estado(habilitado, bg_alternativo=None):
            cv._habilitado = habilitado
            if habilitado:
                cv.config(cursor="hand2")
                _dibujar(color_bg)
            else:
                cv.config(cursor="arrow")
                c = TEMAS[self.tema_actual]
                _dibujar(bg_alternativo if bg_alternativo else c["text_dim"])

        cv.bind("<Enter>", _on_enter)
        cv.bind("<Leave>", _on_leave)
        cv.bind("<Button-1>", _on_click)
        cv._habilitado = True
        cv.set_estado = _set_estado 
        return cv

    def _construir_ui(self):
        c = TEMAS[self.tema_actual]
        self.root.configure(bg=c["bg_main"])

        # ── HEADER ──────────────────────────
        hdr = tk.Frame(self.root, bg=c["bg_panel"], pady=12)
        hdr.pack(fill=tk.X)
        tk.Label(hdr, text="UNIVERSIDAD ESTATAL DE MILAGRO", font=("Times New Roman", 16, "bold"), bg=c["bg_panel"], fg=c["header_fg"]).pack()
        tk.Label(hdr, text="FACULTAD DE CIENCIAS E INGENIERÍA", font=("Times New Roman", 12, "bold"), bg=c["bg_panel"], fg=c["header_sub"]).pack(pady=(2, 0))

        # ── NOTA TÉCNICA ────────────────────
        nota = tk.Frame(self.root, bg=c["nota_bg"], highlightbackground=c["nota_border"], highlightthickness=1)
        nota.pack(fill=tk.X, padx=30, pady=8)
        
        tk.Label(nota,
                 text=("NOTA TÉCNICA: El modelo OSI se lee del 7 al 1 (Emisor) porque describe el proceso de envío desde la aplicación hasta el medio físico.\n"
                       "En el Receptor se lee del 1 al 7 para reconstruir los datos."),
                 justify=tk.CENTER, font=("Times New Roman", 11, "italic"), bg=c["nota_bg"], fg=c["text_main"]).pack(pady=6, padx=10)

        # ── PANEL DE CONTROL ────────────────
        ctrl = tk.Frame(self.root, bg=c["bg_main"])
        ctrl.pack(pady=6)

        tk.Label(ctrl, text="INSERTE SU MENSAJE:", font=("Times New Roman", 12, "bold"), bg=c["bg_main"], fg=c["text_main"]).pack(side=tk.LEFT, padx=(0, 10))

        entry_frame = tk.Frame(ctrl, bg=c["bg_main"], bd=0)
        entry_frame.pack(side=tk.LEFT, padx=10)
        
        self.entrada = tk.Entry(entry_frame, width=30, font=("Times New Roman", 13),
                                bg=c["bg_panel"], fg=c["text_main"], insertbackground=c["text_main"],
                                relief=tk.SOLID, bd=1, highlightthickness=1, highlightcolor=ACCENT_BLUE)
        self.entrada.pack(ipady=3)

        self.btn_enviar = self._boton_redondo(ctrl, "ENVIAR", self.transmitir, ACCENT_GREEN, "#ffffff", ancho=100, alto=32)
        self.btn_enviar.pack(side=tk.LEFT, padx=8)

        self.btn_reset = self._boton_redondo(ctrl, "RESET", self.resetear, c["btn_tema_bg"], c["btn_tema_fg"], ancho=90, alto=32)
        self.btn_reset.pack(side=tk.LEFT, padx=4)

        self.btn_tema = self._boton_redondo(ctrl, "TEMA", self.toggle_tema, c["btn_tema_bg"], c["btn_tema_fg"], ancho=90, alto=32)
        self.btn_tema.pack(side=tk.LEFT, padx=4)

        # ── BARRA DE ESTADO / PROGRESO ──────
        self.lbl_estado = tk.Label(self.root, text="Esperando mensaje…", font=("Times New Roman", 11, "bold"), bg=c["bg_main"], fg=c["text_dim"])
        self.lbl_estado.pack(pady=(6, 4))

        self.prog_width = 850
        self.canvas_prog = tk.Canvas(self.root, width=self.prog_width, height=8, bg=c["layer_idle"], highlightthickness=0)
        self.canvas_prog.pack(pady=2)
        self._barra = self.canvas_prog.create_rectangle(0, 0, 0, 8, fill=ACCENT_BLUE, width=0)

        # ── CONTENEDOR PRINCIPAL ─────────────
        main = tk.Frame(self.root, bg=c["bg_main"])
        main.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, weight=0)
        main.columnconfigure(2, weight=1)

        self.frame_a, self.canvas_a, self.consola_a, self.rects_a = self._crear_terminal(main, col=0, titulo="PC-A · EMISOR", subtitulo="Encapsulamiento (Capas 7 → 1)", color_titulo=ACCENT_GREEN, lado="A")
        self._crear_canal(main, col=1)
        self.frame_b, self.canvas_b, self.consola_b, self.rects_b = self._crear_terminal(main, col=2, titulo="PC-B · RECEPTOR", subtitulo="Desencapsulamiento (Capas 1 → 7)", color_titulo=ACCENT_BLUE, lado="B")

    def _crear_terminal(self, parent, col, titulo, subtitulo, color_titulo, lado):
        c = TEMAS[self.tema_actual]
        frame = tk.Frame(parent, bg=c["bg_panel"], highlightbackground=c["nota_border"], highlightthickness=1)
        frame.grid(row=0, column=col, sticky="nsew", padx=8)

        tk.Label(frame, text=titulo, font=("Times New Roman", 13, "bold"), bg=c["bg_panel"], fg=color_titulo).pack(pady=(10, 0))
        tk.Label(frame, text=subtitulo, font=("Times New Roman", 10, "italic"), bg=c["bg_panel"], fg=c["text_dim"]).pack()

        canvas = tk.Canvas(frame, width=420, height=85, bg=c["bg_panel"], highlightthickness=0)
        canvas.pack(pady=8)

        rects = self._dibujar_capas(canvas, lado)

        consola_frame = tk.Frame(frame, bg=c["console_bg"], bd=0)
        consola_frame.pack(padx=12, pady=(0, 12), fill=tk.BOTH, expand=True)
        
        fg_color = c["console_fg_a"] if lado == "A" else c["console_fg_b"]
        
        txt = tk.Text(consola_frame, width=48, height=14, bg=c["console_bg"], fg=fg_color, font=("Times New Roman", 10, "bold"), relief=tk.FLAT, bd=6, insertbackground=c["text_main"], state=tk.DISABLED)
        txt.pack(fill=tk.BOTH, expand=True)

        return frame, canvas, txt, rects

    def _dibujar_capas(self, canvas, lado):
        c = TEMAS[self.tema_actual]
        rects = []
        capas = CAPAS if lado == "A" else list(reversed(CAPAS))
        for i, (num, abrev, nombre) in enumerate(capas):
            x0 = 12 + i * 57
            x1 = x0 + 52
            r = canvas.create_rectangle(x0, 10, x1, 75, fill=c["layer_idle"], outline=c["nota_border"], width=1)
            canvas.create_text(x0 + 26, 33, text=abrev, font=("Times New Roman", 9, "bold"), fill=c["text_main"])
            canvas.create_text(x0 + 26, 53, text=f"C{num}", font=("Times New Roman", 8), fill=c["text_dim"])
            rects.append(r)
        return rects

    def _crear_canal(self, parent, col):
        c = TEMAS[self.tema_actual]
        frame = tk.Frame(parent, bg=c["bg_main"])
        frame.grid(row=0, column=col, padx=10, sticky="ns")

        tk.Label(frame, text="CANAL", font=("Times New Roman", 11, "bold"), bg=c["bg_main"], fg=c["text_dim"]).pack(pady=(45, 5))

        self.canvas_canal = tk.Canvas(frame, width=60, height=85, bg=c["bg_main"], highlightthickness=0)
        self.canvas_canal.pack()
        self.flecha = self.canvas_canal.create_line(30, 5, 30, 80, arrow=tk.LAST, width=3, fill=c["canvas_flecha"])

        tk.Label(frame, text="M/M/1", font=("Times New Roman", 10, "bold"), bg=c["bg_main"], fg=c["text_dim"]).pack(pady=5)

    def toggle_tema(self):
        if self._en_ejecucion:
            messagebox.showwarning("Simulación Activa", "Espera a que termine la transmisión para cambiar el tema.")
            return

        mensaje_guardado = self.entrada.get()
        self.tema_actual = "oscuro" if self.tema_actual == "claro" else "claro"

        for widget in self.root.winfo_children():
            widget.destroy()

        self._construir_ui()

        if mensaje_guardado:
            self.entrada.insert(0, mensaje_guardado)

    def _log(self, widget: tk.Text, msg: str):
        widget.configure(state=tk.NORMAL)
        widget.insert(tk.END, msg + "\n")
        widget.see(tk.END)
        widget.configure(state=tk.DISABLED)
        self.root.update_idletasks()

    def log_a(self, msg): self._log(self.consola_a, msg)
    def log_b(self, msg): self._log(self.consola_b, msg)

    def _actualizar_progreso(self, paso: int, total: int):
        ancho = int(self.prog_width * (paso / (total - 1))) if total > 1 else self.prog_width
        self.canvas_prog.coords(self._barra, 0, 0, ancho, 8)
        self.root.update_idletasks()

    def resetear(self):
        if self._en_ejecucion: return
        c = TEMAS[self.tema_actual]

        for txt in (self.consola_a, self.consola_b):
            txt.configure(state=tk.NORMAL)
            txt.delete("1.0", tk.END)
            txt.configure(state=tk.DISABLED)

        for r in self.rects_a: self.canvas_a.itemconfig(r, fill=c["layer_idle"], outline=c["nota_border"])
        for r in self.rects_b: self.canvas_b.itemconfig(r, fill=c["layer_idle"], outline=c["nota_border"])

        self.canvas_canal.itemconfig(self.flecha, fill=c["canvas_flecha"])
        self.canvas_prog.coords(self._barra, 0, 0, 0, 8)
        self.lbl_estado.config(text="Esperando mensaje…", fg=c["text_dim"])
        self.btn_enviar.set_estado(True)
        self.root.update_idletasks()

    def transmitir(self):
        if self._en_ejecucion: return
        msg = self.entrada.get().strip()
        if not msg:
            messagebox.showwarning("Sin mensaje", "Por favor inserta un mensaje antes de enviar.")
            return

        self.resetear()
        self._en_ejecucion = True
        c = TEMAS[self.tema_actual]
        self.btn_enviar.set_estado(False, bg_alternativo=c["layer_idle"])

        pasos = self._construir_pasos(msg)
        self._ejecutar_paso(pasos, 0, len(pasos))

    def _construir_pasos(self, msg: str):
        pasos = []
        data_ref = [msg]

        for i in range(7):
            idx, layer_num, pdu_name = i, 7 - i, PDU_NOMBRES[i]
            def paso_a(i=idx, ln=layer_num, pdu=pdu_name):
                self.canvas_a.itemconfig(self.rects_a[i], fill=LAYER_ACTIVE)
                wq = random.expovariate(3.0)
                self.log_a(f"  Capa {ln} ({CAPAS[i][2]})")
                self.log_a(f"    PDU      : {pdu}")
                self.log_a(f"    Header   : H{ln}_{random.randint(100,999)}")
                self.log_a(f"    Wq (M/M/1): {wq:.4f} s")
                if i == 1:
                    try:
                        data_ref[0] = base64.b64encode(data_ref[0].encode("utf-8")).decode("utf-8")
                        self.log_a(f"    [B64]    : {data_ref[0][:30]}…")
                    except Exception as e:
                        self.log_a(f"    [ERROR cifrado]: {e}")
                self.log_a("")
            def fin_a(i=idx): self.canvas_a.itemconfig(self.rects_a[i], fill=LAYER_DONE_A)
            pasos.extend([paso_a, fin_a])

        def paso_canal_start():
            self.canvas_canal.itemconfig(self.flecha, fill=ACCENT_GOLD)
            self.log_a("*" * 40)
            self.log_a("  [CANAL] Programación física en curso…")
            self.log_a("*" * 40)
            self.lbl_estado.config(text="Transmitiendo por el canal físico…", fg=ACCENT_GOLD)

        def paso_canal_end():
            self.canvas_canal.itemconfig(self.flecha, fill=ACCENT_GREEN)
            self.log_b("*" * 40)
            self.log_b("  [CANAL] Trama de bits recibida correctamente.")
            self.log_b("*" * 40 + "\n")

        pasos.extend([paso_canal_start, None, paso_canal_end])

        for i in range(7):
            idx, layer_num, pdu_name, rect_idx = i, i + 1, PDU_NOMBRES[6 - i], i  # CORREGIDO: rect_idx ahora sigue el orden ascendente (i)
            def paso_b(i=idx, ln=layer_num, pdu=pdu_name, ri=rect_idx):
                self.canvas_b.itemconfig(self.rects_b[ri], fill=LAYER_ACTIVE)
                wq = random.uniform(0.01, 0.10)
                self.log_b(f"  Capa {ln} ({CAPAS[6-i][2]})")
                self.log_b(f"    PDU      : {pdu}")
                self.log_b(f"    Trailer  : T{ln}_{random.randint(100,999)}")
                self.log_b(f"    Wq (M/M/1): {wq:.4f} s")
                if i == 5:
                    try:
                        data_ref[0] = base64.b64decode(data_ref[0].encode("utf-8")).decode("utf-8")
                        self.log_b(f"    [B64 dec]: {data_ref[0]}")
                    except Exception as e:
                        self.log_b(f"    [ERROR descifrado]: {e}")
                self.log_b("")
            def fin_b(ri=rect_idx): self.canvas_b.itemconfig(self.rects_b[ri], fill=LAYER_DONE_B)
            pasos.extend([paso_b, fin_b])

        def resultado():
            sep = "*" * 42
            self.log_b(sep)
            self.log_b("  TRANSMISIÓN EXITOSA")
            self.log_b(f"  Mensaje recibido: «{data_ref[0]}»")
            self.log_b(sep)
            self.lbl_estado.config(text=f"Mensaje entregado: «{data_ref[0]}»", fg=ACCENT_GREEN)
            self._en_ejecucion = False
            self.btn_enviar.set_estado(True)
        pasos.append(resultado)

        return pasos

    def _ejecutar_paso(self, pasos: list, idx: int, total: int):
        if idx >= len(pasos): return
        paso = pasos[idx]
        self._actualizar_progreso(idx, total)
        self.lbl_estado.config(text=f"Procesando paso {idx + 1} / {total} …", fg=ACCENT_GOLD)
        if paso is not None: paso()
        delay = 180 if paso is not None else 900
        self.root.after(delay, lambda: self._ejecutar_paso(pasos, idx + 1, total))

if __name__ == "__main__":
    root = tk.Tk()
    app = SimuladorOSI(root)
    root.mainloop()