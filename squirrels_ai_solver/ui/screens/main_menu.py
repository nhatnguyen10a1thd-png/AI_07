# ui/screens/main_menu.py
import sys
import pygame
from ui.screen_manager import ScreenBase
from ui.components.button import Button
from core.constants import BG_COLOR, TEXT_COLOR, PANEL_COLOR

class MainMenuScreen(ScreenBase):
    """Giao diện Menu chính với hiệu ứng bắt mắt."""
    def __init__(self, app):
        super().__init__(app)
        self.buttons = []
        self._build_buttons()

    def _build_buttons(self):
        button_font = self.app.fonts["button"]
        W = self.app.width
        H = self.app.height

        # Define menu choices and target screens
        choices = [
            ("CHƠI GAME (PLAY)", lambda: self.app.switch_to_screen("level_select", mode="play")),
            ("AI SOLVER", lambda: self.app.switch_to_screen("level_select", mode="ai")),
            ("TRÌNH DIỄN THUẬT TOÁN", lambda: self.app.switch_to_screen("level_select", mode="visualizer")),
            ("BÁO CÁO HIỆU NĂNG", lambda: self.app.switch_to_screen("level_select", mode="report")),
            ("THOÁT (QUIT)", lambda: pygame.event.post(pygame.event.Event(pygame.QUIT)))
        ]

        btn_w = 360
        btn_h = 50
        start_y = int(H * 0.38)

        self.buttons = []
        for idx, (label, callback) in enumerate(choices):
            rect = (
                (W - btn_w) // 2,
                start_y + idx * (btn_h + 18),
                btn_w,
                btn_h
            )
            color = (139, 115, 85) if idx == 0 else (79, 110, 138)
            self.buttons.append(
                Button(
                    rect=rect,
                    text=label,
                    font=button_font,
                    callback=callback,
                    color=color,
                    border_radius=10
                )
            )

    def on_enter(self, **kwargs):
        """Rebuild buttons each time we return to this screen (for resize support)."""
        self._build_buttons()

    def handle_event(self, event):
        for btn in self.buttons:
            btn.handle_event(event)

    def draw(self, surface):
        W = self.app.width
        H = self.app.height

        # 1. Clear background
        surface.fill(BG_COLOR)

        # 2. Draw a decorative wooden panel board behind menu content
        panel_w = 520
        panel_h = int(H * 0.8)
        panel_rect = pygame.Rect(
            (W - panel_w) // 2,
            int(H * 0.08),
            panel_w,
            panel_h
        )
        pygame.draw.rect(surface, PANEL_COLOR, panel_rect, border_radius=20)
        pygame.draw.rect(surface, (220, 215, 205), panel_rect, width=2, border_radius=20)

        # 3. Render Game Title
        title_font = self.app.fonts["title_huge"]
        sub_font = self.app.fonts["title"]

        title_surf = title_font.render("SQUIRRELS", True, (139, 115, 85))
        title_rect = title_surf.get_rect(centerx=W // 2, y=int(H * 0.11))
        surface.blit(title_surf, title_rect)

        sub_surf = sub_font.render("GO NUTS! AI SOLVER", True, TEXT_COLOR)
        sub_rect = sub_surf.get_rect(centerx=W // 2, y=int(H * 0.23))
        surface.blit(sub_surf, sub_rect)

        # Draw decorative separator line
        sep_y = int(H * 0.32)
        pygame.draw.line(surface, (180, 150, 110), (panel_rect.left + 50, sep_y), (panel_rect.right - 50, sep_y), width=2)

        # 4. Draw buttons
        for btn in self.buttons:
            btn.draw(surface)

        # Draw credits at the bottom
        credit_font = self.app.fonts["body_small"]
        credit_surf = credit_font.render("Do an Tri Tue Nhan Tao - Mon hoc AI Search", True, (160, 155, 145))
        credit_rect = credit_surf.get_rect(centerx=W // 2, y=H - 50)
        surface.blit(credit_surf, credit_rect)
