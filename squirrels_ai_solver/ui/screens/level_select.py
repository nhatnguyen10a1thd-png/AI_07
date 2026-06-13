# ui/screens/level_select.py
import pygame
from ui.screen_manager import ScreenBase
from ui.components.button import Button
from core.constants import BG_COLOR, TEXT_COLOR, PANEL_COLOR, BORDER_COLOR

class LevelSelectScreen(ScreenBase):
    """Màn hình chọn Level được phân theo 3 cấp độ (Starter, Junior, Expert)."""
    def __init__(self, app):
        super().__init__(app)
        self.mode = "play"  # Mode passed in on enter ("play", "ai", "visualizer", "report")
        self.selected_difficulty = "starter"
        self.back_button = None
        self.tab_buttons = {}
        self.level_buttons = []
        
        self.setup_ui()

    def setup_ui(self):
        font_btn = self.app.fonts["button"]
        W = self.app.width
        H = self.app.height
        self.tab_buttons = {}
        
        # 1. Back button to main menu
        self.back_button = Button(
            rect=(30, 25, 150, 40),
            text="← QUAY LẠI",
            font=self.app.fonts["body_bold"],
            callback=lambda: self.app.switch_to_screen("main_menu"),
            color=(120, 115, 105)
        )
        
        # 2. Tabs for difficulties
        diffs = [
            (difficulty.upper(), difficulty)
            for difficulty in self.app.level_manager.get_difficulties()
        ]
        tab_w = min(160, max(110, (W - 140) // max(1, len(diffs))))
        tab_h = 45
        gap = 20
        start_x = (W - (tab_w * len(diffs) + gap * (len(diffs) - 1))) // 2
        
        for idx, (label, diff_key) in enumerate(diffs):
            tx = start_x + idx * (tab_w + gap)
            self.tab_buttons[diff_key] = Button(
                rect=(tx, 100, tab_w, tab_h),
                text=label,
                font=font_btn,
                callback=lambda k=diff_key: self.select_difficulty(k),
                color=(79, 110, 138)
            )

    def on_enter(self, **kwargs):
        self.mode = kwargs.get("mode", "play")
        self.setup_ui()  # Rebuild buttons for current window size
        self.select_difficulty(self.selected_difficulty)

    def select_difficulty(self, diff_key):
        self.selected_difficulty = diff_key
        
        # Update tab button colors to highlight the active tab
        for key, btn in self.tab_buttons.items():
            if key == diff_key:
                btn.base_color = (139, 115, 85) # Selected: warm wood color
                btn.hover_color = (139, 115, 85)
            else:
                btn.base_color = (79, 110, 138) # Default blue
                btn.hover_color = (98, 132, 161)
                
        # Load levels of selected difficulty and create buttons for them
        self.level_buttons = []
        levels = self.app.level_manager.get_levels_by_difficulty(diff_key)
        W = self.app.width
        
        card_w = min(260, (W - 100) // 4)
        card_h = 180
        margin_x = 30
        margin_y = 30
        
        # Calculate start coordinates for level card grid layout
        grid_cols = 4
        total_card_w = card_w * grid_cols + margin_x * (grid_cols - 1)
        if total_card_w > W - 80:
            grid_cols = 3
            total_card_w = card_w * grid_cols + margin_x * (grid_cols - 1)
        start_x = (W - total_card_w) // 2
        start_y = 200
        
        for idx, lvl in enumerate(levels):
            row = idx // grid_cols
            col = idx % grid_cols
            
            bx = start_x + col * (card_w + margin_x)
            by = start_y + row * (card_h + margin_y)
            
            # Action button inside card
            btn_y = by + card_h - 60
            level_id = lvl["id"]
            
            # Button text depends on mode
            btn_text = {
                "play": "VÀO CHƠI",
                "ai": "GIẢI AI",
                "visualizer": "MÔ PHỎNG",
                "report": "BÁO CÁO",
            }.get(self.mode, "MỞ")
            
            self.level_buttons.append({
                "lvl_data": lvl,
                "card_rect": pygame.Rect(bx, by, card_w, card_h),
                "button": Button(
                    rect=(bx + 20, btn_y, card_w - 40, 40),
                    text=btn_text,
                    font=self.app.fonts["body_bold"],
                    callback=lambda lid=level_id: self.select_level(lid),
                    color=(46, 125, 50) if self.mode == "play" else (139, 115, 85)
                )
            })

    def select_level(self, level_id):
        # Route to correct screen based on mode
        if self.mode == "play":
            self.app.switch_to_screen("game", difficulty=self.selected_difficulty, level_id=level_id, mode="play")
        elif self.mode == "ai":
            self.app.switch_to_screen("game", difficulty=self.selected_difficulty, level_id=level_id, mode="ai")
        elif self.mode == "visualizer":
            self.app.switch_to_screen("algorithm", difficulty=self.selected_difficulty, level_id=level_id)
        elif self.mode == "report":
            self.app.switch_to_screen("report", difficulty=self.selected_difficulty, level_id=level_id)

    def handle_event(self, event):
        self.back_button.handle_event(event)
        for btn in self.tab_buttons.values():
            btn.handle_event(event)
        for card in self.level_buttons:
            card["button"].handle_event(event)

    def draw(self, surface):
        surface.fill(BG_COLOR)
        
        # 1. Header label
        header_font = self.app.fonts["title"]
        mode_str = {
            "play": "TỰ CHƠI GAME",
            "ai": "AI SOLVER",
            "visualizer": "TRÌNH DIỄN THUẬT TOÁN",
            "report": "BÁO CÁO HIỆU NĂNG",
        }.get(self.mode, self.mode.upper())
        header_surf = header_font.render(f"CHỌN LEVEL - CHẾ ĐỘ: {mode_str}", True, TEXT_COLOR)
        header_rect = header_surf.get_rect(centerx=self.app.width // 2, y=35)
        surface.blit(header_surf, header_rect)
        
        # 2. Draw Back and Tab Buttons
        self.back_button.draw(surface)
        for btn in self.tab_buttons.values():
            btn.draw(surface)
            
        # 3. Draw Level Cards grid
        body_font = self.app.fonts["body"]
        body_bold = self.app.fonts["body_bold"]
        
        for card in self.level_buttons:
            rect = card["card_rect"]
            lvl = card["lvl_data"]
            
            # Card background
            pygame.draw.rect(surface, PANEL_COLOR, rect, border_radius=12)
            pygame.draw.rect(surface, BORDER_COLOR, rect, width=2, border_radius=12)
            
            # Level title
            title_surf = body_bold.render(lvl["name"], True, TEXT_COLOR)
            title_rect = title_surf.get_rect(centerx=rect.centerx, y=rect.y + 20)
            surface.blit(title_surf, title_rect)
            
            # Count squirrels and blocks
            squirrel_count = sum(1 for p in lvl["pieces"] if p["type"] == "squirrel")
            blocker_count = sum(1 for p in lvl["pieces"] if p["type"] == "block")
            details_surf = body_font.render(f"Số Sóc: {squirrel_count} | Ô cản: {blocker_count}", True, (120, 115, 105))
            details_rect = details_surf.get_rect(centerx=rect.centerx, y=rect.y + 55)
            surface.blit(details_surf, details_rect)

            target_moves = lvl.get("target_moves")
            if target_moves:
                target_surf = body_bold.render(f"Số bước chuẩn: {target_moves}", True, (139, 115, 85))
                target_rect = target_surf.get_rect(centerx=rect.centerx, y=rect.y + 82)
                surface.blit(target_surf, target_rect)
            
            # Draw card's action button
            card["button"].draw(surface)
            
        # If no levels
        if not self.level_buttons:
            empty_surf = body_font.render("Chưa có level nào trong nhóm này.", True, (120, 115, 105))
            empty_rect = empty_surf.get_rect(centerx=self.app.width // 2, y=300)
            surface.blit(empty_surf, empty_rect)
