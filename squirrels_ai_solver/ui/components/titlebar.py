# ui/components/titlebar.py
"""
Thanh tiêu đề tùy chỉnh hiển thị ở trên cùng màn hình.
Nút Minimize | Fullscreen-toggle | Close — vẽ bằng pygame.draw thuần (không dùng font unicode
để tránh hiện tượng ô vuông trên hệ thống thiếu font Segoe UI Symbol).
"""
import pygame
import sys

try:
    import ctypes
    _HAS_CTYPES = True
except ImportError:
    _HAS_CTYPES = False

TITLEBAR_H = 36  # chiều cao thanh tiêu đề (px)

# Màu sắc
_BAR_BG      = (50,  48,  46)
_BAR_TITLE   = (235, 230, 220)
_BTN_DEFAULT = (65,  63,  60)
_BTN_CLOSE_H = (196,  43,  28)
_BTN_MIN_H   = (200, 160,  30)
_BTN_MAX_H   = ( 45, 140,  75)
_ICON_COLOR  = (230, 228, 224)


class TitleBar:
    """Thanh tiêu đề tùy chỉnh dành cho chế độ fullscreen / borderless."""

    def __init__(self, app):
        self.app = app
        self._is_fullscreen = True
        self._hovered = None   # "min" | "max" | "close" | None
        self._btn_size   = 28
        self._btn_margin = 6
        self._rebuild()

    # ------------------------------------------------------------------
    def _rebuild(self):
        W = self.app.width
        s = self._btn_size
        m = self._btn_margin
        right = W - m
        self._close_rect = pygame.Rect(right - s,            4, s, s)
        self._max_rect   = pygame.Rect(right - 2*s - m,     4, s, s)
        self._min_rect   = pygame.Rect(right - 3*s - 2*m,   4, s, s)

    # ------------------------------------------------------------------
    def toggle_fullscreen(self):
        self._is_fullscreen = not self._is_fullscreen
        if self._is_fullscreen:
            self.app.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.app.screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
        self.app.width  = self.app.screen.get_width()
        self.app.height = self.app.screen.get_height()
        self._rebuild()

    def minimize(self):
        """Thu nhỏ xuống taskbar (Windows)."""
        if _HAS_CTYPES and sys.platform == "win32":
            hwnd = pygame.display.get_wm_info().get("window", 0)
            if hwnd:
                ctypes.windll.user32.ShowWindow(hwnd, 6)  # SW_MINIMIZE

    # ------------------------------------------------------------------
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            pos = event.pos
            if   self._close_rect.collidepoint(pos): self._hovered = "close"
            elif self._max_rect.collidepoint(pos):   self._hovered = "max"
            elif self._min_rect.collidepoint(pos):   self._hovered = "min"
            else:                                    self._hovered = None
            return False   # không tiêu thụ sự kiện move

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            if self._close_rect.collidepoint(pos):
                self.app.running = False;  return True
            if self._max_rect.collidepoint(pos):
                self.toggle_fullscreen();  return True
            if self._min_rect.collidepoint(pos):
                self.minimize();           return True
            if pos[1] < TITLEBAR_H:
                return True   # click trên bar nhưng không trúng nút — chặn

        return False

    # ------------------------------------------------------------------
    def draw(self, surface):
        W = self.app.width
        CY = TITLEBAR_H // 2   # vertical center of bar

        # Nền + đường phân cách
        pygame.draw.rect(surface, _BAR_BG, (0, 0, W, TITLEBAR_H))
        pygame.draw.line(surface, (70, 68, 64), (0, TITLEBAR_H - 1), (W, TITLEBAR_H - 1), 1)

        # Tiêu đề app (trái)
        font = self.app.fonts.get("body_small") or self.app.fonts["body"]
        title_surf = font.render("Squirrels Go Nuts!  —  AI Search Solver", True, _BAR_TITLE)
        surface.blit(title_surf, title_surf.get_rect(midleft=(12, CY)))

        # Nhãn chế độ (giữa)
        mode_text  = "[ Fullscreen ]" if self._is_fullscreen else "[ Windowed ]"
        mode_surf  = font.render(mode_text, True, (160, 155, 145))
        surface.blit(mode_surf, mode_surf.get_rect(center=(W // 2, CY)))

        # Vẽ 3 nút bằng hình học — không cần font unicode
        _draw_btn_minimize(surface, self._min_rect,   self._hovered == "min")
        _draw_btn_maximize(surface, self._max_rect,   self._hovered == "max",
                           self._is_fullscreen)
        _draw_btn_close   (surface, self._close_rect, self._hovered == "close")


# ── Helpers vẽ icon bằng pygame.draw ────────────────────────────────────────

def _btn_bg(surface, rect, hover, hover_color):
    color = hover_color if hover else _BTN_DEFAULT
    pygame.draw.rect(surface, color, rect, border_radius=6)


def _draw_btn_minimize(surface, rect, hover):
    """Dấu gạch ngang ─ ở giữa nút."""
    _btn_bg(surface, rect, hover, _BTN_MIN_H)
    cx, cy = rect.center
    hw = 7   # half-width của thanh gạch
    pygame.draw.rect(surface, _ICON_COLOR, (cx - hw, cy - 1, hw * 2, 2))


def _draw_btn_maximize(surface, rect, hover, is_fullscreen):
    """
    Fullscreen  → hình vuông nhỏ (thu về cửa sổ)
    Windowed    → mũi tên 4 góc (phóng to toàn màn)
    """
    _btn_bg(surface, rect, hover, _BTN_MAX_H)
    cx, cy = rect.center
    if is_fullscreen:
        # Hình vuông rỗng → "thu nhỏ thành cửa sổ"
        s = 8
        pygame.draw.rect(surface, _ICON_COLOR, (cx - s, cy - s, s*2, s*2), width=2)
        # Đường nhỏ ở góc trên-phải (chồng lên) để biểu thị "restore"
        pygame.draw.rect(surface, _ICON_COLOR, (cx - s + 3, cy - s - 3, s*2, s*2), width=2)
    else:
        # 4 mũi tên hướng ra ngoài → "phóng to fullscreen"
        d = 7   # khoảng cách từ tâm đến đỉnh mũi
        lw = 2  # line width
        # ↖
        pygame.draw.line(surface, _ICON_COLOR, (cx - d, cy - d), (cx - d + 4, cy - d), lw)
        pygame.draw.line(surface, _ICON_COLOR, (cx - d, cy - d), (cx - d, cy - d + 4), lw)
        # ↗
        pygame.draw.line(surface, _ICON_COLOR, (cx + d, cy - d), (cx + d - 4, cy - d), lw)
        pygame.draw.line(surface, _ICON_COLOR, (cx + d, cy - d), (cx + d, cy - d + 4), lw)
        # ↙
        pygame.draw.line(surface, _ICON_COLOR, (cx - d, cy + d), (cx - d + 4, cy + d), lw)
        pygame.draw.line(surface, _ICON_COLOR, (cx - d, cy + d), (cx - d, cy + d - 4), lw)
        # ↘
        pygame.draw.line(surface, _ICON_COLOR, (cx + d, cy + d), (cx + d - 4, cy + d), lw)
        pygame.draw.line(surface, _ICON_COLOR, (cx + d, cy + d), (cx + d, cy + d - 4), lw)


def _draw_btn_close(surface, rect, hover):
    """Dấu X vẽ bằng 2 đường chéo."""
    _btn_bg(surface, rect, hover, _BTN_CLOSE_H)
    cx, cy = rect.center
    d  = 6   # khoảng cách từ tâm
    lw = 2
    pygame.draw.line(surface, _ICON_COLOR, (cx - d, cy - d), (cx + d, cy + d), lw)
    pygame.draw.line(surface, _ICON_COLOR, (cx + d, cy - d), (cx - d, cy + d), lw)
