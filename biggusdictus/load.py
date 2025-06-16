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
    isdict,
    Instance,
    Or,
    Http,
    Https,
    Uri,
    Url,
    Isodate,
    parseuri,
)


class FieldType:
    def __init__(self, typelist):
        self.typelist = typelist

        self.state = {}

    def conv(self, x) -> dict:
        return {}

    def add(self, x):
        state = self.conv(x)
        if self.state == {}:
            self.state = state
        else:
            self.merge(self.state, state)

    def func(self) -> Callable:
        return lambda: 0

    def args(self, pedantic: bool = False) -> list:
        return []

    def merge(self, dest: dict, src: dict):
        pass

    def join(self, src: "FieldType"):
        self.merge(self.state, src.state)


class TypeAny(FieldType):
    def conv(self, x) -> dict:
        return {"type": type(x)}

    def func(self) -> Callable:
        return Instance

    def args(self, pedantic: bool = False) -> list:
        return [self.state["type"]]


class TypeNone(FieldType):
    def conv(self, x) -> dict:
        isNone(x)
        return {}

    def func(self) -> Callable:
        return isNone


class TypeBool(FieldType):
    def conv(self, x) -> dict:
        isbool(x)
        return {}

    def func(self) -> Callable:
        return isbool


class TypeNumber(FieldType):
    def conv(self, x) -> dict:
        state = {"min": x, "max": x, "float": False}

        try:
            isint(x)
        except DictError:
            pass
        else:
            return state

        isfloat(x)
        state["float"] = True

        return state

    def func(self) -> Callable:
        if self.state["float"]:
            return isfloat
        if self.state["min"] >= 0:
            return uint
        return isint

    def args(self, pedantic: bool = False) -> list:
        if pedantic:
            return [self.state["min"], self.state["max"]]
        return []

    def merge(self, dest: dict, src: dict):
        dest["float"] = dest["float"] | src["float"]
        dest["min"] = min(dest["min"], src["min"])
        dest["max"] = max(dest["max"], src["max"])


class TypeUrl(FieldType):
    def conv(self, x) -> dict:
        state = {}

        try:
            scheme = parseuri(x, "")
        except DictError:
            raise DictError()

        state[scheme] = True
        return state

    def merge(self, dest: dict, src: dict):
        dest.update(src)

    def func(self) -> Callable:
        state = self.state
        http = state.get("http", False)
        https = state.get("https", False)

        size = len(state)

        if size == 1:
            if http:
                return Http
            if https:
                return Https
        elif size == 2:
            if http and https:
                return Url
        return Uri


class TypeIsodate(FieldType):
    def conv(self, x) -> dict:
        try:
            Isodate(x)
        except DictError:
            raise DictError()

        return {}

    def func(self) -> Callable:
        return Isodate


def expr_simplified(t) -> list:
    def simpler(arr):
        for i, j in enumerate(arr):
            if len(j) == 1:
                arr[i] = j[0]
        return arr

    size = len(t)
    if size == 0:
        return []

    if size == 1:
        types = simpler([t[0]])
    else:
        types = [Or, *simpler(t)]

    return types


class Types(FieldType):
    def conv(self, x) -> dict:
        types = {}

        for i in reversed(self.typelist):
            t = types.get(i, i(self.typelist))

            try:
                t.add(x)
            except DictError:
                continue

            types[i] = t
            return types

        assert 0

    def types(self, pedantic=False) -> list:
        ret = []
        state = self.state

        for i in state.keys():
            val = state[i]
            ret.append((val.func(), *val.args(pedantic=pedantic)))
        return ret

    def merge(self, dest: dict, src: dict):
        s_dest = set(dest.keys())
        s_src = set(src.keys())

        for i in s_src - s_dest:
            dest[i] = src[i]

        for i in s_src & s_dest:
            dest[i].join(src[i])


class Iterable(FieldType):
    def __init__(self, tfunc, typelist):
        self.tfunc = tfunc
        super().__init__(typelist)

    def conv(self, x) -> dict:
        self.tfunc(x)

        size = len(x)
        types = Types(self.typelist)
        state = {"min": size, "max": size, "types": types}

        for i in x:
            types.add(i)

        return state

    def func(self) -> Callable:
        return self.tfunc

    def args(self, pedantic: bool = False) -> list:
        types = tuple(expr_simplified(self.state["types"].types(pedantic=pedantic)))
        size = len(types)

        if size == 1:
            types = types[0]
        elif size == 0:
            if not pedantic:
                return []
            else:
                types = None

        return [
            types,
            *([self.state["min"], self.state["max"]] if pedantic else []),
        ]

    def merge(self, dest: dict, src: dict):
        dest["min"] = min(dest["min"], src["min"])
        dest["max"] = max(dest["max"], src["max"])

        dest["types"].join(src["types"])


class TypeList(Iterable):
    def __init__(self, typelist):
        super().__init__(islist, typelist)


class TypeTuple(Iterable):
    def __init__(self, typelist):
        super().__init__(istuple, typelist)


class TypeSet(Iterable):
    def __init__(self, typelist):
        super().__init__(isset, typelist)


class TypeFrozenset(Iterable):
    def __init__(self, typelist):
        super().__init__(isfrozenset, typelist)


class Text(FieldType):
    def __init__(self, tfunc, typelist):
        self.tfunc = tfunc
        super().__init__(typelist)

    def conv(self, x) -> dict:
        self.tfunc(x)

        size = len(x)
        return {"min": size, "max": size}

    def func(self) -> Callable:
        return self.tfunc

    def args(self, pedantic: bool = False) -> list:
        if pedantic:
            return [self.state["min"], self.state["max"]]
        return []

    def merge(self, dest: dict, src: dict):
        dest["min"] = min(dest["min"], src["min"])
        dest["max"] = max(dest["max"], src["max"])


class TypeStr(Text):
    def __init__(self, typelist):
        super().__init__(isstr, typelist)


class TypeBytes(Text):
    def __init__(self, typelist):
        super().__init__(isbytes, typelist)


class TypeDict(FieldType):
    def conv(self, x) -> dict:
        Instance(x, dict)
        state = {}

        for i in x.keys():
            val = x[i]
            types = Types(self.typelist)
            types.add(val)

            state[i] = {
                "optional": False,
                "types": types,
            }

        return state

    def func(self) -> Callable:
        return isdict

    def args(self, pedantic: bool = False) -> list:
        ret = []
        state = self.state
        for i in state.keys():
            val = state[i]
            types = expr_simplified(val["types"].types(pedantic=pedantic))

            if len(types) == 1 and isinstance(types[0], tuple | list):
                types = types[0]

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
