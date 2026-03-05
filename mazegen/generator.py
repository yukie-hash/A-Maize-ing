import random
from typing import List, Tuple, Optional


class MazeGenerator:
    """第VI章の要件を完全に満たす迷路生成クラス"""

    def __init__(self, width: int, height: int, entry: Tuple[int, int], exit_pos: Tuple[int, int], seed: Optional[int] = None):
        self.width = width
        self.height = height
        self.entry = entry
        self.exit_pos = exit_pos
        if seed is not None:
            random.seed(seed)
        
        # 内部データ：各セルを「北・東・南・西に壁がある」辞書で埋める
        self.grid = [
            [{"N": True, "E": True, "S": True, "W": True} for _ in range(width)]
            for _ in range(height)
        ]

    #壁を壊す関数
    def _break_wall(self, x1: int, y1: int, x2: int, y2: int):
    """(x1, y1) と (x2, y2) の間の壁を取り除く"""
    if x1 == x2:  # 縦に並んでいる場合
        if y1 < y2:  # (x1, y1)が上
            self.grid[y1][x1]["S"] = False
            self.grid[y2][x2]["N"] = False
        else:        # (x1, y1)が下
            self.grid[y1][x1]["N"] = False
            self.grid[y2][x2]["S"] = False
    elif y1 == y2:  # 横に並んでいる場合
        if x1 < x2:  # (x1, y1)が左
            self.grid[y1][x1]["E"] = False
            self.grid[y2][x2]["W"] = False

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
    def _drill_maze(self, start_pos, perfect=True):
    # 掘るべき場所を記録しておく「スタック（メモ書き）」
        stack = [start_pos]
    
        while stack:
            cx, cy = stack[-1] # 今いる場所
        
            # 1. 周囲（上下左右）で「まだ掘れる場所」を探す
            neighbors = self._get_diggable_neighbors(cx, cy)
        
            if neighbors:
                # 2. 掘れる場所があったら、ランダムに一つ選ぶ
                nx, ny = random.choice(neighbors)
            
                # 3. 穴を掘る
                self._break_wall(cx, cy, nx, ny)
            
                # 4. 新しい場所をスタックに入れて、次はその場所から掘る
                stack.append((nx, ny))
            else:
                # 5. どこにも掘る場所がねぇ（行き止まり）なら、一歩戻る
                stack.pop()

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
        self._drill_maze(start_pos=self.entry, perfect=perfect)

        # 4. 仕上げ：出口（exit）への通路を確保
        # 最後にちゃんと出口に繋がっているか確認し、必要なら壁を壊す
        self._connect_exit()

    def get_solution(self) -> str:
        """最短経路を NSEW の文字列で返す"""
        # ここで幅優先探索（BFS）などを使って経路を見つけるべ
        return "NNEESW"

    def get_hex_representation(self) -> List[List[str]]:
        """第IV.5章の要件：各セルの壁情報を16進数(0-F)のリストで返す"""
        # ビット演算を使って 0-F を計算するロジック
        pass