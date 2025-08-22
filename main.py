import arcade
import json
import sys
from tool import PencilTool, MarkerTool, SprayTool, EraserTool, CellTool

WIDTH = 900
HEIGHT = 600
TITLE = "PaintVA"

TOPBAR_H = 120
ROW1_H = 50
PAD = 10

BTN_H = 36
BTN_GAP = 8
PANEL_W = 240

SWATCH_R = 12
SWATCH_GAP = 12
SWATCH_ROW_GAP = 8

GRID_DEFAULT = 24
GRID_MIN = 8
GRID_MAX = 48

RULE_SPACING = 24  # separación entre líneas de hoja

# Colores (arcade.color)
C_BG = arcade.color.WHITE
C_TOP1 = arcade.color.ALMOND
C_TOP2 = arcade.color.BEIGE
C_SHADOW = arcade.color.BONE
C_PANEL = arcade.color.COOL_GREY
C_PANEL_BORDER = arcade.color.WHITE
C_BTN = arcade.color.LIGHT_SLATE_GRAY
C_BTN_TXT = arcade.color.WHITE
C_BTN_ACTIVE = arcade.color.GOLD
C_BTN_HOVER = arcade.color.SILVER
C_SWATCH_BORDER = arcade.color.WHITE
C_SEP = arcade.color.LIGHT_GRAY
C_HELP = arcade.color.DARK_SLATE_GRAY
C_GRID = arcade.color.LIGHT_GRAY

# Modos de papel
PAPER_NONE = "NONE"
PAPER_RULED_BR = "RULED_BR"  # azul/rojo clásico
PAPER_RULED_BLACK = "RULED_BLACK"


class Button:
    def __init__(self, x, y, label, kind, action):
        self.label = label
        # Calcular ancho según el texto
        text_width = len(label) * 7 + 40  # Aproximación basada en longitud de texto
        self.BTN_W = max(90, min(120, text_width))  # Mínimo 90, máximo 120
        self.rect = (x, y, self.BTN_W, BTN_H)
        self.kind = kind
        self.action = action
        self.hover = False

    def contains(self, x, y):
        rx, ry, rw, rh = self.rect
        return rx <= x <= rx + rw and ry <= y <= ry + rh

    def draw_icon(self, rx, ry, rw, rh, color):
        cx = rx + 18
        cy = ry + rh / 2
        if self.kind == "pencil":
            arcade.draw_line(cx - 8, cy, cx + 8, cy, color, 2)
        elif self.kind == "marker":
            arcade.draw_line(cx - 8, cy, cx + 8, cy, color, 6)
        elif self.kind == "spray":
            pts = [(cx - 6 + i * 3, cy + ((i % 2) * 3 - 1)) for i in range(6)]
            arcade.draw_points(pts, color, 2)
        elif self.kind == "eraser":
            arcade.draw_lrbt_rectangle_filled(cx - 9, cx + 9, cy - 6, cy + 6, arcade.color.WHITE_SMOKE)
            arcade.draw_lrbt_rectangle_outline(cx - 9, cx + 9, cy - 6, cy + 6, arcade.color.BLACK_OLIVE, 1)
        elif self.kind == "cell":
            s = 10
            arcade.draw_lrbt_rectangle_filled(cx - s / 2, cx + s / 2, cy - s / 2, cy + s / 2, color)
            arcade.draw_lrbt_rectangle_outline(cx - s / 2, cx + s / 2, cy - s / 2, cy + s / 2, arcade.color.BLACK, 1)
        elif self.kind == "grid":
            s = 4
            for i in range(2):
                for j in range(2):
                    col = color if (i + j) % 2 == 0 else arcade.color.BLACK_OLIVE
                    arcade.draw_lrbt_rectangle_filled(cx - 6 + i * s, cx - 6 + (i + 1) * s, cy - 4 + j * s,
                                                     cy - 4 + (j + 1) * s, col)
        elif self.kind == "paper":
            # margen roja y líneas azules mini
            arcade.draw_line(cx - 8, cy - 6, cx - 8, cy + 6, arcade.color.RED, 1)
            for dy in (-4, 0, 4):
                arcade.draw_line(cx - 4, cy + dy, cx + 8, cy + dy, arcade.color.BLUE, 1)
        elif self.kind == "clear":
            arcade.draw_line(cx - 8, cy - 6, cx + 8, cy + 6, color, 2)
            arcade.draw_line(cx - 8, cy + 6, cx + 8, cy - 6, color, 2)
        elif self.kind == "save":
            arcade.draw_lrbt_rectangle_filled(cx - 8, cx + 8, cy - 8, cy, color)
            arcade.draw_triangle_filled(cx - 8, cy, cx + 8, cy, cx, cy + 8, color)
        elif self.kind == "rainbow":
            # Dibujar pequeño arcoíris
            colors = [arcade.color.RED, arcade.color.ORANGE, arcade.color.YELLOW,
                      arcade.color.GREEN, arcade.color.BLUE, arcade.color.PURPLE]
            for i, c in enumerate(colors):
                arcade.draw_line(cx - 8 + i * 2.5, cy - 3, cx - 8 + i * 2.5, cy + 3, c, 2)

    def draw(self, active=False):
        rx, ry, rw, rh = self.rect
        arcade.draw_lrbt_rectangle_filled(rx + 2, rx + rw + 2, ry - 2, ry + rh - 2, C_SHADOW)
        arcade.draw_lrbt_rectangle_filled(rx, rx + rw, ry, ry + rh, C_BTN)
        border_color = C_BTN_ACTIVE if active else (C_BTN_HOVER if self.hover else C_BTN_TXT)
        border_w = 2 if active else 1
        arcade.draw_lrbt_rectangle_outline(rx, rx + rw, ry, ry + rh, border_color, border_width=border_w)
        self.draw_icon(rx, ry, rw, rh, C_BTN_TXT)
        arcade.draw_text(self.label, rx + 35, ry + rh / 2 - 7, C_BTN_TXT, 11, anchor_x="left", anchor_y="center")


