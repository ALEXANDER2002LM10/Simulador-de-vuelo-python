# Simulador Aéreo Interactivo — UNEMI 2026

Este repositorio contiene un **Simulador de Navegación Aérea Interactivo** desarrollado en Python utilizando la librería gráfica **Tkinter**. El proyecto fue diseñado como parte del Trabajo Práctico Experimental 2 para la asignatura de **Interacción Humano-Computador (IHC)** en la Universidad Estatal de Milagro (UNEMI).

El objetivo fundamental de esta aplicación es validar empíricamente las primitivas de interacción gráfica y la implementación de metáforas visuales, comparando la eficiencia de trayectorias automáticas automatizadas frente al control manual directo por parte del usuario.

---

## Características Principales

* ** Metáfora Global de Transporte:** Interfaz diseñada con una estética de modo oscuro por defecto (`#020617` y `#020203`) que emula un entorno de radar aeronáutico real, reduciendo la fatiga visual y disminuyendo la curva de aprendizaje del usuario.
* ** Planificación de Vuelos Automáticos:** Permite seleccionar y agregar múltiples países a un plan de vuelo dinámico. El sistema calcula las rutas en tiempo real mostrando un efecto visual de resplandor neón en el lienzo (`Canvas`). Tras finalizar un vuelo, el nuevo destino se inicia desde la ubicación actual para evitar secuencias de retorno repetitivas.
* ** Vuelo Libre / Modo Manual:** Control directo de la primitiva del avión (diseño estilo Jet de 12 vértices) mediante dos modalidades:
  * **Teclado:** Desplazamiento preciso y rotación angular automática usando las teclas `W` (Arriba), `S` (Abajo), `A` (Izquierda) y `D` (Derecha).
  * **Ratón (Drag & Drop):** Primitiva de arrastre interactivo vinculada mediante el evento `<B1-Motion>`.
* ** Panel de Telemetría Avanzado:** Monitoreo en tiempo real que calcula:
  * Distancia geodésica acumulada en kilómetros utilizando la **Fórmula de Haversine** basada en latitudes y longitudes reales.
  * Tiempo estimado de vuelo (calculado a una velocidad de crucero simulada de 850 km/h).
  * Historial y registro acumulado de los segmentos de vuelo completados.

---

##  Requisitos del Sistema e Instalación

Para ejecutar el simulador en tu entorno local, asegúrate de contar con los siguientes elementos:

1. **Python 3.x** instalado en tu sistema. Puedes descargarlo desde [python.org](https://www.python.org/).
2. **Librería Pillow:** Necesaria para el procesamiento y escalado dinámico del mapa base. Instalable desde la terminal con el comando:
   ```bash
   pip install Pillow
   
### Estructura de Archivos Obligatoria

Para el correcto funcionamiento del simulador, los archivos deben coexistir en el mismo directorio con la siguiente estructura (empleando rutas relativas dinámicas gestionadas por el módulo `os`):

├── simulador_de_posicionamiento_aereo.py   # Código fuente principal

└── edited-image.png.png                    # Imagen de fondo (Mapa base mundial)

---

### Instrucciones de Ejecución

1. Clona este repositorio o descarga los archivos en una carpeta local:
   ```bash
   git clone [https://github.com/ALEXANDER2002LM10/Simulador-de-vuelo-python.git](https://github.com/ALEXANDER2002LM10/Simulador-de-vuelo-python.git)
2. Abre una terminal dentro del directorio del proyecto.

3. Ejecuta el script principal de Python:
   ```bash
   python simulador_de_posicionamiento_aereo.py
