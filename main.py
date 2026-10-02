"""
GATO DE LOS TEJADOS - Videojuego 2D en Pygame
=============================================
Un gato corre de noche sobre los tejados de la ciudad. Salta obstáculos,
atrapa peces, esquiva cuervos y sobrevive con sus 9 vidas.

Controles:
    ESPACIO / W / Flecha arriba -> saltar (pulsa otra vez en el aire: doble salto)
                                   (suelta pronto la tecla para un salto más corto)
    ENTER / ESPACIO             -> comenzar (en la pantalla de inicio)
    P                           -> pausar / reanudar
    X                           -> atacar a los jefes (mantener pulsado)
    M                           -> activar / silenciar efectos de sonido
    R                           -> reiniciar tras Game Over
    ESC                         -> salir

Objetos:
    Pez azul      +10 puntos          Pez dorado  +50 puntos
    Leche         escudo (absorbe un golpe)
    Ovillo        imán que atrae a los peces durante unos segundos
    Combo         recoger peces seguidos multiplica los puntos (hasta x4)
                  cada 10 peces seguidos recuperas 1 vida (máximo 9)

Restricción del laboratorio: NO se usan bases de datos ni servicios en la nube.
Todo el estado (puntaje, vidas, mejor puntaje de la sesión) vive en memoria.
Todos los gráficos se dibujan con formas de Pygame: no hay archivos externos.
"""

import math
import random
import sys
from array import array

import pygame
import pygame.gfxdraw

# ===========================================================================
# CONFIGURACIÓN GENERAL
# ===========================================================================
ANCHO, ALTO = 800, 600
FPS = 60
SUELO_Y = 480            # altura (en píxeles) de la línea del tejado
GATO_X = 150             # posición horizontal fija del gato

# --- Física del gato ---
GRAVEDAD = 0.8
SALTO_V = -15.0          # impulso del primer salto
SALTO_V2 = -13.0         # impulso del salto en el aire
VIDAS_INICIALES = 9      # ¡los gatos tienen 9 vidas!
INVULNERABLE_FRAMES = 90 # tiempo sin recibir daño tras un golpe

# --- Dificultad ---
VEL_INICIAL = 4.0        # píxeles por fotograma con que se mueve el mundo
VEL_MAX = 8.0
METROS_POR_VELOCIDAD = 180.0  # aceleración gradual para mantener la partida legible

# --- Objetos especiales ---
DURACION_IMAN = 360      # fotogramas (6 segundos)
RADIO_IMAN = 230
VENTANA_COMBO = 75       # fotogramas máximos entre peces para mantener el combo
COMBO_PARA_VIDA = 10     # peces seguidos para recuperar una vida

# --- Colores ---
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
GRIS = (160, 160, 175)
AMARILLO = (255, 220, 90)
ROJO = (235, 70, 90)
CIAN = (110, 210, 255)
NARANJA = (240, 150, 60)
NARANJA_OSC = (196, 100, 35)
CREMA = (250, 226, 190)
ROSA = (255, 150, 175)

APARIENCIAS_GATO = (
    {"nombre": "Sombra", "detalle": "negro puro, ojos verdes", "pelaje": (0, 0, 0), "sombra": (0, 0, 0),
     "panza": (0, 0, 0), "interior": (0, 0, 0), "ojos": (151, 190, 113),
     "collar": (0, 0, 0), "nariz": (0, 0, 0), "marcas": "liso"},
    {"nombre": "Luna", "detalle": "gris atigrada", "pelaje": (111, 119, 126), "sombra": (72, 78, 84),
     "panza": (183, 187, 188), "interior": (83, 88, 92), "ojos": (174, 184, 137),
     "collar": (74, 81, 87), "nariz": (117, 91, 87), "marcas": "rayas"},
    {"nombre": "Chispa", "detalle": "naranja atigrada", "pelaje": (174, 103, 55), "sombra": (112, 65, 39),
     "panza": (226, 194, 151), "interior": (129, 77, 48), "ojos": (174, 187, 106),
     "collar": (104, 77, 51), "nariz": (133, 91, 84), "marcas": "rayas"},
    {"nombre": "Nube", "detalle": "blanca y gris", "pelaje": (205, 203, 193), "sombra": (137, 140, 139),
     "panza": (235, 231, 215), "interior": (151, 143, 133), "ojos": (116, 157, 165),
     "collar": (96, 108, 111), "nariz": (151, 111, 106), "marcas": "bicolor"},
    {"nombre": "Mora", "detalle": "carey oscuro", "pelaje": (76, 66, 62), "sombra": (43, 39, 39),
     "panza": (162, 135, 109), "interior": (99, 74, 67), "ojos": (177, 165, 103),
     "collar": (75, 68, 63), "nariz": (119, 91, 84), "marcas": "carey"},
    {"nombre": "Canela", "detalle": "marron atigrada", "pelaje": (133, 94, 64), "sombra": (82, 58, 43),
     "panza": (194, 164, 126), "interior": (101, 70, 52), "ojos": (173, 163, 107),
     "collar": (91, 71, 53), "nariz": (125, 91, 82), "marcas": "rayas"},
)

# --- Estados del juego ---
INICIO, JUGANDO, PAUSA, GAME_OVER = "inicio", "jugando", "pausa", "game_over"

TECLAS_SALTO = (pygame.K_SPACE, pygame.K_UP, pygame.K_w)


def circulo_suave(superficie, color, centro, radio, ancho=0):
    x, y = round(centro[0]), round(centro[1])
    radio = max(1, round(radio))
    if ancho:
        pygame.draw.circle(superficie, color, (x, y), radio, ancho)
    else:
        pygame.gfxdraw.filled_circle(superficie, x, y, radio, color)
    pygame.gfxdraw.aacircle(superficie, x, y, radio, color)


