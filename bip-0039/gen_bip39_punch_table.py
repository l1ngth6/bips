#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import math
import sys
import unicodedata
import urllib.request


DEFAULT_BIP39_URL = (
    "https://github.com/bitcoin/bips/raw/refs/heads/master/"
    "bip-0039/english.txt"
)


def read_words(source: str) -> list[str]:
    """
    从本地文件或 URL 读取词表。
    兼容一行一个词，也兼容空白分隔。
    """
    if source.startswith(("http://", "https://")):
        with urllib.request.urlopen(source, timeout=30) as response:
            text = response.read().decode("utf-8")
    else:
        with open(source, "r", encoding="utf-8") as f:
            text = f.read()

    return [word.strip() for word in text.split() if word.strip()]


def calc_bits(word_count: int) -> int:
    """
    计算表示词表索引所需的 bit 数。
    BIP39: 2048 个词 -> 11 bit
    SLIP39: 1024 个词 -> 10 bit
    """
    if word_count <= 1:
        return 1
    return math.ceil(math.log2(word_count))


def char_width(ch: str, ambiguous_width: int = 1) -> int:
    """
    估算字符在等宽终端中的显示宽度。

    ambiguous_width:
    - 1: 适合大多数西文字体终端
    - 2: 适合某些中文环境终端
    """
    if unicodedata.combining(ch):
        return 0

    east_asian_width = unicodedata.east_asian_width(ch)

    if east_asian_width in ("F", "W"):
        return 2

    if east_asian_width == "A":
        return ambiguous_width

    return 1


def display_width(text: str, ambiguous_width: int = 1) -> int:
    return sum(char_width(ch, ambiguous_width) for ch in text)


def pad(
    text: str,
    width: int,
    align: str = "left",
    ambiguous_width: int = 1,
) -> str:
    """
    按显示宽度补空格，而不是简单按 len() 补空格。
    """
    current_width = display_width(text, ambiguous_width)
    spaces = max(0, width - current_width)

    if align == "right":
        return " " * spaces + text

    return text + " " * spaces


def make_rows(
    words: list[str],
    bits: int,
    zero_symbol: str,
    one_symbol: str,
) -> list[list[str]]:
    rows = []

    for index, word in enumerate(words):
        binary = format(index, f"0{bits}b")
        reversed_binary = binary[::-1]

        punch = (
            reversed_binary
            .replace("0", zero_symbol)
            .replace("1", one_symbol)
        )

        rows.append([
            word,
            str(index),
            punch,
            binary,
            reversed_binary,
        ])

    return rows


def print_text_table(
    rows: list[list[str]],
    ambiguous_width: int = 1,
) -> None:
    headers = ["词语", "十进制", "符号化反转二进制", "二进制", "反转二进制"]
    table = [headers] + rows

    widths = [
        max(display_width(row[col], ambiguous_width) for row in table)
        for col in range(len(headers))
    ]

    aligns = ["left", "right", "left", "left", "left"]

    def format_row(row: list[str]) -> str:
        return "  ".join(
            pad(row[col], widths[col], aligns[col], ambiguous_width)
            for col in range(len(headers))
        )

    print(format_row(headers))

    separator = "  ".join("-" * width for width in widths)
    print(separator)

    for row in rows:
        print(format_row(row))


def print_tsv_table(rows: list[list[str]]) -> None:
    headers = ["词语", "十进制", "符号化反转二进制", "二进制", "反转二进制"]

    print("\t".join(headers))

    for row in rows:
        print("\t".join(row))


def print_markdown_table(rows: list[list[str]]) -> None:
    headers = ["词语", "十进制", "符号化反转二进制", "二进制", "反转二进制"]

    print("| " + " | ".join(headers) + " |")
    print("| --- | ---: | --- | --- | --- |")

    for row in rows:
        print("| " + " | ".join(row) + " |")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="生成 BIP39 / SLIP39 风格的反转打孔对照表"
    )

    parser.add_argument(
        "source",
        nargs="?",
        default=DEFAULT_BIP39_URL,
        help="词表文件路径或 URL；默认使用 BIP39 English 词表",
    )

    parser.add_argument(
        "--bits",
        type=int,
        default=None,
        help="索引位宽；BIP39 用 11，SLIP39 用 10。默认按词表数量自动计算",
    )

    parser.add_argument(
        "--format",
        choices=["text", "tsv", "markdown"],
        default="text",
        help="输出格式，默认 text",
    )

    parser.add_argument(
        "--zero",
        default="○",
        help="0 对应的符号，默认 ○",
    )

    parser.add_argument(
        "--one",
        default="●",
        help="1 对应的符号，默认 ●",
    )

    parser.add_argument(
        "--ambiguous-width",
        type=int,
        choices=[1, 2],
        default=1,
        help="东亚模糊宽度字符的显示宽度，默认 1；中文终端错位时可试 2",
    )

    args = parser.parse_args()

    try:
        words = read_words(args.source)
    except Exception as exc:
        print(f"读取词表失败: {exc}", file=sys.stderr)
        sys.exit(1)

    if not words:
        print("词表为空", file=sys.stderr)
        sys.exit(1)

    bits = args.bits or calc_bits(len(words))

    if len(words) > 2 ** bits:
        print(
            f"错误: 当前 bits={bits} 最多只能表示 {2 ** bits} 个词，"
            f"但词表有 {len(words)} 个词",
            file=sys.stderr,
        )
        sys.exit(1)

    rows = make_rows(
        words=words,
        bits=bits,
        zero_symbol=args.zero,
        one_symbol=args.one,
    )

    if args.format == "text":
        print_text_table(rows, ambiguous_width=args.ambiguous_width)
    elif args.format == "tsv":
        print_tsv_table(rows)
    elif args.format == "markdown":
        print_markdown_table(rows)


if __name__ == "__main__":
    main()
