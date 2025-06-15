#!/usr/bin/env python
# by Dominik Stanisław Suchora <hexderm@gmail.com>
# License: GNU GPLv3

from datetime import datetime
from typing import Callable
from urllib.parse import urlparse

limits = {
    "i8": (-128, 127),
    "i16": (-32768, 32767),
    "i32": (-2147483648, 2147483647),
    "i64": (-9223372036854775808, 9223372036854775807),
    "u8": 255,
    "u16": 65535,
    "u32": 4294967295,
    "u64": 18446744073709551615,
}


class DictError(Exception):
    pass


class EqError(DictError):
    pass


class IsError(DictError):
    pass


class NotError(DictError):
    pass


class InstanceError(DictError):
    pass


class ConvertError(DictError):
    pass


class RangeError(DictError):
    pass


class LengthError(RangeError):
    pass


def Instance(value, replacements, t):
    if not isinstance(value, t):
        raise InstanceError(value, t)


def isbool(w, replacements):
    Instance(w, replacements, bool)


def Is(w, replacements, *args):
    for i in args:
        if w is not i:
            continue
        return
    raise IsError(w, args)


def Eq(w, replacements, *args):
    for i in args:
        if w != i:
            continue
        return
    raise EqError(w, args)


def isNone(w, replacements):
    Is(w, None)


def inrange(w, x, y):
    if x is not None:
        if w < x:
            raise RangeError(w, x, y)
    if y is not None:
        if w > y:
            raise RangeError(w, x, y)


def isfloat(w, replacements, x=None, y=None):
    Instance(w, replacements, int | float)
    inrange(w, x, y)


def isint(w, replacements, x=None, y=None):
    if isinstance(w, bool):
        raise InstanceError(w, int)
    Instance(w, replacements, int)
    inrange(w, x, y)


def int_lim(w, replacements, x, y, limx=None, limy=None):
    if x is None or (limx is not None and x < limx):
        x = limx
    if y is None or (limy is not None and y > limy):
        y = limy

    isint(
        w,
        replacements,
        x,
        y,
    )


def uint_lim(w, replacements, x, y, limy=None):
    int_lim(w, replacements, x, y, limx=0, limy=limy)


def uint(w, replacements, x=None, y=None):
    uint_lim(w, replacements, x, y)


def isuint_lim(w, replacements, x, y, lim):
    lim = limits[lim]
    int_lim(w, replacements, x, y, limy=lim[0])


def isint_lim(w, replacements, x, y, lim):
    lim = limits[lim]
    int_lim(w, replacements, x, y, limx=lim[0], limy=lim[1])


def i8(w, replacements, x=0, y=None):
    isint_lim(w, replacements, x, y, "i8")


def i16(w, replacements, x=0, y=None):
    isint_lim(w, replacements, x, y, "i16")


def i32(w, replacements, x=0, y=None):
    isint_lim(w, replacements, x, y, "i32")


def i64(w, replacements, x=0, y=None):
    isint_lim(w, replacements, x, y, "i64")


def u8(w, replacements, x=0, y=None):
    isuint_lim(w, replacements, x, y, "u8")


def u16(w, replacements, x=0, y=None):
    isuint_lim(w, replacements, x, y, "u16")


def u32(w, replacements, x=0, y=None):
    isuint_lim(w, replacements, x, y, "u32")


def u64(w, replacements, x=0, y=None):
    isuint_lim(w, replacements, x, y, "u64")


def length(w, replacements, x, y):
    try:
        uint(len(w), replacements, x, y)
    except RangeError as e:
        raise LengthError(*e.args)


def isstr(w, replacements, x=0, y=None):
    Instance(w, replacements, str)
    length(w, replacements, x, y)


def isbytes(w, replacements, x=0, y=None):
    Instance(w, replacements, bytes)
    length(w, replacements, x, y)


def Isodate(w, replacements):
    Instance(w, replacements, str | bytes)
    try:
        datetime.fromisoformat(w)
    except Exception:
        raise ConvertError(w, "an iso date format")


def parseuri(w, replacements, msg, schemes=[]):
    Instance(w, replacements, str | bytes)

    try:
        p = urlparse(w)
    except ValueError:
        raise ConvertError(w, msg)

    if not p.scheme or not p.netloc:
        raise ConvertError(w, msg)

    scheme = p.scheme.lower()
    if len(schemes) == 0:
        return scheme

    if scheme not in schemes:
        raise ConvertError(w, msg)

    return scheme


def Uri(w, replacements):
    parseuri(w, replacements, "an uri")


def Url(w, replacements):
    parseuri(w, replacements, "an url", schemes=["https", "http"])


