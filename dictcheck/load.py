#!/usr/bin/env python
# by Dominik Stanisław Suchora <hexderm@gmail.com>
# License: GNU GPLv3

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
)


def conv_none(x, state: dict, typelist: list[dict]) -> Tuple[Callable, list]:
    isNone(x)
    return isNone, []


def conv_bool(x, state: dict, typelist: list[dict]) -> Tuple[Callable, list]:
    isbool(x)
    return isbool, []


def update_range(x: int | float, state: dict):
    if state["min"] is None:
        state["min"] = x
    else:
        state["min"] = min(state["min"], x)

    if state["max"] is None:
        state["max"] = x
    else:
        state["max"] = max(state["max"], x)


def args_range(state: dict, unsigned: bool = False) -> Tuple[int | float]:
    s_max = state["max"]
    if unsigned:
        if s_max is None:
            return tuple()
        return (s_max,)

    s_min = state["min"]
    if state["max"] is None:
        if state["min"] is None:
            return tuple()
        return (s_min,)

    return s_min, s_max


def conv_number(x, state: dict, typelist: list[dict]) -> Tuple[Callable, list]:
    if state == {}:
        state.update({"min": None, "max": None, "float": False})

    if not state["float"]:
        try:
            isint(x)
        except DictError:
            pass
        else:
            update_range(x, state)
            if state["min"] is not None and state["min"] >= 0:
                return uint, list(*args_range(state, True))
            return isint, list(*args_range(state))

    isfloat(x)
    state["float"] = True

    update_range(x, state)
    return isfloat, list(*args_range(state))


class SchemeType:
    def __init__(self, types):
        self.types = types


def conv_type(x, types: dict, typelist: list[dict]):
    for i in typelist:
        state = types.get(i, {})
        try:
            func, args = i(x, state, typelist)
        except DictError:
            continue

        types[i] = {"func": func, "args": args, "state": state}
        return

    types[type(x)] = {"func": Instance, "args": [type(x)], "state": {}}


def conv_iterable(tfunc, x, state: dict, typelist: list[dict]) -> Tuple[Callable, list]:
    if state == {}:
        state.update({"min": None, "max": None, "types": {}})

    tfunc(x)

    size = len(x)
    update_range(size, state)

    for i in x:
        conv_type(i, state["types"], typelist)

    return tfunc, list(SchemeType(state["types"]), *args_range(state))


def conv_list(x, state: dict, typelist: list[dict]) -> Tuple[Callable, list]:
    return conv_iterable(islist, x, state, typelist)


def conv_tuple(x, state: dict, typelist: list[dict]) -> Tuple[Callable, list]:
    return conv_iterable(istuple, x, state, typelist)


def conv_set(x, state: dict, typelist: list[dict]) -> Tuple[Callable, list]:
    return conv_iterable(isset, x, state, typelist)


def conv_frozenset(x, state: dict, typelist: list[dict]) -> Tuple[Callable, list]:
    return conv_iterable(isfrozenset, x, state, typelist)


def conv_text(tfunc, x, state: dict, typelist: list[dict]) -> Tuple[Callable, list]:
    if state == {}:
        state.update({"min": None, "max": None})

    tfunc(x)

    size = len(x)
    update_range(size, state)

    return tfunc, list(*args_range(state))


def conv_string(x, state: dict, typelist: list[dict]) -> Tuple[Callable, list]:
    return conv_text(isstr, x, state, typelist)


def conv_bytes(x, state: dict, typelist: list[dict]) -> Tuple[Callable, list]:
    return conv_text(isbytes, x, state, typelist)


def conv_dict_args(state: dict) -> list:
    ret = []
    for i in state.keys():
        val = state[i]
        types = SchemeType(val["types"])

        if val["optional"]:
            ret.append((None, i, types))
        else:
            ret.append((i, types))

    return ret


def conv_dict(x, state: dict, typelist: list[dict]) -> Tuple[Callable, list]:
    Instance(x, dict)

    x_keys = set(x.keys())
    state_keys = set(state.keys())

    for i in state_keys - x_keys:
        state[i]["optional"] = True

    for i in x_keys:
        x_value = x[i]
        state_value = state.get(i, {"optional": False, "types": {}})

        conv_type(x_value, state_value["types"], typelist)
        state[i] = state_value

    return dictcheck, conv_dict_args(state)
