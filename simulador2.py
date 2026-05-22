import tkinter as tk
from tkinter import ttk
import math
import os
import PIL.Image # type: ignore
import PIL.ImageTk # type: ignore

# 🎨 COLORES
COLOR_FONDO = "#020617"
COLOR_PANEL = "#020203"
COLOR_GRID = "#1e293b"
COLOR_RUTA = "#00f5ff"
COLOR_PUNTO = "#ffcc00"
COLOR_TEXTO = "#ffffff"
COLOR_AUTO = "#ff2d55"
COLOR_MANUAL = "#22c55e"

class SimuladorMapa:

    def __init__(self, root):
        self.root = root
        self.root.title("🚀 Simulador Aéreo Interactivo - UNEMI 2026")
        self.root.geometry("1300x600")
        self.root.configure(bg=COLOR_FONDO)

        # --- ESTRUCTURA DE LA INTERFAZ ---
        self.map_frame = tk.Frame(root, bg=COLOR_FONDO, width=1000, height=600)
        self.map_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)

        self.panel_stats = tk.Frame(root, bg=COLOR_PANEL, width=300, height=600, bd=0)
        self.panel_stats.pack(side=tk.RIGHT, fill=tk.Y)
        self.panel_stats.pack_propagate(False) 
        
        # --- CONFIGURACIÓN DEL MAPA ---
        # Obtiene la ruta exacta de la carpeta donde está este script
        directorio_actual = os.path.dirname(os.path.abspath(__file__))
        # Une la ruta de la carpeta con el nombre de la imagen
        ruta_imagen = os.path.join(directorio_actual, "edited-image.png.png")

        if os.path.exists(ruta_imagen):
            img = PIL.Image.open(ruta_imagen).resize((1000, 600))
        else:
            print("⚠️ No se encontró la imagen. Usando fondo por defecto.")
            img = PIL.Image.new("RGB", (1000, 600), COLOR_FONDO)

        self.bg = PIL.ImageTk.PhotoImage(img)

        self.canvas = tk.Canvas(self.map_frame, width=1000, height=600, bg=COLOR_FONDO, highlightthickness=0)
        self.canvas.pack()
        self.canvas.create_image(0, 0, anchor="nw", image=self.bg)

        self.dibujar_cuadricula()

        # 🌍 Países: (Pos_X, Pos_Y, Latitud_Real, Longitud_Real)
        self.paises = {
            "Portugal": (100, 160, 39.39, -8.22),
            "Rusia": (360, 80, 61.52, 105.31),
            "Japón": (460, 170, 36.20, 138.25),
            "China": (370, 180, 35.86, 104.19),
            "Australia": (450, 400, -25.27, 133.77),
            "Estados Unidos": (780, 180, 37.09, -95.71),
            "Canadá": (750, 110, 56.13, -106.34),
            "Ecuador": (860, 300, -1.83, -78.18),
            "Angola": (140, 340, -11.20, 17.87),
            "Argentina": (870, 440, -38.41, -63.61),
            "Arabia Saudí": (220, 220, 23.88, 45.07),
            "México": (800, 230, 23.63, -102.55),
            "Ucrania": (200, 120, 48.37, 31.16),
            "Brasil": (930, 340, -14.23, -51.92)
        }

        self.dibujar_paises()

        # ✈ Aviones (Inician en la primera opción por defecto)
        x, y, _, _ = self.paises["Portugal"]
        self.manual_x, self.manual_y = x + 30, y + 30
        self.manual_angulo = -math.pi / 2 

        self.avion_auto = self.crear_avion(x, y, COLOR_AUTO)
        self.avion_manual = self.crear_avion(self.manual_x, self.manual_y, COLOR_MANUAL)

        # 📊 Variables de Vuelo y Rutas
        self.ruta_personalizada = []
        self.ruta_actual = []
        self.historial_vuelos = [] 
        
        self.idx_ruta = 0
        self.tick_animacion = 0
        self.angulo_auto = 0
        
        # Estadísticas Reales (Haversine)
        self.dist_total_real = 0.0
        self.tiempo_total_real = 0.0
        self.dist_segmento_real = 0.0
        self.tiempo_segmento_real = 0.0

        # Variables Manual
        self.dist_total_manual = 0
        self.last_manual_pos = (self.manual_x, self.manual_y)
        self.dragging = False
        self.offset_x = 0
        self.offset_y = 0

        # Cargar elementos del panel
        self.crear_elementos_panel()

        # 🎮 Controles Manuales
        root.bind("<w>", self.mover_manual)
        root.bind("<s>", self.mover_manual)
        root.bind("<a>", self.mover_manual)
        root.bind("<d>", self.mover_manual)

        self.canvas.tag_bind(self.avion_manual, "<ButtonPress-1>", self.start_drag)
        self.canvas.tag_bind(self.avion_manual, "<B1-Motion>", self.drag)
        self.canvas.tag_bind(self.avion_manual, "<ButtonRelease-1>", self.stop_drag)

    def crear_elementos_panel(self):
        contenedor = tk.Frame(self.panel_stats, bg=COLOR_PANEL, padx=15, pady=15)
        contenedor.pack(fill="both", expand=True)

        tk.Label(contenedor, text="🛰️ PANEL DE VUELO", fg=COLOR_RUTA, bg=COLOR_PANEL, 
                 font=("Times new roman", 14, "bold")).pack(pady=(0,10))

        # --- SECCIÓN CREADOR DE RUTAS ---
        frame_ruta = tk.Frame(contenedor, bg=COLOR_PANEL)
        frame_ruta.pack(fill="x", pady=5)
        
        tk.Label(frame_ruta, text="1. Plan de Vuelo:", fg="white", bg=COLOR_PANEL, font=("times new roman", 9, "bold")).pack(anchor="w")
        
        self.combo_paises = ttk.Combobox(frame_ruta, values=list(self.paises.keys()), state="readonly")
        self.combo_paises.set("Seleccionar país...")
        self.combo_paises.pack(fill="x", pady=5)

        frame_btns = tk.Frame(frame_ruta, bg=COLOR_PANEL)
        frame_btns.pack(fill="x")
        tk.Button(frame_btns, text="➕ Agregar", bg="#4eb910", fg="white", font=("times new roman", 8, "bold"),
                  command=self.agregar_a_ruta).pack(side=tk.LEFT, expand=True, fill="x", padx=(0,2))
        tk.Button(frame_btns, text="🗑 Limpiar", bg="#44b9ef", fg="white", font=("times new roman", 8, "bold"),
                  command=self.limpiar_ruta).pack(side=tk.RIGHT, expand=True, fill="x", padx=(2,0))

        self.label_ruta_visual = tk.Label(contenedor, text="Ruta: [Vacía]", fg="#94a3b8", bg=COLOR_PANEL, 
                                          font=("times new roman", 8), wraplength=250, justify="left")
        self.label_ruta_visual.pack(fill="x", pady=5)

