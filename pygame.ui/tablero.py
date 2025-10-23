import sys
import pygame
from typing import List, Tuple, Optional

Color = Tuple[int, int, int]
Point = Tuple[float, float]
Triangle = Tuple[Point, Point, Point]

# Colores
WOOD: Color = (186, 140, 99)
WOOD_DARK: Color = (139, 94, 60)
POINT_A: Color = (234, 225, 210)
POINT_B: Color = (86, 60, 50)
BAR: Color = (70, 50, 40)
FRAME: Color = (50, 35, 25)
HILITE: Color = (255, 210, 0)
TEXT: Color = (25, 25, 25)
BG: Color = (20, 20, 20)

class BackgammonUI:
    def __init__(self, width: int = 1000, height: int = 700) -> None:
        pygame.init()
        pygame.display.set_caption("Backgammon - Tablero")
        self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 20)

        # Layout
        self.margin = 20
        self.bar_frac = 0.06  # ancho de barra relativo al tablero
        self.triangles: List[Triangle] = []
        self.labels: List[int] = []  # numeración estándar BG en cada triángulo
        self.point_colors: List[Color] = []
        self.board_rect = pygame.Rect(0, 0, 0, 0)
        self.bar_rect = pygame.Rect(0, 0, 0, 0)
        self.tri_height = 0
        self.point_width = 0

        self.hover_index: Optional[int] = None

        self.rebuild_geometry(*self.screen.get_size())

    def rebuild_geometry(self, width: int, height: int) -> None:
        self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)

        # Rectángulo del tablero (madera) dentro de márgenes
        board_w = width - 2 * self.margin
        board_h = height - 2 * self.margin
        self.board_rect = pygame.Rect(self.margin, self.margin, board_w, board_h)

        # Barra central y tamaños
        bar_w = max(48, int(board_w * self.bar_frac))
        # 12 puntas horizontales en total por fila (6 + barra + 6)
        self.point_width = (board_w - bar_w) / 12.0
        self.tri_height = (board_h / 2.0) - 24  # deja espacio para fichas

        bar_x = self.margin + int(self.point_width * 6)
        self.bar_rect = pygame.Rect(bar_x, self.margin, bar_w, board_h)

        # Construcción de triángulos (0..11 fila superior izq->der, 12..23 fila inferior izq->der)
        self.triangles.clear()
        self.point_colors.clear()
        self.labels = [0] * 24

        # Numeración estándar:
        # - Fila superior (izq->der): 13..24
        # - Fila inferior (izq->der): 12..1
        for i in range(12):
            self.labels[i] = 13 + i
        for i in range(12):
            self.labels[12 + i] = 12 - i

        # Generar triángulos superiores
        for col in range(12):
            x0 = self.margin + col * self.point_width + (bar_w if col >= 6 else 0)
            base_y = self.margin
            apex_y = self.margin + self.tri_height
            tri: Triangle = ((x0, base_y), (x0 + self.point_width, base_y), (x0 + self.point_width / 2.0, apex_y))
            self.triangles.append(tri)
            self.point_colors.append(POINT_A if (col % 2 == 0) else POINT_B)

        # Generar triángulos inferiores
        for col in range(12):
            x0 = self.margin + col * self.point_width + (bar_w if col >= 6 else 0)
            base_y = self.margin + board_h
            apex_y = self.margin + board_h - self.tri_height
            tri: Triangle = ((x0, base_y), (x0 + self.point_width, base_y), (x0 + self.point_width / 2.0, apex_y))
            self.triangles.append(tri)
            # Alternar colores igual que arriba
            self.point_colors.append(POINT_A if (col % 2 == 0) else POINT_B)

    def point_in_triangle(self, p: Point, t: Triangle) -> bool:
        # Barycentric technique
        (x, y) = p
        (x1, y1), (x2, y2), (x3, y3) = t

        def sign(px, py, qx, qy, rx, ry):
            return (px - rx) * (qy - ry) - (qx - rx) * (py - ry)

        b1 = sign(x, y, x1, y1, x2, y2) < 0.0
        b2 = sign(x, y, x2, y2, x3, y3) < 0.0
        b3 = sign(x, y, x3, y3, x1, y1) < 0.0
        return (b1 == b2) and (b2 == b3)

    def find_point_index(self, pos: Point) -> Optional[int]:
        for i, tri in enumerate(self.triangles):
            if self.point_in_triangle(pos, tri):
                return i
        return None

    def draw_board(self) -> None:
        self.screen.fill(BG)

        # Marco exterior
        pygame.draw.rect(self.screen, FRAME, self.board_rect.inflate(16, 16), border_radius=10)
        # Fondo madera
        pygame.draw.rect(self.screen, WOOD, self.board_rect, border_radius=6)

        # Barra central
        pygame.draw.rect(self.screen, BAR, self.bar_rect)

        # Puntas
        for i, tri in enumerate(self.triangles):
            pygame.draw.polygon(self.screen, self.point_colors[i], tri)

        # Hover highlight
        if self.hover_index is not None:
            pygame.draw.polygon(self.screen, HILITE, self.triangles[self.hover_index], width=3)

        # Separador horizontal (centro)
        cx = self.board_rect.centerx
        pygame.draw.line(self.screen, WOOD_DARK, (self.board_rect.left, cx - cx + self.board_rect.centery),
                         (self.board_rect.right, cx - cx + self.board_rect.centery), 2)

        # Numeración
        for i, tri in enumerate(self.triangles):
            lbl = str(self.labels[i])
            text = self.font.render(lbl, True, TEXT)
            (x1, y1), (x2, y2), (x3, y3) = tri
            base_y = (y1 + y2) / 2.0
            is_top = y1 < y3  # triángulo hacia abajo
            if is_top:
                # colocar el número un poco debajo de la base
                pos = (x1 + (x2 - x1) / 2.0 - text.get_width() / 2.0, base_y + 6)
            else:
                # colocar el número un poco encima de la base
                pos = (x1 + (x2 - x1) / 2.0 - text.get_width() / 2.0, base_y - text.get_height() - 6)
            self.screen.blit(text, pos)

    def run(self) -> None:
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    self.rebuild_geometry(event.w, event.h)
                elif event.type == pygame.MOUSEMOTION:
                    self.hover_index = self.find_point_index(event.pos)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    idx = self.find_point_index(event.pos)
                    if idx is not None:
                        print(f"Clic en punta índice={idx} (número {self.labels[idx]})")

            self.draw_board()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit(0)

def main():
    ui = BackgammonUI(1000, 700)
    ui.run()

if __name__ == "__main__":
    main()
