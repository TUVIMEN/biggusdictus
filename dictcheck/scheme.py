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
    Type,
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
            Type,
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
        ]

        self.t = TypeDict(self.types, self.replacements)

    def check(self, data: dict, *args):
        if len(args) == 0:
            if self.scheme is None:
                raise DictError("scheme wasn't specified")
            dictcheck(data, self.replacements, *self.scheme)
        else:
            dictcheck(data, self.replacements, *args)

    def merge(self, scheme: dict):
        # if self.scheme is None:
        # self.scheme = scheme
        # return

        pass

    @property
    def scheme(self):
        pass

    def add(self, data: dict):
        self.t.add(data)
