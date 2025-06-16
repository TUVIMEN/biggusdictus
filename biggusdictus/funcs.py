#!/usr/bin/env python
# by Dominik Stanisław Suchora <hexderm@gmail.com>
# License: GNU GPLv3

from datetime import datetime
from typing import Callable
from urllib.parse import urlparse
import inspect

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

replacements = {}


class DictError(Exception):
    pass


class FieldError(DictError):
    pass


class OrError(DictError):
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


def Instance(value, t):
    if not isinstance(value, t):
        raise InstanceError(value, t)


def isbool(w):
    Instance(w, bool)


def checkstop(stop):
    if stop is not ...:
        raise TypeError("Too many arguments to matching function")


def Is(w, *args):
    for i in args:
        if w is not i:
            continue
        return
    raise IsError(w, args)


def Eq(w, *args):
    for i in args:
        if w != i:
            continue
        return
    raise EqError(w, args)


def isNone(w):
    Is(w, None)


def inrange(w, x, y):
    if x is not None:
        if w < x:
            raise RangeError(w, x, y)
    if y is not None:
        if w > y:
            raise RangeError(w, x, y)


def isfloat(w, x=None, y=None):
    Instance(w, int | float)
    inrange(w, x, y)


def isint(w, x=None, y=None):
    if isinstance(w, bool):
        raise InstanceError(w, int)
    Instance(w, int)
    inrange(w, x, y)


def int_lim(w, x, y, limx=None, limy=None):
    if x is None or (limx is not None and x < limx):
        x = limx
    if y is None or (limy is not None and y > limy):
        y = limy

    isint(
        w,
        x,
        y,
    )


def uint_lim(w, x, y, limy=None):
    int_lim(w, x, y, limx=0, limy=limy)


def uint(w, x=None, y=None):
    uint_lim(w, x, y)


def isuint_lim(w, x, y, lim):
    lim = limits[lim]
    int_lim(w, x, y, limy=lim[0])


def isint_lim(w, x, y, lim):
    lim = limits[lim]
    int_lim(w, x, y, limx=lim[0], limy=lim[1])


def i8(w, x=0, y=None):
    isint_lim(w, x, y, "i8")


def i16(w, x=0, y=None):
    isint_lim(w, x, y, "i16")


def i32(w, x=0, y=None):
    isint_lim(w, x, y, "i32")


def i64(w, x=0, y=None):
    isint_lim(w, x, y, "i64")


def u8(w, x=0, y=None):
    isuint_lim(w, x, y, "u8")


def u16(w, x=0, y=None):
    isuint_lim(w, x, y, "u16")


def u32(w, x=0, y=None):
    isuint_lim(w, x, y, "u32")


def u64(w, x=0, y=None):
    isuint_lim(w, x, y, "u64")


def length(w, x, y):
    try:
        uint(len(w), x, y)
    except RangeError as e:
        raise LengthError(*e.args) from None


def isstr(w, x=0, y=None):
    Instance(w, str)
    length(w, x, y)


def isbytes(w, x=0, y=None):
    Instance(w, bytes)
    length(w, x, y)


def Isodate(w):
    Instance(w, str | bytes)
    try:
        datetime.fromisoformat(w)
    except Exception:
        raise ConvertError(w, "an iso date format") from None


def parseuri(w, msg, schemes=[]):
    Instance(w, str | bytes)

    try:
        p = urlparse(w)
    except ValueError:
        raise ConvertError(w, msg) from None

    if not p.scheme or not p.netloc:
        raise ConvertError(w, msg)

    scheme = p.scheme.lower()
    if len(schemes) == 0:
        return scheme

    if scheme not in schemes:
        raise ConvertError(w, msg)

    return scheme


def Uri(w):
    parseuri(w, "an uri")


def Url(w):
    parseuri(w, "an url", schemes=["https", "http"])


def Http(w):
    parseuri(w, "an http url", schemes=["http"])


def Https(w):
    parseuri(w, "an https url", schemes=["https"])


