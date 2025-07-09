import pygame
import os
import random

# Inicializar Pygame
pygame.init()

# Configuración general
WIDTH, HEIGHT = 1200, 800  # Pantalla más grande
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simulación de Baraja")

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
LIGHT_GRAY = (200, 200, 200)

# Dimensiones
CARD_WIDTH, CARD_HEIGHT = 100, 150
BUTTON_WIDTH, BUTTON_HEIGHT = 120, 40

CARD_OFFSET_H = 20  # Desplazamiento horizontal para el efecto escalerita
CARD_OFFSET_V = 2   # Desplazamiento vertical para el mazo

# Posiciones ajustadas de las cartas en la mesa (más separadas)
posiciones = [
    (WIDTH // 2 - 350, 80),    # [1]
    (WIDTH // 2 - 150, 80),    # [2]
    (WIDTH // 2 + 50, 80),     # [3]
    (WIDTH // 2 + 250, 80),    # [4]
    (WIDTH // 2 + 250, 240),    # [5]
    (WIDTH // 2 + 250, 400),    # [6]
    (WIDTH // 2 + 250, 560),    # [7]
    (WIDTH // 2 + 50, 560),     # [8]
    (WIDTH // 2 - 150, 560),    # [9]
    (WIDTH // 2 - 350, 560),    # [10]
    (WIDTH // 2 - 350, 400),    # [11]
    (WIDTH // 2 - 350, 240),    # [12]
    (WIDTH // 2 - 40, 325),    # [13]
]

class Carta:
    def __init__(self, imagen_frontal, imagen_reverso, nombre_archivo):
        self.imagen_frontal = imagen_frontal
        self.imagen_reverso = imagen_reverso
        self.nombre_archivo = nombre_archivo
        self.rect = imagen_frontal.get_rect()
        
    def obtener_valor(self):
        # Obtener el valor del inicio del nombre del archivo
        nombre = self.nombre_archivo.lower()  # Convertir a minúsculas para manejar mejor
        
        # Manejar casos especiales primero
        if nombre.startswith('a'):
            return 1
        elif nombre.startswith('j'):
            return 11
        elif nombre.startswith('q'):
            return 12
        elif nombre.startswith('k'):
            return 13
        else:
            # Para números del 2-10, tomar los dígitos del inicio
            valor = ''
            for char in nombre:
                if char.isdigit():
                    valor += char
                else:
                    break
            return int(valor) if valor else 0

    def obtener_siguiente_posicion(self, carta):
        # Usar el nombre del archivo para determinar el valor
        valor = carta.obtener_valor()
        if valor == 13:  # K
            return 12  # índice 12 corresponde a posición 13 (centro)
        return valor - 1  # índice 0-11 corresponde a posiciones 1-12
        
class Boton:
    def __init__(self, x, y, width, height, imagen_path):
        self.rect = pygame.Rect(x, y, width, height)
        self.imagen = pygame.image.load(os.path.join("recursos", imagen_path))
        self.imagen = pygame.transform.scale(self.imagen, (width, height))
        self.imagen_inactiva = self.imagen.copy()  # Crear copia para versión inactiva
        # Hacer la imagen inactiva más oscura
        self.imagen_inactiva.fill((128, 128, 128), special_flags=pygame.BLEND_MULT)
        self.activo = True
        
    def draw(self, surface):
        # Usar imagen normal o inactiva según el estado
        imagen_actual = self.imagen if self.activo else self.imagen_inactiva
        surface.blit(imagen_actual, self.rect)


class Juego:
    def __init__(self):
        # Atributos para la animación
        self.animando_mezcla = False
        self.tiempo_animacion = 0
        self.duracion_animacion = 1000
        self.cartas_mezcladas = []
        self.grupos_mezcla = []
        self.carta_actual = None
        self.pos_central = (WIDTH // 2 - 100, HEIGHT // 2 - 100)  # Más arriba y a la izquierda
        self.pos_inicial_izq = (WIDTH // 2 - 250, HEIGHT // 2 - 100)  # Más separado a la izquierda
        self.pos_inicial_der = (WIDTH // 2 + 50, HEIGHT // 2 - 100)   # Más separado a la derecha
        self.estado_animacion = 'inicio'

        self.tiempo_reparto = 0
        # Asegurarnos de que no haya cartas fantasma
        self.animando_reparto = False
        self.carta_actual_reparto = None
        self.cartas_por_repartir = []
        self.cartas_a_repartir = []
        self.posicion_destino = None
        self.duracion_reparto_carta = 300  # milisegundos por carta

        # Cargar imágenes
        self.fondo = self.cargar_imagen(os.path.join("recursos", "fondo.png"), (WIDTH, HEIGHT))
        self.reverso_base = self.cargar_imagen(os.path.join("recursos", "reverso.png"), (CARD_WIDTH, CARD_HEIGHT))
         
        # Cargar mazo
        self.mazo = self.cargar_cartas()
        self.mazo_pos = (50, HEIGHT//2 - CARD_HEIGHT//2)
        self.cartas_por_posicion = {pos: [] for pos in posiciones}
        
        # Inicializar sistema de audio con manejo de errores
        #try:
        #    pygame.mixer.init()
            # Cargar efectos de sonido y música
        #    self.sonido_click = pygame.mixer.Sound(os.path.join("recursos", "click.mp3"))
        #    
            # Configurar y reproducir música de fondo
        #    pygame.mixer.music.load(os.path.join("recursos", "jazz.mp3"))
        #    pygame.mixer.music.set_volume(0.3)  # Volumen al 30%
        #    pygame.mixer.music.play(-1)  # -1 significa loop infinito
            
        #    self.audio_disponible = True
        #except:
        #    print("No se pudo inicializar el sistema de audio")
        #    self.audio_disponible = False
        

        # Crear botones con imágenes
        self.boton_mezclar = Boton(WIDTH-150, 100, BUTTON_WIDTH, BUTTON_HEIGHT, "btnMezclar.png")
        self.boton_repartir = Boton(WIDTH-150, 200, BUTTON_WIDTH, BUTTON_HEIGHT, "btnRepartir.png")
        self.boton_jugar = Boton(WIDTH-150, 300, BUTTON_WIDTH, BUTTON_HEIGHT, "btnJugar.png")
        self.boton_reiniciar = Boton(WIDTH-150, 400, BUTTON_WIDTH, BUTTON_HEIGHT, "btnReiniciar.png")
        
        # Estado inicial de los botones
        self.boton_jugar.activo = False
        self.boton_reiniciar.activo = False
        
        # Estado del juego
        self.cartas_mesa = []

        # Ajustar los offsets para los efectos escalerita
        self.CARD_OFFSET_H = 20  # Para los bloques horizontales
        self.CARD_OFFSET_V = 0.5  # Para el mazo vertical (mucho más sutil)

        # Variables para el juego del Reloj
        self.jugando = False
        self.carta_actual_juego = None
        self.cartas_volteadas = set()
        self.pila_actual = 12  # Empezamos en la pila central
        self.total_cartas = 52
        
        # Variables para arrastrar cartas
        self.arrastrando = False
        self.carta_arrastrada = None
        self.pos_arrastre = None
        self.pos_origen = None
        self.pos_origen_index = None

        # Cargar imágenes de respuesta
        self.img_si = self.cargar_imagen(os.path.join("recursos", "respSI.png"), (480, 300))
        self.img_no = self.cargar_imagen(os.path.join("recursos", "respNO.png"), (480, 300))
        
        # Variables para el cuadro de texto
        self.pregunta = ""
        self.mostrando_input = False
        self.font = pygame.font.Font(None, 32)
        self.input_rect = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 - 20, 400, 40)
        self.color_input_activo = pygame.Color('lightskyblue3')
        self.color_input_inactivo = pygame.Color('gray15')
        self.color_input = self.color_input_inactivo
        
        # Variable para mostrar respuesta
        self.mostrando_respuesta = False
        self.respuesta_img = None
        self.tiempo_respuesta = 0

        # Cargar imagen de pregunta
        self.img_pregunta = self.cargar_imagen(os.path.join("recursos", "pregunta.png"), (600, 200))
        
        # Cargar la fuente personalizada
        try:
            self.font = pygame.font.Font(os.path.join("recursos", "JandaEverydayCasual.ttf"), 18)
        except:
            print("No se pudo cargar la fuente personalizada, usando fuente por defecto")
            self.font = pygame.font.Font(None, 20)  # Fuente por defecto si falla la carga
        

        # Variables para el cuadro de texto
        self.pregunta = ""
        self.mostrando_input = False
        self.font = pygame.font.Font(os.path.join("recursos", "JandaEverydayCasual.ttf"), 18)
        
        # Definir el área de texto dentro de la imagen
        self.area_texto = {
            'ancho': 300,      # Ajusta según necesites
            'alto': 110,        # Ajusta según necesites
            'offset_x': 250,   # Ajusta según necesites
            'offset_y': 60     # Ajusta según necesites
        }
        self.margen_texto = 10
        self.font = pygame.font.Font(os.path.join("recursos", "JandaEverydayCasual.ttf"), 18) 

        # Cargar imagen meditando
        self.img_meditando = self.cargar_imagen(os.path.join("recursos", "meditando.png"), (150, 150))  # Ajusta el tamaño según necesites
        self.mostrar_meditando = True  # Variable para controlar cuando se muestra la imagen

        # Inicializar sistema de audio con manejo de errores
        try:
            pygame.mixer.init()
            # Cargar efectos de sonido y música
            self.sonido_click = pygame.mixer.Sound(os.path.join("recursos", "click.mp3"))
            
            # Configurar y reproducir música de fondo
            pygame.mixer.music.load(os.path.join("recursos", "jazz.mp3"))
            pygame.mixer.music.set_volume(0.3)  # Volumen al 30%
            pygame.mixer.music.play(-1)  # -1 significa loop infinito
            
            self.sonido_error = pygame.mixer.Sound(os.path.join("recursos", "error.mp3"))
            self.sonido_tomar = pygame.mixer.Sound(os.path.join("recursos", "cartaTomada.mp3"))
            self.sonido_soltar = pygame.mixer.Sound(os.path.join("recursos", "cartaSoltada.mp3"))
            self.sonido_barajar = pygame.mixer.Sound(os.path.join("recursos", "barajada.mp3"))
            self.sonido_barajar.set_volume(0.5)
            self.sonido_error.set_volume(0.5)
            
            self.audio_disponible = True
            self.barajando_sonando = False
        except:
            print("No se pudo inicializar el sistema de audio")
            self.audio_disponible = False
        
        self.duracion_reparto_carta = 100  # Originalmente era más alto, ajusta este valor según necesites

    def render_texto_multilinea(self, texto, ancho_disponible):
        lineas = []
        palabras = texto.split()
        linea_actual = []
        
        for palabra in palabras:
            # Añadir palabra de prueba
            linea_prueba = linea_actual + [palabra]
            # Obtener el ancho de la línea con la nueva palabra
            texto_prueba = ' '.join(linea_prueba)
            ancho_texto = self.font.render(texto_prueba, True, (0, 0, 0)).get_width()
            
            if ancho_texto <= ancho_disponible:
                # La palabra cabe en la línea actual
                linea_actual = linea_prueba
            else:
                # La palabra no cabe, guardar línea actual y empezar nueva línea
                if linea_actual:  # Si hay texto en la línea actual
                    lineas.append(' '.join(linea_actual))
                    linea_actual = [palabra]
                else:  # Si la palabra es más larga que el ancho disponible
                    # Dividir la palabra
                    lineas.append(palabra[:len(palabra)//2] + '-')
                    linea_actual = [palabra[len(palabra)//2:]]
        
        # Añadir la última línea si existe
        if linea_actual:
            lineas.append(' '.join(linea_actual))
            
        return lineas
    
    def __del__(self):
        try:
            if hasattr(self, 'audio_disponible') and self.audio_disponible:
                pygame.mixer.music.stop()
        except:
            pass
    
    def reiniciar_juego(self):
        self.detener_todos_sonidos()

        # Reiniciar variables del juego
        self.jugando = False
        self.mazo = self.cargar_cartas()
        self.cartas_por_posicion = {pos: [] for pos in posiciones}
        self.cartas_volteadas = set()
        self.carta_arrastrada = None
        self.arrastrando = False
        self.mostrando_respuesta = False
        self.respuesta_img = None
        self.pregunta = ""
        self.mostrando_input = False
        
        # Reiniciar estado de los botones
        self.boton_mezclar.activo = True
        self.boton_repartir.activo = True  # Ahora también activamos el botón de repartir
        self.boton_jugar.activo = False
        self.boton_reiniciar.activo = False
        
        # Reiniciar música
        pygame.mixer.music.load(os.path.join("recursos", "jazz.mp3"))
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)

        self.mostrar_meditando = True  # Mostrar meditando al reiniciar

        # Asegurarse de que todos los sonidos se detengan
        if self.audio_disponible:
            if self.barajando_sonando:
                self.sonido_barajar.stop()
                self.barajando_sonando = False
            self.sonido_tomar.stop()
            self.sonido_soltar.stop()
        
    def iniciar_juego(self):
        if not self.boton_jugar.activo:
            return
            
        self.detener_todos_sonidos()
        self.jugando = True
        self.boton_jugar.activo = False
        self.pila_actual = 12  # Empezamos en la pila central
        # No volteamos automáticamente, esperamos el click del usuario
        
    def voltear_carta_en_posicion(self, pos_index):
        if not self.jugando or pos_index != self.pila_actual:
            return  # Solo permitir voltear en la pila actual
            
        pila = self.cartas_por_posicion[posiciones[pos_index]]
        if not pila:  # Si la pila está vacía
            self.terminar_juego(False)  # Perdiste
            return
            
        carta = pila[-1]  # Tomar la carta superior
        if carta in self.cartas_volteadas:
            self.terminar_juego(False)  # Perdiste - la carta ya estaba volteada
            return
            
        # Voltear la carta
        self.carta_actual_juego = carta
        self.cartas_volteadas.add(carta)
        
        # Determinar la siguiente posición basada en el valor de la carta
        valor = (carta.valor % 13) + 1  # Convertir valor 0-51 a 1-13
        if valor == 13:  # K
            self.pila_actual = 12  # Centro
        else:
            self.pila_actual = valor - 1  # Posiciones 0-11 para valores 1-12
        
        # Verificar victoria
        if len(self.cartas_volteadas) == self.total_cartas:
            self.terminar_juego(True)
        
    def obtener_siguiente_posicion(self, carta):
        # Usar el nombre del archivo para determinar el valor
        valor = carta.obtener_valor()
        if valor == 13:  # K
            return 12  # índice 12 corresponde a posición 13 (centro)
        return valor - 1  # índice 0-11 corresponde a posiciones 1-12

    def terminar_juego(self, victoria):
        self.detener_todos_sonidos()
        self.jugando = False
        mensaje = "¡Ganaste!" if victoria else "Perdiste"
        print(mensaje)
        
        # Mostrar imagen de respuesta
        self.mostrando_respuesta = True
        self.respuesta_img = self.img_si if victoria else self.img_no
        
        # Ocultar imagen meditando cuando se muestra la respuesta
        self.mostrar_meditando = False
        
        # Activar botón de reiniciar
        self.boton_reiniciar.activo = True
        
        pygame.mixer.music.stop()
        
    def obtener_pila_clickeada(self, pos_mouse):
        # Verificar en qué pila se hizo click
        for i, pos in enumerate(posiciones):
            # Crear un rectángulo para la pila
            rect = pygame.Rect(pos[0], pos[1], CARD_WIDTH, CARD_HEIGHT)
            if rect.collidepoint(pos_mouse):
                return i
        return None
        
    def cargar_imagen(self, ruta, size=None):
        imagen = pygame.image.load(ruta).convert_alpha()
        if size:
            imagen = pygame.transform.scale(imagen, size)
        return imagen
        
    def cargar_cartas(self):
        mazo = []
        for carta in os.listdir("img"):
            if carta.endswith(".png"):
                ruta_carta = os.path.join("img", carta)
                imagen_frontal = self.cargar_imagen(ruta_carta, (CARD_WIDTH, CARD_HEIGHT))
                # Crear una copia del reverso para cada carta
                imagen_reverso = self.reverso_base.copy()
                mazo.append(Carta(imagen_frontal, imagen_reverso, carta))
        return mazo
        
    def mezclar_hojeo(self):
        if self.animando_mezcla or not self.boton_mezclar.activo:
            return
            
        self.animando_mezcla = True
        self.cartas_mezcladas = []
        self.estado_animacion = 'inicio'
        self.tiempo_animacion = 0
        
        # Desactivar botón de repartir mientras se mezcla
        self.boton_repartir.activo = False
        mazo_temp = self.mazo.copy()
        
        # Dividir el mazo en dos mitades
        mitad = len(mazo_temp) // 2
        mazo_izquierdo = mazo_temp[:mitad]
        mazo_derecho = mazo_temp[mitad:]
        
        # Crear grupos de cartas para la mezcla
        self.grupos_mezcla = []
        while mazo_izquierdo or mazo_derecho:
            if mazo_izquierdo:
                cant = random.randint(1, min(3, len(mazo_izquierdo)))
                cartas = mazo_izquierdo[:cant]
                del mazo_izquierdo[:cant]
                for carta in cartas:
                    self.grupos_mezcla.append({
                        'carta': carta,
                        'lado': 'izquierda',
                        'pos_actual': self.pos_inicial_izq,
                        'progreso': 0
                    })
            
            if mazo_derecho:
                cant = random.randint(1, min(3, len(mazo_derecho)))
                cartas = mazo_derecho[:cant]
                del mazo_derecho[:cant]
                for carta in cartas:
                    self.grupos_mezcla.append({
                        'carta': carta,
                        'lado': 'derecha',
                        'pos_actual': self.pos_inicial_der,
                        'progreso': 0
                    })
    
    def detener_todos_sonidos(self):
        #detiene los efectos de sonido
        if self.audio_disponible:
            self.sonido_tomar.stop()
            self.sonido_soltar.stop()
            self.sonido_barajar.stop()
            self.barajando_sonando = False

    def reproducir_sonido(self, sonido):
        #reproduce un sonido despues de detener los otros
        if self.audio_disponible:
            self.detener_todos_sonidos()
            sonido.play()

    def actualizar_animacion(self, dt):
        if not self.animando_mezcla:
            return
            
        self.tiempo_animacion += dt
        
        if self.estado_animacion == 'inicio':
            # Mover el mazo al centro
            progreso = min(1, self.tiempo_animacion / 500)  # 500ms para el movimiento inicial
            if progreso >= 1:
                self.estado_animacion = 'dividiendo'
                self.tiempo_animacion = 0
                
        elif self.estado_animacion == 'dividiendo':
            progreso = min(1, self.tiempo_animacion / 500)
            if progreso >= 1:
                self.estado_animacion = 'mezclando'
                self.tiempo_animacion = 0
                if self.audio_disponible and not self.barajando_sonando:
                    self.detener_todos_sonidos()
                    self.sonido_barajar.play(-1)
                    self.barajando_sonando = True
                
        elif self.estado_animacion == 'mezclando':
            # Mover cartas una por una
            if self.carta_actual is None and self.grupos_mezcla:
                self.carta_actual = self.grupos_mezcla.pop(0)
                self.carta_actual['progreso'] = 0
                
            if self.carta_actual:
                self.carta_actual['progreso'] += dt / 100  # Velocidad de movimiento
                
                if self.carta_actual['progreso'] >= 1:
                    self.cartas_mezcladas.append(self.carta_actual['carta'])
                    self.carta_actual = None
                else:
                    # Interpolar posición
                    prog = self.carta_actual['progreso']
                    pos_inicial = self.pos_inicial_izq if self.carta_actual['lado'] == 'izquierda' else self.pos_inicial_der
                    self.carta_actual['pos_actual'] = (
                        pos_inicial[0] + (self.pos_central[0] - pos_inicial[0]) * prog,
                        pos_inicial[1] + (self.pos_central[1] - pos_inicial[1]) * prog
                    )
            
            # Terminar animación
        if not self.carta_actual and not self.grupos_mezcla:
            self.animando_mezcla = False
            self.mazo = self.cartas_mezcladas
            self.detener_todos_sonidos()
            self.boton_repartir.activo = True

    def repartir(self):
        if self.animando_reparto:
            return
            
        self.animando_reparto = True
        self.tiempo_reparto = 0
        self.cartas_mesa = []
        self.cartas_por_posicion = {pos: [] for pos in posiciones}

        # Desactivar botón de mezclar y repartir
        self.boton_mezclar.activo = False
        self.boton_repartir.activo = False
        
        # Preparar las cartas para repartir
        self.cartas_por_repartir = self.mazo.copy()
        self.cartas_a_repartir = []
        
        for vuelta in range(4):
            for pos_index in range(13):
                if self.cartas_por_repartir:
                    carta = self.cartas_por_repartir.pop(0)
                    self.cartas_a_repartir.append({
                        'carta': carta,
                        'pos_destino': posiciones[pos_index],
                        'progreso': 0
                    })


    def actualizar_reparto(self, dt):
        if not self.animando_reparto:
            return
            
        self.tiempo_reparto += dt
        
        if self.carta_actual_reparto is None and self.cartas_a_repartir:
            self.carta_actual_reparto = self.cartas_a_repartir.pop(0)
            self.carta_actual_reparto['progreso'] = 0
            # Remover la carta del mazo cuando comienza a moverse
            if len(self.mazo) > 0:
                self.mazo.pop()
                
        if self.carta_actual_reparto:
            self.carta_actual_reparto['progreso'] += dt / self.duracion_reparto_carta
            
            if self.carta_actual_reparto['progreso'] >= 1:
                # La carta llegó a su destino
                carta = self.carta_actual_reparto['carta']
                pos_destino = self.carta_actual_reparto['pos_destino']
                self.cartas_por_posicion[pos_destino].append(carta)
                
                # Reproducir sonido cuando la carta llega a su posición
                if self.audio_disponible:
                    self.reproducir_sonido(self.sonido_tomar)
                
                self.carta_actual_reparto = None
            
        #if not self.carta_actual_reparto and not self.cartas_a_repartir:
        #    self.animando_reparto = False
        #    self.boton_jugar.activo = True
        
        if not self.carta_actual_reparto and not self.cartas_a_repartir:
            self.animando_reparto = False
            self.mostrando_input = True
            self.mostrar_meditando = False
    
    def obtener_ultima_carta_no_volteada(self, pila):
        # Recorrer la pila desde arriba hacia abajo
        for carta in reversed(pila):
            if carta not in self.cartas_volteadas:
                return carta
        return None
        
    def manejar_evento(self, event):
        # Manejar entrada de texto primero
        if self.mostrando_input:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and self.pregunta:
                    print(f"Pregunta realizada: {self.pregunta}")
                    self.mostrando_input = False
                    self.boton_jugar.activo = True
                    self.mostrar_meditando = True
                elif event.key == pygame.K_BACKSPACE:
                    self.pregunta = self.pregunta[:-1]
                else:
                    if event.unicode.isprintable():
                        self.pregunta += event.unicode
                return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Click izquierdo
            if not self.jugando:
                # Manejar clicks en botones cuando no estamos jugando
                mouse_pos = event.pos
                if self.boton_mezclar.rect.collidepoint(mouse_pos) and self.boton_mezclar.activo:
                    if self.audio_disponible:
                        self.sonido_click.play()
                    self.mezclar_hojeo()
                elif self.boton_repartir.rect.collidepoint(mouse_pos) and self.boton_repartir.activo:
                    if self.audio_disponible:
                        self.sonido_click.play()
                    self.repartir()
                elif self.boton_jugar.rect.collidepoint(mouse_pos) and self.boton_jugar.activo:
                    if self.audio_disponible:
                        self.sonido_click.play()
                    self.detener_todos_sonidos()  # Asegurarse de que no haya sonidos activos
                    self.iniciar_juego()
                elif self.boton_reiniciar.rect.collidepoint(mouse_pos) and self.boton_reiniciar.activo:
                    if self.audio_disponible:
                        self.sonido_click.play()
                    self.reiniciar_juego()
            else:
                # Intentar agarrar una carta de la pila actual
                if not self.arrastrando:  # Solo si no estamos arrastrando ya
                    pila_clickeada = self.obtener_pila_clickeada(event.pos)
                    if pila_clickeada == self.pila_actual:
                        pila = self.cartas_por_posicion[posiciones[self.pila_actual]]
                        carta = self.obtener_ultima_carta_no_volteada(pila)
                        if carta:
                            self.reproducir_sonido(self.sonido_tomar)
                            self.arrastrando = True
                            self.carta_arrastrada = carta
                            self.pos_arrastre = event.pos
                            self.pos_origen = posiciones[self.pila_actual]
                            self.pos_origen_index = self.pila_actual

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:  # Soltar click izquierdo
            if self.arrastrando:
                pila_destino = self.obtener_pila_clickeada(event.pos)
                siguiente_pos = self.obtener_siguiente_posicion(self.carta_arrastrada)
                
                if pila_destino is not None and pila_destino == siguiente_pos:
                    self.reproducir_sonido(self.sonido_soltar)
                    
                    pila_origen = self.cartas_por_posicion[posiciones[self.pos_origen_index]]
                    if self.carta_arrastrada in pila_origen:
                        pila_origen.remove(self.carta_arrastrada)
                    
                    pila_destino_cartas = self.cartas_por_posicion[posiciones[siguiente_pos]]
                    pila_destino_cartas.append(self.carta_arrastrada)
                    self.cartas_volteadas.add(self.carta_arrastrada)
                    self.pila_actual = siguiente_pos
                    
                    # Verificar victoria/derrota
                    if len(self.cartas_volteadas) == self.total_cartas:
                        self.terminar_juego(True)
                    else:
                        nueva_pila = self.cartas_por_posicion[posiciones[self.pila_actual]]
                        if not self.obtener_ultima_carta_no_volteada(nueva_pila):
                            self.terminar_juego(False)
                else:
                    if self.audio_disponible:
                        self.reproducir_sonido(self.sonido_error)
                
                # Limpiar estado de arrastre
                self.arrastrando = False
                self.carta_arrastrada = None
                self.pos_arrastre = None
                
        elif event.type == pygame.MOUSEMOTION:
            # Actualizar posición de la carta siendo arrastrada
            if self.arrastrando:
                self.pos_arrastre = event.pos

    def draw(self, screen):
        screen.blit(self.fondo, (0, 0))

        # Dibujar imagen meditando solo si corresponde y no hay imagen de respuesta
        if self.mostrar_meditando and not self.mostrando_input and not self.mostrando_respuesta:
            screen.blit(self.img_meditando, (20, 20))

        if self.animando_mezcla:
            if self.estado_animacion == 'inicio':
                # Dibujar mazo moviéndose al centro
                progreso = min(1, self.tiempo_animacion / 500)
                pos_x = self.mazo_pos[0] + (self.pos_central[0] - self.mazo_pos[0]) * progreso
                pos_y = self.mazo_pos[1] + (self.pos_central[1] - self.mazo_pos[1]) * progreso
                screen.blit(self.reverso_base, (pos_x, pos_y))  # Cambiar aquí
                
            elif self.estado_animacion == 'dividiendo':
                # Dibujar mazos separándose
                progreso = min(1, self.tiempo_animacion / 500)
                pos_izq_x = self.pos_central[0] + (self.pos_inicial_izq[0] - self.pos_central[0]) * progreso
                pos_der_x = self.pos_central[0] + (self.pos_inicial_der[0] - self.pos_central[0]) * progreso
                screen.blit(self.reverso_base, (pos_izq_x, self.pos_central[1]))  # Cambiar aquí
                screen.blit(self.reverso_base, (pos_der_x, self.pos_central[1]))  # Cambiar aquí
                
            elif self.estado_animacion == 'mezclando':
                # Dibujar grupos que esperan en los lados
                for grupo in self.grupos_mezcla:
                    pos = self.pos_inicial_izq if grupo['lado'] == 'izquierda' else self.pos_inicial_der
                    screen.blit(self.reverso_base, pos)  # Cambiar aquí
                
                # Dibujar carta en movimiento
                if self.carta_actual:
                    screen.blit(self.reverso_base, self.carta_actual['pos_actual'])  # Cambiar aquí
                
                # Dibujar cartas ya mezcladas
                for i, carta in enumerate(self.cartas_mezcladas):
                    screen.blit(self.reverso_base, (self.pos_central[0], self.pos_central[1] - i * 2))  # Cambiar aquí
        else:
            # Si hay cartas en el mazo, mostrar el mazo
            if len(self.mazo) > 0:
                # Dibujar mazo normal con efecto escalerita vertical
                for i in range(len(self.mazo)-1, -1, -1):
                    screen.blit(self.mazo[i].imagen_reverso, 
                            (self.mazo_pos[0] + i * self.CARD_OFFSET_V, 
                            self.mazo_pos[1]))

        # Durante el reparto, mostrar la carta en movimiento
        if self.animando_reparto and self.carta_actual_reparto:
            progreso = self.carta_actual_reparto['progreso']
            pos_inicial = self.mazo_pos
            pos_final = self.carta_actual_reparto['pos_destino']
            pos_actual = (
                pos_inicial[0] + (pos_final[0] - pos_inicial[0]) * progreso,
                pos_inicial[1] + (pos_final[1] - pos_inicial[1]) * progreso
            )
            screen.blit(self.carta_actual_reparto['carta'].imagen_reverso, pos_actual)

        # Dibujar cartas en la mesa con efecto escalerita horizontal
        #for pos in posiciones:
        #    cartas = self.cartas_por_posicion[pos]
        #    for i, carta in enumerate(cartas):
        #        screen.blit(carta.imagen_reverso, 
        #                (pos[0] + i * self.CARD_OFFSET_H, 
        #                pos[1]))

        # Dibujar cartas en la mesa
        for pos_index, pos in enumerate(posiciones):
            cartas = self.cartas_por_posicion[pos]
            for i, carta in enumerate(cartas):
                if carta == self.carta_arrastrada:
                    continue  # No dibujar la carta que se está arrastrando
                if carta in self.cartas_volteadas:
                    screen.blit(carta.imagen_frontal, 
                            (pos[0] + i * self.CARD_OFFSET_H, 
                            pos[1]))
                else:
                    screen.blit(carta.imagen_reverso, 
                            (pos[0] + i * self.CARD_OFFSET_H, 
                            pos[1]))

        # Si estamos jugando, resaltar la pila actual y la pila destino válida
        if self.jugando:
            # Resaltar pila actual
            pos_actual = posiciones[self.pila_actual]
            pygame.draw.rect(screen, (255, 255, 0), 
                           (pos_actual[0], pos_actual[1], CARD_WIDTH, CARD_HEIGHT), 2)
            
            # Si estamos arrastrando una carta, resaltar la pila destino válida
            if self.arrastrando:
                siguiente_pos = self.obtener_siguiente_posicion(self.carta_arrastrada)
                pos_destino = posiciones[siguiente_pos]
                pygame.draw.rect(screen, (0, 255, 0), 
                               (pos_destino[0], pos_destino[1], CARD_WIDTH, CARD_HEIGHT), 2)

        # Dibujar la carta siendo arrastrada
        if self.arrastrando and self.carta_arrastrada:
            screen.blit(self.carta_arrastrada.imagen_frontal, 
                       (self.pos_arrastre[0] - CARD_WIDTH//2, 
                        self.pos_arrastre[1] - CARD_HEIGHT//2))
                               
        # Mostrar imagen de respuesta si corresponde (sin límite de tiempo)
        if self.mostrando_respuesta and self.respuesta_img:
            pos_x = WIDTH//2 - self.respuesta_img.get_width()//2
            pos_y = HEIGHT//2 - self.respuesta_img.get_height()//2
            screen.blit(self.respuesta_img, (pos_x, pos_y))

        # Dibujar botones
        self.boton_mezclar.draw(screen)
        self.boton_repartir.draw(screen)
        self.boton_jugar.draw(screen)
        
        # Mostrar imagen de respuesta y botón de reiniciar si corresponde
        if self.mostrando_respuesta and self.respuesta_img:
            # Dibujar imagen de respuesta
            pos_x = WIDTH//2 - self.respuesta_img.get_width()//2
            pos_y = HEIGHT//2 - self.respuesta_img.get_height()//2
            screen.blit(self.respuesta_img, (pos_x, pos_y))
            
            # Dibujar botón de reiniciar debajo de la imagen de respuesta
            self.boton_reiniciar.rect.centerx = WIDTH//2  # Centrar horizontalmente
            self.boton_reiniciar.rect.top = pos_y + self.respuesta_img.get_height() + 20  # 20 píxeles debajo de la imagen
            self.boton_reiniciar.draw(screen)
        
        # Dibujar cuadro de texto si está activo
        if self.mostrando_input:
            # Dibujar imagen de pregunta
            pos_x = WIDTH//2 - self.img_pregunta.get_width()//2
            pos_y = HEIGHT//2 - self.img_pregunta.get_height()//2
            screen.blit(self.img_pregunta, (pos_x, pos_y))
            
            # Calcular posición del marco
            marco_x = pos_x + self.area_texto['offset_x']
            marco_y = pos_y + self.area_texto['offset_y']
            
            # Dibujar marco
            pygame.draw.rect(screen, (255, 255, 255), (
                marco_x,
                marco_y,
                self.area_texto['ancho'],
                self.area_texto['alto']
            ), 2)
            
            # Calcular ancho disponible para el texto
            ancho_disponible = self.area_texto['ancho'] - (self.margen_texto * 2)
            
            # Renderizar texto
            lineas = self.render_texto_multilinea(self.pregunta, ancho_disponible)
            
            # Dibujar texto
            y_offset = 0
            altura_linea = 25
            for linea in lineas:
                if y_offset + altura_linea <= self.area_texto['alto'] - (self.margen_texto * 2):
                    text_surface = self.font.render(linea, True, (0, 0, 0))
                    screen.blit(text_surface, (
                        marco_x + self.margen_texto,
                        marco_y + self.margen_texto + y_offset
                    ))
                    y_offset += altura_linea
            
            # Dibujar cursor
            if pygame.time.get_ticks() % 1000 < 500 and lineas:
                ultima_linea = lineas[-1]
                cursor_surface = self.font.render(ultima_linea, True, (0, 0, 0))
                cursor_x = marco_x + self.margen_texto + cursor_surface.get_width()
                cursor_y = marco_y + self.margen_texto + y_offset - altura_linea
                if y_offset <= self.area_texto['alto'] - (self.margen_texto * 2):
                    pygame.draw.line(screen, (0, 0, 0),
                                   (cursor_x, cursor_y),
                                   (cursor_x, cursor_y + altura_linea), 2)

def main():
    juego = Juego()
    running = True
    clock = pygame.time.Clock()
    
    while running:
        dt = clock.tick(100)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            juego.manejar_evento(event)
        
        juego.actualizar_animacion(dt)
        juego.actualizar_reparto(dt)  # Añadir esta línea
        juego.draw(screen)
        pygame.display.flip()
        clock.tick(60)
        
    pygame.quit()

if __name__ == "__main__":
    main()
