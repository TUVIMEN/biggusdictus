#!/usr/bin/env python
# by Dominik Stanisław Suchora <hexderm@gmail.com>
# License: GNU GPLv3

from .funcs import (
    isbool,
    isNone,
    isfloat,
    isint,
    isstr,
    isbytes,
    islist,
    istuple,
    isset,
    isfrozenset,
    isdict,
    uint,
    i8,
    i16,
    i32,
    i64,
    u8,
    u16,
    u32,
    u64,
    Instance,
    Isodate,
    Url,
    Uri,
    Http,
    Https,
    Hash,
    Md5,
    Sha1,
    Sha256,
    Sha512,
    Or,
    And,
    Is,
    Eq,
    Not,
    DictError,
)

from .load import FieldType

from .scheme import Scheme


def main():
    import sys, json, argparse

    def add_file(sche, path):
        with open(path, "rb") as f:
            sche.add(json.load(f))

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

    sche = Scheme()

    for i in args.files:
        add_file(sche, i)

    print(sche.scheme(pedantic=args.pedantic))
