#!/usr/bin/env python
# by Dominik Stanisław Suchora <hexderm@gmail.com>
# License: GNU GPLv3

import sys
import argparse
import json

import biggusdictus


def add_file(sche, path):
    with open(path, "rb") as f:
        sche.add(json.load(f))


def main():
    parser = argparse.ArgumentParser(
        description="Tool for generating validation schemes for json files",
        add_help=False,
    )

    parser.add_argument(
        "files",
        metavar="FILE",
        type=str,
        nargs="*",
        help="json files",
    )

    general = parser.add_argument_group("General")
    general.add_argument(
        "-h",
        "--help",
        action="help",
        help="Show this help message and exit",
    )
    general.add_argument(
        "-p",
        "--pedantic",
        action="store_true",
        help="return scheme with more detailed constrains",
    )

    args = parser.parse_args(sys.argv[1:] if sys.argv[1:] else ["-h"])

    sche = biggusdictus.Scheme()

    for i in args.files:
        add_file(sche, i)

    print(sche.scheme(pedantic=args.pedantic))


if __name__ == "__main__":
    sys.exit(main())
