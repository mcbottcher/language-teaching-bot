#!/usr/bin/env python3
"""Report token usage and cost per user (Haiku pricing)."""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "users.db"

INPUT_PRICE_PER_M = 1.0   # $ per million input tokens
OUTPUT_PRICE_PER_M = 5.0  # $ per million output tokens


def calc_cost(input_tokens: int, output_tokens: int) -> float:
    return (input_tokens / 1_000_000) * INPUT_PRICE_PER_M + \
           (output_tokens / 1_000_000) * OUTPUT_PRICE_PER_M


def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT name, user_id, input_tokens, output_tokens FROM users ORDER BY name"
    ).fetchall()
    conn.close()

    if not rows:
        print("No users found.")
        return

    total_input = total_output = 0

    print(f"{'User':<25} {'User ID':<15} {'Input':>12} {'Output':>12} {'Cost':>10}")
    print("-" * 78)

    for row in rows:
        inp = row["input_tokens"] or 0
        out = row["output_tokens"] or 0
        cost = calc_cost(inp, out)
        total_input += inp
        total_output += out
        print(f"{row['name'] or 'unknown':<25} {row['user_id']:<15} {inp:>12,} {out:>12,} ${cost:>9.4f}")

    print("-" * 78)
    total_cost = calc_cost(total_input, total_output)
    print(f"{'TOTAL':<25} {'':<15} {total_input:>12,} {total_output:>12,} ${total_cost:>9.4f}")
    print()
    print(f"Pricing: ${INPUT_PRICE_PER_M}/M input tokens, ${OUTPUT_PRICE_PER_M}/M output tokens (Haiku)")


if __name__ == "__main__":
    main()
