#!/usr/bin/env python
# by Dominik Stanisław Suchora <hexderm@gmail.com>
# License: GNU GPLv3

from typing import Callable

from .funcs import (
    DictError,
    isNone,
    isbool,
    isstr,
    isbytes,
    isint,
    isfloat,
    islist,
    isset,
    istuple,
    isfrozenset,
    dictcheck,
)
from .load import (
    TypeAny,
    TypeNone,
    TypeBool,
    TypeNumber,
    TypeList,
    TypeSet,
    TypeFrozenset,
    TypeTuple,
    TypeDict,
    TypeStr,
    TypeBytes,
    TypeUrl,
    TypeIsodate,
)


def dict_by_item(data, item, default=None):
    for i in data.keys():
        if data[i] == item:
            return i
    return default


class Scheme:
    def __init__(self, pedantic=False):
        self.replacements = {
            None: isNone,
            bool: isbool,
            str: isstr,
            bytes: isbytes,
            int: isint,
            float: isfloat,
            list: islist,
            set: isset,
            frozenset: isfrozenset,
            tuple: istuple,
            dict: dictcheck,
        }

        self.types = [
            TypeAny,
            TypeNone,
            TypeBool,
            TypeNumber,
            TypeList,
            TypeSet,
            TypeFrozenset,
            TypeTuple,
            TypeDict,
            TypeStr,
            TypeBytes,
            TypeUrl,
            TypeIsodate,
        ]

        self.struct = TypeDict(self.types, self.replacements, pedantic=pedantic)

    def check(self, data: dict, *args):
        if len(args) == 0:
            if self.struct.state == {}:
                raise DictError("scheme wasn't specified")
            assert dictcheck == self.struct.func()
            dictcheck(data, self.replacements, *self.struct.args())
        else:
            dictcheck(data, self.replacements, *args)

    def merge(self, scheme: "Scheme"):
        if self.struct.state == {}:
            self.struct = scheme.struct
            return

        self.struct.join(scheme.struct)

    def schemeprint(self, itern: tuple | list) -> str:
        tupl = isinstance(itern, tuple)
        ret = "(" if tupl else "["

        g = 0

        for i in itern:
            if g != 0 or (tupl and g == len(itern) - 1):
                ret += ", "
            g += 1

            if isinstance(i, tuple | list):
                ret += self.schemeprint(i)
            elif i == isNone:
                ret += "None"
            elif isinstance(i, type) or isinstance(i, Callable):
                if (r := dict_by_item(self.replacements, i)) is not None:
                    ret += r.__name__
                else:
                    ret += i.__name__
            else:
                ret += repr(i)

        ret += ")" if tupl else "]"
        return ret

    @property
    def scheme(self) -> str:
        return self.schemeprint(self.struct.args())[1:-1]

    def add(self, data: dict):
        self.struct.add(data)