def Hash(w, x=1, y=None):
    Instance(w, bytes | str)
    length(w, x, y)

    for i in w:
        i = i.lower()
        if not (i.isdigit() or (i >= "a" and i <= "f")):
            raise ConvertError(w, "a hexadecimal string")


def Md5(w):
    Hash(w, x=32, y=32)


def Sha1(w):
    Hash(w, x=40, y=40)


def Sha256(w):
    Hash(w, x=64, y=64)


def Sha512(w):
    Hash(w, x=128, y=128)


def isiterable(t, w, checker=-1, x=0, y=None, __stop=..., __replacements=replacements):
    checkstop(__stop)
    Instance(w, t)
    length(w, x, y)

    if checker != -1:
        for i in w:
            match_expr(i, __replacements, checker)


def islist(w, checker=-1, x=0, y=None, __stop=..., __replacements=replacements):
    isiterable(list, w, checker, x, y, __stop=__stop, __replacements=__replacements)


def istuple(w, checker=-1, x=0, y=None, __stop=..., __replacements=replacements):
    isiterable(tuple, w, checker, x, y, __stop=__stop, __replacements=__replacements)


def isset(w, checker=-1, x=0, y=None, __stop=..., __replacements=replacements):
    isiterable(set, w, checker, x, y, __stop=__stop, __replacements=__replacements)


def isfrozenset(w, checker=-1, x=0, y=None, __stop=..., __replacements=replacements):
    isiterable(
        frozenset, w, checker, x, y, __stop=__stop, __replacements=__replacements
    )


def match_expr(value, replacements, expr: Callable | type):
    def match(func, args):
        def run(f):
            a = inspect.getfullargspec(f).args
            if "__replacements" in a and "__stop" in a:
                f(value, *args, __replacements=replacements)
            else:
                f(value, *args)

        if (r := replacements.get(func)) is not None:
            run(r)
        elif isinstance(func, type):
            Instance(value, func)
        elif not isinstance(func, Callable):
            Instance(func, type)
        else:
            run(func)

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


def Not(w, *args, __stop=..., __replacements=replacements):
    checkstop(__stop)
    try:
        match_expr(w, __replacements, args)
    except DictError:
        pass
    else:
        raise NotError(w, args)


def Or(w, *args, __stop=..., __replacements=replacements):
    checkstop(__stop)
    for i in args:
        try:
            match_expr(w, replacements, i)
        except DictError:
            pass
        else:
            return

    raise OrError(w, args)


def And(w, *args, __stop=..., __replacements=replacements):
    checkstop(__stop)
    for i in args:
        match_expr(w, replacements, i)


def pretty_exception(name, e):
    name = str(name)

    t = type(e)
    if t == DictError:
        return DictError(
            "." + name + ("" if e.args[0][:1] == "." else ": ") + e.args[0]
        )

    msg = "." + name + ": "
    args = e.args

    if t == EqError:
        msg += repr(args[0]) + " is not equal to any of " + repr(args[1])
    elif t == IsError:
        msg += repr(args[0]) + " is not in " + repr(args[1])
    elif t == OrError:
        msg += repr(args[0]) + " did not match to any of " + repr(args[1])
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
            "length of "
            + repr(args[0])
            + " is not in range of "
            + ("-" if args[1] is None else str(args[1]))
            + " to "
            + ("-" if args[2] is None else str(args[2]))
        )
    elif t == ConvertError:
        msg += repr(args[0]) + " isn't " + str(args[1])
    else:
        assert 0

    return DictError(msg)


def isdict(d, *check, __stop=..., __replacements=replacements):
    checkstop(__stop)
    Instance(d, dict)

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
        except KeyError:
            if optional:
                continue
            raise DictError("." + name + ": field was not found") from None

        keys[name] = 1

        try:
            match_expr(value, __replacements, expr)
        except DictError as e:
            raise pretty_exception(name, e) from None

    if strict:
        unused = []
        for i in keys:
            if keys[i] == 0:
                unused.append(i)
        if len(unused) > 0:
            raise DictError("Some of fields weren't matched " + repr(unused))


replacements.update(
    {
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
)
