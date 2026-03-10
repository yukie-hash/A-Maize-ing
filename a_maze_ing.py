from mazegen.generator import MazeGenerator
import os


def save_to_file(maze: MazeGenerator, filename: str, path_str: str) -> None:
    """
    16進数の迷路データと最短経路をテキストファイルに保存する
    """
    # 1. 16進数のリストを取得する
    hex_data = maze.get_hex_representation()

    with open(filename, "w", encoding="utf-8") as f:
        # 2. 迷路の各行を16進数で書き出す
        for row in hex_data:
            # ["F", "A", "3"] を "FA3" という一本の文字列にして書き込むべ
            f.write("".join(row) + "\n")

        f.write(f"\n{maze.entry[0]},{maze.entry[1]}\n")
        f.write(f"{maze.exit_pos[0]},{maze.exit_pos[1]}\n")
        # 3. 最後に最短経路（NSEW）を一行書き添える
        f.write(f"\n{path_str}\n")


def draw_real_maze(maze: MazeGenerator, path_coords, WALL, NUM) -> None:
    """
    壁と通路を全く同じ太さ（2文字分）で描画するだす。
    1マスを「北西角・北壁」「西壁・中心」の2x2ブロックとして扱うべ。
    """
    RESET = "\033[0m"
    PATH = "\033[40m  "      # 通常の通路（黒）
    ROUTE = "\033[44m  "     # 経路（青）
    ENTRY = "\033[45m  "     # 入口（紫）
    EXIT = "\033[41m  "      # 出口（赤)   
    path_set = set(path_coords) if path_coords else set()

    for y in range(maze.height):
        row_top, row_mid = "", ""
        for x in range(maze.width):
            cell = maze.grid[y][x]
            is_route = (x, y) in path_set and path_coords

            # --- 1. 北西の角と北側の壁 ---
            # 角は常に壁。その隣（北側）が壁かどうか
            row_top += WALL
            row_top += (WALL if cell["N"] else (ROUTE if (is_route and (x, y-1) in path_set) else PATH))

            # --- 2. 西側の壁と中心 ---
            # 西側が壁かどうか
            row_mid += (WALL if cell["W"] else (ROUTE if (is_route and (x-1, y) in path_set) else PATH))

            # 中心の決定
            if (x, y) == maze.entry:
                center = ENTRY
            elif (x, y) == maze.exit_pos:
                center = EXIT
            elif (x, y) in getattr(maze, 'forty_two_coords', []): center = NUM
            elif is_route:
                center = ROUTE
            else:
                center = PATH
            row_mid += center

        # 右端の壁（東側の境界）を付け足す
        last_cell = maze.grid[y][maze.width-1]
        row_top += WALL  # 右上の角
        row_mid += (WALL if last_cell["E"] else PATH)

        print(f"{row_top}{RESET}")
        print(f"{row_mid}{RESET}")

    # 一番下の南側の壁を一行まるごと付け足す
    bottom_line = ""
    for x in range(maze.width):
        cell = maze.grid[maze.height-1][x]
        bottom_line += (WALL + (WALL if cell["S"] else PATH)) 
    print(f"{bottom_line}{WALL}{RESET}")    # 右下の角まで描いて終了


def load_config(filename: str) -> dict:
    config = {}
    try:
        # コンテキストマネージャ（with）を使って安全にファイルを開く [cite: 75]
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                # 空行や '#' で始まるコメント行を無視する [cite: 120]
                if not line or line.startswith('#'):
                    continue

                # 'KEY=VALUE' の形式を分割する [cite: 119]
                if '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()

    except FileNotFoundError:
        # ファイルがない場合はクラッシュさせず、エラーを表示して終了する 
        print(f"Error: {filename} not found.")
        exit(1)

    # 必須キー（WIDTH, HEIGHTなど）が含まれているか確認する [cite: 121, 122]
    required_keys = ["WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"]
    for r_key in required_keys:
        if r_key not in config:
            print(f"Error: Missing mandatory key '{r_key}'")
            exit(1)

    return config


