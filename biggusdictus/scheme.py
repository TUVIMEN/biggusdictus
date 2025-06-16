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
    isdict,
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
    def __init__(self):
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
            dict: isdict,
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

        self.struct = TypeDict(self.types, self.replacements)

    def check(self, data: dict, *args, pedantic: bool = False):
        if len(args) == 0:
            if self.struct.state == {}:
                raise DictError("scheme wasn't specified")
            assert isdict == self.struct.func()
            isdict(data, self.replacements, *self.struct.args(pedantic=pedantic))
        else:
            isdict(data, self.replacements, *args)

    def merge(self, scheme: "Scheme"):
        if self.struct.state == {}:
            self.struct = scheme.struct
            return

        self.struct.join(scheme.struct)

    def _schemeprint(self, itern: tuple | list) -> str:
        tupl = isinstance(itern, tuple)
        ret = "(" if tupl else "["

        g = 0

        for i in itern:
            if g != 0 or (tupl and g == len(itern) - 1):
                ret += ", "
            g += 1

            if isinstance(i, tuple | list):
                ret += self._schemeprint(i)
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

    def scheme(self, pedantic: bool = False) -> str:
        return self._schemeprint(self.struct.args(pedantic=pedantic))[1:-1]

    def add(self, data: dict):
        self.struct.add(data)