class Paint(arcade.View):
    def __init__(self, load_path: str = None):
        super().__init__()
        self.background_color = C_BG

        # herramientas / estado
        self.tool = PencilTool()
        self.used_tools = {self.tool.name: self.tool}
        self.color = arcade.color.BLUE
        self.rainbow_on = False
        self.rainbow_colors = [
            arcade.color.RED, arcade.color.ORANGE, arcade.color.YELLOW,
            arcade.color.GREEN, arcade.color.BLUE, arcade.color.PURPLE,
            arcade.color.PINK, arcade.color.CYAN, arcade.color.BROWN
        ]
        self.rainbow_idx = 0

        # paper / grid
        self.paper_mode = PAPER_NONE
        self.grid_on = False
        self.grid_size = GRID_DEFAULT
        self.last_mouse = (0, 0)

        # ui
        self.traces = []
        self.btns_row1 = []
        self.swatches = []  # [(x,y), r, color]
        self.help_text = "A rojo  S verde  D azul  F negro  |  1 Lápiz 2 Marcador 3 Spray 4 Borrador 5 Celdas  |  O Guardar  |  Cuadrícula:G  |  Papel:H  |  Arcoíris:R"

        self._layout_build()
        if load_path is not None:
            try:
                with open(load_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for t in data:
                    item = {
                        "tool": t["tool"],
                        "color": tuple(t["color"]),
                        "trace": [tuple(p) for p in t["trace"]],
                    }
                    if t["tool"] == "CELL":
                        item["size"] = t.get("size", GRID_DEFAULT)
                    self.traces.append(item)
                    # asegurar herramientas registradas
                    if t["tool"] == "PENCIL" and "PENCIL" not in self.used_tools:
                        self.used_tools["PENCIL"] = PencilTool()
                    elif t["tool"] == "MARKER" and "MARKER" not in self.used_tools:
                        self.used_tools["MARKER"] = MarkerTool()
                    elif t["tool"] == "SPRAY" and "SPRAY" not in self.used_tools:
                        self.used_tools["SPRAY"] = SprayTool()
                    elif t["tool"] == "CELL" and "CELL" not in self.used_tools:
                        self.used_tools["CELL"] = CellTool()
                print(f"Cargado: {load_path}")
            except Exception as e:
                self.traces = []
                print(f"No se pudo cargar {load_path}: {e}")

    # --------- layout ----------
    def _layout_build(self):
        left = PAD
        right = WIDTH - PANEL_W - PAD
        row1_y = HEIGHT - ROW1_H - (PAD // 2)
        x = left
        specs = [
            ("Lápiz [1]", "pencil", self._act_pencil),
            ("Marcador [2]", "marker", self._act_marker),
            ("Spray [3]", "spray", self._act_spray),
            ("Borrador [4]", "eraser", self._act_eraser),
            ("Celda [5]", "cell", self._act_cell),
            ("Cuadrícula [G]", "grid", self._act_grid_toggle),
            ("Papel [H]", "paper", self._act_paper_cycle),
            ("Arcoíris [R]", "rainbow", self._act_rainbow),
            ("Guardar [O]", "save", self._act_save),
            ("Limpiar", "clear", self._act_clear),
        ]
        self.btns_row1 = []
        for label, kind, act in specs:
            btn = Button(x, row1_y, label, kind, act)
            if x + btn.BTN_W > right:
                break
            self.btns_row1.append(btn)
            x += btn.BTN_W + BTN_GAP

        # Swatches: 2 filas si no entran en una
        work_left, work_right = left, right
        sw_area_bottom = HEIGHT - TOPBAR_H + 10
        colors = [
            arcade.color.RED, arcade.color.ORANGE, arcade.color.YELLOW,
            arcade.color.GREEN, arcade.color.CYAN, arcade.color.BLUE,
            arcade.color.PURPLE, arcade.color.PINK, arcade.color.BROWN,
            arcade.color.BLACK, arcade.color.GRAY, arcade.color.WHITE_SMOKE
        ]
        sw_diam = SWATCH_R * 2
        max_per_row = int((work_right - work_left) // (sw_diam + SWATCH_GAP))
        max_per_row = max(5, min(max_per_row, len(colors)))

        rows = [colors[:max_per_row], colors[max_per_row:]]
        self.swatches.clear()
        for r_i, row in enumerate(rows):
            if not row: continue
            total_w = len(row) * sw_diam + (len(row) - 1) * SWATCH_GAP
            start_x = work_left + (work_right - work_left - total_w) / 2 + SWATCH_R
            y = sw_area_bottom + SWATCH_R + (SWATCH_ROW_GAP + sw_diam) * r_i
            x = start_x
            for col in row:
                self.swatches.append(((x, y), SWATCH_R, col))
                x += sw_diam + SWATCH_GAP

        self.panel_rect = (WIDTH - PANEL_W - PAD, WIDTH - PAD, HEIGHT - TOPBAR_H + PAD, HEIGHT - PAD)

    # --------- acciones ----------
    def _act_pencil(self):
        self.tool = PencilTool();
        self.used_tools[self.tool.name] = self.tool

    def _act_marker(self):
        self.tool = MarkerTool();
        self.used_tools[self.tool.name] = self.tool

    def _act_spray(self):
        self.tool = SprayTool();
        self.used_tools[self.tool.name] = self.tool

    def _act_eraser(self):
        self.tool = EraserTool();
        self.used_tools[self.tool.name] = self.tool

    def _act_cell(self):
        self.tool = CellTool();
        self.used_tools[self.tool.name] = self.tool

    def _act_grid_toggle(self):
        self.grid_on = not self.grid_on

    def _act_paper_cycle(self):
        if self.paper_mode == PAPER_NONE:
            self.paper_mode = PAPER_RULED_BR
        elif self.paper_mode == PAPER_RULED_BR:
            self.paper_mode = PAPER_RULED_BLACK
        else:
            self.paper_mode = PAPER_NONE

    def _act_rainbow(self):
        self.rainbow_on = not self.rainbow_on

    def _act_clear(self):
        self.traces.clear()

    def _act_save(self):
        try:
            out = []
            for t in self.traces:
                item = {"tool": t["tool"], "color": list(t["color"]), "trace": [list(p) for p in t["trace"]]}
                if t["tool"] == "CELL":
                    item["size"] = int(t.get("size", self.grid_size))
                out.append(item)
            with open("dibujo.txt", "w", encoding="utf-8") as f:
                json.dump(out, f)
            print("Guardado en dibujo.txt")
        except Exception as e:
            print(f"No se pudo guardar: {e}")

    # --------- helpers ----------
    def _snap_to_cell_center(self, x, y):
        size = self.grid_size
        cx = int(x // size) * size + size / 2
        cy = int(y // size) * size + size / 2
        return (cx, cy)

    def _next_rainbow_color(self):
        c = self.rainbow_colors[self.rainbow_idx % len(self.rainbow_colors)]
        self.rainbow_idx += 1
        return c

    # --------- input ----------
    def on_mouse_motion(self, x, y, dx, dy):
        self.last_mouse = (x, y)
        for b in self.btns_row1:
            b.hover = b.contains(x, y)

    def on_key_press(self, symbol, modifiers):
        if symbol in (arcade.key.KEY_1, arcade.key.NUM_1):
            self._act_pencil()
        elif symbol in (arcade.key.KEY_2, arcade.key.NUM_2):
            self._act_marker()
        elif symbol in (arcade.key.KEY_3, arcade.key.NUM_3):
            self._act_spray()
        elif symbol in (arcade.key.KEY_4, arcade.key.NUM_4):
            self._act_eraser()
        elif symbol in (arcade.key.KEY_5, arcade.key.NUM_5):
            self._act_cell()
        elif symbol == arcade.key.A:
            self.color = arcade.color.RED
        elif symbol == arcade.key.S:
            self.color = arcade.color.GREEN
        elif symbol == arcade.key.D:
            self.color = arcade.color.BLUE
        elif symbol == arcade.key.F:
            self.color = arcade.color.BLACK
        elif symbol == arcade.key.G:
            self._act_grid_toggle()
        elif symbol == arcade.key.H:
            self._act_paper_cycle()
        elif symbol == arcade.key.R:
            self._act_rainbow()
        elif symbol == arcade.key.O:
            self._act_save()
        elif symbol == arcade.key.Z:
            self.grid_size = max(GRID_MIN, self.grid_size - 2)
        elif symbol == arcade.key.X:
            self.grid_size = min(GRID_MAX, self.grid_size + 2)
        self.used_tools[self.tool.name] = self.tool

    def _click_ui(self, x, y):
        for b in self.btns_row1:
            if b.contains(x, y):
                b.action();
                return True
        for (sx, sy), r, col in self.swatches:
            if (x - sx) ** 2 + (y - sy) ** 2 <= r * r:
                self.color = col;
                return True
        return False

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            if y >= HEIGHT - TOPBAR_H:
                self._click_ui(x, y);
                return

            # Si grid ON: pinta celdas completas (excepto borrador)
            if self.grid_on and not isinstance(self.tool, EraserTool):
                cx, cy = self._snap_to_cell_center(x, y)
                if "CELL" not in self.used_tools:
                    self.used_tools["CELL"] = CellTool()
                color = self._next_rainbow_color() if self.rainbow_on else self.color
                self.traces.append({"tool": "CELL", "color": color, "trace": [(cx, cy)], "size": int(self.grid_size)})
                return

            # Comportamiento normal por herramienta
            if isinstance(self.tool, EraserTool):
                self.tool.erase_at(self.traces, x, y)
            elif isinstance(self.tool, SprayTool):
                color = self._next_rainbow_color() if self.rainbow_on else self.color
                pts = self.tool.scatter(x, y)
                self.traces.append({"tool": self.tool.name, "color": color, "trace": pts})
            elif isinstance(self.tool, CellTool):
                color = self._next_rainbow_color() if self.rainbow_on else self.color
                cx, cy = self._snap_to_cell_center(x, y)
                self.traces.append({"tool": "CELL", "color": color, "trace": [(cx, cy)], "size": int(self.grid_size)})
            else:
                color = self._next_rainbow_color() if self.rainbow_on else self.color
                self.traces.append({"tool": self.tool.name, "color": color, "trace": [(x, y)]})

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if buttons & arcade.MOUSE_BUTTON_LEFT:
            if y >= HEIGHT - TOPBAR_H: return

            if self.grid_on and not isinstance(self.tool, EraserTool):
                if self.traces:
                    cx, cy = self._snap_to_cell_center(x, y)
                    last = self.traces[-1]["trace"][-1]
                    if (abs(last[0] - cx) > 1e-6) or (abs(last[1] - cy) > 1e-6):
                        self.traces[-1]["trace"].append((cx, cy))
                    self.traces[-1]["size"] = int(self.grid_size)
                return

            if isinstance(self.tool, EraserTool):
                self.tool.erase_at(self.traces, x, y)
            elif isinstance(self.tool, SprayTool):
                if self.traces: self.traces[-1]["trace"].extend(self.tool.scatter(x, y))
            elif isinstance(self.tool, CellTool):
                if self.traces:
                    cx, cy = self._snap_to_cell_center(x, y)
                    last = self.traces[-1]["trace"][-1]
                    if (abs(last[0] - cx) > 1e-6) or (abs(last[1] - cy) > 1e-6):
                        self.traces[-1]["trace"].append((cx, cy))
                    self.traces[-1]["size"] = int(self.grid_size)
            else:
                if self.traces: self.traces[-1]["trace"].append((x, y))

    # --------- dibujo ----------
    def _draw_panel(self):
        left, right, bottom, top = self.panel_rect
        arcade.draw_lrbt_rectangle_filled(left + 2, right + 2, bottom - 2, top - 2, C_SHADOW)
        arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, C_PANEL)
        arcade.draw_lrbt_rectangle_outline(left, right, bottom, top, C_PANEL_BORDER, 1)
        
        # Información de herramienta (alineada a la izquierda)
        arcade.draw_text(f"Herramienta: {self.tool.name}", left + 10, top - 24, arcade.color.WHITE, 12)
        
        # Información de cuadrícula y papel (alineada a la izquierda)
        gy = bottom + 20
        arcade.draw_text(f"Cuadrícula: {'ON' if self.grid_on else 'OFF'}  (G)", left + 10, gy + 15, arcade.color.WHITE, 10)
        arcade.draw_text(f"Celda: {self.grid_size}px  (Z-/X+)", left + 10, gy, arcade.color.WHITE, 10)
        
        # Papel y arcoíris (alineados a la izquierda)
        pm = {"NONE": "Sin papel", "RULED_BR": "Hoja azul/roja", "RULED_BLACK": "Hoja negra"}[self.paper_mode]
        arcade.draw_text(f"Papel: {pm}  (H)", left + 10, gy + 30, arcade.color.WHITE, 10)
        arcade.draw_text(f"Arcoíris: {'ON' if self.rainbow_on else 'OFF'}  (R)", left + 10, gy + 45, arcade.color.WHITE, 10)
        
        # Color seleccionado (en la parte inferior derecha del panel)
        cx, cy = right - 25, bottom + 25
        arcade.draw_circle_filled(cx, cy, 15, self.color)  # Más grande
        arcade.draw_circle_outline(cx, cy, 17, arcade.color.BLACK, 2)  # Borde más grueso
        arcade.draw_text("Color actual", cx, cy + 25, arcade.color.WHITE, 10, anchor_x="center")

    def _draw_ruled_paper(self):
        if self.paper_mode == PAPER_NONE:
            return
        top = HEIGHT - TOPBAR_H
        # margen vertical
        margin_x = 80
        if self.paper_mode == PAPER_RULED_BR:
            vcol = arcade.color.RED
            hcol = arcade.color.BLUE
        else:
            vcol = arcade.color.BLACK
            hcol = arcade.color.BLACK
        arcade.draw_line(margin_x, 0, margin_x, top, vcol, 2)
        # líneas horizontales
        y = 0
        while y <= top:
            arcade.draw_line(0, y, WIDTH, y, hcol, 1)
            y += RULE_SPACING

    def _draw_grid(self):
        if not self.grid_on: return
        size = self.grid_size
        top = HEIGHT - TOPBAR_H
        x = 0
        while x <= WIDTH:
            arcade.draw_line(x, 0, x, top, C_GRID, 1)
            x += size
        y = 0
        while y <= top:
            arcade.draw_line(0, y, WIDTH, y, C_GRID, 1)
            y += size
        mx, my = self.last_mouse
        if my < top:
            cx = int(mx // size) * size + size / 2
            cy = int(my // size) * size + size / 2
            half = size / 2
            arcade.draw_lrbt_rectangle_outline(cx - half, cx + half, cy - half, cy + half, arcade.color.GOLD, 1)

    def on_draw(self):
        self.clear()

        # Fondo de papel (debajo de los trazos)
        self._draw_ruled_paper()

        # Lienzo (trazos)
        for tool in self.used_tools.values():
            tool.draw_traces(self.traces)

        # Grid encima del lienzo (opcional)
        self._draw_grid()

        # Topbar en dos bandas
        top1_bottom = HEIGHT - ROW1_H
        arcade.draw_lrbt_rectangle_filled(0, WIDTH, top1_bottom, HEIGHT, C_TOP1)
        arcade.draw_lrbt_rectangle_filled(0, WIDTH, HEIGHT - TOPBAR_H, top1_bottom, C_TOP2)
        arcade.draw_line(0, HEIGHT - TOPBAR_H, WIDTH, HEIGHT - TOPBAR_H, C_SEP, 1)

        # Panel derecho
        self._draw_panel()

        # Botones fila 1
        for b in self.btns_row1:
            is_active = (
                    (b.kind == "pencil" and isinstance(self.tool, PencilTool)) or
                    (b.kind == "marker" and isinstance(self.tool, MarkerTool)) or
                    (b.kind == "spray" and isinstance(self.tool, SprayTool)) or
                    (b.kind == "eraser" and isinstance(self.tool, EraserTool)) or
                    (b.kind == "cell" and isinstance(self.tool, CellTool)) or
                    (b.kind == "grid" and self.grid_on) or
                    (b.kind == "paper" and self.paper_mode != PAPER_NONE) or
                    (b.kind == "rainbow" and self.rainbow_on)
            )
            b.draw(active=is_active)

        # Swatches (2 filas si hace falta)
        for (sx, sy), r, col in self.swatches:
            arcade.draw_circle_filled(sx, sy, r, col)
            border = C_SWATCH_BORDER if col != self.color else C_BTN_ACTIVE
            arcade.draw_circle_outline(sx, sy, r + 1, border, 1)

        # Footer ayuda
        arcade.draw_lrbt_rectangle_filled(0, WIDTH, 0, 22, arcade.color.LIGHT_GRAY)
        arcade.draw_text(
            self.help_text,
            WIDTH / 2, 6,
            C_HELP, 10,
            anchor_x="center"
        )


def main():
    window = arcade.Window(WIDTH, HEIGHT, TITLE)
    if len(sys.argv) > 1:
        app = Paint(sys.argv[1])
    else:
        app = Paint()
    window.show_view(app)
    arcade.run()


if __name__ == "__main__":
    main()