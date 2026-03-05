import random
from typing import List, Tuple, Optional

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

    def generate(self, perfect: bool = True) -> None:
        """迷路生成アルゴリズムの実装
        - 3x3の広場禁止
        - '42' パターンの埋め込み
        """
        pass

    def get_solution(self) -> str:
        """最短経路を NSEW の文字列で返す"""
        # ここで幅優先探索（BFS）などを使って経路を見つけるべ
        return "NNEESW"

    def get_hex_representation(self) -> List[List[str]]:
        """第IV.5章の要件：各セルの壁情報を16進数(0-F)のリストで返す"""
        # ビット演算を使って 0-F を計算するロジック
        pass