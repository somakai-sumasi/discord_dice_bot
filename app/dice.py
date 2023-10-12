import random
import re
from dataclasses import dataclass
from typing import List
from lark import Lark, Transformer, LarkError


class Dice:
    """ダイス

    Attributes
    ----------
    base_txt : int
        元の文字列
    is_dice_roll : bool
        ダイスを振ったかどうか
    dice_results : List[DiceResult]
        ダイス結果
    display_txt : str
        表示用文字列
    calculate_txt : srt
        計算用文字列
    """

    def __init__(self, txt: str) -> None:
        self.base_txt: str = txt
        self.is_dice_roll: bool = False
        self.dice_results: List[DiceResult] = []
        self.display_txt: str = ""
        self.calculate_txt: str = ""

        self.roll()
        self.set_value()

    def roll(self) -> None:
        """ダイスを振る"""
        dice_results = []
        for match in re.finditer(r"(?<!\d)([dD](\d+))(?!\d)", self.base_txt):
            target = match.group(1)
            sided = int(match.group(2))
            dice_results.append(DiceResult(target, dice_roll(sided)))

        for match in re.finditer(r"((\d+)[Dd](\d+))", self.base_txt):
            target = match.group(1)
            dice_qty = int(match.group(2))
            sided = int(match.group(3))
            dice_results.append(DiceResult(target, dice_roll(sided, dice_qty)))

        self.dice_results = dice_results
        if len(dice_results) > 0:
            self.is_dice_roll = True

    def set_value(self) -> None:
        """値をセットする"""
        display_txt = self.base_txt
        calculate_txt = self.base_txt
        for dice_result in self.dice_results:
            list_txt = "[" + ",".join(map(str, dice_result.result)) + "]"
            sum_txt = str(sum(dice_result.result))
            display_txt = display_txt.replace(dice_result.key, list_txt, 1)
            calculate_txt = calculate_txt.replace(dice_result.key, sum_txt, 1)

        self.display_txt = display_txt
        self.calculate_txt = calculate_txt


@dataclass
class DiceResult:
    key: str
    """置換先のダイスコマンド
    """

    result: list
    """ダイスの結果
    """


def dice_roll(sided: int, dice_qty: int = 1) -> List[int]:
    """ダイスを振る

    Parameters
    ----------
    sided : int
        ダイスの面数
    dice_qty : int, optional
        ダイスの個数, by default 1

    Returns
    -------
    List[int]
        ダイスの結果
    """
    roll_list = list()
    for _ in range(dice_qty):
        roll_list.append((random.randint(1, sided)))
    return roll_list


# 文法規則の定義
grammar = """
    start: comparison
    ?comparison: sum
        | sum ">" sum  -> gt
        | sum "<" sum  -> lt
        | sum ">=" sum -> ge
        | sum "<=" sum -> le
    ?sum: product
        | sum "+" product   -> add
        | sum "-" product   -> sub
    ?product: atom
        | product "*" atom  -> mul
        | product "/" atom  -> div
    ?atom: NUMBER           -> number
         | "-" atom         -> neg
         | "(" comparison ")"
    %import common.NUMBER   // 数字
    %import common.WS       // 空白
    %ignore WS              // 空白を無視
"""

# Larkインスタンスの生成
parser = Lark(grammar, start="start", parser="lalr")


# 計算ロジックを実装
class CalculateTree(Transformer):
    def __init__(self):
        self.has_comparison = False
        self.has_arithmetic = False

    def add(self, args):
        self.has_arithmetic = True
        return args[0] + args[1]

    def sub(self, args):
        self.has_arithmetic = True
        return args[0] - args[1]

    def mul(self, args):
        self.has_arithmetic = True
        return args[0] * args[1]

    def div(self, args):
        self.has_arithmetic = True
        return args[0] / args[1]

    def gt(self, args):
        self.has_comparison = True
        return args[0], args[0] > args[1]

    def lt(self, args):
        self.has_comparison = True
        return args[0], args[0] < args[1]

    def ge(self, args):
        self.has_comparison = True
        return args[0], args[0] >= args[1]

    def le(self, args):
        self.has_comparison = True
        return args[0], args[0] <= args[1]

    def number(self, args):
        return float(args[0])

    def neg(self, args):
        return -args[0]

    def start(self, args):
        if self.has_comparison and self.has_arithmetic:
            return CalculateResult(True, args[0][0], True, args[0][1])
        elif self.has_comparison:
            return CalculateResult(False, 0, True, args[0][1])
        elif self.has_arithmetic:
            return CalculateResult(True, args[0], False, True)


@dataclass
class CalculateResult:
    is_calculate: bool
    """算術演算があったか
    """
    calculate_result: float
    """算術演算結果
    """
    is_comparative: bool
    """比較演算があったか
    """
    comparative_result: bool
    """比較演算結果
    """


# Transformerインスタンスの生成
calc = CalculateTree()


def evaluate_expression(expression: str) -> str | None:
    """算術表現を評価する関数

    Parameters
    ----------
    expression : str
        評価する算術表現

    Returns
    -------
    str | None
        評価結果
    """
    try:
        # 構文解析
        parse_tree = parser.parse(expression)

        # 計算
        calc.has_comparison = False
        calc.has_arithmetic = False
        result = calc.transform(parse_tree)

        return result

    except LarkError:
        return None
