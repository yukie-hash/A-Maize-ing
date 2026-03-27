"""迷路を生成し、最短経路を探索する."""
import random
import collections
from typing import List, Tuple, Optional


class MazeGenerator:
    """迷路を生成し、最短経路を探索する."""

    def __init__(self, width: int, height: int, entry: Tuple[int, int],
                 exit_pos: Tuple[int, int],
                 seed: Optional[int] = None) -> None:
        """迷路の情報を初期化する.

        Args:
            width (int): 迷路の幅.
            height (int): 迷路の高さ.
            entry (Tuple[int, int]): 入口の座標.
            exit_pos (Tuple[int, int]): 出口の座標.
            seed (Optional[int], optional): シード値 Defaults to None.
        """
        self.width = width
        self.height = height
        self.entry = entry
        self.exit_pos = exit_pos
        random.seed(seed)
        self._reset_grid()
        self.forty_two_coords: set[tuple[int, int]] = set()

    def _open_outer_wall(self, pos: Tuple[int, int]) -> None:
        """入口もしくは出口の壁を開ける.

        Args:
            pos (Tuple[int, int]): 入口もしくは出口の座標.
        """
        x, y = pos

        if y == 0:
            self.grid[y][x]["N"] = False
        if y == self.height - 1:
            self.grid[y][x]["S"] = False
        if x == 0:
            self.grid[y][x]["W"] = False
        if x == self.width - 1:
            self.grid[y][x]["E"] = False

    def _break_wall(self, x1: int, y1: int, x2: int, y2: int) -> None:
        """指定された2つのセル間の壁を取り除く.

        Args:
            x1 (int): 現在のセルのX座標.
            y1 (int): 現在のセルのY座標.
            x2 (int): 隣接するセルのX座標.
            y2 (int): 隣接するセルのY座標.

        Returns:
            None: 戻り値はない。
        """
        if x1 == x2:
            if y1 < y2:
                self.grid[y1][x1]["S"] = False
                self.grid[y2][x2]["N"] = False
            else:
                self.grid[y1][x1]["N"] = False
                self.grid[y2][x2]["S"] = False
        elif y1 == y2:
            if x1 < x2:
                self.grid[y1][x1]["E"] = False
                self.grid[y2][x2]["W"] = False
            else:
                self.grid[y1][x1]["W"] = False
                self.grid[y2][x2]["E"] = False

    def _creates_square(self, x: int, y: int) -> bool:
        """(x, y) を通路にすると、どこかに3✕3の空白ができてしまわないかをチェックする.

        Args:
            x (int): 現在のセルのX座標.
            y (int): 現在のセルのY座標.

        Returns:
            True (bool): 通路にすると3✕3の空白ができてしまう
            False (bool): 3✕3の通路にならない、つまり穴を掘っていいセルである
        """
        check_offsets = [
            [(-1, -1), (-1, 0), (0, -1)],
            [(1, -1), (1, 0), (0, -1)],
            [(-1, 1), (-1, 0), (0, 1)],
            [(1, 1), (1, 0), (0, 1)]
        ]

        for offset in check_offsets:
            is_square = True
            for dx, dy in offset:
                nx, ny = x + dx, y + dy
                if not (0 <= nx < self.width and 0 <= ny < self.height) or \
                   all(self.grid[ny][nx].values()):
                    is_square = False
                    break

            if is_square:
                return True

        return False

    def _is_42_area(self, x: int, y: int) -> bool:
        """
        指定された座標 (x, y) が『42』の形を構成する範囲かどうかを判定する.

        Args:
            x (int): 指定されたX座標.
            y (int): 指定されたY座標.

        Returns:
            True (bool): 42の範囲である.
            False (bool): 42の範囲でない.
        """
        return (x, y) in self.forty_two_coords

    def _can_dig(self, nx: int, ny: int) -> bool:
        """指定したセルが壊してもいい壁かどうかを確認する.

        Args:
            nx (int): 指定されたX座標.
            ny (int): 指定されたY座標.

        Returns:
            True (bool): 壊して良い壁である.
            False (bool): 壊せない壁である.
        """
        if not (0 <= nx < self.width and 0 <= ny < self.height):
            return False

        if not all(self.grid[ny][nx].values()):
            return False

        if self._is_42_area(nx, ny):
            return False

        if self._creates_square(nx, ny):
            return False

        return True

    def _drill_maze(self, start_pos: Tuple[int, int], perfect: bool) -> None:
        """穴掘り法を用いて通路を掘っていく.

        スタックに現在地を保存しながら

        Args:
            start_pos (Tuple[int, int]): 入口の座標.
            perfect (bool): 完璧な迷路を生成するか否かの指示.
        """
        stack = [start_pos]
        while stack:
            cx, cy = stack[-1]
            # print(f"DEBUG: Now at {cx, cy}, stack size: {len(stack)}")

            directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
            random.shuffle(directions)

            found = False
            for dx, dy in directions:
                nx, ny = cx + dx, cy + dy

                if self._can_dig(nx, ny):
                    self._break_wall(cx, cy, nx, ny)
                    stack.append((nx, ny))
                    found = True
                    break
                if not perfect:
                    if not self._is_42_area(nx, ny) and \
                       (0 <= nx < self.width and 0 <= ny < self.height):

                        if random.random() < 0.1:  # 10%の確率
                            self._break_wall(cx, cy, nx, ny)

            if not found:
                stack.pop()

    def _embed_42_pattern(self) -> bool:
        """迷路の真ん中に『42』の形の壁を配置し、壊されないようにマークする.

        Returns:
            bool: 42を描けたらTrue、迷路の範囲が小さすぎて描けなかったらFalseを返す.
        """
        center_x, center_y = (self.width // 2) - 3, (self.height // 2) - 2

        shape_4 = [
            (0, 0), (0, 1), (0, 2),
            (1, 2), (2, 2),
            (2, 3), (2, 4)
        ]

        shape_2 = [
            (4, 0), (5, 0), (6, 0),
            (4, 2), (5, 2), (6, 2),
            (4, 4), (5, 4), (6, 4),
            (4, 3), (6, 1)
        ]

        tmp_coords = set()

        for diff_x, diff_y in shape_4 + shape_2:
            nx_x, nx_y = center_x + diff_x, center_y + diff_y
            if not 0 <= nx_x < self.width and 0 <= nx_y < self.height:
                return False
            tmp_coords.add((nx_x, nx_y))

        self.forty_two_coords = tmp_coords
        return True

    def _fill_remaining_cells(self) -> None:
        """孤立したセルをなくす.

        四方が壁に囲まれたセルをみつけ、壁に穴を開ける.
        """
        for y in range(self.height):
            for x in range(self.width):
                if all(self.grid[y][x].values()) \
                        and not self._is_42_area(x, y):

                    directions = [
                        (0, -1, "N", "S"),
                        (0, 1, "S", "N"),
                        (1, 0, "E", "W"),
                        (-1, 0, "W", "E")
                    ]
                    random.shuffle(directions)

                    for dx, dy, self_dir, neighbor_dir in directions:
                        nx, ny = x + dx, y + dy

                        if 0 <= nx < self.width and 0 <= ny < self.height:
                            if not all(self.grid[ny][nx].values()):
                                self.grid[y][x][self_dir] = False
                                self.grid[ny][nx][neighbor_dir] = False
                                break

    def _reset_grid(self) -> None:
        """各セルを「北・東・南・西に壁がある」辞書で埋める."""
        self.grid = [
            [{"N": True, "E": True, "S": True, "W": True}
                for _ in range(self.width)]
            for _ in range(self.height)
        ]

    def _break_wall_further(self) -> None:
        """完璧な迷路生成後に、3方向の壁が立っている行き止まりのセルを見つけ穴を開けることで、完璧でない迷路を作る."""
        for y in range(self.height):
            for x in range(self.width):
                wall_count = sum(self.grid[y][x].values())
                if wall_count == 3 and not self._is_42_area(x, y):

                    directions = [
                        (0, -1, "N", "S"),  # 北
                        (0, 1, "S", "N"),   # 南
                        (1, 0, "E", "W"),   # 東
                        (-1, 0, "W", "E")   # 西
                    ]
                    random.shuffle(directions)

                    for dx, dy, self_dir, neighbor_dir in directions:
                        nx, ny = x + dx, y + dy

                        if 0 <= nx < self.width and 0 <= ny < self.height:
                            if not all(self.grid[ny][nx].values()):
                                self.grid[y][x][self_dir] = False
                                self.grid[ny][nx][neighbor_dir] = False
                                break

    def generate(self, perfect: bool = True) -> bool:
        """迷路を生成する.

        Args:
            perect (bool): 完璧な迷路を生成するか否か.デフォルトではTrue.

        Returns:
            success (bool): 42の配置に成功した場合Trueを返す.
                            配置できなかった場合Falseを返す.
        """
        self._reset_grid()

        success = self._embed_42_pattern()

        self._drill_maze(self.entry, perfect)

        self._fill_remaining_cells()

        if not perfect:
            self._break_wall_further()

        return success

    def get_solution(self) -> Tuple[str, List[Tuple[int, int]]]:
        """幅優先探索（BFS）を使って最短経路を見つけ、座標とNSEWの文字列で返す.

        Returns:
            Tuple[str, List[Tuple[int, int]]]: 最短経路の座標とNSEWの文字列.
        """
        start = self.entry
        goal = self.exit_pos

        queue = collections.deque([start])
        parent: dict[tuple[int, int],
                     tuple[Optional[tuple[int, int]],
                           Optional[str]]] = {start: (None, None)}

        found = False
        while queue:
            cx, cy = queue.popleft()

            if (cx, cy) == goal:
                found = True
                break

            directions = {
                "N": (0, -1), "S": (0, 1),
                "E": (1, 0), "W": (-1, 0)
            }

            for d_name, (dx, dy) in directions.items():
                nx, ny = cx + dx, cy + dy

                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if not self.grid[cy][cx][d_name] \
                            and (nx, ny) not in parent:
                        parent[(nx, ny)] = ((cx, cy), d_name)
                        queue.append((nx, ny))

        if not found:
            return "", []

        path: list[str] = []
        path_coords = [goal]
        curr = goal
        while curr != start:
            prev_pos, direction = parent[curr]
            if prev_pos is None or direction is None:
                break
            path.append(direction)
            path_coords.append(prev_pos)
            curr = prev_pos

        return "".join(reversed(path)), path_coords[::-1]

    def get_hex_representation(self) -> List[List[str]]:
        """各セルの壁情報を 0-F の16進数に変換してリストで返す.

        各セルの上の壁が立っていたら1、右の壁が立っていたら2、下なら4、左なら8として、
        その合計値でどの壁が立っているかを表す.

            Returns:
                hex_grid (List[List[str]]) : 各セルのどの壁が立っているかを16進数で表したもの.
        """
        hex_grid = []

        for y in range(self.height):
            row = []
            for x in range(self.width):
                val = 0
                if self.grid[y][x]["N"]:
                    val += 1
                if self.grid[y][x]["E"]:
                    val += 2
                if self.grid[y][x]["S"]:
                    val += 4
                if self.grid[y][x]["W"]:
                    val += 8

                hex_char = hex(val)[2:].upper()
                row.append(hex_char)

            hex_grid.append(row)

        return hex_grid
