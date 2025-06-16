#!/usr/bin/env python

from typing import Callable

from biggusdictus import *


def expect(func, exceptions):
    o = None
    try:
        func()
    except exceptions as e:
        o = e
        return o.args
    else:
        assert 0


sche = Scheme()


def dictcheck(*args, pedantic=False):
    sche.dict(*args, pedantic=pedantic)


def dictexpect(msg, *args, pedantic=False):
    args = expect(lambda: dictcheck(*args, pedantic=pedantic), DictError)
    if isinstance(msg, Callable):
        assert msg(args[0])
    else:
        assert msg == args[0]


class Nonstandardtype:
    pass


def loadexpect(data: list, check=None, msg=None, pedantic=False, repre=None):
    sche = Scheme()

    for i in data:
        sche.add(i)

    if repre is not None:
        assert sche.scheme(pedantic=pedantic) == repre

    if check is None:
        return

    if msg is None:
        sche.dict(check, pedantic=pedantic)
    else:
        args = expect(lambda: sche.dict(check, pedantic=pedantic), DictError)
        if isinstance(msg, Callable):
            assert msg(args[0])
        else:
            assert msg == args[0]


def matching_test_1():
    t = {"a": 12, "b": "na", "c": "", "h": True}

    dictcheck(t, ("a", int, 3, 20), ("b", str), ("c", str), ("h",))

    dictexpect(
        "Some of fields weren't matched ['c', 'h']",
        t,
        ("a", int),
        ("b", str),
    )

    dictexpect(".c: length of 0 is not in range of 1 to -", t, False, ("c", str, 1))

    dictcheck(
        t,
        False,
        ("b", Eq, "na"),
        ("h", Is, True),
        ("h", Not, (Is, False)),
        ("h", Not, Is, False),
    )


def matching_test_2():
    t = {
        "c": {"a": 12, "b": "na", "c": "", "h": True},
        "a": False,
        "date": "2025-02-22T00:00:00+0000",
        "url1": "http://wikipedia.org/list",
        "url2": "https://gitlab.com/TUVIMEN/reliq",
        "url3": "ftp://ftp.gnu.org/",
        "hash": "d41d8cd98f00b204e9800998ecf8427e",
    }

    dictexpect(
        ".c.c: '' is not an instance of <class 'list'>",
        t,
        False,
        (
            "c",
            dict,
            ("b", str),
            ("c", list),
        ),
        (
            "c",
            (
                dict,
                ("b", str),
                ("c", list),
            ),
        ),
    )

    dictexpect(
        ".a: False is not an instance of <class 'int'>",
        t,
        False,
        ("a", int),
    )

    dictcheck(
        t,
        False,
        ("date", Isodate),
    )

    dictexpect(
        ".date: '2025-02-22T00:00:00+0000' isn't an url",
        t,
        False,
        ("date", Url),
    )

    dictexpect(
        ".url1: 'http://wikipedia.org/list' isn't an https url",
        t,
        False,
        ("url1", And, Url, Http, Https),
    )

    dictexpect(
        ".url2: 'https://gitlab.com/TUVIMEN/reliq' isn't an http url",
        t,
        False,
        ("url2", And, Url, Https, Http),
    )

    dictexpect(
        ".url3: 'ftp://ftp.gnu.org/' isn't an url",
        t,
        False,
        ("url3", And, Uri, Url),
    )

    dictexpect(
        ".date: '2025-02-22T00:00:00+0000' did not match to any of (<class 'float'>, <class 'int'>, <class 'bool'>)",
        t,
        False,
        ("a", Or, str, Isodate, Uri, bool),
        ("date", Or, float, int, bool),
    )

    dictexpect(
        ".hash: length of 32 is not in range of 40 to 40",
        t,
        False,
        ("hash", Hash),
        ("hash", Md5),
        ("hash", Sha1),
    )

    dictexpect(
        ".date: '2025-02-22T00:00:00+0000' isn't a hexadecimal string",
        t,
        False,
        ("date", Hash),
    )

    dictexpect(
        ".a: False is not an instance of <class 'str'>",
        t,
        False,
        (None, "b", str),
        (None, "a", bool),
        (None, "a", str),
    )

    dictexpect(
        ".a: 0 is not an instance of <class 'type'>",
        t,
        False,
        ("a", bool),
        ("a", 0),
    )

    dictexpect(
        ".a: False is not an instance of <class '__main__.Nonstandardtype'>",
        t,
        False,
        ("a", bool),
        ("a", Nonstandardtype),
    )


def matching_test_3():
    t = {"d": Nonstandardtype(), "r": [1, 5, 6, 2]}

    dictcheck(
        t, False, ("d", Nonstandardtype), ("r", list, (int, 1, 50)), ("r", list, int)
    )

    dictexpect(
        ".r: length of 4 is not in range of 6 to 99",
        t,
        False,
        ("r", list, int, 2),
        ("r", list, int, 6, 99),
    )

    dictexpect(
        ".r: length of 4 is not in range of 0 to 3",
        t,
        False,
        ("r", list, (int, 1), 2),
        ("r", list, (int, 1), -2, 3),
    )