# --- BOTÓN INICIAR ---
        self.btn_iniciar = tk.Button(contenedor, text="▶ Iniciar Vuelo", bg="#2563eb", fg="white", 
                                     disabledforeground="white", # <-- Mantiene el texto blanco al estar desactivado
                                     font=("Times new roman", 11, "bold"), cursor="hand2", command=self.iniciar_vuelo, state="disabled")
        self.btn_iniciar.pack(fill="x", pady=(10, 15))

        # --- ESTADÍSTICAS ---
        self.label_auto = tk.Label(contenedor, text="✈ ESTADO EN VIVO\n\nEsperando inicio...", 
                                   fg="white", bg=COLOR_PANEL, font=("Times new roman", 9), justify="left")
        self.label_auto.pack(fill="x", anchor="w", pady=(0, 10))

        # Etiqueta para las estadísticas del avión manual
        self.label_manual = tk.Label(contenedor, text="🟢 VUELO LIBRE (Manual)\n\n ├ Distancia: 0 km", 
                                     fg=COLOR_MANUAL, bg=COLOR_PANEL, font=("Times new roman", 9, "bold"), justify="left")
        self.label_manual.pack(fill="x", anchor="w")

       #NUEVO: Botón para reiniciar el vuelo manual
        self.btn_reset_manual = tk.Button(contenedor, text="🔄 Reiniciar Vuelo Manual", bg="#16a34a", fg="white", 
                                          font=("Times new roman", 9, "bold"), cursor="hand2", command=self.reiniciar_manual)
        self.btn_reset_manual.pack(fill="x", pady=(5, 0))

        # Línea divisoria
        tk.Frame(contenedor, height=1, bg="#334155").pack(fill="x", pady=10)

        # Historial de vuelos
        self.label_historial = tk.Label(contenedor, text="📋 REGISTRO DE VUELO\n\nSin datos aún.", 
                                   fg="#94a3b8", bg=COLOR_PANEL, font=("Times new roman", 11), justify="left")
        self.label_historial.pack(fill="x", anchor="w")

    # --- MATEMÁTICAS GEOGRÁFICAS ---
    def calcular_distancia_real(self, lat1, lon1, lat2, lon2):
        R = 6371.0 
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def formato_tiempo(self, horas_decimales):
        h = int(horas_decimales)
        m = int((horas_decimales - h) * 60)
        return f"{h}h {m}m"

    # --- LÓGICA DE RUTA ---
    def agregar_a_ruta(self):
        pais = self.combo_paises.get()
        if pais in self.paises:
            if len(self.ruta_personalizada) == 0 or self.ruta_personalizada[-1] != pais:
                self.ruta_personalizada.append(pais)
                self.actualizar_ui_ruta()

    def limpiar_ruta(self):
        self.ruta_personalizada = []
        self.ruta_actual = []
        self.idx_ruta = 0  # <--- Reseteamos la "memoria" del vuelo
        self.canvas.delete("ruta_linea") # <--- Borramos las líneas dibujadas
        self.actualizar_ui_ruta()

    def actualizar_ui_ruta(self):
        if len(self.ruta_personalizada) > 0:
            texto = " ➔ ".join(self.ruta_personalizada)
            self.label_ruta_visual.config(text=f"Ruta: {texto}", fg="#00f5ff")
        else:
            self.label_ruta_visual.config(text="Ruta: [Vacía]", fg="#94a3b8")

        if len(self.ruta_personalizada) >= 2:
            self.btn_iniciar.config(state="normal")
        else:
            self.btn_iniciar.config(state="disabled")

    # --- LÓGICA DE VUELO AUTOMÁTICO ---
    def iniciar_vuelo(self):
        self.btn_iniciar.config(state="disabled", bg="#475569", text="⏳ Volando...")
        
        # Verificamos si es un vuelo nuevo (idx_ruta == 0) o si estamos continuando
        if self.idx_ruta == 0 or len(self.ruta_actual) == 0:
            # --- INICIO DESDE CERO ---
            self.ruta_actual = list(self.ruta_personalizada)
            self.dist_total_real = 0.0
            self.tiempo_total_real = 0.0
            self.historial_vuelos = [] 
            self.label_historial.config(text="📋 REGISTRO DE VUELO\n")
            
            x_ini, y_ini, _, _ = self.paises[self.ruta_actual[0]]
            self.canvas.coords(self.avion_auto, *self.rotar_poligono(x_ini, y_ini, -math.pi/2))
            self.canvas.delete("ruta_linea")
        else:
            # --- CONTINUAR VUELO ---
            self.ruta_actual = list(self.ruta_personalizada)
            # NO reseteamos las distancias ni el historial. El avión ya está en su última posición.

        self.tick_animacion = 0
        self.animar_vuelo()

    def animar_vuelo(self):
        if self.idx_ruta >= len(self.ruta_actual) - 1:
            self.btn_iniciar.config(state="normal", bg="#2563eb", text="▶ Continuar Vuelo") # <--- Cambio de texto
            self.label_auto.config(text="✈ ESTADO EN VIVO\n\n✅ ESPERANDO NUEVO DESTINO...")
            return

        o = self.ruta_actual[self.idx_ruta]
        d = self.ruta_actual[self.idx_ruta + 1]
        x1, y1, lat1, lon1 = self.paises[o]
        x2, y2, lat2, lon2 = self.paises[d]

        if self.tick_animacion == 0:
         # 🌟 Efecto Neón/Resplandor para la ruta
            self.canvas.create_line(x1, y1, x2, y2, fill="#0284c7", width=6, tags="ruta_linea") # Resplandor azul oscuro
            self.canvas.create_line(x1, y1, x2, y2, fill="#00ffff", width=2, dash=(10, 5), tags="ruta_linea") # Centro brillante
            
            self.angulo_auto = math.atan2(y2 - y1, x2 - x1)
            self.dist_segmento_real = self.calcular_distancia_real(lat1, lon1, lat2, lon2)
            self.tiempo_segmento_real = self.dist_segmento_real / 850.0

        t = self.tick_animacion
        nx = x1 + (x2 - x1) * t / 100
        ny = y1 + (y2 - y1) * t / 100

        coords = self.rotar_poligono(nx, ny, self.angulo_auto)
        self.canvas.coords(self.avion_auto, *coords)

        avance_dist = self.dist_segmento_real * (t / 100)
        avance_tiempo = self.tiempo_segmento_real * (t / 100)

        dist_global_actual = self.dist_total_real + avance_dist
        tiempo_global_actual = self.tiempo_total_real + avance_tiempo

        texto_stats = (
            f"✈ VUELO SIMULADO\n\n"
            f"📍 {o} → {d}\n"
            f" ├ Progreso: {avance_dist:.0f} km\n"
            f" └ Tpo Est.: {self.formato_tiempo(avance_tiempo)}\n\n"
            f"🌍 GLOBAL (Acumulado)\n"
            f" ├ Distancia: {dist_global_actual:.0f} km\n"
            f" └ Tpo Vuelo: {self.formato_tiempo(tiempo_global_actual)}"
        )
        self.label_auto.config(text=texto_stats)

        self.tick_animacion += 1

        if self.tick_animacion <= 100:
            self.root.after(30, self.animar_vuelo)
        else:
            self.dist_total_real += self.dist_segmento_real
            self.tiempo_total_real += self.tiempo_segmento_real
            
            registro = f"✅ {o[:3].upper()} ➔ {d[:3].upper()}: {self.dist_segmento_real:.0f}km | {self.formato_tiempo(self.tiempo_segmento_real)}"
            self.historial_vuelos.append(registro)
            
            texto_historial = "📋 REGISTRO DE VUELO\n\n" + "\n".join(self.historial_vuelos)
            self.label_historial.config(text=texto_historial)

            self.tick_animacion = 0
            self.idx_ruta += 1
            self.root.after(30, self.animar_vuelo)

    # --- DIBUJO E INTERFAZ BASE ---
    def rotar_poligono(self, cx, cy, angulo):
        ang = angulo + math.pi / 2
        # ✈️ Nuevo diseño de avión estilo Jet
        puntos = [
            (0, -18),     # Nariz
            (3, -6),      # Fuselaje derecho
            (16, 4),      # Punta ala derecha
            (4, 6),       # Base ala derecha interior
            (2, 12),      # Cola derecha base
            (6, 16),      # Estabilizador derecho
            (0, 14),      # Centro cola
            (-6, 16),     # Estabilizador izquierdo
            (-2, 12),     # Cola izquierda base
            (-4, 6),      # Base ala izquierda interior
            (-16, 4),     # Punta ala izquierda
            (-3, -6)      # Fuselaje izquierdo
        ]
        coords = []
        for px, py in puntos:
            rx = px * math.cos(ang) - py * math.sin(ang)
            ry = px * math.sin(ang) + py * math.cos(ang)
            coords.extend([cx + rx, cy + ry])
        return coords
    def crear_avion(self, x, y, color):
        coords = self.rotar_poligono(x, y, -math.pi / 2)
        return self.canvas.create_polygon(*coords, fill=color, outline="white", width=1)

    def dibujar_cuadricula(self):
        for i in range(0, 1000, 50):
            self.canvas.create_line(i, 0, i, 600, fill=COLOR_GRID, stipple="gray50")
        for j in range(0, 600, 50):
            self.canvas.create_line(0, j, 1000, j, fill=COLOR_GRID, stipple="gray50")

    def dibujar_paises(self):
        for n, datos in self.paises.items():
            x, y = datos[0], datos[1]
            self.canvas.create_oval(x-6, y-6, x+6, y+6, fill=COLOR_PUNTO, outline="white")
            self.canvas.create_text(x, y-12, text=n, fill="white", font=("Arial", 9, "bold"))

    # --- MODO MANUAL ---
    def mover_manual(self, event):
        paso = 10
        if event.keysym == "w": 
            self.manual_y -= paso; self.manual_angulo = -math.pi/2
        if event.keysym == "s": 
            self.manual_y += paso; self.manual_angulo = math.pi/2
        if event.keysym == "a": 
            self.manual_x -= paso; self.manual_angulo = math.pi
        if event.keysym == "d": 
            self.manual_x += paso; self.manual_angulo = 0

        coords = self.rotar_poligono(self.manual_x, self.manual_y, self.manual_angulo)
        self.canvas.coords(self.avion_manual, *coords)
        self.actualizar_manual()

    def start_drag(self, event):
        self.dragging = True
        self.offset_x = event.x - self.manual_x
        self.offset_y = event.y - self.manual_y

    def drag(self, event):
        if not self.dragging: return
        self.manual_x = event.x - self.offset_x
        self.manual_y = event.y - self.offset_y

        coords = self.rotar_poligono(self.manual_x, self.manual_y, self.manual_angulo)
        self.canvas.coords(self.avion_manual, *coords)
        self.actualizar_manual()

    def stop_drag(self, event):
        self.dragging = False
        
    def actualizar_manual(self):
        lx, ly = self.last_manual_pos
        dist = math.sqrt((self.manual_x - lx)**2 + (self.manual_y - ly)**2) * 30.0 
        self.dist_total_manual += dist
        self.last_manual_pos = (self.manual_x, self.manual_y)

        # Actualiza el texto en el panel en tiempo real
        texto_manual = f"🟢 VUELO LIBRE (Manual)\n\n ├ Distancia: {self.dist_total_manual:.0f} km"
        self.label_manual.config(text=texto_manual)

    def reiniciar_manual(self):
        # 1. Obtenemos las coordenadas iniciales (cerca de Portugal)
        x, y, _, _ = self.paises["Portugal"]
        self.manual_x, self.manual_y = x + 30, y + 30
        self.manual_angulo = -math.pi / 2 
        
        # 2. Reseteamos la distancia y la última posición
        self.dist_total_manual = 0
        self.last_manual_pos = (self.manual_x, self.manual_y)
        
        # 3. Movemos el avión verde de regreso en el mapa
        coords = self.rotar_poligono(self.manual_x, self.manual_y, self.manual_angulo)
        self.canvas.coords(self.avion_manual, *coords)
        
        # 4. Actualizamos el texto en el panel
        self.label_manual.config(text="🟢 VUELO LIBRE (Manual)\n\n ├ Distancia: 0 km")

# 🚀 RUN
if __name__ == "__main__":
    root = tk.Tk()
    app = SimuladorMapa(root)
    root.mainloop()