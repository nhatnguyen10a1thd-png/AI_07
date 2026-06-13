# ui/components/toast.py
import pygame
from core.constants import SCREEN_WIDTH

class Toast:
    """Displays temporary overlay notifications that automatically fade out."""
    def __init__(self, font):
        self.font = font
        self.message = ""
        self.duration = 2.0  # seconds
        self.timer = 0.0
        self.active = False
        self.bg_color = (40, 40, 40, 230) # Dark translucent
        self.text_color = (255, 255, 255)

    def show(self, message, duration=2.0):
        self.message = message
        self.duration = duration
        self.timer = duration
        self.active = True

    def update(self, dt):
        if not self.active:
            return
        self.timer -= dt
        if self.timer <= 0:
            self.active = False

    def draw(self, surface):
        if not self.active:
            return

        # Render message text
        text_surf = self.font.render(self.message, True, self.text_color)
        text_rect = text_surf.get_rect()
        
        # Calculate padding and box size
        padding_x = 20
        padding_y = 12
        box_width = text_rect.width + padding_x * 2
        box_height = text_rect.height + padding_y * 2
        
        # Bottom center positioning
        box_x = (SCREEN_WIDTH - box_width) // 2
        box_y = 600
        
        # Create translucent box surface
        toast_surf = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        
        # Compute alpha fadeout
        alpha = 255
        if self.timer < 0.5:
            alpha = int((self.timer / 0.5) * 255)
            alpha = max(0, min(255, alpha))
            
        # Draw rounded rect on the surface
        bg = (self.bg_color[0], self.bg_color[1], self.bg_color[2], int(alpha * 0.9))
        pygame.draw.rect(toast_surf, bg, (0, 0, box_width, box_height), border_radius=8)
        
        # Render text onto surface
        text_color_alpha = (self.text_color[0], self.text_color[1], self.text_color[2], alpha)
        text_surf_faded = self.font.render(self.message, True, text_color_alpha)
        text_surf_rect = text_surf_faded.get_rect(center=(box_width // 2, box_height // 2))
        toast_surf.blit(text_surf_faded, text_surf_rect)
        
        # Draw on main screen
        surface.blit(toast_surf, (box_x, box_y))
