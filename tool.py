import arcade
import math
import random
from typing import Protocol

class Tool(Protocol):
    name: str
    def draw_traces(self, traces: list[dict]):
        ...
    def get_name(self):
        return self.name

class PencilTool(Tool):
    name = "PENCIL"
    def draw_traces(self, traces: list[dict]):
        for t in traces:
            if t["tool"] == self.name:
                pts = t["trace"]
                if len(pts) >= 2:
                    arcade.draw_line_strip(pts, t["color"], 3)
                elif len(pts) == 1:
                    x, y = pts[0]
                    arcade.draw_point(x, y, t["color"], 3)

class MarkerTool(Tool):
    name = "MARKER"
    def draw_traces(self, traces: list[dict]):
        for t in traces:
            if t["tool"] == self.name:
                pts = t["trace"]
                if len(pts) >= 2:
                    arcade.draw_line_strip(pts, t["color"], 10)
                elif len(pts) == 1:
                    x, y = pts[0]
                    arcade.draw_point(x, y, t["color"], 10)

class SprayTool(Tool):
    name = "SPRAY"
    def draw_traces(self, traces: list[dict]):
        for t in traces:
            if t["tool"] == self.name and t["trace"]:
                arcade.draw_points(t["trace"], t["color"], 5)

    @staticmethod
    def scatter(cx: float, cy: float, count: int = 28, radius: float = 16.0):
        pts = []
        for _ in range(count):
            r = random.uniform(0.0, radius)
            a = random.uniform(0.0, 2.0 * math.pi)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        return pts

class CellTool(Tool):
    name = "CELL"
    def draw_traces(self, traces: list[dict]):
        for t in traces:
            if t["tool"] == self.name:
                size = t.get("size", 16)
                half = size / 2
                for (x, y) in t["trace"]:
                    arcade.draw_lrbt_rectangle_filled(x - half, x + half, y - half, y + half, t["color"])
                    arcade.draw_lrbt_rectangle_outline(x - half, x + half, y - half, y + half, arcade.color.BLACK, 1)

class EraserTool(Tool):
    name = "ERASER"
    def draw_traces(self, traces: list[dict]):
        return

    def erase_at(self, traces: list[dict], x: float, y: float, radius: float = 12.0):
        r2 = radius * radius
        keep = []
        for t in traces:
            pts = t["trace"]
            hit = False
            for (px, py) in pts:
                dx = px - x
                dy = py - y
                if dx * dx + dy * dy <= r2:
                    hit = True
                    break
            if not hit:
                keep.append(t)
        traces.clear()
        traces.extend(keep)
