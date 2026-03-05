from mazegen.generator import MazeGenerator


def draw_maze(maze, show_path, color):
    """ターミナルにASCIIで迷路を描画する関数だべ"""
    path_coords = maze.get_solution_coords() if show_path else []

    for y in range(maze.height):
        line = ""
        for x in range(maze.width):
            # 優先順位をつけて描画する文字を決めるべ
            if (x, y) == maze.entry:
                line += Fore.MAGENTA + "IN"
            elif (x, y) == maze.exit_pos:
                line += Fore.MAGENTA + "OUT"
            elif (x, y) in path_coords:
                line += Fore.RED + "● " # 最短経路
            elif hasattr(maze, 'is_42') and maze.is_42(x, y):
                line += Fore.YELLOW + "42" # 42パターン（オプション）
            elif maze.is_wall(x, y):
                line += color + "██" # 壁
            else:
                line += "  " # 通路
        print(line)


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
    solution_path = maze.get_solution_coords() 
    
    show_solution = False
    wall_color = Fore.WHITE

    # --- 視覚的表現（Visual representation）のループ ---
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # 描画の呼び出し（pathを表示するかどうか選んで渡すべ）
        current_path = solution_path if show_solution else []
        draw_maze(maze, current_path, wall_color)

        print("\n[R]再生成 [S]経路切替 [C]色変更 [Q]保存して終了")
        cmd = input("コマンドを入力してけれ: ").upper()

        if cmd == 'R':
            maze.generate(perfect=is_perfect)
            solution_path = maze.get_solution_coords() 
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
    
    print(f"\n迷路データを {output_filename} に保存したんし！")
    print(f"最短経路（NSEW形式）: {final_path_str}")


if __name__ == "__main__":
    main()