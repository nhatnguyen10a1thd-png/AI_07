import pygame

from ai.solver_interface import ALGORITHMS, solve
from core.constants import BG_COLOR, BORDER_COLOR, PANEL_COLOR, TEXT_COLOR, TEXT_MUTED
from core.rules import BoardRules
from ui.components.button import Button
from ui.components.dropdown import Dropdown
from ui.components.scrollbar import Scrollbar
from ui.renderers.board_renderer import draw_board
from ui.screen_manager import ScreenBase


class AlgorithmScreen(ScreenBase):
    """Trình diễn thuật toán với nhật ký duyệt đầy đủ và có thể tương tác."""

    def __init__(self, app):
        super().__init__(app)
        self.difficulty = "starter"
        self.level_id = "starter_01"
        self.level_meta = None
        self.initial_state = None
        self.current_state = None
        self.rules = BoardRules()

        self.result = None
        self.solver_steps = []
        self.step_idx = 0
        self.current_algo = "A*"
        self.is_playing = False
        self.play_timer = 0.0
        self.play_speed = 0.55

        self.log_scroll_offset = 0
        self.log_row_h = 25
        self.log_visible_rows = 1
        self.log_area_rect = pygame.Rect(0, 0, 0, 0)
        self.log_scrollbar = Scrollbar((0, 0, 12, 100), self._set_log_offset)
        self.setup_ui()

    def setup_ui(self):
        font_btn = self.app.fonts["button"]
        font_body = self.app.fonts["body_bold"]
        bottom_y = self.app.height - 62
        right_x = int(self.app.width * 0.54)

        self.btn_menu = Button(
            (25, bottom_y, 135, 42), "← MENU", font_body,
            lambda: self.app.switch_to_screen("main_menu"), color=(120, 115, 105)
        )
        self.btn_levels = Button(
            (175, bottom_y, 145, 42), "CHỌN LEVEL", font_body,
            lambda: self.app.switch_to_screen("level_select", mode="visualizer"),
            color=(79, 110, 138)
        )
        self.btn_reset = Button(
            (335, bottom_y, 125, 42), "ĐẶT LẠI", font_body,
            self.reset_visualizer, color=(211, 47, 47)
        )

        self.algo_dropdown = Dropdown(
            (right_x, 72, 255, 38), list(ALGORITHMS.keys()),
            self.app.fonts["body_bold"], default_index=2
        )
        self.btn_start = Button(
            (right_x + 270, 72, 110, 38), "BẮT ĐẦU", font_btn,
            self.start_visualization, color=(46, 125, 50)
        )
        self.btn_prev = Button(
            (right_x, bottom_y, 105, 42), "◀ TRƯỚC", font_body,
            self.prev_step, color=(120, 115, 105)
        )
        self.btn_next = Button(
            (right_x + 120, bottom_y, 105, 42), "TIẾP ▶", font_body,
            self.next_step, color=(79, 110, 138)
        )
        self.btn_play = Button(
            (right_x + 240, bottom_y, 125, 42), "▶ TỰ CHẠY", font_body,
            self.toggle_play, color=(46, 125, 50)
        )

    def on_enter(self, **kwargs):
        self.difficulty = kwargs.get("difficulty", "starter")
        self.level_id = kwargs.get("level_id", "starter_01")
        self.level_meta, self.initial_state = self.app.level_manager.load_level(
            self.difficulty, self.level_id
        )
        self.current_state = self.initial_state.clone()
        self.setup_ui()
        self.start_visualization()

    def reset_visualizer(self):
        self.current_state = self.initial_state.clone()
        self.step_idx = 0
        self.play_timer = 0.0
        self.set_playing(False)
        self._auto_scroll_log()

    def start_visualization(self):
        self.current_algo = self.algo_dropdown.get_selected()
        self.result = solve(self.current_algo, self.initial_state, self.rules)
        self.solver_steps = self.result.steps or [(0, "Trạng thái ban đầu", self.initial_state)]
        self.step_idx = 0
        self.play_timer = 0.0
        self.set_playing(False)
        self.log_scroll_offset = 0
        self.current_state = self.solver_steps[0][2]

    def next_step(self):
        if self.step_idx >= len(self.solver_steps) - 1:
            self.set_playing(False)
            return
        self.step_idx += 1
        self.current_state = self.solver_steps[self.step_idx][2]
        self._auto_scroll_log()

    def prev_step(self):
        if self.step_idx <= 0:
            return
        self.step_idx -= 1
        self.current_state = self.solver_steps[self.step_idx][2]
        self._auto_scroll_log()

    def toggle_play(self):
        if len(self.solver_steps) > 1:
            self.set_playing(not self.is_playing)

    def set_playing(self, is_playing):
        self.is_playing = is_playing
        self.btn_play.text = "⏸ DỪNG" if is_playing else "▶ TỰ CHẠY"
        self.btn_play.base_color = (245, 124, 0) if is_playing else (46, 125, 50)

    def _set_log_offset(self, offset):
        self.log_scroll_offset = offset

    def _sync_scrollbar(self):
        self.log_visible_rows = max(1, (self.log_area_rect.height - 8) // self.log_row_h)
        self.log_scrollbar.rect = pygame.Rect(
            self.log_area_rect.right - 14, self.log_area_rect.y + 4,
            10, self.log_area_rect.height - 8
        )
        self.log_scrollbar.configure(
            len(self.solver_steps), self.log_visible_rows, self.log_scroll_offset
        )
        self.log_scroll_offset = self.log_scrollbar.offset

    def _auto_scroll_log(self):
        max_offset = max(0, len(self.solver_steps) - self.log_visible_rows)
        if self.step_idx < self.log_scroll_offset:
            self.log_scroll_offset = self.step_idx
        elif self.step_idx >= self.log_scroll_offset + self.log_visible_rows:
            self.log_scroll_offset = self.step_idx - self.log_visible_rows + 1
        self.log_scroll_offset = min(max_offset, self.log_scroll_offset)

    def handle_event(self, event):
        for button in (
            self.btn_menu, self.btn_levels, self.btn_reset,
            self.btn_start, self.btn_prev, self.btn_next, self.btn_play
        ):
            button.handle_event(event)

        if self.algo_dropdown.handle_event(event):
            return

        self._sync_scrollbar()
        if self.log_scrollbar.handle_event(event):
            return

        if event.type == pygame.MOUSEWHEEL and self.log_area_rect.collidepoint(pygame.mouse.get_pos()):
            self.log_scrollbar.scroll(-event.y * 3)
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.log_area_rect.collidepoint(event.pos):
                row = (event.pos[1] - self.log_area_rect.y - 4) // self.log_row_h
                index = self.log_scroll_offset + row
                if 0 <= index < len(self.solver_steps):
                    self.step_idx = index
                    self.current_state = self.solver_steps[index][2]
                    self.set_playing(False)

    def update(self, dt):
        if self.is_playing:
            self.play_timer += dt
            if self.play_timer >= self.play_speed:
                self.play_timer = 0.0
                self.next_step()

    def draw(self, surface):
        width, height = self.app.width, self.app.height
        surface.fill(BG_COLOR)
        title_font = self.app.fonts["title"]
        body = self.app.fonts["body"]
        body_bold = self.app.fonts["body_bold"]
        mono = self.app.fonts["mono"]

        surface.blit(title_font.render("TRÌNH DIỄN THUẬT TOÁN", True, TEXT_COLOR), (25, 18))
        subtitle = f"Màn: {self.level_meta['name']}  |  Thuật toán: {self.current_algo}"
        surface.blit(body.render(subtitle, True, TEXT_MUTED), (25, 52))

        board_rect = pygame.Rect(25, 85, int(width * 0.50), height - 165)
        draw_board(surface, self.current_state, board_rect)

        right_x = int(width * 0.54)
        right_w = width - right_x - 20
        panel = pygame.Rect(right_x - 10, 15, right_w + 10, height - 90)
        pygame.draw.rect(surface, PANEL_COLOR, panel, border_radius=14)
        pygame.draw.rect(surface, BORDER_COLOR, panel, width=2, border_radius=14)

        surface.blit(body.render("Chọn thuật toán:", True, TEXT_MUTED), (right_x, 48))
        status_y = 125
        solved = bool(self.result and self.result.solved)
        status = "ĐÃ TÌM THẤY LỜI GIẢI" if solved else "KHÔNG TÌM THẤY LỜI GIẢI"
        status_color = (46, 125, 50) if solved else (190, 55, 55)
        surface.blit(body_bold.render(status, True, status_color), (right_x, status_y))

        if self.result:
            summary = (
                f"Log: {len(self.solver_steps):,} | Hiện tại: {self.step_idx + 1:,} | "
                f"Visited: {self.result.visited_count:,} | {self.result.elapsed_time * 1000:.1f} ms"
            )
            surface.blit(body.render(summary, True, TEXT_MUTED), (right_x, status_y + 27))

        log_title_y = status_y + 65
        surface.blit(body_bold.render("NHẬT KÝ DUYỆT - click dòng để xem trạng thái", True, TEXT_COLOR),
                     (right_x, log_title_y))
        self.log_area_rect = pygame.Rect(right_x, log_title_y + 28, right_w, height - log_title_y - 112)
        pygame.draw.rect(surface, (248, 248, 246), self.log_area_rect, border_radius=8)
        pygame.draw.rect(surface, BORDER_COLOR, self.log_area_rect, width=1, border_radius=8)
        self._sync_scrollbar()

        clip = surface.subsurface(self.log_area_rect)
        text_width = self.log_area_rect.width - 28
        for row in range(self.log_visible_rows):
            index = self.log_scroll_offset + row
            if index >= len(self.solver_steps):
                break
            step_num, description, _ = self.solver_steps[index]
            y = 4 + row * self.log_row_h
            active = index == self.step_idx
            if active:
                pygame.draw.rect(clip, (220, 239, 224), (3, y, text_width + 10, self.log_row_h - 1),
                                 border_radius=4)
            prefix = "▶" if active else " "
            text = f"{prefix} [{step_num:04d}] {description}"
            while mono.size(text)[0] > text_width and len(text) > 4:
                text = text[:-2] + "…"
            color = (30, 115, 55) if active else TEXT_COLOR
            clip.blit(mono.render(text, True, color), (8, y + 3))

        self.log_scrollbar.draw(surface)
        self.algo_dropdown.draw(surface)
        for button in (
            self.btn_start, self.btn_menu, self.btn_levels, self.btn_reset,
            self.btn_prev, self.btn_next, self.btn_play
        ):
            button.draw(surface)
