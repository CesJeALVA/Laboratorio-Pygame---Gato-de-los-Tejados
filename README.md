# Gato de los Tejados

Videojuego arcade de plataformas y supervivencia desarrollado con Python y Pygame. El jugador elige un gato, corre sobre los tejados, esquiva obstáculos, recoge peces y se enfrenta a jefes cada vez más fuertes.

## Ficha técnica

| Campo | Detalle |
| --- | --- |
| **Nombre** | Gato de los Tejados |
| **Autor(es)** | Cesia Jemima Alacama Vargas |
| **Asignatura** | Taller de Programacion |
| **Género** | Arcade / endless runner / acción |
| **Lenguaje** | Python 3.10+ |
| **Librería** | Pygame (`pip install pygame`) |
| **Herramientas de IA** | GitHub Copilot, Claude y Gemini |
| **Persistencia** | No utiliza bases de datos ni servicios en la nube. El récord dura durante la sesión. |

## Cómo jugar

Elige uno de los seis gatos con las flechas izquierda y derecha y pulsa `Enter` o `Espacio` para comenzar. Salta sobre los obstáculos y recoge peces para sumar puntos y mantener el combo. El escenario empieza de día y cambia gradualmente a la noche. A partir de los 250 metros aparece el primer jefe; al vencerlo, la carrera continúa y aparecen jefes más difíciles.

### Controles

| Tecla | Acción |
| --- | --- |
| ← / → | Elegir gato en el menú inicial |
| `Enter` / `Espacio` | Comenzar; también permite reanudar o reiniciar |
| `Espacio` / `W` / `↑` | Saltar; pulsa de nuevo en el aire para el doble salto |
| `X` (mantener) | Atacar durante los combates contra jefes |
| `P` | Pausar o reanudar |
| `M` | Silenciar o reactivar música y efectos |
| `R` | Reiniciar después de Game Over |
| `Esc` | Salir |

### Objetos

| Objeto | Efecto |
| --- | --- |
| Pez azul | +10 puntos |
| Pez dorado | +50 puntos |
| Leche | Escudo que absorbe un golpe |
| Ovillo | Atrae peces durante unos segundos |

Recoger peces seguidos aumenta el multiplicador hasta x4. Cada 10 peces consecutivos recupera una vida, hasta un máximo de nueve; recibir daño rompe el combo.

## Características

- Ventana de 800 × 600 píxeles y bucle de juego limitado a 60 FPS.
- Seis apariencias de gato seleccionables, incluida Sombra, de pelaje negro.
- Escenario con parallax que cambia progresivamente de día a noche.
- Velocidad progresiva, de 4 a 8 píxeles por fotograma.
- Obstáculos de basura, cajas, cuervos, pinchos y drones; aparecen en combinaciones más difíciles según el nivel.
- Tres diseños de jefe que se repiten con más vida y ataques más frecuentes.
- Peces, escudo, imán, vidas, récord de sesión y combos.
- Música ambiental en bucle y efectos de sonido sintetizados durante la ejecución; no requieren archivos de audio externos. `M` silencia o reactiva el audio.
- Gráficos dibujados con formas de Pygame; no requiere archivos de imagen externos.
- Estado mantenido en memoria, sin bases de datos ni conexión a servicios externos.

## Ejecución

Requisito: Python 3.10 o posterior.

```bash
python -m pip install pygame
python main.py
```

## Bitácora de Prompts (Prompt Log)

Los prompts siguientes se transcriben de las solicitudes realizadas durante el desarrollo. Los resultados describen los cambios que se conservaron en la versión actual.

### 0. Juego en proceso

> mm... que otro juego puedes hacer?? quisiera uno que tenga mas detalles... no quiero algo simple... mm... puedes hacer algun juego con gatos??

**Resultado:** juego mucho más completo con un gato: «Gato de los Tejados», un corredor nocturno por los techos de la ciudad. Tiene doble salto, peces, combos, power-ups, 9 vidas, parallax con luna y edificios, y partículas.

### 1. Gato negro y combate

> puedes hacer que el gato sea de color negro?? quisera que tuviera como un jefe final... como pelea XD

**Resultado:** se incorporó la apariencia Sombra, negra, y un combate con ataque del jugador, proyectiles enemigos y barra de vida.

### 2. Selección, escenario y progresión

> puedes añadirle mas mas detalles en la parte grafica?? quiero que el gato sea completamente negro... mientras pasa... aver que comience de dia y luego el ambiente cambie a la noche... sera que puedes agregar de que... no solo el gato negro... sino que puedes meter seleccion al inicio para que el jugador elija en gato con el que quiere jugar... unos 3 o 6 gatos maximo... que tenga mas desafio los obstaculos y que despues del primer jefe haya mas... para que asi el jugador siga jugando

**Resultado:** se añadieron seis apariencias seleccionables, transición de día a noche, nuevos obstáculos y una secuencia de jefes que continúa tras cada victoria.

### 3. Velocidad y jefes distintos

> chepes... va muy rapido XD... puedes hacerlo estilo kawaii?? y los jefes deben tener un diseño distinto al anterior

**Resultado:** se redujo la velocidad del corredor y se crearon tres siluetas de jefe. El estilo kawaii se probó y se retiró después, siguiendo las siguientes indicaciones.

### 4. Quitar el estilo kawaii

> el kawaii... no le queda... quitalo e intenta que los gatos se vean mas realistas pero tiernos

**Resultado:** se quitaron los detalles kawaii y se probaron pelajes naturales, bigotes y rasgos felinos.

### 5. Suavizar los gráficos

> mm... puedes hacer que el juego no se vea muy pixelado??

**Resultado:** se añadieron primitivas antialias de Pygame para suavizar los bordes de personajes, obstáculos y elementos del escenario.

### 6. Ajustar la forma de los gatos

> noo... no me convence el diseño de los gatos... cambialos... que se vean mejor... pareces gatos flacos... la parte de sus caras mejoralo... no se ven tierno ni hermosos

**Resultado:** se retocaron las proporciones y la cara. Después, a petición del usuario, se recuperó la silueta original del juego.

### 7. Restaurar la silueta y añadir efectos

> ... mejor como estaban al principio... se veian mejor... y añade sonidos

**Resultado:** se restauró la silueta redondeada inicial y se añadieron efectos sonoros sintetizados para acciones del juego.

### 8. Música de fondo

> este ya probe si tiene sonido... puede añadirle algo de fondo para que se escuche??

**Resultado:** se agregó una melodía ambiental sintetizada en bucle, con volumen reducido durante los combates. La tecla `M` silencia o reactiva la música y los efectos.

## Reflexión sobre el uso de IA

- **Qué funcionó:** implementar y probar los cambios por partes ayudó a comprobar el render, la progresión de jefes, el combo y el canal de audio.
- **Errores detectados y corregidos:** el README inicial describía otro juego; durante los cambios también se corrigieron errores de sangría y del render del gato.
- **Ajustes realizados:** se revisaron la velocidad, la dificultad, la silueta de los gatos y el volumen de la música.
- **Aprendizaje:** el código generado debe ejecutarse y verificarse; la documentación también debe contrastarse con el código actual.

