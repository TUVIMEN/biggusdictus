#!/usr/bin/env python
# by Dominik Stanisław Suchora <hexderm@gmail.com>
# License: GNU GPLv3

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

        self.struct = TypeDict(self.types, self.replacements)

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

    @property
    def scheme(self):
        pass

    def add(self, data: dict):
        self.struct.add(data)
