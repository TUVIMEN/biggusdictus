#!/usr/bin/env python

from dictcheck import *


def expect(func, exceptions, args=None):
    o = None
    try:
        func()
    except exceptions as e:
        o = e
        if args is None:
            raise 0
        assert o.args == args
    else:
        assert 0


sche = Scheme()


def dictcheck(*args):
    sche.check(*args)


def dictexpect(msg, *args):
    expect(lambda: dictcheck(*args), DictError, (msg,))


t1 = {"a": 12, "b": "na", "c": "", "h": True}
t2 = {
    "c": t1,
    "a": False,
    "date": "2025-02-22T00:00:00+0000",
    "url1": "http://wikipedia.org/list",
    "url2": "https://gitlab.com/TUVIMEN/reliq",
    "url3": "ftp://ftp.gnu.org/",
    "hash": "d41d8cd98f00b204e9800998ecf8427e",
}

dictcheck(t1, ("a", int, 3, 20), ("b", str), ("c", str), ("h",))

dictexpect(
    "Some of fields weren't matched ['c', 'h']",
    t1,
    ("a", int),
    ("b", str),
)

dictexpect(".c: 0 length is not in range of 1 to -", t1, False, ("c", str, 1))

dictexpect(
    ".c.c: '' is not an instance of <class 'list'>",
    t2,
    False,
    (
        "c",
        (
            dict,
            ("b", str),
            ("c", list),
        ),
    ),
)

dictcheck(t1, False, ("b", Eq, "na"), ("h", Is, True), ("h", Not, (Is, False)))

dictexpect(
    ".a: False is not an instance of <class 'int'>",
    t2,
    False,
    ("a", int),
)

dictcheck(
    t2,
    False,
    ("date", Isodate),
)

dictexpect(
    ".date: '2025-02-22T00:00:00+0000' isn't an url",
    t2,
    False,
    ("date", Url),
)

dictexpect(
    ".url1: 'http://wikipedia.org/list' isn't an https url",
    t2,
    False,
    ("url1", And, Url, Http, Https),
)

dictexpect(
    ".url2: 'https://gitlab.com/TUVIMEN/reliq' isn't an http url",
    t2,
    False,
    ("url2", And, Url, Https, Http),
)

dictexpect(
    ".url3: 'ftp://ftp.gnu.org/' isn't an url",
    t2,
    False,
    ("url3", And, Uri, Url),
)

dictexpect(
    ".date: '2025-02-22T00:00:00+0000' is not an instance of <class 'bool'>",
    t2,
    False,
    ("a", Or, str, Isodate, Uri, bool),
    ("date", Or, float, int, bool),
)

dictexpect(
    ".hash: 32 length is not in range of 40 to 40",
    t2,
    False,
    ("hash", Hash),
    ("hash", Md5),
    ("hash", Sha1),
)

dictexpect(
    ".date: '2025-02-22T00:00:00+0000' isn't a hexadecimal string",
    t2,
    False,
    ("date", Hash),
)

dictexpect(
    ".a: False is not an instance of <class 'str'>",
    t2,
    False,
    (None, "b", str),
    (None, "a", bool),
    (None, "a", str),
)

dictexpect(
    ".a: 0 is not an instance of <class 'type'>",
    t2,
    False,
    ("a", bool),
    ("a", 0),
)


class Nonstandardtype:
    pass


dictexpect(
    ".a: False is not an instance of <class '__main__.Nonstandardtype'>",
    t2,
    False,
    ("a", bool),
    ("a", Nonstandardtype),
)

t3 = {"d": Nonstandardtype()}

dictcheck(
    t3,
    False,
    ("d", Nonstandardtype),
)