def matching_test_4():
    sche.list(["s", "c", 12], (Or, str, int), 2)
    sche.set({"s", "c", 12}, (Or, str, int), 2)
    sche.frozenset(frozenset(["s", "c", 12]), (Or, str, int), 2)
    sche.tuple(("s", "c", 12), (Or, str, int), 2)


def matching_tests():
    matching_test_1()
    matching_test_2()
    matching_test_3()
    matching_test_4()


def loading_test_1():
    t = [
        {
            "name": "t3",
            "number": 421,
            "info": {
                "id": 12,
                "date": "2025-02-22T00:00:00+0000",
                "link": "https://something.xyz/user",
            },
        },
        {
            "name": "t2",
            "number": None,
            "info": {
                "id": 12.12,
                "date": "2024-01-02",
                "link": "ftp://something.xyz/home/x",
            },
        },
    ]

    loadexpect(
        t,
        repre="('name', str), ('number', Or, uint, None), ('info', dict, ('id', float), ('date', Isodate), ('link', Uri))",
    )
    loadexpect(
        [t[0]],
        repre="('name', str), ('number', uint), ('info', dict, ('id', uint), ('date', Isodate), ('link', Https))",
    )
    loadexpect(
        [t[1]],
        repre="('name', str), ('number', None), ('info', dict, ('id', float), ('date', Isodate), ('link', Uri))",
    )

    loadexpect(t, check={"name": "na"}, msg=".number: field was not found")
    loadexpect(
        t,
        check={"name": "na", "number": -2},
        msg=lambda x: str.startswith(x, ".number: -2 did not match to any of ("),
    )

    loadexpect(
        t,
        check={"name": "na", "number": 14, "info": 0},
        msg=".info: 0 is not an instance of <class 'dict'>",
    )

    loadexpect(
        t,
        check={"name": "na", "number": 14, "info": {}},
        msg=".info.id: field was not found",
    )

    loadexpect(
        t,
        check={"name": "na", "number": 14, "info": {"id": -2.1, "date": "2024"}},
        msg=".info.date: '2024' isn't an iso date format",
    )

    loadexpect(
        t,
        check={"name": "na", "number": 14, "info": {"id": -2.1, "date": "2024-01-01"}},
        msg=".info.link: field was not found",
    )

    loadexpect(
        t,
        check={
            "name": "na",
            "number": 14,
            "info": {
                "id": -2.1,
                "date": "2024-01-01",
                "link": b"ssh://name@192.168.1.12:8000/name",
            },
        },
    )

    loadexpect(
        t,
        check={
            "name": "na",
            "number": 14,
            "info": {
                "id": -2.1,
                "date": "2024-01-01",
                "link": "ssh//name",
            },
        },
        msg=".info.link: 'ssh//name' isn't an uri",
    )

    loadexpect(
        t,
        check={
            "name": "na",
            "number": 14,
            "info": {
                "id": -2.1,
                "date": "2024-01-01",
                "link": "ssh://name",
                "other": 12,
            },
        },
        msg=".info: Some of fields weren't matched ['other']",
    )


def loading_test_2():
    t = [
        {
            "text": "824",
            "hash": "68b329da9893e34099c7d8ad5cb9c940",
            "sub": {"comments": [1, 2, "t892"], "count": 3},
        },
        {
            "text": "Title of something",
            "hash": "136cddd7b38b90aebf7abaf45af641c6",
            "sub": {
                "comments": [
                    {"id": 12, "user": "Unique user", "msg": "....<>...."},
                    {
                        "id": 0,
                        "user": "Admin",
                        "msg": "===================================",
                        "role": "moderator",
                    },
                ],
                "count": 2,
            },
        },
    ]

    loadexpect(
        t,
        repre="('text', str), ('hash', str), ('sub', dict, ('comments', list, (Or, uint, str, (dict, ('id', uint), ('user', str), ('msg', str), (None, 'role', str)))), ('count', uint))",
    )

    loadexpect(
        t,
        repre="('text', str, 3, 18), ('hash', str, 32, 32), ('sub', dict, ('comments', list, (Or, (uint, 1, 2), (str, 4, 4), (dict, ('id', uint, 0, 12), ('user', str, 5, 11), ('msg', str, 10, 35), (None, 'role', str, 9, 9))), 2, 3), ('count', uint, 2, 3))",
        pedantic=True,
    )

    loadexpect(
        t,
        check={
            "text": "824",
            "hash": "68b329da9893e34099c7d8ad5cb9c940",
            "sub": {"comments": [1, 2, "t892"], "count": 3},
        },
    )

    loadexpect(
        t,
        check={
            "text": "8",
        },
        pedantic=True,
        msg=".text: length of 1 is not in range of 3 to 18",
    )

    loadexpect(
        t,
        check={
            "text": "824",
            "hash": "68b329da9893e34099c7d8ad5cb9c940",
            "sub": {"comments": ["t892"], "count": -2},
        },
        msg=".sub.count: -2 is not in range of 0 to -",
    )

    loadexpect(
        t,
        check={
            "text": "5812",
            "hash": "68b329da9893e38ad5cb9c940",
            "sub": {"comments": ["t892", {"name": 99}], "count": 24},
        },
        msg=lambda x: str.startswith(
            x, ".sub.comments: {'name': 99} did not match to any of ("
        ),
    )


def loading_tests():
    loading_test_1()
    loading_test_2()


matching_tests()
loading_tests()
