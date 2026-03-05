import random
import collections
from typing import List, Tuple, Optional
from .exceptions import FortyTwoRenderingError


class MazeGenerator:
    """第VI章の要件を完全に満たす迷路生成クラス"""

    def __init__(self, width: int, height: int, entry: Tuple[int, int], exit_pos: Tuple[int, int], seed: Optional[int] = None):
        if not (0 <= entry[0] < width and 0 <= entry[1] < height) or \
           not (0 <= exit_pos[0] < width and 0 <= exit_pos[1] < height):
           raise ValueError(f"Invalid entry {entry} or exit {exit_pos} for grid size {width}x{height}")
        self.width = width
        self.height = height
        self.entry = entry
        self.exit_pos = exit_pos
            random.seed(seed)
        self._reset_grid()

    def _open_outer_wall(self, pos: Tuple[int, int]) -> None:
        """
        入口もしくは出口の壁を開ける
        """
        x, y = pos # 入口か出口の座標

        # 1. 左端（西）が出口の場合
        if y == 0:
            self.grid[y][x]["N"] = False
        elif y == self.height - 1:
            self.grid[y][x]["S"] = False
        # 上下に当てはまらねば、左右をチェックだべ
        elif x == 0:
            self.grid[y][x]["W"] = False
        elif x == self.width - 1:
            self.grid[y][x]["E"] = False

    #壁を壊す関数
    def _break_wall(self, x1: int, y1: int, x2: int, y2: int):
        if x1 == x2:  # 縦に並んでいる場合
            if y1 < y2:  # 下（南）へ
                self.grid[y1][x1]["S"] = False
                self.grid[y2][x2]["N"] = False
            else:        # 上（北）へ
                self.grid[y1][x1]["N"] = False
                self.grid[y2][x2]["S"] = False
        elif y1 == y2:  # 横に並んでいる場合
            if x1 < x2:  # 右（東）へ
                self.grid[y1][x1]["E"] = False
                self.grid[y2][x2]["W"] = False
            else:        # 左（西）へ ★ここを追加だべ！
                self.grid[y1][x1]["W"] = False
                self.grid[y2][x2]["E"] = False


    def _creates_square(self, x: int, y: int) -> bool:
        """
        (x, y) を通路にすると、どこかに2x2の空白ができちまうかチェックするべ
        """
        # チェックする4つの「2x2エリア」のオフセット
        # 左上方向、右上方向、左下方向、右下方向
        check_offsets = [
            [(-1, -1), (-1, 0), (0, -1)], # 自分の左上
            [(1, -1), (1, 0), (0, -1)],  # 自分の右上
            [(-1, 1), (-1, 0), (0, 1)],   # 自分の左下
            [(1, 1), (1, 0), (0, 1)]      # 自分の右下
        ]

        for offset in check_offsets:
            is_square = True
            for dx, dy in offset:
                nx, ny = x + dx, y + dy
                # もし隣人が範囲外、もしくは「まだ壁（all True）」なら、そこは四角形にならねぇ
                if not (0 <= nx < self.width and 0 <= ny < self.height) or \
                   all(self.grid[ny][nx].values()):
                    is_square = False
                    break
            
            if is_square: # 3つの隣人が全部通路だったら、自分が加わると2x2完成...ダメだべ！
                return True
                
        return False

    def _is_42_area(self, x: int, y: int) -> bool:
        """
        指定された座標 (x, y) が『42』の形を構成する範囲かどうかを判定する
        """
        return (x, y) in self.forty_two_coords

    def _can_dig(self, nx, ny):
        # 1. そもそも迷路の範囲内だが？
        if not (0 <= nx < self.width and 0 <= ny < self.height):
            return False

        # 2. すでに「通路」になってねぇか？
        # all(values()) が False なら、どこか壁が壊れてる（＝通路）ってことだべ
        if not all(self.grid[ny][nx].values()):
            return False

        # 3. 【重要】そこは「42」パターンの大事な壁じゃねぇか？
        if self._is_42_area(nx, ny):
            return False

        # 4. 【最重要】3x3（または2x2）の空白ができねぇか？
        # 自分の周囲をチェックして、隣り合う4マスが全部「通路」にならないか確認するべ
        if self._creates_square(nx, ny):
            return False

        return True

    #どこをいつどちら向きに掘ればいいかを決める関数
    def _drill_maze(self, start_pos: Tuple[int, int], perfect: bool):
        stack = [start_pos]
        
        while stack:
            cx, cy = stack[-1] # 今いる場所
            #print(f"DEBUG: Now at {cx, cy}, stack size: {len(stack)}")            
            
            # 1. 周囲（上下左右）の座標をリストにする
            directions = [(0, -1), (1, 0), (0, 1), (-1, 0)] # 北、東、南、西
            random.shuffle(directions) # ランダムに掘るために混ぜるべ！
            
            found = False
            for dx, dy in directions:
                nx, ny = cx + dx, cy + dy
                
                # 2. ★ここで「次の目的地(nx, ny)」が掘れるか門番に聞く！★
                if self._can_dig(nx, ny):
                    # 3. 門番がOK出したら、壁を壊して進むべ！
                    self._break_wall(cx, cy, nx, ny)
                    stack.append((nx, ny))
                    found = True
                    break # 一歩進んだら、その場所からまた探し直すんし
                elif not perfect:
                    # 「聖域じゃねぇ」かつ「範囲内」なら、ごく稀に壁をぶち抜くべ
                    if not self._is_42_area(nx, ny) and \
                       (0 <= nx < self.width and 0 <= ny < self.height):
                        
                        # 例えば「10回に1回」くらい、すでに通路になってる場所とも繋いじまう！
                        if random.random() < 0.1: # 10%の確率
                            self._break_wall(cx, cy, nx, ny)
                            # ここでは stack.append はしねぇ。壁を壊すだけだべ。
            
            if not found:
                # どこにも行けねぇ（行き止まり）なら、一歩戻る
                stack.pop()

    def _embed_42_pattern(self) -> None:
        """
        迷路の真ん中に『42』の形の壁を配置し、掘られないようにマークする
        """
        #　整数除算をして中心の座標を割り出す
        center_x, center_y = self.width // 2, self.height // 2

        #　'4'の形(相対座標)
        shape_4 = [
            (0, 0), (0, 1), (0, 2),  # 縦棒
            (-1, 1), (-2, 1),        # 横棒
            (-2, 0)                  # 左の角
        ]

        # '2' の形（相対座標）
        shape_2 = [
            (2, 0), (3, 0), (4, 0),  # 上
            (4, 1), (3, 1), (2, 1),  # 中
            (2, 2), (3, 2), (4, 2),  # 下
            (4, 1), (2, 2)           # つなぎ（微調整してけれ！）
        ]

        # 実際に「ここが42の範囲」という集合（Set）に座標を入れる
        self.forty_two_coords = set()

        for diff_x, diff_y in shape_4 + shape_2:
            nx_x, nx_y = center_x + diff_x, center_y + diff_y  # 絶対座標に変換
            # 迷路の範囲内であったら集合に加える
            if not 0 <= nx_x < self.width and 0 <= nx_y < self.height:
                raise FortyTwoRenderingError("Could not render '42'.")
            self.forty_two_coords.add((nx_x, nx_y))

    def _reset_grid(self) -> None:
        """
        内部データ：各セルを「北・東・南・西に壁がある」辞書で埋める
        """
        self.grid = [
            [{"N": True, "E": True, "S": True, "W": True} for _ in range(self.width)]
            for _ in range(self.height)
        ]

    def generate(self, perfect: bool = True) -> None:
        """
        迷路を生成するメインルーチン
        """
        # 1. 準備：グリッドを「全部壁」でリセット
        self._reset_grid()

        # 2. 特殊要件：'42' の形に壁を「固定」する
        # この場所はドリルで掘っちゃダメな場所としてマークするべ
        self._embed_42_pattern()

        # 3. メイン生成：穴掘り（ドリル）開始
        # 入口（entry）からスタートして、掘り進める
        self._drill_maze(self.entry, perfect)

        # 4. 仕上げ：入口出口への通路を確保
        self._open_outer_wall(self.entry)
        self._open_outer_wall(self.exit_pos)

    def get_solution(self):
        """
        幅優先探索（BFS）を使って最短経路を見つけ、NSEWの文字列で返すべ！
        """
        start = self.entry
        goal = self.exit_pos
        
        # 1. 探索用の準備
        # queue: 次に調べる場所を入れるもの
        # parent: 「(今の座標): (一つ前の座標, 進んできた方向)」を記録するもの
        queue = collections.deque([start])
        parent = {start: (None, None)} 
        
        found = False
        while queue:
            cx, cy = queue.popleft()
            
            if (cx, cy) == goal:
                found = True
                break
                
            # 2. 今の場所から「壁がねぇ方向」を探す
            # 北(N), 南(S), 東(E), 西(W) の順にチェック
            directions = {
                "N": (0, -1), "S": (0, 1), 
                "E": (1, 0), "W": (-1, 0)
            }
            
            for d_name, (dx, dy) in directions.items():
                nx, ny = cx + dx, cy + dy
                
                # 範囲内か？ 
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    # ★ここが大事！ 壁が壊れてる（False）かつ、まだ行ってねぇ場所か？
                    if not self.grid[cy][cx][d_name] and (nx, ny) not in parent:
                        parent[(nx, ny)] = ((cx, cy), d_name)
                        queue.append((nx, ny))
        
        if not found:
            return "" # ゴールが見つからねぇ時は空っぽを返すべ

        # 3. ゴールから「親」を辿って逆走するべ！
        path = []
        path_coords = [goal]
        curr = goal
        while curr != start:
            prev_pos, direction = parent[curr] # 座標を記録するリスト
            path.append(direction)
            path_coords.append(prev_pos) # 座標もどんどん追加するべ
            curr = prev_pos
            
        # 逆順になってるから、ひっくり返して一本の文字列にするべ
        return "".join(reversed(path)), path_coords[::-1]

    def get_hex_representation(self) -> List[List[str]]:
        """
        各セルの壁情報を 0-F の16進数に変換してリストで返す
        """
        hex_grid = []
        
        for y in range(self.height):
            row = []
            for x in range(self.width):
                # 1. そのマスの壁情報をチェックして、合計値を計算するべ
                val = 0
                if self.grid[y][x]["N"]: val += 1
                if self.grid[y][x]["E"]: val += 2
                if self.grid[y][x]["S"]: val += 4
                if self.grid[y][x]["W"]: val += 8
                
                # 2. 合計値を16進数（1文字）に変換して、大文字にするべ
                # hex(15) は '0xf' になるから、最後の1文字だけ取って大文字にすんだ
                hex_char = hex(val)[2:].upper()
                row.append(hex_char)
                
            hex_grid.append(row)
            
        return hex_grid
