from mazegen.generator import MazeGenerator
import os
import colorama
from colorama import Fore, Back, Style
from mazegen.exceptions import FortyTwoRenderingError


def save_to_file(maze, filename: str, path_str: str) -> None:
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


def draw_real_maze(maze, path_coords, show_solution: bool, wall_color) -> None:
    # ANSIエスケープコード（標準機能だべ）
    RESET = "\033[0m"
    BLACK = "\033[40m"    # 通路（黒）
    ENTRY_CLR = "\033[45m" # 入口（紫）
    EXIT_CLR = "\033[41m"  # 出口（赤）
    PATTERN_42 = "\033[48;5;250m" # 「42」用のグレー

    # 横と縦それぞれ2回描くとセルが正方形に見える
    horiz_repeat = 2
    vert_repeat = 1
    # 必要に応じて vert_repeat=1 で縦方向のみ1行にする

    for y in range(maze.height):
        # --- 1段目：北側の壁を描く行 ---
        line1 = ""
        for x in range(maze.width):
            # 北(N)か西(W)に壁があれば壁色、なければ通路色
            is_wall = maze.grid[y][x]["N"]
            color = wall_color if is_wall else BLACK
            # 各セルパーツを横方向に繰り返す
            line1 += (f"{color}  {RESET}" * horiz_repeat)
        # 右端に東側の壁を1つ追加
        e_wall = maze.grid[y][maze.width-1]["E"]
        line1 += (f"{wall_color if e_wall else BLACK} {RESET}" * horiz_repeat)
        for _ in range(vert_repeat):
            print(line1)

        # --- 2段目：西側の壁と通路（中心）を描く行 ---
        line2 = ""
        for x in range(maze.width):
            # 1. 西側の壁
            w_color = wall_color if maze.grid[y][x]["W"] else BLACK
            line2 += (f"{w_color} {RESET}" * horiz_repeat) 

            # 2. セルの中心（通路 / 入口 / 出口 / 42 / 経路）
            target_color = BLACK
            if (x, y) == maze.entry:
                target_color = ENTRY_CLR
            elif (x, y) == maze.exit_pos:
                target_color = EXIT_CLR
            elif (x, y) in maze.forty_two_coords: # 42パターンの座標
                target_color = PATTERN_42
            elif (x, y) in path_coords: # 最短経路
                target_color = "\033[44m" # 経路は青とかにするべ

            line2 += (f"{target_color} {RESET}" * horiz_repeat)
        # 右側の東壁を追加
        e_wall = maze.grid[y][maze.width-1]["E"]
        line2 += (f"{wall_color if e_wall else BLACK} {RESET}" * horiz_repeat)
        for _ in range(vert_repeat):
            print(line2)

        # 3段目：南側の壁（最後の行だけ）
        if y == maze.height - 1:
            line3 = ""
            for x in range(maze.width):
                s_wall = maze.grid[y][x]["S"]
                color = wall_color if s_wall else BLACK
                line3 += (f"{color}  {RESET}" * horiz_repeat)
            # 南東の角
            e_wall = maze.grid[y][maze.width-1]["E"]
            line3 += (f"{wall_color if e_wall else BLACK} {RESET}" * horiz_repeat)
            for _ in range(vert_repeat):
                print(line3)


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


def main():
    # 1. 設定の読み込み
    config = load_config("config.txt")
    
    # 2. 値の変換
    w = int(config["WIDTH"])
    h = int(config["HEIGHT"])
    is_perfect = config["PERFECT"].lower() == "true"
    # 入口と出口も設定から持ってくるべ
    entry = tuple(map(int, config["ENTRY"].split(',')))
    exit_pos = tuple(map(int, config["EXIT"].split(',')))
    
    # 3. 迷路の生成
    try:
        maze = MazeGenerator(w, h, entry, exit_pos)
    except ValueError as e:
        print(f"Error: {e}")
        exit(1)

    try:
        maze.generate(perfect=is_perfect)
    except FortyTwoRenderingError as e:
        print(f"Error: {e}")
        exit(1)
    
    # 最初に最短経路（座標リスト）を計算しておくべ
    path_str, path_coords = maze.get_solution()
    
    show_solution = True
    wall_color = "\033[47m"

    # --- 視覚的表現（Visual representation）のループ ---
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # 描画の呼び出し（pathを表示するかどうか選んで渡すべ）
        if show_solution == True:
            # 「答えを見せる」設定がONなら
            display_path = path_coords  # 用意してた「正解の座標リスト」を入れる
        else:
            # 「答えを見せる」設定がOFFなら
            display_path = []   # 空っぽ（何もなし）を入れる
        draw_real_maze(maze, display_path, show_solution, wall_color)
        print("\n[R]再生成 [S]経路切替 [C]色変更 [Q]保存して終了")
        cmd = input("コマンドを入力してください: ").upper()

        if cmd == 'R':
            maze.generate(perfect=is_perfect)
            path_str, path_coords = maze.get_solution() 
        elif cmd == 'S':
            show_solution = not show_solution
        elif cmd == 'C':
            colors = [Fore.WHITE, Fore.RED, Fore.GREEN, Fore.CYAN, Fore.YELLOW]
            current_idx = colors.index(wall_color)
            wall_color = colors[(current_idx + 1) % len(colors)]
        elif cmd == 'Q':
            break # ループを抜けて、ファイル出力へ進むべ！

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