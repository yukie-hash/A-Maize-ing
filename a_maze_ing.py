from mazegen.generator import MazeGenerator
import os
import colorama
from colorama import Fore, Back, Style


def is_wall(maze, x: int, y: int) -> bool:
    """
    指定された座標 (x, y) が『42』の壁、
    もしくはまだ誰も掘ってねぇ真っさらな壁かどうかを判定するべ！
    """
    # 1. 範囲外なら、とりあえず壁扱いにしとくべ
    if not (0 <= x < maze.width and 0 <= y < maze.height):
        return True

    # 2. 『42』の聖域なら、そこは絶対的な壁だべ
    if maze._is_42_area(x, y):
        return True

    # 3. 4方向全部が壁（True）のままなら、そこはまだ手付かずの壁だんし
    cell = maze.grid[y][x]
    return all(cell.values())

def draw_real_maze(maze, path_coords):
    hex_grid = maze.get_hex_representation()
    
    for y, row in enumerate(hex_grid):
        top = ""
        mid = ""
        for x, char in enumerate(row):
            val = int(char, 16)
            curr_pos = (x, y)
            
            # --- 1. 頭（北側の壁）を作る ---
            # 北(1)に壁があるか？
            top += Fore.WHITE + "+--" if (val & 1) else Fore.WHITE + "+  "
            
            # --- 2. 胴体（西側の壁と中身）を作る ---
            # 西(8)に壁があるか？
            mid += Fore.WHITE + "| " if (val & 8) else "  "
            
            # --- 3. 中身（最短経路、入口、出口、通路）を決める ---
            if curr_pos == maze.entry:
                mid += Fore.MAGENTA + "I" # 入口(In)
            elif curr_pos == maze.exit_pos:
                mid += Fore.MAGENTA + "O" # 出口(Out)
            elif curr_pos in path_coords:
                mid += Fore.RED + "●"      # 最短経路
            else:
                mid += " "                # ただの道
                
            mid += Style.RESET_ALL # 色をリセット

        # 各行の右端（東）と下端（南）を閉じるべ
        print(top + "+")
        print(mid + "|")
        
    # 一番下の底辺を描く
    print(Fore.WHITE + "---" * len(hex_grid[0]) + "+")

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
    maze = MazeGenerator(w, h, entry, exit_pos)
    maze.generate(perfect=is_perfect)
    
    # 最初に最短経路（座標リスト）を計算しておくべ
    path_str, path_coords = maze.get_solution() 
    
    show_solution = True
    wall_color = Fore.WHITE

    # --- 視覚的表現（Visual representation）のループ ---
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # 描画の呼び出し（pathを表示するかどうか選んで渡すべ）
        if show_solution == True:
            # 「答えを見せる」設定がONなら
            current_path = path_coords  # 用意してた「正解の座標リスト」を入れる
        else:
            # 「答えを見せる」設定がOFFなら
            path_coords = []             # 空っぽ（何もなし）を入れるcurrent_path = solution_path if show_solution else []
        draw_real_maze(maze, path_coords)
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
    final_path_str = maze.get_solution() 
    
    # 5. ファイル出力（OUTPUT_FILEに書き出すべ）
    output_filename = config["OUTPUT_FILE"]
    maze.save_to_file(output_filename, final_path_str)
    
    print(f"\n迷路データを {output_filename} に保存しました！")
    print(f"最短経路（NSEW形式）: {final_path_str}")


if __name__ == "__main__":
    main()