def elipse_suave(superficie, color, rect, ancho=0):
    x, y, w, h = (round(valor) for valor in rect)
    w, h = max(1, w), max(1, h)
    if ancho:
        pygame.draw.ellipse(superficie, color, (x, y, w, h), ancho)
    else:
        pygame.gfxdraw.filled_ellipse(superficie, x + w // 2, y + h // 2,
                                      max(1, w // 2), max(1, h // 2), color)
    pygame.gfxdraw.aaellipse(superficie, x + w // 2, y + h // 2,
                             max(1, w // 2), max(1, h // 2), color)


def poligono_suave(superficie, color, puntos, ancho=0):
    puntos = [(round(x), round(y)) for x, y in puntos]
    if ancho:
        pygame.draw.polygon(superficie, color, puntos, ancho)
    else:
        pygame.gfxdraw.filled_polygon(superficie, puntos, color)
    pygame.gfxdraw.aapolygon(superficie, puntos, color)


def crear_efecto_sonoro(inicio, fin, duracion, volumen):
    """Genera un tono breve sin archivos de audio externos."""
    mixer = pygame.mixer.get_init()
    if mixer is None:
        return None
    frecuencia_muestreo = mixer[0]
    muestras = array("h")
    total = int(frecuencia_muestreo * duracion)
    fase = 0.0
    for indice in range(total):
        progreso = indice / max(1, total - 1)
        frecuencia = inicio + (fin - inicio) * progreso
        fase += math.tau * frecuencia / frecuencia_muestreo
        ataque = min(1.0, indice / max(1, int(frecuencia_muestreo * 0.012)))
        envolvente = ataque * (1.0 - progreso) ** 1.7
        onda = math.sin(fase) + 0.2 * math.sin(fase * 2)
        muestras.append(int(32767 * volumen * envolvente * onda))
    return pygame.mixer.Sound(buffer=muestras.tobytes())


def crear_musica_fondo():
    """Crea una frase instrumental suave que puede reproducirse en bucle."""
    mixer = pygame.mixer.get_init()
    if mixer is None:
        return None
    frecuencia_muestreo = mixer[0]
    notas = (392, 440, 523, 440, 392, 330, 349, 392,
             330, 294, 330, 392, 440, 392, 330, 294)
    bajos = (98, 82, 110, 87)
    duracion_nota = 0.30
    total = int(frecuencia_muestreo * duracion_nota * len(notas))
    muestras = array("h")
    fase_melodia = fase_bajo = 0.0
    for indice in range(total):
        tiempo = indice / frecuencia_muestreo
        paso = min(len(notas) - 1, int(tiempo / duracion_nota))
        dentro_nota = tiempo - paso * duracion_nota
        envolvente = min(1.0, dentro_nota / 0.025, (duracion_nota - dentro_nota) / 0.04)
        frecuencia = notas[paso]
        frecuencia_bajo = bajos[(paso // 4) % len(bajos)]
        fase_melodia += math.tau * frecuencia / frecuencia_muestreo
        fase_bajo += math.tau * frecuencia_bajo / frecuencia_muestreo
        melodia = (math.sin(fase_melodia) + 0.16 * math.sin(fase_melodia * 2)) * envolvente
        armonia = 0.32 * math.sin(fase_bajo)
        borde = min(1.0, tiempo / 0.035, (total / frecuencia_muestreo - tiempo) / 0.035)
        muestra = int(32767 * 0.31 * (melodia + armonia) * borde)
        muestras.append(max(-32767, min(32767, muestra)))
    return pygame.mixer.Sound(buffer=muestras.tobytes())


# ===========================================================================
# FUNCIONES AUXILIARES DE DIBUJO
# ===========================================================================
def texto(superficie, msg, fuente, color, pos, ancla="c", sombra=True):
    """Dibuja texto con sombra. ancla: 'c' centro, 'i' izquierda, 'd' derecha."""
    def rect_de(img, p):
        if ancla == "c":
            return img.get_rect(center=p)
        if ancla == "i":
            return img.get_rect(topleft=p)
        return img.get_rect(topright=p)

    if sombra:
        img = fuente.render(msg, True, (0, 0, 0))
        superficie.blit(img, rect_de(img, (pos[0] + 2, pos[1] + 2)))
    img = fuente.render(msg, True, color)
    superficie.blit(img, rect_de(img, pos))


def dibujar_corazon(s, x, y, tam, color):
    """Corazón hecho con dos círculos y un triángulo."""
    r = max(2, round(tam * 0.27))
    d = tam * 0.23
    circulo_suave(s, color, (x - d, y), r)
    circulo_suave(s, color, (x + d, y), r)
    poligono_suave(
        s, color,
        [(x - tam * 0.49, y + r * 0.35), (x + tam * 0.49, y + r * 0.35), (x, y + tam * 0.55)],
    )


def dibujar_pez(s, x, y, dorado, t):
    """Pez que mira hacia la izquierda (hacia donde corre el mundo)."""
    cuerpo = (255, 214, 60) if dorado else (110, 190, 255)
    oscuro = (214, 150, 20) if dorado else (60, 130, 205)
    poligono_suave(s, oscuro, [(x + 8, y), (x + 18, y - 8), (x + 18, y + 8)])  # cola
    elipse_suave(s, cuerpo, (x - 15, y - 8, 26, 16))                          # cuerpo
    poligono_suave(s, oscuro, [(x - 2, y - 7), (x + 4, y - 12), (x + 5, y - 6)])  # aleta
    circulo_suave(s, BLANCO, (x - 8, y - 2), 3)
    circulo_suave(s, NEGRO, (x - 9, y - 2), 1)
    if dorado:  # destello que pulsa
        k = 3 + abs(math.sin(t * 0.12)) * 4
        pygame.draw.line(s, BLANCO, (x - 4, y - 15 - k), (x - 4, y - 15 + k), 2)
        pygame.draw.line(s, BLANCO, (x - 4 - k, y - 15), (x - 4 + k, y - 15), 2)


def dibujar_leche(s, x, y):
    """Cartón de leche (power-up de escudo)."""
    poligono_suave(s, (205, 205, 225), [(x - 11, y - 12), (x, y - 22), (x + 11, y - 12)])
    pygame.draw.rect(s, (242, 242, 252), (x - 11, y - 12, 22, 30), border_radius=2)
    pygame.draw.rect(s, (70, 130, 230), (x - 7, y - 4, 14, 12), border_radius=2)
    circulo_suave(s, BLANCO, (x, y + 2), 3)


def dibujar_ovillo(s, x, y, t):
    """Ovillo de lana (power-up de imán)."""
    circulo_suave(s, (170, 80, 200), (x, y), 13)
    claro = (225, 160, 245)
    pygame.draw.arc(s, claro, pygame.Rect(int(x - 10), int(y - 10), 20, 20), 0.4, 2.6, 2)
    pygame.draw.arc(s, claro, pygame.Rect(int(x - 12), int(y - 4), 24, 16), 3.4, 5.6, 2)
    pygame.draw.line(s, claro, (x - 6, y - 8), (x + 8, y + 9), 2)
    hilo = math.sin(t * 0.1) * 3
    pygame.draw.line(s, (170, 80, 200), (x + 9, y + 9), (x + 19, y + 15 + hilo), 3)


def dibujar_retrato_gato(s, x, y, apariencia, t):
    """Retrato sencillo de perfil, a juego con el gato del juego."""
    gato = APARIENCIAS_GATO[apariencia]
    bigotes = gato["pelaje"] if gato["marcas"] == "liso" else (190, 190, 185)
    onda = math.sin(t * 0.06) * 2
    pygame.draw.lines(s, gato["pelaje"], False,
                      [(x - 20, y + 12), (x - 30, y + 8), (x - 31, y - 3), (x - 27, y - 8)], 5)
    elipse_suave(s, gato["pelaje"], (x - 24, y - 2 + onda, 51, 24))
    pygame.draw.line(s, gato["sombra"], (x - 14, y + 16), (x - 14, y + 22), 4)
    pygame.draw.line(s, gato["pelaje"], (x + 13, y + 16), (x + 14, y + 22), 4)
    poligono_suave(s, gato["pelaje"], [(x - 5, y - 8), (x - 4, y - 30), (x + 8, y - 17)])
    poligono_suave(s, gato["pelaje"], [(x + 9, y - 17), (x + 24, y - 30), (x + 25, y - 5)])
    elipse_suave(s, gato["interior"], (x - 1, y - 23, 6, 11))
    elipse_suave(s, gato["interior"], (x + 14, y - 23, 6, 11))
    circulo_suave(s, gato["pelaje"], (x + 9, y - 7), 15)
    for ojo_x in (x + 4, x + 14):
        circulo_suave(s, gato["ojos"], (ojo_x, y - 8), 3)
        elipse_suave(s, (24, 25, 24), (ojo_x, y - 10, 2, 6))
    elipse_suave(s, gato["panza"], (x + 14, y - 2, 12, 8))
    elipse_suave(s, gato["panza"], (x + 21, y - 2, 11, 8))
    circulo_suave(s, gato["nariz"], (x + 30, y + 1), 2)
    pygame.draw.aaline(s, gato["sombra"], (x + 29, y + 3), (x + 26, y + 6))
    pygame.draw.aaline(s, bigotes, (x + 27, y + 1), (x + 40, y - 2))
    pygame.draw.aaline(s, bigotes, (x + 28, y + 3), (x + 41, y + 4))
    pygame.draw.aaline(s, gato["sombra"], (x + 35, y + 7), (x + 44, y + 9))


# ===========================================================================
# PARTÍCULAS Y TEXTO FLOTANTE
# ===========================================================================
class Particula:
    """Círculo pequeño que se mueve, se encoge y desaparece (polvo, chispas...)."""

    def __init__(self, x, y, vx, vy, vida, color, radio, gravedad=0.0):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.vida = self.vida_max = vida
        self.color = color
        self.radio = radio
        self.gravedad = gravedad

    def actualizar(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravedad
        self.vida -= 1

    def dibujar(self, s):
        r = max(1, int(self.radio * self.vida / self.vida_max))
        circulo_suave(s, self.color, (self.x, self.y), r)


class TextoFlotante:
    """Texto que sube y se desvanece (por ejemplo '+10')."""

    def __init__(self, msg, x, y, color, fuente, vida=45):
        self.msg, self.x, self.y = msg, x, y
        self.color, self.fuente = color, fuente
        self.vida = self.vida_max = vida

    def actualizar(self):
        self.y -= 1.0
        self.vida -= 1

    def dibujar(self, s):
        img = self.fuente.render(self.msg, True, self.color)
        img.set_alpha(int(255 * self.vida / self.vida_max))
        s.blit(img, img.get_rect(center=(int(self.x), int(self.y))))


# ===========================================================================
# EL GATO (jugador)
# ===========================================================================
class Gato:
    """Gato negro dibujado con formas. Tiene gravedad, doble salto y animación."""

    def __init__(self):
        self.x = GATO_X
        self.apariencia = 0
        self.reiniciar()

    def reiniciar(self):
        self.y = float(SUELO_Y)      # posición de las patas
        self.vy = 0.0
        self.saltos = 0              # saltos usados desde que tocó el suelo
        self.en_suelo = True
        self.anim = 0.0              # fase de la animación de carrera
        self.parpadeo = 0            # fotogramas restantes con los ojos cerrados
        self.invulnerable = 0
        self.escudo = False
        self.iman = 0

    @property
    def rect(self):
        """Caja de colisión (un poco más pequeña que el dibujo, para ser justos)."""
        return pygame.Rect(int(self.x - 20), int(self.y - 46), 50, 46)

    @property
    def centro(self):
        return (self.x + 5, self.y - 24)

    def saltar(self):
        """Salta si quedan saltos disponibles. Devuelve True si saltó."""
        if self.saltos >= 2:
            return False
        self.vy = SALTO_V if self.saltos == 0 else SALTO_V2
        self.saltos += 1
        self.en_suelo = False
        return True

    def soltar_salto(self):
        """Si se suelta la tecla durante la subida, el salto se acorta."""
        if self.vy < -5:
            self.vy *= 0.5

    def animar(self, velocidad):
        """Avanza la animación de patas y el parpadeo."""
        self.anim += 0.12 + velocidad * 0.03
        if self.parpadeo > 0:
            self.parpadeo -= 1
        elif random.random() < 0.01:
            self.parpadeo = 8

    def actualizar(self, velocidad):
        """Aplica física. Devuelve True en el fotograma en que aterriza."""
        aterrizo = False
        self.vy += GRAVEDAD
        self.y += self.vy
        if self.y >= SUELO_Y:
            if not self.en_suelo:
                aterrizo = True
            self.y = float(SUELO_Y)
            self.vy = 0.0
            self.saltos = 0
            self.en_suelo = True
        self.animar(velocidad)
        if self.invulnerable > 0:
            self.invulnerable -= 1
        if self.iman > 0:
            self.iman -= 1
        return aterrizo

    def dibujar(self, s, t):
        x, y = self.x, self.y
        cx, cy = self.centro
        aspecto = APARIENCIAS_GATO[self.apariencia]
        pelaje = aspecto["pelaje"]
        pelaje_sombra = aspecto["sombra"]
        panza = aspecto["panza"]
        bigotes = pelaje if aspecto["marcas"] == "liso" else (190, 190, 185)

        # Efectos de los power-ups (se dibujan aunque el gato parpadee)
        if self.escudo:
            circulo_suave(s, CIAN, (cx, cy), 54, 3)
        if self.iman > 0:
            for i in range(4):
                ang = t * 0.1 + i * math.pi / 2
                circulo_suave(
                    s, (225, 160, 245),
                    (cx + math.cos(ang) * 46, cy + math.sin(ang) * 46), 4,
                )

        # Parpadeo de invulnerabilidad: el gato desaparece a ratos
        if self.invulnerable > 0 and (self.invulnerable // 4) % 2 == 0:
            return

        aire = not self.en_suelo

        # --- Cola (ondula con el movimiento) ---
        onda = math.sin(self.anim * 0.7) * 6
        punta = [(x - 26, y - 30), (x - 40, y - 34 + onda * 0.5),
                 (x - 50, y - 48 + onda), (x - 47, y - 62 + onda * 1.3)]
        pygame.draw.lines(s, pelaje, False, punta, 7)
        circulo_suave(s, pelaje_sombra, punta[-1], 4)

        # --- Patas: primero las del lado lejano (más oscuras) ---
        patas = [(-8, math.pi, pelaje_sombra), (8, math.pi, pelaje_sombra),
                 (-18, 0.0, pelaje), (18, 0.0, pelaje)]
        for dx, fase, color in patas:
            if aire:   # en el aire: delanteras estiradas y traseras hacia atrás
                pie_x = x + dx + (12 if dx > 0 else -12)
                pie_y = y - 12
            else:      # en el suelo: ciclo de carrera
                pie_x = x + dx + math.sin(self.anim + fase) * 10
                pie_y = y - max(0.0, math.cos(self.anim + fase)) * 7
            pygame.draw.line(s, color, (x + dx, y - 16), (pie_x, pie_y), 5)
            circulo_suave(s, color, (pie_x, pie_y), 3)

        # --- Cuerpo y pecho, con las marcas propias de cada pelaje ---
        elipse_suave(s, pelaje, (x - 30, y - 44, 60, 30))
        elipse_suave(s, panza, (x - 16, y - 26, 34, 11))
        if aspecto["marcas"] == "rayas":
            for i in (-16, -6, 4):
                pygame.draw.line(s, pelaje_sombra, (x + i, y - 43), (x + i + 3, y - 34), 2)
        elif aspecto["marcas"] == "bicolor":
            elipse_suave(s, panza, (x + 2, y - 43, 19, 16))
        elif aspecto["marcas"] == "carey":
            elipse_suave(s, (174, 126, 77), (x - 18, y - 41, 17, 10))
            elipse_suave(s, (184, 151, 118), (x + 1, y - 38, 16, 9))

        # --- Cabeza redonda y expresiva, como en el diseño original ---
        rebote = 0 if aire else math.sin(self.anim * 2) * 1.5
        hx, hy = x + 26, y - 46 + rebote
        poligono_suave(s, pelaje, [(hx - 13, hy - 6), (hx - 10, hy - 25), (hx - 1, hy - 13)])
        poligono_suave(s, pelaje, [(hx + 1, hy - 13), (hx + 9, hy - 25), (hx + 14, hy - 5)])
        poligono_suave(s, aspecto["interior"], [(hx - 10, hy - 9), (hx - 9, hy - 20), (hx - 3, hy - 13)])
        poligono_suave(s, aspecto["interior"], [(hx + 3, hy - 13), (hx + 8, hy - 20), (hx + 11, hy - 8)])
        circulo_suave(s, pelaje, (hx, hy), 16)
        if aspecto["marcas"] == "rayas":
            for i in (-8, 0, 8):
                pygame.draw.line(s, pelaje_sombra, (hx + i, hy - 13), (hx + i + 2, hy - 7), 2)
        pygame.draw.ellipse(s, panza, (hx + 2, hy + 1, 15, 11))
        # Collar y cascabel discretos
        pygame.draw.line(s, aspecto["collar"], (hx - 8, hy + 12), (hx + 12, hy + 13), 3)
        circulo_suave(s, aspecto["collar"], (hx + 3, hy + 17), 2)
        # Ojos felinos con pupila vertical
        for ox in (2, 11):
            ex, ey = hx + ox, hy - 3
            if self.parpadeo > 0:
                pygame.draw.line(s, pelaje_sombra, (ex - 4, ey), (ex + 4, ey), 2)
            else:
                circulo_suave(s, aspecto["ojos"], (ex, ey), 4)
                elipse_suave(s, pelaje_sombra, (ex, ey - 3, 3, 6))
                circulo_suave(s, BLANCO, (ex + 1, ey - 1), 1)
        # Nariz, boca y bigotes
        circulo_suave(s, aspecto["nariz"], (hx + 15, hy + 3), 2)
        pygame.draw.arc(s, pelaje_sombra, pygame.Rect(hx + 11, hy + 4, 9, 7), 3.1, 6.1, 1)
        pygame.draw.aaline(s, bigotes, (hx + 14, hy + 4), (hx + 28, hy + 1))
        pygame.draw.aaline(s, bigotes, (hx + 14, hy + 6), (hx + 29, hy + 9))


# ===========================================================================
# OBSTÁCULOS, PECES Y POWER-UPS
# ===========================================================================
class Obstaculo:
    """Tres tipos: 'bote' (basura), 'cajas' y 'cuervo' (vuela y va más rápido)."""

    TAMANOS = {
        "bote": (44, 60), "cajas": (58, 52), "cuervo": (46, 26),
        "pinchos": (54, 40), "dron": (58, 34),
    }

    def __init__(self, tipo, x):
        self.tipo = tipo
        self.x = float(x)
        self.w, self.h = self.TAMANOS[tipo]
        if tipo == "cuervo":
            # Vuela bajo: se esquiva quedándose en el suelo, no saltando
            self.y = float(SUELO_Y - random.randint(100, 120))
        elif tipo == "dron":
            self.y = float(SUELO_Y - random.randint(155, 185))
        else:
            self.y = float(SUELO_Y - self.h)
        self.fase = random.random() * 6.28

    @property
    def rect(self):
        """Caja de colisión ligeramente reducida (más justo para el jugador)."""
        return pygame.Rect(int(self.x) + 4, int(self.y) + 4, self.w - 8, self.h - 8)

    def actualizar(self, velocidad):
        self.x -= velocidad + (2.5 if self.tipo == "cuervo" else 0)
        self.fase += 0.3

    def dibujar(self, s):
        x, y, w, h = int(self.x), int(self.y), self.w, self.h
        if self.tipo == "bote":
            poligono_suave(s, (105, 112, 125),
                                [(x + 2, y + 10), (x + w - 2, y + 10), (x + w - 6, y + h), (x + 6, y + h)])
            for i in range(1, 4):
                pygame.draw.line(s, (72, 78, 92), (x + w * i // 4, y + 14), (x + w * i // 4, y + h - 4), 2)
            pygame.draw.rect(s, (135, 142, 158), (x - 2, y, w + 4, 10), border_radius=3)
            pygame.draw.rect(s, (80, 86, 98), (x + w // 2 - 6, y - 4, 12, 5), border_radius=2)
        elif self.tipo == "cajas":
            pygame.draw.rect(s, (176, 128, 78), (x, y, w, h))
            pygame.draw.rect(s, (120, 84, 48), (x, y, w, h), 3)
            pygame.draw.line(s, (120, 84, 48), (x, y + h // 2), (x + w, y + h // 2), 2)
            pygame.draw.rect(s, (214, 190, 140), (x + w // 2 - 5, y, 10, h))
        elif self.tipo == "cuervo":  # vuela hacia la izquierda y bate las alas
            aleteo = math.sin(self.fase) * 14
            poligono_suave(s, (25, 25, 38), [(x + 36, y + 14), (x + 52, y + 8), (x + 50, y + 21)])  # cola
            elipse_suave(s, (25, 25, 38), (x + 8, y + 6, 32, 17))                                # cuerpo
            poligono_suave(s, (45, 45, 62),
                                [(x + 14, y + 12), (x + 32, y + 12), (x + 26, y - 4 - aleteo)])          # ala
            circulo_suave(s, (25, 25, 38), (x + 8, y + 11), 8)                                      # cabeza
            poligono_suave(s, (240, 170, 40), [(x, y + 8), (x - 11, y + 13), (x, y + 16)])          # pico
            circulo_suave(s, (255, 90, 60), (x + 6, y + 9), 2)                                      # ojo
        elif self.tipo == "dron":
            pygame.draw.line(s, (125, 150, 175), (x + 7, y + 5), (x + 51, y + 5), 3)
            for rotor_x in (x + 9, x + 49):
                elipse_suave(s, (115, 145, 175), (rotor_x - 8, y, 16, 4))
            elipse_suave(s, (74, 96, 125), (x + 8, y + 8, 42, 19))
            elipse_suave(s, (175, 198, 215), (x + 14, y + 10, 30, 8))
            circulo_suave(s, (255, 70, 75), (x + 43, y + 17), 4)
        else:  # pinchos: barrera de puas que obliga a usar el doble salto
            pygame.draw.rect(s, (85, 91, 110), (x + 2, y + 18, w - 4, h - 18))
            for punta_x in range(x + 3, x + w - 5, 12):
                poligono_suave(s, (180, 188, 205),
                                    [(punta_x, y + 20), (punta_x + 6, y), (punta_x + 12, y + 20)])


class Pez:
    """Pez coleccionable. El dorado vale más. Flota suavemente y el imán lo atrae."""

    def __init__(self, x, y, dorado=False):
        self.x, self.y = float(x), float(y)
        self.base_y = float(y)
        self.dorado = dorado
        self.valor = 50 if dorado else 10
        self.t = random.random() * 6.28
        self.atraido = False

    @property
    def rect(self):
        return pygame.Rect(int(self.x - 15), int(self.y - 11), 30, 22)

    def actualizar(self, velocidad, centro_gato, iman_activo):
        self.t += 0.1
        if iman_activo and not self.atraido:
            if math.hypot(centro_gato[0] - self.x, centro_gato[1] - self.y) < RADIO_IMAN:
                self.atraido = True
        if self.atraido:  # vuela hacia el gato
            dx, dy = centro_gato[0] - self.x, centro_gato[1] - self.y
            d = max(1.0, math.hypot(dx, dy))
            self.x += dx / d * (velocidad + 9)
            self.y += dy / d * (velocidad + 9)
        else:
            self.x -= velocidad
            self.y = self.base_y + math.sin(self.t) * 4

    def dibujar(self, s):
        dibujar_pez(s, self.x, self.y, self.dorado, self.t * 10)


class PowerUp:
    """'leche' = escudo, 'ovillo' = imán."""

    def __init__(self, tipo, x, y):
        self.tipo = tipo
        self.x, self.base_y = float(x), float(y)
        self.y = float(y)
        self.t = random.random() * 6.28

    @property
    def rect(self):
        return pygame.Rect(int(self.x - 15), int(self.y - 20), 30, 40)

    def actualizar(self, velocidad):
        self.t += 0.08
        self.x -= velocidad
        self.y = self.base_y + math.sin(self.t) * 6

    def dibujar(self, s):
        # Halo pulsante para que destaque
        circulo_suave(s, (90, 80, 140), (self.x, self.y), int(26 + math.sin(self.t * 2) * 3), 2)
        if self.tipo == "leche":
            dibujar_leche(s, self.x, self.y)
        else:
            dibujar_ovillo(s, self.x, self.y, self.t * 10)


class Disparo:
    """Proyectil del gato o del jefe final."""

    def __init__(self, x, y, enemigo=False):
        self.x, self.y = float(x), float(y)
        self.enemigo = enemigo
        self.velocidad = -5.5 if enemigo else 9.5

    @property
    def rect(self):
        return pygame.Rect(int(self.x - 10), int(self.y - 7), 20, 14)

    def actualizar(self):
        self.x += self.velocidad

    def dibujar(self, s):
        x, y = int(self.x), int(self.y)
        if self.enemigo:
            pygame.draw.line(s, (112, 47, 48), (x + 11, y), (x - 12, y), 3)
            circulo_suave(s, (153, 57, 53), (x, y), 7)
            circulo_suave(s, (225, 103, 73), (x - 2, y - 2), 4)
            circulo_suave(s, (255, 198, 126), (x - 3, y - 3), 1)
        else:
            pygame.draw.line(s, (198, 158, 77), (x - 12, y + 3), (x + 10, y - 3), 2)
            poligono_suave(s, (255, 226, 153),
                           [(x - 8, y + 3), (x + 10, y - 5), (x + 5, y + 4),
                            (x - 10, y + 7)])
            circulo_suave(s, (255, 248, 213), (x + 4, y - 2), 2)


class JefeFinal:
    """Cuervo gigante que lanza proyectiles y recibe los zarpazos del gato."""

    VIDA_MAXIMA = 12

    def __init__(self, numero=1):
        self.numero = numero
        self.tipo = (numero - 1) % 3
        self.nombre = ("Cuervo de la Tormenta", "Espectro Felino", "Leviatan del Cielo")[self.tipo]
        self.vida_maxima = self.VIDA_MAXIMA + 4 * (numero - 1)
        self.x = 650
        self.y = 410.0
        self.vida = self.vida_maxima
        self.frame = 0

    @property
    def rect(self):
        return pygame.Rect(int(self.x - 70), int(self.y - 55), 140, 110)

    def actualizar(self):
        self.frame += 1
        if self.tipo == 0:
            self.y = 405 + math.sin(self.frame * 0.035) * 14
        elif self.tipo == 1:
            self.x = 635 + math.sin(self.frame * 0.025) * 18
            self.y = 398 + math.sin(self.frame * 0.04) * 25
        else:
            self.x = 640 + math.sin(self.frame * 0.022) * 22
            self.y = 390 + math.sin(self.frame * 0.032) * 28
        periodo = max(58, 145 - (self.numero - 1) * 9)
        if self.frame % periodo == 0:
            altura = random.choice((SUELO_Y - 22, SUELO_Y - 105))
            return Disparo(self.x - 66, altura, enemigo=True)
        return None

    def dibujar(self, s):
        x, y = int(self.x), int(self.y)
        if self.tipo == 0:
            aleteo = math.sin(self.frame * 0.12) * 10
            poligono_suave(s, (31, 34, 43),
                           [(x - 28, y - 13), (x - 103, y - 43 - aleteo),
                            (x - 76, y + 12), (x - 32, y + 27)])
            poligono_suave(s, (31, 34, 43),
                           [(x + 24, y - 13), (x + 100, y - 43 + aleteo),
                            (x + 69, y + 18), (x + 31, y + 27)])
            for pluma in range(4):
                pygame.draw.aaline(s, (77, 78, 86), (x - 36 - pluma * 5, y - 8),
                                   (x - 83 - pluma * 4, y - 25 - aleteo))
                pygame.draw.aaline(s, (77, 78, 86), (x + 34 + pluma * 5, y - 8),
                                   (x + 82 + pluma * 4, y - 25 + aleteo))
            elipse_suave(s, (47, 48, 57), (x - 49, y - 39, 95, 79))
            elipse_suave(s, (58, 59, 67), (x - 35, y - 60, 64, 50))
            poligono_suave(s, (34, 35, 43),
                           [(x - 34, y - 38), (x - 27, y - 78), (x - 8, y - 48)])
            elipse_suave(s, (210, 151, 72), (x + 8, y - 21, 34, 8))
            elipse_suave(s, (217, 79, 62), (x - 19, y - 39, 9, 3))
            elipse_suave(s, (217, 79, 62), (x + 7, y - 39, 9, 3))
        elif self.tipo == 1:
            cola = math.sin(self.frame * 0.08) * 9
            pygame.draw.lines(s, (71, 75, 91), False,
                              [(x - 36, y + 7), (x - 64, y + 30), (x - 57, y + 44 + cola),
                               (x - 41, y + 35 + cola)], 9)
            elipse_suave(s, (86, 91, 108), (x - 46, y - 19, 89, 81))
            poligono_suave(s, (78, 84, 101),
                           [(x - 39, y - 10), (x - 34, y - 63), (x - 8, y - 35)])
            poligono_suave(s, (78, 84, 101),
                           [(x + 5, y - 35), (x + 34, y - 63), (x + 39, y - 8)])
            poligono_suave(s, (111, 116, 128),
                           [(x - 31, y - 18), (x - 33, y - 51), (x - 15, y - 33)])
            poligono_suave(s, (111, 116, 128),
                           [(x + 13, y - 33), (x + 31, y - 51), (x + 30, y - 15)])
            elipse_suave(s, (146, 154, 168), (x - 17, y + 15, 35, 42))
            elipse_suave(s, (181, 202, 201), (x - 23, y - 10, 12, 4))
            elipse_suave(s, (181, 202, 201), (x + 11, y - 10, 12, 4))
            pygame.draw.line(s, (47, 53, 67), (x - 4, y + 3), (x + 4, y + 3), 2)
            pygame.draw.arc(s, (105, 117, 132), pygame.Rect(x + 30, y + 13, 44, 37), 0.4, 5.4, 5)
        else:
            cola = math.sin(self.frame * 0.07) * 8
            poligono_suave(s, (57, 78, 96),
                           [(x - 49, y + 1), (x - 91, y - 28 + cola),
                            (x - 78, y + 25 + cola), (x - 39, y + 31)])
            poligono_suave(s, (78, 102, 119),
                           [(x + 25, y + 10), (x + 70, y + 37), (x + 23, y + 30)])
            poligono_suave(s, (83, 106, 122),
                           [(x - 20, y - 25), (x + 5, y - 62), (x + 14, y - 22)])
            elipse_suave(s, (91, 119, 136), (x - 61, y - 42, 128, 82))
            elipse_suave(s, (143, 158, 162), (x - 31, y + 2, 81, 30))
            elipse_suave(s, (36, 51, 64), (x + 24, y - 9, 6, 4))
            pygame.draw.arc(s, (61, 81, 93), pygame.Rect(x - 2, y + 4, 62, 22), 0.1, 2.8, 2)
            for branquia in range(3):
                pygame.draw.aaline(s, (70, 91, 103),
                                   (x - 27 + branquia * 8, y - 4),
                                   (x - 32 + branquia * 8, y + 12))


# ===========================================================================
# FONDO CON PARALLAX (cielo, luna, estrellas, edificios, tejado)
# ===========================================================================
class Edificio:
    """Silueta de edificio con ventanas, algunas encendidas."""

    def __init__(self, x, capa):
        self.x = float(x)
        if capa == 0:   # capa lejana: más alta y ancha
            self.w, self.h = random.randint(70, 130), random.randint(130, 270)
        else:           # capa cercana
            self.w, self.h = random.randint(50, 100), random.randint(70, 190)
        self.ventanas = []
        for c in range((self.w - 12) // 18):
            for f in range((self.h - 16) // 26):
                if random.random() < 0.28:  # solo guardamos las ventanas encendidas
                    self.ventanas.append((8 + c * 18, 10 + f * 26))


class Fondo:
    def __init__(self):
        self.cielo_dia = self._crear_cielo(False)
        self.cielo_noche = self._crear_cielo(True)
        self.noche = 0.0
        # Estrellas (evitando la zona de la luna) con fase propia para titilar
        self.estrellas = []
        while len(self.estrellas) < 80:
            ex, ey = random.randint(0, ANCHO), random.randint(0, SUELO_Y - 150)
            if math.hypot(ex - 650, ey - 110) > 95:
                self.estrellas.append((ex, ey, random.random() * 6.28, random.choice([1, 1, 2])))
        # Dos capas de edificios que se mueven a distinta velocidad (parallax)
        self.capas = [
            {"factor": 0.12, "dia_color": (77, 120, 151), "color": (30, 28, 70),
             "dia_ventana": (178, 220, 235), "ventana": (95, 95, 150), "lista": []},
            {"factor": 0.30, "dia_color": (52, 91, 119), "color": (20, 18, 48),
             "dia_ventana": (255, 233, 166), "ventana": (255, 214, 120), "lista": []},
        ]
        for i, capa in enumerate(self.capas):
            x = -60.0
            while x < ANCHO + 200:
                e = Edificio(x, i)
                capa["lista"].append(e)
                x += e.w + random.randint(0, 8)
        self.scroll = 0.0

    @staticmethod
    def _crear_cielo(nocturno):
        """Genera una vez las capas de cielo que se mezclan durante la partida."""
        cielo = pygame.Surface((ANCHO, ALTO))
        for y in range(ALTO):
            k = min(1.0, y / SUELO_Y)
            if nocturno:
                color = (int(8 + 62 * k), int(8 + 32 * k), int(35 + 65 * k))
            else:
                color = (int(70 + 108 * k), int(155 + 64 * k), int(220 + 22 * k))
            pygame.draw.line(cielo, color, (0, y), (ANCHO, y))
        cx, cy = 650, 110
        if nocturno:
            for radio, alfa in ((78, 14), (64, 22), (52, 34)):
                halo = pygame.Surface((radio * 2, radio * 2), pygame.SRCALPHA)
                pygame.draw.circle(halo, (255, 250, 210, alfa), (radio, radio), radio)
                cielo.blit(halo, (cx - radio, cy - radio))
            circulo_suave(cielo, (238, 236, 205), (cx, cy), 40)
            for dx, dy, r in ((-12, -8, 9), (14, 6, 7), (-4, 16, 5)):
                circulo_suave(cielo, (214, 211, 178), (cx + dx, cy + dy), r)
        else:
            circulo_suave(cielo, (255, 231, 145), (cx, cy), 44)
            circulo_suave(cielo, (255, 245, 194), (cx - 8, cy - 8), 30)
            for nube_x, nube_y, escala in ((170, 125, 1), (405, 205, 0.8), (690, 260, 1.1)):
                elipse_suave(cielo, (223, 240, 248),
                             (nube_x - 38 * escala, nube_y - 8 * escala,
                              76 * escala, 23 * escala))
                circulo_suave(cielo, (223, 240, 248),
                              (nube_x - 15 * escala, nube_y - 5 * escala), 15 * escala)
                circulo_suave(cielo, (223, 240, 248),
                              (nube_x + 10 * escala, nube_y - 9 * escala), 18 * escala)
        return cielo

    @staticmethod
    def _mezclar_color(dia, noche, cantidad):
        return tuple(int(a + (b - a) * cantidad) for a, b in zip(dia, noche))

    def actualizar(self, velocidad, progreso_noche=None):
        self.scroll += velocidad
        if progreso_noche is not None:
            self.noche = max(0.0, min(1.0, progreso_noche))
        for i, capa in enumerate(self.capas):
            lista = capa["lista"]
            for e in lista:
                e.x -= velocidad * capa["factor"]
            while lista and lista[0].x + lista[0].w < 0:   # sale por la izquierda
                lista.pop(0)
            while lista[-1].x + lista[-1].w < ANCHO + 120:  # entra por la derecha
                ult = lista[-1]
                lista.append(Edificio(ult.x + ult.w + random.randint(0, 8), i))

    def dibujar(self, s, t):
        s.blit(self.cielo_dia, (0, 0))
        self.cielo_noche.set_alpha(int(255 * self.noche))
        s.blit(self.cielo_noche, (0, 0))
        for ex, ey, fase, tam in self.estrellas:
            brillo = int((170 + 80 * math.sin(t * 0.05 + fase)) * self.noche)
            if brillo:
                circulo_suave(s, (brillo, brillo, brillo), (ex, ey), tam)
        for capa in self.capas:
            color = self._mezclar_color(capa["dia_color"], capa["color"], self.noche)
            ventana = self._mezclar_color(capa["dia_ventana"], capa["ventana"], self.noche)
            for e in capa["lista"]:
                pygame.draw.rect(s, color, (int(e.x), SUELO_Y - e.h, e.w, e.h))
                for dx, dy in e.ventanas:
                    pygame.draw.rect(s, ventana, (int(e.x) + dx, SUELO_Y - e.h + dy, 8, 12))
        self._dibujar_suelo(s)

    def _dibujar_suelo(self, s):
        """Tejado de ladrillos que se desplaza para dar sensación de velocidad."""
        suelo = self._mezclar_color((126, 79, 62), (52, 34, 44), self.noche)
        borde = self._mezclar_color((200, 130, 92), (98, 66, 78), self.noche)
        linea = self._mezclar_color((91, 55, 45), (38, 24, 32), self.noche)
        pygame.draw.rect(s, suelo, (0, SUELO_Y, ANCHO, ALTO - SUELO_Y))
        pygame.draw.rect(s, borde, (0, SUELO_Y, ANCHO, 8))
        for fila in range(4):
            y = SUELO_Y + 8 + fila * 28
            pygame.draw.line(s, linea, (0, y), (ANCHO, y), 2)
            x = -((self.scroll + (fila % 2) * 30) % 60)
            while x < ANCHO:
                pygame.draw.line(s, linea, (int(x), y), (int(x), y + 28), 2)
                x += 60


# ===========================================================================
# CONTROL DEL JUEGO
# ===========================================================================
class Juego:
    def __init__(self):
        pygame.mixer.pre_init(22050, -16, 1, 512)
        pygame.init()
        if pygame.mixer.get_init() is None:
            try:
                pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
            except pygame.error:
                pass
        self.pantalla = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption("Gato de los Tejados")
        self.reloj = pygame.time.Clock()
        self.f_titulo = pygame.font.SysFont("arial", 54, bold=True)
        self.f_grande = pygame.font.SysFont("arial", 44, bold=True)
        self.f_media = pygame.font.SysFont("arial", 28, bold=True)
        self.f_chica = pygame.font.SysFont("arial", 20)

        self.lienzo = pygame.Surface((ANCHO, ALTO))  # el mundo se dibuja aquí (permite temblor)
        self.velo = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        self.velo.fill((0, 0, 0, 150))

        self.fondo = Fondo()
        self.gato = Gato()
        self.seleccion_gato = 0
        self.sonidos = {}
        if pygame.mixer.get_init() is not None:
            self.sonidos = {
                "salto": crear_efecto_sonoro(310, 620, 0.11, 0.16),
                "pez": crear_efecto_sonoro(650, 980, 0.10, 0.15),
                "poder": crear_efecto_sonoro(420, 820, 0.18, 0.17),
                "golpe": crear_efecto_sonoro(190, 75, 0.22, 0.22),
                "ataque": crear_efecto_sonoro(760, 360, 0.07, 0.10),
                "impacto": crear_efecto_sonoro(280, 145, 0.09, 0.14),
                "vida": crear_efecto_sonoro(500, 1120, 0.30, 0.18),
                "jefe": crear_efecto_sonoro(360, 95, 0.38, 0.20),
            }
        self.musica_fondo = crear_musica_fondo()
        self.canal_musica = None
        if self.musica_fondo is not None:
            pygame.mixer.set_reserved(1)
            self.canal_musica = pygame.mixer.Channel(0)
        self.sonido_activo = bool(self.sonidos and self.musica_fondo)
        self.mejor = 0          # mejor puntaje de la sesión (solo en memoria)
        self.t = 0              # contador global de fotogramas (para animaciones)
        self.estado = INICIO
        self.reiniciar_partida()
        self.actualizar_musica()

    # ----- Gestión de partida -------------------------------------------------
    def reiniciar_partida(self):
        """Deja todas las variables de una partida en su valor inicial."""
        self.gato.reiniciar()
        self.gato.apariencia = self.seleccion_gato
        self.obstaculos, self.peces, self.powerups = [], [], []
        self.jefe = None
        self.disparos = []
        self.cooldown_garra = 0
        self.jefes_derrotados = 0
        self.siguiente_jefe = 250.0
        self.particulas, self.textos = [], []
        self.vidas = VIDAS_INICIALES
        self.velocidad = VEL_INICIAL
        self.nivel = 1
        self.metros = 0.0
        self.puntos_extra = 0
        self.peces_recogidos = 0
        self.combo = 0
        self.ultimo_pez = -999
        self.frame = 0
        self.temblor = 0
        self.record_nuevo = False
        self.dist_obstaculo = 500.0    # px que faltan para el siguiente obstáculo
        self.dist_powerup = 2200.0     # px que faltan para el siguiente power-up

    def empezar(self):
        self.reiniciar_partida()
        self.fondo.noche = 0.0
        self.estado = JUGANDO
        self.actualizar_musica()

    @property
    def puntaje(self):
        return int(self.metros) + self.puntos_extra

    @property
    def multiplicador(self):
        """Combo: x1 (1-3 peces), x2 (4-6), x3 (7-9), x4 (10+)."""
        return min(4, 1 + max(0, self.combo - 1) // 3)

    @staticmethod
    def salir():
        pygame.quit()
        sys.exit()

    def sonar(self, nombre):
        if not self.sonido_activo:
            return
        sonido = self.sonidos.get(nombre)
        if sonido is not None:
            try:
                sonido.play()
            except pygame.error:
                self.sonido_activo = False
                self.actualizar_musica()

    def actualizar_musica(self):
        if self.canal_musica is None:
            return
        if not self.sonido_activo:
            self.canal_musica.stop()
            return
        self.canal_musica.set_volume(0.48 if self.jefe is not None else 0.72)
        if not self.canal_musica.get_busy():
            self.canal_musica.play(self.musica_fondo, loops=-1)

    # ----- Efectos visuales ---------------------------------------------------
    def chispas(self, x, y, color, cantidad, fuerza=3.0, gravedad=0.1, vida=28, radio=4):
        for _ in range(cantidad):
            ang = random.uniform(0, 2 * math.pi)
            vel = random.uniform(0.5, fuerza)
            self.particulas.append(
                Particula(x, y, math.cos(ang) * vel, math.sin(ang) * vel,
                          random.randint(vida // 2, vida), color, radio, gravedad)
            )
        if len(self.particulas) > 300:  # límite para no ralentizar el juego
            del self.particulas[:len(self.particulas) - 300]

    def polvo(self, cantidad):
        for _ in range(cantidad):
            self.particulas.append(
                Particula(self.gato.x - 20 + random.uniform(-6, 6), SUELO_Y - 2,
                          -random.uniform(0.5, 2.0), -random.uniform(0.3, 1.6),
                          random.randint(12, 20), (160, 140, 150), 3, 0.03)
            )

    def aviso(self, msg, x, y, color, fuente=None):
        self.textos.append(TextoFlotante(msg, x, y, color, fuente or self.f_chica))

    # ----- Eventos ------------------------------------------------------------
    def manejar_eventos(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.salir()
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    self.salir()
                elif e.key == pygame.K_m:
                    if self.sonidos:
                        self.sonido_activo = not self.sonido_activo
                        self.actualizar_musica()
                elif self.estado == INICIO:
                    if e.key in (pygame.K_LEFT, pygame.K_RIGHT):
                        paso = -1 if e.key == pygame.K_LEFT else 1
                        self.seleccion_gato = (self.seleccion_gato + paso) % len(APARIENCIAS_GATO)
                    elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.empezar()
                elif self.estado == JUGANDO:
                    if e.key in TECLAS_SALTO:
                        estaba_en_suelo = self.gato.en_suelo
                        if self.gato.saltar():
                            self.sonar("salto")
                            if estaba_en_suelo:
                                self.polvo(5)
                    elif e.key == pygame.K_p:
                        self.estado = PAUSA
                elif self.estado == PAUSA and e.key in (pygame.K_p, pygame.K_RETURN):
                    self.estado = JUGANDO
                elif self.estado == GAME_OVER and e.key in (pygame.K_r, pygame.K_RETURN):
                    self.empezar()
            elif e.type == pygame.KEYUP:
                if self.estado == JUGANDO and e.key in TECLAS_SALTO:
                    self.gato.soltar_salto()

    # ----- Generación de objetos ----------------------------------------------
    def generar_obstaculo(self):
        opciones, pesos = ["bote", "cajas"], [4, 3]
        if self.nivel >= 2:                 # los cuervos aparecen desde el nivel 2
            opciones.append("cuervo")
            pesos.append(3)
        if self.nivel >= 3:
            opciones.append("pinchos")
            pesos.append(3)
        if self.nivel >= 5:
            opciones.append("dron")
            pesos.append(2)
        tipo = random.choices(opciones, weights=pesos)[0]
        o = Obstaculo(tipo, ANCHO + 60)
        self.obstaculos.append(o)
        if self.nivel >= 4 and random.random() < min(0.35, 0.14 + (self.nivel - 4) * 0.04):
            segundo = random.choice(("bote", "cajas", "pinchos"))
            self.obstaculos.append(Obstaculo(segundo, o.x + 175))
        # Recompensa asociada: arco de peces sobre el obstáculo o fila después de él
        if tipo != "cuervo" and random.random() < 0.65:
            self.generar_arco_peces(o.x + o.w / 2)
        elif random.random() < 0.7:
            self.generar_fila_peces(o.x + o.w + 80)

    def generar_arco_peces(self, cx):
        """5 peces en forma de arco: guían el salto sobre el obstáculo."""
        for i in range(5):
            k = (i - 2) / 2
            y = SUELO_Y - 35 - (1 - k * k) * 95
            self.peces.append(Pez(cx + (i - 2) * 42, y, random.random() < 0.06))

    def generar_fila_peces(self, x0):
        y = SUELO_Y - random.choice([32, 32, 70, 100])
        for i in range(random.randint(3, 6)):
            self.peces.append(Pez(x0 + i * 38, y, random.random() < 0.06))

    def generar_powerup(self):
        tipo = random.choice(["leche", "ovillo"])
        self.powerups.append(PowerUp(tipo, ANCHO + 40, SUELO_Y - random.randint(45, 120)))

    # ----- Lógica de colisiones y eventos de juego -----------------------------
    def recoger_pez(self, pez):
        # El combo continúa si el pez anterior se recogió hace poco
        if self.frame - self.ultimo_pez <= VENTANA_COMBO:
            self.combo += 1
        else:
            self.combo = 1
        self.ultimo_pez = self.frame
        puntos = pez.valor * self.multiplicador
        self.puntos_extra += puntos
        self.peces_recogidos += 1
        if self.combo % COMBO_PARA_VIDA == 0 and self.vidas < VIDAS_INICIALES:
            self.vidas += 1
            self.sonar("vida")
            self.chispas(self.gato.x, self.gato.y - 34, CIAN, 20, fuerza=4, gravedad=0.0)
            self.aviso("¡Combo! +1 vida", self.gato.x + 30, self.gato.y - 82, CIAN, self.f_media)
        else:
            self.sonar("pez")
        color = AMARILLO if pez.dorado else CIAN
        self.chispas(pez.x, pez.y, color, 8, fuerza=3.5, gravedad=0.05, vida=22, radio=3)
        self.aviso(f"+{puntos}", pez.x, pez.y - 16, color)

    def recoger_powerup(self, pu):
        self.sonar("poder")
        if pu.tipo == "leche":
            self.gato.escudo = True
            self.aviso("¡Escudo!", pu.x, pu.y - 24, CIAN, self.f_media)
        else:
            self.gato.iman = DURACION_IMAN
            self.aviso("¡Imán!", pu.x, pu.y - 24, (225, 160, 245), self.f_media)
        self.chispas(pu.x, pu.y, BLANCO, 14, fuerza=4, gravedad=0.0, vida=24)

    def golpe(self):
        """El gato choca con un obstáculo."""
        cx, cy = self.gato.centro
        self.combo = 0
        if self.gato.escudo:               # el escudo absorbe el golpe
            self.sonar("impacto")
            self.gato.escudo = False
            self.gato.invulnerable = 60
            self.chispas(cx, cy, CIAN, 18, fuerza=5, gravedad=0.0)
            self.aviso("¡Escudo roto!", cx, cy - 70, CIAN)
            return
        self.sonar("golpe")
        self.vidas -= 1
        self.gato.invulnerable = INVULNERABLE_FRAMES
        self.temblor = 14
        self.chispas(cx, cy, ROJO, 16, fuerza=5)
        self.aviso("-1 vida", cx, cy - 70, ROJO, self.f_media)
        if self.vidas <= 0:
            self.terminar_partida()

    def terminar_partida(self):
        self.estado = GAME_OVER
        self.record_nuevo = self.puntaje > self.mejor
        self.mejor = max(self.mejor, self.puntaje)
        self.temblor = 20
        cx, cy = self.gato.centro
        self.chispas(cx, cy, NARANJA, 30, fuerza=6)

    def derrotar_jefe(self):
        if self.jefe is None:
            return
        self.sonar("jefe")
        jefe = self.jefe
        self.jefes_derrotados += 1
        recompensa = 250 + self.jefes_derrotados * 100
        self.puntos_extra += recompensa
        self.vidas = min(VIDAS_INICIALES, self.vidas + 1)
        self.chispas(jefe.x, jefe.y, AMARILLO, 50, fuerza=7, vida=42)
        self.aviso(f"¡Jefe {jefe.numero} derrotado! +{recompensa}",
                   ANCHO // 2, 175, AMARILLO, self.f_grande)
        self.jefe = None
        self.disparos.clear()
        self.siguiente_jefe = self.metros + 180 + self.jefes_derrotados * 35
        self.dist_obstaculo = 240.0
        self.dist_powerup = min(self.dist_powerup, 900.0)
        self.actualizar_musica()

    # ----- Actualización ---------------------------------------------------------
    def actualizar_partida(self):
        self.frame += 1
        vel = self.velocidad

        # Dificultad progresiva con la distancia recorrida
        self.metros += vel / 50
        self.velocidad = min(VEL_MAX, VEL_INICIAL + self.metros / METROS_POR_VELOCIDAD)
        nuevo_nivel = int(self.velocidad - VEL_INICIAL) + 1
        if nuevo_nivel > self.nivel:
            self.nivel = nuevo_nivel
            self.aviso(f"¡Nivel {self.nivel}!", ANCHO // 2, 190, AMARILLO, self.f_grande)

        if self.jefe is None and self.metros >= self.siguiente_jefe:
            self.jefe = JefeFinal(self.jefes_derrotados + 1)
            self.actualizar_musica()
            self.obstaculos.clear()
            self.aviso(f"¡JEFE {self.jefe.numero}! Mantén X para atacar",
                       ANCHO // 2, 175, ROJO, self.f_grande)

        # Gato y fondo
        if self.gato.actualizar(vel):
            self.polvo(8)
        elif self.gato.en_suelo and self.frame % 5 == 0:
            self.polvo(1)
        self.fondo.actualizar(vel, min(1.0, self.metros / 180.0))

        # El combo se pierde si pasa demasiado tiempo sin recoger peces
        if self.frame - self.ultimo_pez > VENTANA_COMBO:
            self.combo = 0

        # Durante el combate no aparecen más obstáculos de carrera.
        if self.jefe is None:
            self.dist_obstaculo -= vel
            if self.dist_obstaculo <= 0:
                self.generar_obstaculo()
                minimo = max(245, 390 - self.nivel * 18)
                maximo = max(minimo + 70, 540 - self.nivel * 18)
                self.dist_obstaculo = random.randint(minimo, maximo) + vel * 9
            self.dist_powerup -= vel
            if self.dist_powerup <= 0:
                self.generar_powerup()
                self.dist_powerup = random.randint(2500, 4000)

        if self.jefe is not None:
            disparo_enemigo = self.jefe.actualizar()
            if disparo_enemigo is not None:
                self.disparos.append(disparo_enemigo)
                self.sonar("disparo")
            if self.cooldown_garra > 0:
                self.cooldown_garra -= 1
            if pygame.key.get_pressed()[pygame.K_x] and self.cooldown_garra == 0:
                self.disparos.append(Disparo(self.gato.x + 42, self.gato.y - 29))
                self.sonar("ataque")
                self.cooldown_garra = 18

        hit = self.gato.rect

        for disparo in self.disparos[:]:
            disparo.actualizar()
            if disparo.enemigo and self.gato.invulnerable == 0 and disparo.rect.colliderect(hit):
                self.disparos.remove(disparo)
                self.golpe()
                if self.estado == GAME_OVER:
                    return
            elif not disparo.enemigo and self.jefe is not None and disparo.rect.colliderect(self.jefe.rect):
                self.disparos.remove(disparo)
                self.jefe.vida -= 1
                self.sonar("impacto")
                self.chispas(disparo.x, disparo.y, AMARILLO, 5, fuerza=3, vida=18, radio=3)
                if self.jefe.vida <= 0:
                    self.derrotar_jefe()
                    return
            elif disparo.x < -30 or disparo.x > ANCHO + 30:
                self.disparos.remove(disparo)

        # Obstáculos (iterar sobre copia porque se eliminan elementos)
        for o in self.obstaculos[:]:
            o.actualizar(vel)
            if o.x + o.w < -60:
                self.obstaculos.remove(o)
            elif self.gato.invulnerable == 0 and o.rect.colliderect(hit):
                self.golpe()
                if self.estado == GAME_OVER:
                    return

        # Peces
        for p in self.peces[:]:
            p.actualizar(vel, self.gato.centro, self.gato.iman > 0)
            if p.rect.colliderect(hit):
                self.peces.remove(p)
                self.recoger_pez(p)
            elif p.x < -40:
                self.peces.remove(p)

        # Power-ups
        for pu in self.powerups[:]:
            pu.actualizar(vel)
            if pu.rect.colliderect(hit):
                self.powerups.remove(pu)
                self.recoger_powerup(pu)
            elif pu.x < -40:
                self.powerups.remove(pu)

    def actualizar(self):
        self.t += 1
        if self.estado == INICIO:
            self.fondo.actualizar(3, 0.0)
            self.gato.animar(3)
        elif self.estado == JUGANDO:
            self.actualizar_partida()
        if self.estado != PAUSA:
            for lista in (self.particulas, self.textos):
                for item in lista[:]:
                    item.actualizar()
                    if item.vida <= 0:
                        lista.remove(item)
            if self.temblor > 0:
                self.temblor -= 1

    # ----- Dibujo -------------------------------------------------------------------
    def dibujar_hud(self, s):
        for i in range(VIDAS_INICIALES):
            color = ROJO if i < self.vidas else (70, 60, 85)
            dibujar_corazon(s, 24 + i * 22, 24, 18, color)
        texto(s, f"Puntos: {self.puntaje}", self.f_media, BLANCO, (14, 44), "i")
        texto(s, f"Mejor: {self.mejor}", self.f_chica, GRIS, (ANCHO - 14, 12), "d")
        texto(s, f"Distancia: {int(self.metros)} m", self.f_chica, BLANCO, (ANCHO - 14, 36), "d")
        texto(s, f"Nivel {self.nivel}", self.f_chica, AMARILLO, (ANCHO - 14, 60), "d")
        y = 88
        if self.combo >= 4:
            texto(s, f"COMBO x{self.multiplicador}", self.f_media, AMARILLO, (14, y), "i")
            y += 36
        if 0 < self.vidas < VIDAS_INICIALES and self.combo > 0:
            avance = self.combo % COMBO_PARA_VIDA
            texto(s, f"Proxima vida: {avance}/{COMBO_PARA_VIDA}",
                  self.f_chica, CIAN, (14, y), "i")
            y += 26
        if self.gato.escudo:
            dibujar_leche(s, 26, y + 14)
            texto(s, "Escudo activo", self.f_chica, CIAN, (48, y + 4), "i")
            y += 38
        if self.gato.iman > 0:
            dibujar_ovillo(s, 26, y + 14, self.t)
            pygame.draw.rect(s, (60, 50, 90), (48, y + 8, 110, 12), border_radius=4)
            ancho = int(110 * self.gato.iman / DURACION_IMAN)
            pygame.draw.rect(s, (200, 130, 230), (48, y + 8, ancho, 12), border_radius=4)
        if self.jefe is not None:
            texto(s, f"JEFE {self.jefe.numero}", self.f_chica, ROJO, (ANCHO // 2, 24))
            pygame.draw.rect(s, (55, 40, 55), (ANCHO // 2 - 150, 38, 300, 16), border_radius=5)
            ancho = int(296 * self.jefe.vida / self.jefe.vida_maxima)
            pygame.draw.rect(s, ROJO, (ANCHO // 2 - 148, 40, ancho, 12), border_radius=4)
        estado_audio = "ON" if self.sonido_activo else "OFF"
        texto(s, f"Audio: {estado_audio} (M)", self.f_chica, GRIS, (ANCHO - 14, 84), "d")

    def dibujar_menu(self, s):
        rebote = math.sin(self.t * 0.05) * 5
        texto(s, "GATO DE LOS TEJADOS", self.f_titulo, CREMA, (ANCHO // 2, 50 + rebote))
        texto(s, "ELIGE A TU CORREDOR", self.f_media, AMARILLO, (ANCHO // 2, 100))
        ancho, alto, espacio = 220, 126, 13
        inicio_x = (ANCHO - (ancho * 3 + espacio * 2)) // 2
        fondos_tarjeta = ((29, 31, 45), (33, 38, 49), (38, 34, 42),
                          (34, 40, 44), (37, 33, 46), (43, 37, 34))
        for indice, aspecto in enumerate(APARIENCIAS_GATO):
            columna, fila = indice % 3, indice // 3
            x = inicio_x + columna * (ancho + espacio)
            y = 130 + fila * (alto + 12)
            seleccionado = indice == self.seleccion_gato
            borde = AMARILLO if seleccionado else (83, 87, 103)
            pygame.draw.rect(s, fondos_tarjeta[indice], (x, y, ancho, alto), border_radius=8)
            pygame.draw.rect(s, borde, (x, y, ancho, alto), 3 if seleccionado else 1, border_radius=8)
            dibujar_retrato_gato(s, x + 44, y + 69, indice, self.t)
            texto(s, aspecto["nombre"], self.f_media, BLANCO, (x + 80, y + 38), "i")
            texto(s, aspecto["detalle"], self.f_chica, aspecto["ojos"], (x + 80, y + 69), "i")
            if seleccionado:
                texto(s, "SELECCIONADO", self.f_chica, AMARILLO, (x + 80, y + 99), "i")
        texto(s, "Flechas izquierda/derecha: elegir gato", self.f_chica, GRIS, (ANCHO // 2, 411))
        texto(s, f"ESPACIO / W: saltar     X: atacar     P: pausa     M: audio {'ON' if self.sonido_activo else 'OFF'}",
              self.f_chica, CREMA, (ANCHO // 2, 440))
        texto(s, "El cielo pasa del día a la noche mientras corres.",
              self.f_chica, CIAN, (ANCHO // 2, 470))
        texto(s, "Cada jefe derrotado trae otro más fuerte.",
              self.f_chica, ROJO, (ANCHO // 2, 494))
        texto(s, "10 peces seguidos recuperan una vida.",
              self.f_chica, CIAN, (ANCHO // 2, 518))
        if (self.t // 30) % 2 == 0:
            texto(s, "ENTER para comenzar", self.f_media, AMARILLO, (ANCHO // 2, 558))

    def dibujar_game_over(self, s):
        s.blit(self.velo, (0, 0))
        pygame.draw.rect(s, (25, 22, 55), (200, 120, 400, 330), border_radius=14)
        pygame.draw.rect(s, ROJO, (200, 120, 400, 330), 3, border_radius=14)
        texto(s, "GAME OVER", self.f_grande, ROJO, (ANCHO // 2, 168))
        texto(s, "Se acabaron las 9 vidas", self.f_chica, GRIS, (ANCHO // 2, 208))
        texto(s, f"Puntaje: {self.puntaje}", self.f_media, BLANCO, (ANCHO // 2, 258))
        texto(s, f"Distancia: {int(self.metros)} m", self.f_chica, BLANCO, (ANCHO // 2, 298))
        texto(s, f"Peces atrapados: {self.peces_recogidos}", self.f_chica, BLANCO, (ANCHO // 2, 326))
        if self.record_nuevo:
            texto(s, "¡NUEVO RÉCORD!", self.f_media, AMARILLO, (ANCHO // 2, 372))
        else:
            texto(s, f"Mejor: {self.mejor}", self.f_chica, AMARILLO, (ANCHO // 2, 372))
        if (self.t // 30) % 2 == 0:
            texto(s, "Presiona R para reiniciar", self.f_chica, CREMA, (ANCHO // 2, 418))

    def dibujar(self):
        # 1) Mundo dibujado en un lienzo aparte (así podemos hacerlo temblar)
        mundo = self.lienzo
        self.fondo.dibujar(mundo, self.t)
        for o in self.obstaculos:
            o.dibujar(mundo)
        for p in self.peces:
            p.dibujar(mundo)
        for pu in self.powerups:
            pu.dibujar(mundo)
        if self.jefe is not None:
            self.jefe.dibujar(mundo)
        for disparo in self.disparos:
            disparo.dibujar(mundo)
        self.gato.dibujar(mundo, self.t)
        for part in self.particulas:
            part.dibujar(mundo)
        for tx in self.textos:
            tx.dibujar(mundo)

        # 2) Se copia a la pantalla con el desplazamiento del temblor
        ox = oy = 0
        if self.temblor > 0:
            fuerza = self.temblor // 3 + 1
            ox, oy = random.randint(-fuerza, fuerza), random.randint(-fuerza, fuerza)
        self.pantalla.fill(NEGRO)
        self.pantalla.blit(mundo, (ox, oy))

        # 3) Interfaz (no tiembla)
        if self.estado == INICIO:
            self.dibujar_menu(self.pantalla)
        else:
            self.dibujar_hud(self.pantalla)
            if self.estado == PAUSA:
                self.pantalla.blit(self.velo, (0, 0))
                texto(self.pantalla, "PAUSA", self.f_titulo, BLANCO, (ANCHO // 2, 270))
                texto(self.pantalla, "Presiona P para continuar", self.f_chica, CREMA, (ANCHO // 2, 320))
            elif self.estado == GAME_OVER:
                self.dibujar_game_over(self.pantalla)
        pygame.display.flip()

    # ----- Bucle principal -----------------------------------------------------------
    def ejecutar(self):
        while True:
            self.manejar_eventos()
            self.actualizar()
            self.dibujar()
            self.reloj.tick(FPS)  # limita a 60 FPS


if __name__ == "__main__":
    Juego().ejecutar()
