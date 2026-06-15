# main.py
import os
import sys
# pyrefly: ignore [missing-import]
import pygame

# Add project root to path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from core.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BG_COLOR
from core.level import LevelManager
from ui.screen_manager import ScreenManager
from ui.screens.main_menu import MainMenuScreen
from ui.screens.level_select import LevelSelectScreen
from ui.screens.game_screen import GameScreen
from ui.screens.algorithm_screen import AlgorithmScreen
from ui.screens.report_screen import ReportScreen
from ui.font import Font
from ui.renderers.board_renderer import make_app_icon
from ui.components.titlebar import TitleBar

class App:
    """The main Pygame Application manager class."""
    def __init__(self):
        pygame.init()
        try:
            pygame.mixer.init()
        except pygame.error:
            pass

        # --- Fullscreen: chiếm toàn bộ màn hình ở độ phân giải gốc ---
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.width = self.screen.get_width()
        self.height = self.screen.get_height()

        pygame.display.set_caption("Squirrels Go Nuts! - AI Search Solver")
        pygame.display.set_icon(make_app_icon())

        self.clock = pygame.time.Clock()
        self.running = True
        self.project_dir = os.path.dirname(os.path.abspath(__file__))

        # Khởi tạo TitleBar tùy chỉnh
        self.titlebar = TitleBar(self)

        # Load assets and managers
        self.level_manager = LevelManager()

        # Load fonts robustly with system fallbacks
        self.load_fonts()

        # Initialize screen manager
        self.screen_manager = ScreenManager()
        self.setup_screens()

        # Start at main menu
        self.screen_manager.switch_to("main_menu")

    def load_fonts(self):
        """Loads system fonts, scaled relative to window height (baseline 800px)."""
        pygame.font.init()

        title_font_candidates = ["Segoe UI", "Arial"]
        body_font_candidates = ["Segoe UI", "Arial"]
        mono_font_candidates = ["Cascadia Mono", "Consolas", "Courier New"]

        # Scale font sizes proportionally to window height
        scale = self.height / 800

        def fs(base):
            """Return a font size scaled to current resolution."""
            return max(10, round(base * scale))

        self.fonts = {
            "title_huge": Font(pygame.font.SysFont(title_font_candidates, fs(54), bold=True)),
            "title": Font(pygame.font.SysFont(title_font_candidates, fs(28), bold=True)),
            "button": Font(pygame.font.SysFont(body_font_candidates, fs(16), bold=True)),
            "body_bold": Font(pygame.font.SysFont(body_font_candidates, fs(16), bold=True)),
            "body": Font(pygame.font.SysFont(body_font_candidates, fs(16))),
            "body_small": Font(pygame.font.SysFont(body_font_candidates, fs(13))),
            "mono": Font(pygame.font.SysFont(mono_font_candidates, fs(14)))
        }

    def setup_screens(self):
        """Registers all screens with the ScreenManager."""
        self.screen_manager.add_screen("main_menu", MainMenuScreen(self))
        self.screen_manager.add_screen("level_select", LevelSelectScreen(self))
        self.screen_manager.add_screen("game", GameScreen(self))
        self.screen_manager.add_screen("algorithm", AlgorithmScreen(self))
        self.screen_manager.add_screen("report", ReportScreen(self))

    def switch_to_screen(self, screen_name, **kwargs):
        """Helper to switch screens via the manager."""
        self.screen_manager.switch_to(screen_name, **kwargs)

    def run(self):
        """Main application game loop."""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0  # Delta time in seconds
            
            # 1. Handle event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    # ESC thoát khỏi chương trình
                    self.running = False
                elif self.titlebar.handle_event(event):
                    pass  # Event đã được tiêu thụ bởi titlebar
                else:
                    self.screen_manager.handle_event(event)
            
            # 2. Update screen state
            self.screen_manager.update(dt)
            
            # 3. Draw screen graphics
            self.screen.fill(BG_COLOR)
            self.screen_manager.draw(self.screen)
            # TitleBar luôn vẽ TRÊN CÙNG để không bị che
            self.titlebar.draw(self.screen)
            pygame.display.flip()
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    app = App()
    app.run()