def main() -> None:
    # 1. 設定の読み込み
    config = load_config("config.txt")

    # 2. 値の変換
    try:
        w = int(config["WIDTH"])
        h = int(config["HEIGHT"])
        if not (0 < w < 500 and 0 < h < 500):
            raise ValueError("WIDTH/HEIGHT must be between 1 and 499")

        is_perfect = config["PERFECT"].lower() == "true"
        if config["PERFECT"].lower() not in ["true", "false"]:
            raise ValueError("PERFECT must be 'true' or 'false'")

        e_vals = list(map(int, config["ENTRY"].split(',')))
        if len(e_vals) != 2:
            raise ValueError("ENTRY must be 'x,y'")
        entry: tuple[int, int] = (e_vals[0], e_vals[1])

        x_vals = list(map(int, config["EXIT"].split(',')))
        if len(x_vals) != 2:
            raise ValueError("EXIT must be 'x,y'")
        exit_pos: tuple[int, int] = (x_vals[0], x_vals[1])

        if not (0 <= entry[0] < w and 0 <= entry[1] < h) or \
           not (0 <= exit_pos[0] < w and 0 <= exit_pos[1] < h):
            raise ValueError(f"Invalid entry {entry} or exit {exit_pos} for grid size {w}x{h}")
    except ValueError as e:
        print(f"Error in config.txt: {e}")
        exit(1)

    # 3. 迷路の生成
    maze = MazeGenerator(w, h, entry, exit_pos)

    status_msg = ""
    if not maze.generate(perfect=is_perfect):
        status_msg = "Error: Could not render '42'."

    # 最初に最短経路（座標リスト）を計算しておくべ
    path_str, path_coords = maze.get_solution()

    show_solution = True

    WHITE = "\033[47m  "
    GREEN = "\033[42m  "
    YELLOW = "\033[43m  "
    CYAN = "\033[46m  "
    GRAY = "\033[48;5;250m  "
    RED = "\033[41m  "
    PERPLE = "\033[45m  "

    wall_color = WHITE
    num_color = GRAY

    # --- 視覚的表現（Visual representation）のループ ---
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        if status_msg:
            print(f"{status_msg}")
 
        # 描画の呼び出し（pathを表示するかどうか選んで渡すべ）
        if show_solution is True:
            # 「答えを見せる」設定がONなら
            display_path = path_coords  # 用意してた「正解の座標リスト」を入れる
        else:
            # 「答えを見せる」設定がOFFなら
            display_path = []   # 空っぽ（何もなし）を入れる
        draw_real_maze(maze, display_path, wall_color, num_color)

        print("\n[R]再生成 [S]経路切替 [C]色変更 [N]42・色変更 [Q]保存して終了")
        cmd = input("コマンドを入力してください: ").upper()

        if cmd == 'R':
            maze.generate(perfect=is_perfect)
            path_str, path_coords = maze.get_solution() 
        elif cmd == 'S':
            show_solution = not show_solution
        elif cmd == 'C':
            colors = [WHITE, GREEN, YELLOW, CYAN]
            current_idx = colors.index(wall_color)
            wall_color = colors[(current_idx + 1) % len(colors)]
        elif cmd == 'N':
            num_colors = [GRAY, RED, PERPLE]
            num_idx = num_colors.index(num_color)
            num_color = num_colors[(num_idx + 1) % len(num_colors)]
        elif cmd == 'Q':
            break  # ループを抜けて、ファイル出力へ進むべ！

    # --- 4. 最終的なデータの取得と保存 ---
    # PDF要件にある「NSEW」形式の文字列としての解を取得
    final_path_str, path_coords = maze.get_solution() 

    # 5. ファイル出力（OUTPUT_FILEに書き出すべ）
    output_filename = config["OUTPUT_FILE"]
    save_to_file(maze, output_filename, final_path_str)

    print(f"\n迷路データを {output_filename} に保存しました！")
    print(f"最短経路（NSEW形式）: {final_path_str}")


if __name__ == "__main__":
    main()
