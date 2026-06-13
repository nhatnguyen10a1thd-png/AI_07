# Squirrels Go Nuts! AI Solver & Visualizer

Dự án này là một ứng dụng giải đố thông minh cho trò chơi **Squirrels Go Nuts!** (của SmartGames) được viết bằng **Python** và **Pygame**. Ứng dụng tích hợp các thuật toán tìm kiếm từ cơ bản đến nâng cao trong Trí tuệ Nhân tạo để giải quyết trò chơi và so sánh hiệu năng thực nghiệm. Bộ dữ liệu hiện có **32 đề bài từ sách**, chia thành bốn mức Starter, Junior, Expert và Master.

---

## 🌟 Các tính năng chính
1. **Chế độ tự chơi (Play Mode):** Click chọn chú Sóc và sử dụng phím Mũi Tên (hoặc WASD) để tự mình trượt mảnh ghép giải đố. Có hỗ trợ Đặt lại (Reset) và Hoàn tác (Undo) nước đi.
2. **AI Solver:** Chọn một trong các thuật toán và xem AI giải quyết màn chơi. Cho phép phát lại tự động (Auto Play) và điều chỉnh tốc độ, hoặc duyệt thủ công từng bước (Step-by-step).
3. **Algorithm Visualizer:** Xem quá trình duyệt không gian trạng thái của các thuật toán với highlight mã giả (pseudocode) trực quan.
4. **Báo cáo thực nghiệm (Performance Report):** Chạy đồng thời toàn bộ 12 thuật toán để so sánh các số liệu:
   * Số bước giải (Solution length)
   * Số trạng thái đã duyệt (Visited states)
   * Số trạng thái đã sinh (Generated states)
   * Thời gian chạy giải (ms)
   * Biểu đồ so sánh cột trực quan
   * Xuất báo cáo chi tiết ra file CSV (`results/algorithm_results.csv`)

---

## 🛠️ Cấu trúc thư mục dự án
```text
squirrels_ai_solver/
├── main.py                     # File chạy chính giao diện Pygame
├── verify_core.py              # Script test console nhanh logic core & 12 thuật toán
├── requirements.txt            # Thư viện phụ thuộc (pygame)
├── README.md                   # Hướng dẫn này
│
├── core/                       # Logic trò chơi
│   ├── constants.py            # Kích thước, màu sắc và hằng số
│   ├── piece.py                # Lớp Piece đại diện các mảnh ghép
│   ├── state.py                # Trạng thái GameState (hashable)
│   ├── rules.py                # Quy tắc di chuyển và va chạm (BoardRules)
│   └── level.py                # Trình đọc level JSON
│
├── data/
│   └── levels.json             # Dữ liệu màn chơi Starter, Junior, Expert
│
├── ai/                         # Bộ giải AI (12 thuật toán)
│   ├── solver_interface.py     # Cổng giao tiếp chung của bộ giải
│   ├── search_result.py        # Cấu trúc kết quả chuẩn hóa
│   ├── utils.py                # SearchNode và hàm truy vết đường đi
│   ├── informed/
│   │   ├── heuristics.py       # Khoảng cách Manhattan tới lỗ trống gần nhất
│   │   ├── greedy.py           # Greedy Best-First Search
│   │   └── astar.py            # A* Search
│   ├── uninformed/
│   │   ├── bfs.py              # Breadth-First Search
│   │   └── dfs.py              # Depth-First Search
│   ├── local_search/
│   │   ├── hill_climbing.py    # Simple Hill Climbing
│   │   └── simulated_annealing.py # Simulated Annealing
│   ├── csp/
│   │   ├── backtracking.py     # CSP Backtracking
│   │   └── min_conflicts.py    # CSP Min-Conflicts
│   ├── adversarial/
│   │   ├── minimax.py          # Minimax Simulation
│   │   └── alpha_beta.py       # Alpha-Beta Pruning Simulation
│   └── complex/
│       ├── and_or_search.py    # AND-OR Graph Search
│       └── belief_state_search.py # Belief-State Search
│
├── ui/                         # Giao diện Pygame
│   ├── screen_manager.py       # Trình chuyển đổi màn hình
│   ├── renderers/
│   │   └── board_renderer.py   # Vẽ bàn cờ, hoa cản, sóc và acorn 3D
│   ├── components/
│   │   ├── button.py           # Nút bấm có hiệu ứng hover/click/shadow
│   │   ├── dropdown.py         # Danh sách lựa chọn thuật toán
│   │   ├── toast.py            # Thông báo tự tắt ở cuối màn hình
│   │   └── modal.py            # Hộp thoại popup khi chiến thắng
│   └── screens/
│       ├── main_menu.py        # Menu chính
│       ├── level_select.py     # Chọn màn chơi
│       ├── game_screen.py      # Màn hình chơi game chính + AI panel
│       ├── algorithm_screen.py # Trình trực quan hóa thuật toán
│       └── report_screen.py    # So sánh 12 thuật toán + Xuất CSV
```

---

## 🚀 Hướng dẫn cài đặt và khởi chạy

### 1. Cài đặt các thư viện cần thiết
Mở Terminal/CMD tại thư mục chứa dự án và chạy lệnh:
```bash
pip install -r squirrels_ai_solver/requirements.txt
```

### 2. Kiểm tra nhanh logic core và các thuật toán (Chế độ Console)
Bạn có thể chạy thử script kiểm tra nhanh để đảm bảo toàn bộ 12 thuật toán và game engine hoạt động đúng bằng lệnh:
```bash
python squirrels_ai_solver/verify_core.py
```
Script sẽ in ra nước đi chi tiết và bảng thống kê kết quả giải của từng thuật toán trên màn chơi mẫu.

### 3. Chạy giao diện đồ họa chính (Pygame App)
Chạy lệnh sau để mở cửa sổ trò chơi:
```bash
python squirrels_ai_solver/main.py
```
Giao diện đồ họa sẽ mở ra với kích thước `1280 x 720` hỗ trợ đầy đủ các tính năng tương tác.
