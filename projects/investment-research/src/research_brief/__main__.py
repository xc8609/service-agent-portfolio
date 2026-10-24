"""Run a comparison from a local evidence packet; no network or model calls."""

import argparse
import json
import sys

from .comparison import ComparisonError, compare


def main():
    parser = argparse.ArgumentParser(description="Compare two annual evidence periods.")
    parser.add_argument("path", help="Path to a JSON evidence packet")
    args = parser.parse_args()
    try:
        with open(args.path, encoding="utf-8") as source:
            packet = json.load(source)
        result = compare(packet)
    except (OSError, UnicodeError, ValueError, ComparisonError) as exc:
        print("research_brief: {}".format(exc), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
