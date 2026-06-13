import csv
import os

import pygame

from ai.search_result import SearchResult
from ai.solver_interface import ALGORITHMS, solve
from core.constants import BG_COLOR, BORDER_COLOR, PANEL_COLOR, TEXT_COLOR, TEXT_MUTED
from core.rules import BoardRules
from ui.components.button import Button
from ui.components.toast import Toast
from ui.screen_manager import ScreenBase


class ReportScreen(ScreenBase):
    """Compare every registered algorithm for the selected level."""

    def __init__(self, app):
        super().__init__(app)
        self.difficulty = "starter"
        self.level_id = "starter_01"
        self.level_meta = None
        self.initial_state = None
        self.rules = BoardRules()
        self.results = {}
        self.toast = Toast(self.app.fonts["body"])
        self.setup_ui()

    def setup_ui(self):
        font_body = self.app.fonts["body_bold"]
        font_btn = self.app.fonts["button"]
        button_y = self.app.height - 65
        self.btn_menu = Button(
            rect=(50, button_y, 160, 45), text="< MENU CHÍNH", font=font_body,
            callback=lambda: self.app.switch_to_screen("main_menu"), color=(120, 115, 105),
        )
        self.btn_levels = Button(
            rect=(230, button_y, 160, 45), text="CHỌN LEVEL", font=font_body,
            callback=lambda: self.app.switch_to_screen("level_select", mode="report"), color=(79, 110, 138),
        )
        self.btn_run_all = Button(
            rect=(850, button_y, 170, 45), text="CHẠY TẤT CẢ", font=font_btn,
            callback=self.run_all_algorithms, color=(46, 125, 50),
        )
        self.btn_export = Button(
            rect=(1040, button_y, 170, 45), text="XUẤT FILE CSV", font=font_btn,
            callback=self.export_csv_report, color=(139, 115, 85),
        )
        self.btn_export.is_enabled = False

    def _pending_results(self):
        return {
            name: SearchResult(name, False, extra={"report_status": "pending"})
            for name in ALGORITHMS
        }

    def on_enter(self, **kwargs):
        self.difficulty = kwargs.get("difficulty", "starter")
        self.level_id = kwargs.get("level_id", "starter_01")
        self.level_meta, self.initial_state = self.app.level_manager.load_level(self.difficulty, self.level_id)
        self.results = self._pending_results()
        self.btn_export.is_enabled = False
        self.toast.show("Báo cáo luôn hiển thị đầy đủ thuật toán. Bấm CHẠY TẤT CẢ để đo.")

    def run_all_algorithms(self):
        self.toast.show("Đang đo hiệu năng toàn bộ thuật toán...")
        self.results = self._pending_results()
        for name in ALGORITHMS:
            try:
                result = solve(name, self.initial_state, self.rules, max_nodes=20000, max_seconds=2.0)
                result.extra["report_status"] = "done"
                self.results[name] = result
            except Exception as exc:
                self.results[name] = SearchResult(
                    name, False, extra={"report_status": "error", "error": str(exc)}
                )
        self.btn_export.is_enabled = True
        self.toast.show(f"Đã đo đủ {len(ALGORITHMS)} thuật toán.")

    def export_csv_report(self):
        if not self.results:
            return
        out_dir = os.path.join(self.app.project_dir, "results")
        os.makedirs(out_dir, exist_ok=True)
        csv_path = os.path.join(out_dir, "algorithm_results.csv")
        try:
            with open(csv_path, "w", newline="", encoding="utf-8-sig") as file:
                writer = csv.writer(file)
                writer.writerow([
                    "Level", "Algorithm", "Status", "Solved", "Steps",
                    "Visited", "Generated", "Time (s)", "Details",
                ])
                for name in ALGORITHMS:
                    result = self.results[name]
                    status = result.extra.get("report_status", "done")
                    writer.writerow([
                        self.level_meta["name"], name, status,
                        "Yes" if result.solved else "No",
                        len(result.path) if result.solved else "N/A",
                        result.visited_count, result.generated_count,
                        f"{result.elapsed_time:.6f}",
                        result.extra.get("error", ""),
                    ])
            self.toast.show("Đã xuất đầy đủ báo cáo: results/algorithm_results.csv")
        except Exception as exc:
            self.toast.show(f"Lỗi khi xuất CSV: {exc}")

    def handle_event(self, event):
        self.btn_menu.handle_event(event)
        self.btn_levels.handle_event(event)
        self.btn_run_all.handle_event(event)
        self.btn_export.handle_event(event)

    def update(self, dt):
        self.toast.update(dt)

    def _status(self, result):
        report_status = result.extra.get("report_status", "done")
        if report_status == "pending":
            return "CHỜ CHẠY", TEXT_MUTED
        if report_status == "error":
            return "LỖI", (211, 47, 47)
        if result.solved:
            return "CÓ", (46, 125, 50)
        return "KHÔNG", (211, 47, 47)

    def draw(self, surface):
        surface.fill(BG_COLOR)
        title_font = self.app.fonts["title"]
        body_font = self.app.fonts["body"]
        body_bold = self.app.fonts["body_bold"]
        body_small = self.app.fonts["body_small"]

        level_name = self.level_meta["name"] if self.level_meta else "-"
        surface.blit(title_font.render(f"BÁO CÁO HIỆU NĂNG - MÀN: {level_name}", True, TEXT_COLOR), (50, 25))
        surface.blit(body_font.render(
            f"Đầy đủ {len(ALGORITHMS)} thuật toán | Mỗi thuật toán được bảo vệ giới hạn RAM và thời gian.",
            True, TEXT_MUTED,
        ), (52, 63))

        panel_rect = pygame.Rect(50, 95, 1180, 365)
        pygame.draw.rect(surface, PANEL_COLOR, panel_rect, border_radius=14)
        pygame.draw.rect(surface, BORDER_COLOR, panel_rect, width=2, border_radius=14)
        headers = ["THUẬT TOÁN", "KẾT QUẢ", "SỐ BƯỚC", "ĐÃ DUYỆT", "ĐÃ SINH", "THỜI GIAN (MS)"]
        col_xs = [80, 300, 445, 590, 795, 1040]
        for x, header in zip(col_xs, headers):
            surface.blit(body_bold.render(header, True, (139, 115, 85)), (x, 108))
        pygame.draw.line(surface, BORDER_COLOR, (65, 139), (1215, 139), 2)

        for index, name in enumerate(ALGORITHMS):
            result = self.results.get(name) or self._pending_results()[name]
            row_y = 147 + index * 27
            if index % 2:
                pygame.draw.rect(surface, (250, 248, 244), (65, row_y - 3, 1150, 26), border_radius=5)
            status, status_color = self._status(result)
            values = [
                (name, body_bold, TEXT_COLOR),
                (status, body_bold, status_color),
                (str(len(result.path)) if result.solved else "-", body_font, TEXT_COLOR),
                (f"{result.visited_count:,}", body_font, TEXT_COLOR),
                (f"{result.generated_count:,}", body_font, TEXT_COLOR),
                (f"{result.elapsed_time * 1000:.3f}", body_font, TEXT_COLOR),
            ]
            for x, (value, font, color) in zip(col_xs, values):
                surface.blit(font.render(value, True, color), (x, row_y))

        chart_rect = pygame.Rect(50, 475, 1180, 180)
        pygame.draw.rect(surface, PANEL_COLOR, chart_rect, border_radius=14)
        pygame.draw.rect(surface, BORDER_COLOR, chart_rect, width=2, border_radius=14)
        surface.blit(body_bold.render("SO SÁNH SỐ NÚT ĐÃ DUYỆT - ĐỦ TOÀN BỘ THUẬT TOÁN", True, TEXT_COLOR), (70, 487))

        max_visited = max(1, max((result.visited_count for result in self.results.values()), default=1))
        start_x, spacing, bar_y, bar_max_h = 82, 102, 520, 82
        for index, name in enumerate(ALGORITHMS):
            result = self.results.get(name) or self._pending_results()[name]
            x = start_x + index * spacing
            height = max(3, int(result.visited_count / max_visited * bar_max_h))
            status = result.extra.get("report_status", "done")
            color = (190, 190, 190) if status == "pending" else ((70, 160, 95) if result.solved else (210, 92, 75))
            pygame.draw.rect(surface, color, (x, bar_y + bar_max_h - height, 46, height), border_radius=5)
            label = name.replace("Simulated ", "Sim. ").replace("Forward ", "Fwd. ").replace("Backtracking", "Backtrack")
            text = body_small.render(label, True, TEXT_COLOR)
            surface.blit(text, text.get_rect(centerx=x + 23, y=bar_y + bar_max_h + 7))

        self.btn_menu.draw(surface)
        self.btn_levels.draw(surface)
        self.btn_run_all.draw(surface)
        self.btn_export.draw(surface)
        self.toast.draw(surface)
