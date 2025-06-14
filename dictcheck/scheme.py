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
    conv_none,
    conv_bool,
    conv_number,
    conv_list,
    conv_set,
    conv_frozenset,
    conv_tuple,
    conv_string,
    conv_bytes,
    conv_dict,
)


class Scheme:
    def __init__(self):
        self.scheme = None

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
            conv_none,
            conv_bool,
            conv_number,
            conv_list,
            conv_set,
            conv_frozenset,
            conv_tuple,
            conv_string,
            conv_bytes,
            conv_dict,
        ]

    def check(self, data: dict, *args):
        if len(args) == 0:
            if self.scheme is None:
                raise DictError("scheme wasn't specified")
            dictcheck(data, self.replacements, *self.scheme)
        else:
            dictcheck(data, self.replacements, *args)

    def merge(self, scheme: dict):
        if self.scheme is None:
            self.scheme = scheme
            return

        pass

    def append(self, data: dict):
        self.merge(conv_dict(data, {}, self.types))
