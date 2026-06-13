# ui/components/modal.py
import pygame
from core.constants import SCREEN_WIDTH, SCREEN_HEIGHT, BG_COLOR, TEXT_COLOR, PANEL_COLOR, BORDER_COLOR
from ui.components.button import Button

class Modal:
    """A blocking modal dialog overlay for win or solve status reports."""
    def __init__(self, title, message_lines, font_title, font_body, font_btn, buttons_config):
        # buttons_config: list of dicts: {"text": str, "callback": func, "color": tuple}
        self.title = title
        self.message_lines = message_lines
        self.font_title = font_title
        self.font_body = font_body
        self.font_btn = font_btn
        
        self.width = 450
        self.height = 320
        self.rect = pygame.Rect(
            (SCREEN_WIDTH - self.width) // 2,
            (SCREEN_HEIGHT - self.height) // 2,
            self.width,
            self.height
        )
        
        self.active = False
        
        # Instantiate buttons
        self.buttons = []
        btn_y = self.rect.bottom - 60
        btn_w = 120
        btn_h = 40
        num_btns = len(buttons_config)
        
        # Space out buttons evenly
        total_width = num_btns * btn_w + (num_btns - 1) * 20
        start_x = self.rect.x + (self.width - total_width) // 2
        
        for i, config in enumerate(buttons_config):
            bx = start_x + i * (btn_w + 20)
            btn_color = config.get("color", (79, 110, 138))
            self.buttons.append(
                Button(
                    rect=(bx, btn_y, btn_w, btn_h),
                    text=config["text"],
                    font=self.font_btn,
                    callback=config["callback"],
                    color=btn_color
                )
            )

    def handle_event(self, event):
        if not self.active:
            return False
            
        # Block event propagation to screens behind the modal
        for btn in self.buttons:
            if btn.handle_event(event):
                return True
                
        # If click inside modal but not on buttons, consume event
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
            if self.rect.collidepoint(event.pos):
                return True
            else:
                # Clicked outside modal (dismiss or block)
                return True
                
        return True # Consume all mouse events when active

    def draw(self, surface):
        if not self.active:
            return
            
        # Draw translucent grey background blocker
        blocker = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        blocker.fill((0, 0, 0, 100)) # 100 alpha overlay
        surface.blit(blocker, (0, 0))
        
        # Draw shadow
        shadow_rect = self.rect.move(4, 4)
        pygame.draw.rect(surface, (40, 40, 40, 50), shadow_rect, border_radius=12)
        
        # Draw main modal panel
        pygame.draw.rect(surface, PANEL_COLOR, self.rect, border_radius=12)
        pygame.draw.rect(surface, BORDER_COLOR, self.rect, width=2, border_radius=12)
        
        # Render Title
        title_surf = self.font_title.render(self.title, True, (46, 125, 50))  # Green tone for win/solve
        title_rect = title_surf.get_rect(centerx=self.rect.centerx, y=self.rect.y + 25)
        surface.blit(title_surf, title_rect)
        
        # Render message lines
        for idx, line in enumerate(self.message_lines):
            line_surf = self.font_body.render(line, True, TEXT_COLOR)
            line_rect = line_surf.get_rect(centerx=self.rect.centerx, y=self.rect.y + 80 + idx * 24)
            surface.blit(line_surf, line_rect)
            
        # Draw buttons
        for btn in self.buttons:
            btn.draw(surface)
class Theme:
    pass