def Http(w, replacements):
    parseuri(w, replacements, "an http url", schemes=["http"])


def Https(w, replacements):
    parseuri(w, replacements, "an https url", schemes=["https"])


def Hash(w, replacements, x=1, y=None):
    Instance(w, replacements, bytes | str)
    length(w, replacements, x, y)

    for i in w:
        i = i.lower()
        if not (i.isdigit() or (i >= "a" and i <= "f")):
            raise ConvertError(w, "a hexadecimal string")


def Md5(w, replacements):
    Hash(w, replacements, x=32, y=32)


def Sha1(w, replacements):
    Hash(w, replacements, x=40, y=40)


def Sha256(w, replacements):
    Hash(w, replacements, x=64, y=64)


def Sha512(w, replacements):
    Hash(w, replacements, x=128, y=128)


def isiterable(t, w, replacements, checker=None, x=0, y=None):
    Instance(w, replacements, t)
    length(w, replacements, x, y)

    if checker is not None:
        for i in w:
            checker(i, replacements)


def islist(w, replacements, checker=None, x=0, y=None):
    isiterable(list, w, replacements, checker, x, y)


def istuple(w, replacements, checker=None, x=0, y=None):
    isiterable(tuple, w, replacements, checker, x, y)


def isset(w, replacements, checker=None, x=0, y=None):
    isiterable(set, w, replacements, checker, x, y)


def isfrozenset(w, replacements, checker=None, x=0, y=None):
    isiterable(frozenset, w, replacements, checker, x, y)


def match_expr(value, replacements, expr: Callable | type):
    def match(func, args):
        if (r := replacements.get(func)) is not None:
            r(value, replacements, *args)
        elif isinstance(func, type):
            Instance(value, replacements, func)
        elif not isinstance(func, Callable):
            Instance(func, replacements, type)
        else:
            func(value, replacements, *args)

    if not isinstance(expr, tuple | list):
        match(expr, [])
        return

    if len(expr) == 0:
        return

    func = expr[0]
    args = expr[1:]

    if isinstance(func, tuple | list):
        pfunc = func

        def ret(x):
            match_expr(x, replacements, pfunc)

        ret(value)
    else:
        match(func, args)


def Not(w, replacements, *args):
    for i in args:
        try:
            match_expr(w, replacements, i)
        except DictError:
            pass
        else:
            raise NotError(w, args)


def Or(w, replacements, *args):
    last = None
    for i in args:
        try:
            match_expr(w, replacements, i)
        except DictError as e:
            last = e
        else:
            return

    if last is not None:
        raise last


def And(w, replacements, *args):
    for i in args:
        match_expr(w, replacements, i)


def pretty_exception(name, e):
    name = str(name)

    t = type(e)
    if t == DictError:
        return DictError("." + name + e.args[0])

    msg = "." + name + ": "
    args = e.args

    if t == EqError:
        msg += repr(args[0]) + " is not equal to any of " + repr(args[1])
    elif t == IsError:
        msg += repr(args[0]) + " is not in " + repr(args[1])
    elif t == NotError:
        msg += repr(args[0]) + " matched " + repr(args[1])
    elif t == InstanceError:
        msg += repr(args[0]) + " is not an instance of " + repr(args[1])
    elif t == RangeError:
        msg += (
            repr(args[0])
            + " is not in range of "
            + ("-" if args[1] is None else str(args[1]))
            + " to "
            + ("-" if args[2] is None else str(args[2]))
        )
    elif t == LengthError:
        msg += (
            repr(args[0])
            + " length is not in range of "
            + ("-" if args[1] is None else str(args[1]))
            + " to "
            + ("-" if args[2] is None else str(args[2]))
        )
    elif t == ConvertError:
        msg += repr(args[0]) + " isn't " + str(args[1])
    else:
        assert 0

    return DictError(msg)


def dictcheck(d, replacements, *check):
    Instance(d, replacements, dict)

    strict = True
    if len(check) != 0 and isinstance(check[0], bool):
        strict = check[0]
        check = check[1:]

    keys = {i: 0 for i in d.keys()}

    for j in check:
        name = j[0]
        optional = False
        if name is None:
            optional = True
            name = j[1]
            expr = j[2:]
        else:
            expr = j[1:]

        try:
            value = d[name]
        except KeyError as e:
            if optional:
                continue
            raise e

        keys[name] = 1

        try:
            match_expr(value, replacements, expr)
        except DictError as e:
            raise pretty_exception(name, e)

    if strict:
        unused = []
        for i in keys:
            if keys[i] == 0:
                unused.append(i)
        if len(unused) > 0:
            raise DictError("Some of fields weren't matched " + repr(unused))
