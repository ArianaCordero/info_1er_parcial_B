# PAINT VA
## Proyecto Paint en Arcade 
##### Por Valeria Martinez y Ariana Cordero 

![Python](https://img.shields.io/badge/python-3.10+-blue?logo=python)
![Arcade](https://img.shields.io/badge/arcade-3.3.2-orange?logo=arcade)
![Estado](https://img.shields.io/badge/estado-completo-success)

Aplicación tipo **Paint** desarrollada en Python con la librería [Arcade](https://api.arcade.academy/), como parte del proyecto de la materia de *Infografía*.  
Permite dibujar con diferentes herramientas, cambiar modos de papel, activar cuadrícula, pintar celda por celda, activar un modo arcoíris y guardar/cargar proyectos.

##  Orden de la práctica
> **Implementación de características adicionales**  
>
> - La aplicación cuenta con una herramienta de lápiz implementada.  
> - Se debe implementar: **marcador, spray, borrador, celda**.  
> - **Guardado y carga** de dibujos (se guarda `self.traces` en un archivo de texto con la tecla `O`).  
> - *(Extra)*: interfaz gráfica con botones, selección de herramientas, colores y funcionalidades adicionales.
##  Estructura del código
### `tool.py`
Define las **herramientas de dibujo**: 

| Herramienta | Clase        | Función                                   |
|-------------|-------------|-------------------------------------------|
| Lápiz       | `PencilTool` | Trazo fino, continuo                      |
| Marcador    | `MarkerTool` | Línea gruesa                              |
| Spray       | `SprayTool`  | Puntos aleatorios dispersos               |
| Borrador    | `EraserTool` | Elimina trazos que colisionan             |
| Celda       | `CellTool`   | Pinta cuadrado por cuadrado con cuadrícula |

Todas heredan un patrón común y usan funciones de Arcade (`draw_line_strip`, `draw_points`, `draw_lrbt_rectangle_filled`, etc.).
---
### `main.py`
Controla la **interfaz, entrada de usuario y renderizado**:
- **Interfaz** con botones pequeños en español.  
- **Teclas rápidas**:  
  - `1` Lápiz | `2` Marcador | `3` Spray | `4` Borrador | `5` Celdas  
  - `G` Cuadrícula | `H` Papel rayado (azul/rojo o negro)  
  - `R` Modo arcoíris | `O` Guardar | *Click en botones para alternar*  
- **Panel lateral** con estado de herramienta.  
- **Fondos**: papel clásico, con lineas rojas y azules.
- **Modo arcoíris**: cada trazo adopta un color distinto con al volver a darle click.  
- **Guardar / cargar** dibujos en JSON (`dibujo.txt`).  
---
##  Funcionalidades implementadas

- ✅ Lápiz, marcador, spray, borrador, celdas.  
- ✅ Interfaz gráfica con botones.  
- ✅ Tipos de papeles.  
- ✅ Cuadrícula activable para pintar celda por celda.  
- ✅ Modo arcoíris.  
- ✅ Guardado y carga de proyectos en archivo `.txt`.  
---
## Ejecución
1. Instalar dependencias:  
   ```bash
   pip install arcade==3.3.2````
2. Ejecutar normalmente:
   ```bash
   python main.py
   ```
## Inspiración y base de código (docente → adaptación en este Paint)

```infografia-2-2025-1/
├─ 1._intro_python/
├─ 2._turn_game/
├─ 3._arcade/
├─ 3.1_bresenham/
├─ 4._sprites/
├─ 5._physics/
└─ 6._transformations/
```

A continuación se indica **en qué carpeta/archivo del docente** está la base de cada parte y **qué hicimos nosotros** para adaptarla al Paint:

---

### 1) Lápiz → herramienta modular
- **Docente (base):** `3._arcade/hello_arcade.py` y `3._arcade/basic_events.py`  
  - Uso de eventos de mouse y `draw_point`, `draw_points`, `draw_line`.  
- **Docente (línea continua):** `3.1_bresenham/bresenham.py` (algoritmo para generar secuencias de puntos).  
- **Nuestro cambio:** creamos `PencilTool` en `tool.py`, que guarda coordenadas y las dibuja con `arcade.draw_line_strip`.


### 2) Marcador → mismo algoritmo, mayor grosor
- **Docente (base):** `3._arcade/hello_arcade.py` (parámetro `line_width`).  
- **Nuestro cambio:** `MarkerTool` replica la lógica del lápiz pero dibuja con mayor espesor para simular un marcador.



### 3) Spray → dispersión de puntos aleatorios
- **Docente (base de puntos):** `3._arcade/hello_arcade.py` (`draw_points`).  
- **Nuestro cambio:** `SprayTool` genera puntos aleatorios en un radio alrededor del cursor, que se van acumulando durante el arrastre.



### 4) Borrador → colisión y supresión de trazos
- **Docente (estructura modular):** `2._turn_game/tools.py`  
- **Docente (eventos y listas):** `3._arcade/basic_events.py`  
- **Nuestro cambio:** `EraserTool.erase_at` revisa colisiones con los segmentos de cada trazo y elimina los que caen dentro de un radio.



### 5) Cuadrícula y celda
- **Docente (líneas repetidas):** `3._arcade/game_loop.py` y `3._arcade/primitives.py`  
- **Nuestro cambio:**  
  - En `main.py`, tecla `G` activa cuadrícula.  
  - Creamos `CellTool`, que “imanta” el clic al centro de cada celda y pinta cuadrados completos con `draw_lrbt_rectangle_filled`.



### 6) Papel rayado y papel negro
- **Docente (patrón de líneas):** `3._arcade/hello_arcade.py`  
- **Nuestro cambio:** en `main.py` se dibuja:  
  - **Papel clásico:** líneas horizontales azules + margen vertical roja.  
  - **Papel negro:** mismo patrón en negro.  
  - Se renderizan como fondo antes de los trazos.



### 7) Modo arcoíris
- **Docente (ciclos de listas):** `1._intro_python/dice2.py`  
- **Nuestro cambio:** `_next_rainbow_color()` rota una lista de colores y asigna uno distinto a cada nuevo trazo.



### 8) Interfaz con botones
- **Docente (eventos y estados):** `3._arcade/basic_events.py`  
- **Docente (organización modular):** `2._turn_game/main.py` + `tools.py`  
- **Nuestro cambio:** creamos `Button` en `main.py`, que dibuja rectángulos con íconos vectoriales y ejecuta acciones (`_act_pencil`, `_act_grid_toggle`, etc.).



### 9) Guardado y carga
- **Docente (entrada/salida de archivos):** `1._intro_python/hello.py`  
- **Nuestro cambio:** usamos `json.dump` y `json.load` para guardar y leer `self.traces`.  
  - **Guardar:** tecla `O` → archivo `.txt`.  
  - **Cargar:** `python main.py archivo.txt`.



## Conclusión

Este proyecto **Paint en Arcade** integra en un solo programa las técnicas enseñadas por el docente:  
- Manejo de eventos de teclado y mouse.  
- Uso de listas y diccionarios para almacenar estado.  
- Organización modular en `tool.py` y `main.py`.  
- Dibujo de primitivas con Arcade (`draw_line`, `draw_points`, `draw_line_strip`).  
- Creación de fondos, cuadrículas y patrones repetitivos.  
- Persistencia con lectura y escritura de archivos.  

Cada parte del código parte de un ejemplo visto en `infografia-2-2025-1/` y fue **adaptada, ampliada y unificada** para construir un Paint funcional, con múltiples herramientas, modos de fondo, cuadrícula interactiva, arcoíris dinámico, botones gráficos e incluso guardado/carga de proyectos.

