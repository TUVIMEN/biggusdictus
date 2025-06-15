#!/usr/bin/env python
# by Dominik Stanisław Suchora <hexderm@gmail.com>
# License: GNU GPLv3

import itertools
from typing import Callable, Tuple

from .funcs import (
    DictError,
    isNone,
    isbool,
    isstr,
    uint,
    isbytes,
    isint,
    isfloat,
    islist,
    isset,
    istuple,
    isfrozenset,
    dictcheck,
    Instance,
    Or,
)


class Type:
    def __init__(self, typelist, replacements):
        self.typelist = typelist
        self.replacements = replacements

        self.state = {}

    def conv(self, x) -> dict:
        return {"type": type(x)}

    def add(self, x):
        state = self.conv(x)
        if self.state == {}:
            self.state = state
        else:
            self.merge(self.state, state)

    def func(self):
        return Instance

    def args(self) -> list:
        return [self.state["type"]]

    def merge(self, dest: dict, src: dict):
        pass

    def join(self, src: "Type"):
        self.merge(self.state, src.state)


class TypeNone(Type):
    def conv(self, x) -> dict:
        isNone(x, self.replacements)
        return {}


class TypeBool(Type):
    def conv(self, x) -> dict:
        isbool(x, self.replacements)
        return {}


class TypeNumber(Type):
    def conv(self, x) -> dict:
        state = {"min": x, "max": x, "float": False}

        try:
            isint(x, self.replacements)
        except DictError:
            pass
        else:
            return state

        isfloat(x, self.replacements)
        state["float"] = True

        return state

    def func(self) -> Callable:
        if self.state["float"]:
            return isfloat
        if self.state["min"] >= 0:
            return uint
        return isint

    def args(self) -> list:
        return [self.state["min"], self.state["max"]]

    def merge(self, dest: dict, src: dict):
        dest["float"] = dest["float"] | src["float"]
        dest["min"] = min(dest["min"], src["min"])
        dest["max"] = max(dest["max"], src["max"])


class Types(Type):
    def conv(self, x) -> dict:
        types = {}

        for i in reversed(self.typelist):
            t = types.get(i, i(self.typelist, self.replacements))

            try:
                t.add(x)
            except DictError:
                continue

            types[i] = t
            return types

        assert 0

    def types(self) -> list:
        ret = []
        state = self.state

        for i in state.keys():
            val = state[i]
            ret.append((val.func(), *val.args()))
        return ret

    def merge(self, dest: dict, src: dict):
        s_dest = set(dest.keys())
        s_src = set(src.keys())

        for i in s_src - s_dest:
            dest[i] = src[i]

        for i in s_src & s_dest:
            dest[i].join(src[i])


class Iterable(Type):
    def __init__(self, tfunc, typelist, replacements):
        self.tfunc = tfunc
        super().__init__(typelist, replacements)

    def conv(self, x) -> dict:
        self.tfunc(x, self.replacements)

        size = len(x)
        types = Types(self.typelist, self.replacements)
        state = {"min": size, "max": size, "types": types}

        for i in x:
            types.add(i)

        return state

    def func(self):
        return self.tfunc

    def args(self):
        t = self.state["types"].types()
        if len(t) == 1:
            types = t[0]
        else:
            types = (Or, *t)

        return [types, self.state["min"], self.state["max"]]

    def merge(self, dest: dict, src: dict):
        dest["min"] = min(dest["min"], src["min"])
        dest["max"] = max(dest["max"], src["max"])

        dest["types"].join(src["types"])


class TypeList(Iterable):
    def __init__(self, typelist, replacements):
        super().__init__(islist, typelist, replacements)


class TypeTuple(Iterable):
    def __init__(self, typelist, replacements):
        super().__init__(istuple, typelist, replacements)


class TypeSet(Iterable):
    def __init__(self, typelist, replacements):
        super().__init__(isset, typelist, replacements)


class TypeFrozenset(Iterable):
    def __init__(self, typelist, replacements):
        super().__init__(isfrozenset, typelist, replacements)


class Text(Type):
    def __init__(self, tfunc, typelist, replacements):
        self.tfunc = tfunc
        super().__init__(typelist, replacements)

    def conv(self, x) -> dict:
        self.tfunc(x, self.replacements)

        size = len(x)
        return {"min": size, "max": size}

    def func(self):
        return self.tfunc

    def args(self):
        return [self.state["min"], self.state["max"]]

    def merge(self, dest: dict, src: dict):
        dest["min"] = min(dest["min"], src["min"])
        dest["max"] = max(dest["max"], src["max"])


class TypeStr(Text):
    def __init__(self, typelist, replacements):
        super().__init__(isstr, typelist, replacements)


class TypeBytes(Text):
    def __init__(self, typelist, replacements):
        super().__init__(isbytes, typelist, replacements)


class TypeDict(Type):
    def conv(self, x) -> dict:
        Instance(x, self.replacements, dict)
        state = {}

        for i in x.keys():
            val = x[i]
            types = Types(self.typelist, self.replacements)
            types.add(val)

            state[i] = {
                "optional": False,
                "types": types,
            }

        return state

    def func(self):
        return dictcheck

    def args(self):
        ret = []
        state = self.state
        for i in state.keys():
            val = state[i]
            t = val["types"].types()
            if len(t) == 1:
                types = t[0]
            else:
                types = (Or, *t)

            if val["optional"]:
                ret.append((None, i, *types))
            else:
                ret.append((i, *types))

        return ret

    def merge(self, dest: dict, src: dict):
        dest_keys = set(dest.keys())
        src_keys = set(src.keys())

        for i in dest_keys - src_keys:
            dest[i]["optional"] = True

        for i in src_keys - dest_keys:
            dest[i] = src[i]
            dest[i]["optional"] = True

        for i in dest_keys & src_keys:
            dest[i]["types"].join(src[i]["types"])
