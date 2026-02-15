# ClockSolitaire

Este proyecto es una implementación en Python del juego de cartas "Clock Solitaire" (también conocido como "Clock Patience"). La versión incluida usa Pygame para la interfaz y está pensada como un proyecto didáctico y jugable escrito completamente en Python.

## ¿Qué es Clock Solitaire?

Clock Solitaire es un juego de paciencia para un solo jugador basado en 13 pilas (12 alrededor de un reloj y 1 en el centro). Se muestran cartas siguiendo reglas del juego hasta que se revelen todas o se alcance una condición de fin.

## Propósito del proyecto

- Implementar la lógica del juego de forma clara y testeable en Python.
- Proveer una interfaz simple con Pygame para jugar y visualizar el estado del juego.
- Servir como ejemplo educativo de programación de juegos en Python, manejo de eventos y animaciones sencillas.

## Tecnologías

- Python 3.8+ (u 3.x compatible)
- Pygame para la interfaz gráfica

Si aún no tienes Pygame, instálalo con:

```bash
pip install pygame
```

O usando un archivo `requirements.txt` (recomendado):

```bash
pip install -r requirements.txt
```

## Archivos importantes

- La implementación principal del juego se encuentra en: [ClockSolitaire/baraja.py](ClockSolitaire/baraja.py)
- Recursos (imágenes, audio) se cargan desde la carpeta `recursos` y `img` dentro del repositorio.

## Cómo ejecutar

1. Crea y activa un entorno virtual (opcional pero recomendado):

```bash
python -m venv venv
venv\Scripts\activate    # Windows
source venv/bin/activate # macOS / Linux
```

2. Instala dependencias:

```bash
pip install pygame
```

3. Ejecuta el juego:

```bash
python baraja.py
```

Nota: ejecuta los comandos desde la carpeta `ClockSolitaire`.

## Funcionalidades incluidas

- Barajado y reparto de la baraja en las 13 pilas.
- Animaciones y efectos básicos durante el reparto y mezcla.
- Interacción con el mouse: voltear cartas, arrastrar y soltar (según implementaciones en `baraja.py`).
- Reproducción de audio (si el sistema soporta Pygame mixer y los archivos están presentes).

## Estructura del proyecto

- `baraja.py` — lógica y UI principal (Pygame).
- `recursos/` — imágenes y audios usados por el juego.
- `img/` — imágenes de cartas (nombre de archivo usado para derivar valores).
