"""configファイルの数値をもとにMazeGeneratorを実行しターミナルに表示した後、実行結果をファイルに出力する."""
from mazegen.generator import MazeGenerator
import os


def save_to_file(maze: MazeGenerator, filename: str, path_str: str) -> None:
    """16進数の迷路データと最短経路をテキストファイルに保存する.

    Args:
        maze (MazeGenerator): 生成した迷路の実体.
        filename (str): 結果を出力するファイル.
        path_str (str): 最短経路.
    """
    hex_data = maze.get_hex_representation()

    with open(filename, "w", encoding="utf-8") as f:
        for row in hex_data:
            f.write("".join(row) + "\n")

        f.write(f"\n{maze.entry[0]},{maze.entry[1]}\n")
        f.write(f"{maze.exit_pos[0]},{maze.exit_pos[1]}\n")
        f.write(f"\n{path_str}\n")


def draw_real_maze(maze: MazeGenerator, path_coords: list[tuple[int, int]],
                   WALL: str, NUM: str) -> None:
    """迷路をターミナルに表示する.

    壁と通路を全く同じ太さ（2文字分）で描画する.
    1マスを「北西角・北壁」「西壁・中心」の2x2ブロックとして扱う.

    Args:
        maze (MazeGenerator) : 生成した迷路の実体.
        path_coords (tuple[int, int]) : 最短経路を座標で表したもの.
        WALL: (str) : 壁の表示色.
        NUM: (str) : 42の表示色.
    """
    RESET = "\033[0m"
    PATH = "\033[40m  "
    ROUTE = "\033[44m  "
    ENTRY = "\033[45m  "
    EXIT = "\033[41m  "
    path_set = set(path_coords) if path_coords else set()

    for y in range(maze.height):
        row_top, row_mid = "", ""
        for x in range(maze.width):
            cell = maze.grid[y][x]
            is_route = (x, y) in path_set and path_coords

            row_top += WALL
            if cell["N"]:
                row_top += WALL
            else:
                if is_route and (x, y-1) in path_set:
                    row_top += ROUTE
                else:
                    row_top += PATH

            if cell["W"]:
                row_mid += WALL
            elif is_route and (x-1, y) in path_set:
                row_mid += ROUTE
            else:
                row_mid += PATH

            if (x, y) == maze.entry:
                center = ENTRY
            elif (x, y) == maze.exit_pos:
                center = EXIT
            elif (x, y) in getattr(maze, 'forty_two_coords', []):
                center = NUM
            elif is_route:
                center = ROUTE
            else:
                center = PATH
            row_mid += center

        last_cell = maze.grid[y][maze.width-1]
        row_top += WALL
        row_mid += (WALL if last_cell["E"] else PATH)

        print(f"{row_top}{RESET}")
        print(f"{row_mid}{RESET}")

    bottom_line = ""
    for x in range(maze.width):
        cell = maze.grid[maze.height-1][x]
        bottom_line += (WALL + (WALL if cell["S"] else PATH))
    print(f"{bottom_line}{WALL}{RESET}")


def load_config(filename: str) -> dict[str, str]:
    """configファイルを開き、中身を保存する.

    Args:
        filename (str): configファイル.

    Returns:
        dict: configファイルから読み取った情報.
    """
    config = {}
    try:
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                if '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()

    except FileNotFoundError:
        print(f"Error: {filename} not found.")
        exit(1)

    required_keys = [
        "WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"
        ]
    for r_key in required_keys:
        if r_key not in config:
            print(f"Error: Missing mandatory key '{r_key}'")
            exit(1)

    return config


def main() -> None:
    """迷路生成に必要な情報を変数に保存する.MazeGeneratorを実行する.ターミナルに描画する.実行結果をresultファイルに出力する.

    Raises:
        ValueError: 迷路の幅、高さ設定が無効範囲である場合.
        ValueError: perfectの値がtrue/false以外である場合.
        ValueError: entryの座標の値が2以外である場合.
        ValueError: exitの座標の値が2以外である場合.
        ValueError: entry,exitの座標が迷路の範囲外に有る場合.
    """
    config = load_config("config.txt")

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
            raise ValueError(f"Invalid entry {entry} or exit"
                             f" {exit_pos} for grid size {w}x{h}")
    except ValueError as e:
        print(f"Error in config.txt: {e}")
        exit(1)

    maze = MazeGenerator(w, h, entry, exit_pos)

    status_msg = ""
    if not maze.generate(perfect=is_perfect):
        status_msg = "Error: Could not render '42'."

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

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        if status_msg:
            print(f"{status_msg}")

        if show_solution is True:
            display_path = path_coords
        else:
            display_path = []
        draw_real_maze(maze, display_path, wall_color, num_color)

        print("\n[R]再生成 [S]経路切替 [C]色変更 [N]42・色変更 [Q]保存して終了")
        cmd = input("コマンドを入力してください: ").upper()

        if cmd == 'R':
            maze.generate(is_perfect)
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
            break

    final_path_str, path_coords = maze.get_solution()
    output_filename = config["OUTPUT_FILE"]
    save_to_file(maze, output_filename, final_path_str)

    print(f"\n迷路データを {output_filename} に保存しました！")
    print(f"最短経路（NSEW形式）: {final_path_str}")


if __name__ == "__main__":
    main()
