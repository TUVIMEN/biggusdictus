# biggusdictus

A library for validating dictionaries.

# Installation

    pip install biggusdictus

# Usage

## CLI

```
usage: __main__.py [-h] [-p] [FILE ...]

Tool for generating validation schemes for json files

positional arguments:
  FILE            json files

General:
  -h, --help      Show this help message and exit
  -p, --pedantic  return scheme with more detailed constrains
```

Generate scheme in python code from json files

```shell
biggusdictus -p FILE1 FILE2 FILE3
```

## Code

```python
from biggusdictus import *

sche = Scheme()

data = {
    "private": False,
    "date": "2025-02-22T00:00:00+0000",
    "id": 24,
    "avg": -24.2,
    "name": "user82224",
    "badges": [
        "b1",
        "b2",
        24
    ],
    "info": {
        "country": "Brazil",
        "posts": 421
    },
    "comments": [
        { "id": 254, "msg": "!!!!!!" },
        { "id": 254, "msg": "------", "likes": -2 }
    ]
}

# data can be checked by specifying scheme in arguments
sche.dict(
    data,
    ("private", bool),
    ("date", Isodate),
    ("id", uint),
    ("avg", float),
    ("name", str, 1), # name has to be at least 1 character long
    ("badges", list, (Or, str, uint)), # elements in list can be either str() or uint()
    ("info", dict,
        ("country", str),
        ("posts", uint)
    ),
    ("comments", list, (dict,
        ("id", uint),
        ("msg", str),
        (None, "likes", int) # if first arg is None, the field is optional
    ))
) # if test fails DictError() will be raised


sche.dict(
    data,
    False, # if first argument is scheme is False, scheme won't have to strictly match to all fields
    ("private", bool)
)

# scheme can be defined by passing "valid" dictionaries
sche.add(data)
data['private'] = None
sche.add(data) # scheme generated should always match to all dictionaries that defined it

sche.dict(data) # if no scheme is specified, the scheme defined by dictionaries is used

sche.dict(data, pedantic=True) # use more detailed constraints in defined scheme

# return python code representation of defined scheme in string (not formatted)
print(sche.scheme()) # results are not prettified
    # ('private', Or, float, None),
    # ('date', Isodate),
    # ('id', uint),
    # ('avg', float),
    # ('name', str),
    # ('badges', list, (Or, str, uint)),
    # ('info', dict, ('country', str), ('posts', uint)),
    # ('comments', list, (dict,
    #    ('id', uint),
    #    ('msg', str),
    #    (None, 'likes', int))
    # )

print(sche.scheme(pedantic=True))
    # ('private', Or, (float, False, False), None),
    # ('date', Isodate),
    # ('id', uint, 24, 24),
    # ('avg', float, -24.2, -24.2),
    # ('name', str, 9, 9),
    # ('badges', list, (Or, (str, 2, 2), (uint, 24, 24)), 3, 3),
    # ('info', dict, ('country', str, 6, 6), ('posts', uint, 421, 421)),
    # ('comments', list, (dict,
    #    ('id', uint, 254, 254),
    #    ('msg', str, 6, 6),
    #    (None, 'likes', int, -2, -2)
    # ), 2, 2)
```

## Scheme

`Scheme()` class stores scheme, `replacements` and `types` tables.

### dict()

`dict(self, data: dict, *args, pedantic: bool = False)` method validates `data` dict. If no `args` are specified then defined scheme will be used, otherwise `args` will be directly passed to `isdict()`.

If `pedantic` is set, scheme constrains become more detailed.

### list() tuple() set() frozenset() Not() Or() And()

All of them have the same arguments as `islist()`, `istuple()`, `isset()`, `isfrozenset()` `Not()`, `Or()`, `And()` counterparts. By calling them as class method replacements are preserved (normal functions inside expressions preserve replacements by being called from these methods).

### add()

`add(self, data: dict)` generates and merges scheme of `data` with scheme in class.

### replacements

Is a dictionary of classes to be replaced by functions in expressions.

```python
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
    dict: isdict,
}
```

You can freely change this

```python
from biggusdictus import Scheme, Instance

class mytype:
    def __init__(self, data):
        self.data = data

def ismytype(x, min=0):
    Instance(x, mytype)
    if min > 0:
        assert len(x.data) >= min

sche = Scheme()
sche.replacements[mytype] = ismytype

data = {
    "name": "something",
    "data": mytype([1,2,3,4])
}

sche.dict(
    data,
    ("name", str),
    ("data", mytype, 2), # is now equivalent to ("data", ismytype, 2)
)
```

### types

Is a list of types that are instances of `FieldType`. Can be changed freely, matching is done in reversed order so that new types are matched first.

```python
from biggusdictus import Scheme, Instance

class myFieldType(FieldType):
    pass

sche = Scheme()
sche.types.append(myFieldType)
```

### scheme()

`scheme(self, pedantic: bool = False) -> str` Is a method that returns a string that represents python code of scheme in class. `pedantic` param works the same way as for `dict()`

## Matching functions

They have to take at least 1 argument. Other arguments will be appended only if specified in scheme. Failure is indicated by raising exceptions, preferably `DictError()`.

```python
from biggusdictus import *
sche = Scheme()
data = {"name":824}

def iseven(x, min=0):
    Instance(x, int)

    assert x >= min
    assert x%2 == 0

sche.dict(data,("name",iseven,20))
```

### Default functions

The two first arguments are not shown in following definitions.

`Instance(type)` matches instances of `type`

`Is(*values)` matches if value `is` one of `values` https://stackoverflow.com/questions/13650293/understanding-the-is-operator

`Eq(*values)` matches if value is equal to one of `values`

`Not(*expr)` matches if passed expression fails, `(Not, Is, True)`, `(Not, (Is, True))`, `(Is, False)` is equivalent

`Or(*exprs)` matches if one of passed expressions matches

`And(*exprs)` matches only if all passed expressions match

`isdict(*args)` matches `dict` type, if the first of `args` is boolean, it will set strict mode i.e. `False` as the first argument will disable strict mode where all fields have to be matched. All other `args` have to be tuples or lists of field name, matching function and later it's arguments. If before field name `None` is specified the field becomes optional. For example `("avatar", str, 1, 256)` evaluates to field `avatar` matched by `str` that gets translated to `isstr`, to which later arguments are applied

`isbool()` matches `bool` type

`isNone()` matches `None` type

In the following functions `min` and `max` params are initialized to `None` indicating infinity, otherwise they have numeric type.

`isfloat(min=None, max=None)` matches `float` type

`isint(min=None, max=None)` matches `int` type

`uint(min=None, max=None)` matches unsigned integers

`i8(min=None, max=None)` matches 8 bit integers

`u8(min=None, max=None)` matches 8 bit unsigned integers

`i16(min=None, max=None)` matches 16 bit integers

`u16(min=None, max=None)` matches 16 bit unsigned integers

`i32(min=None, max=None)` matches 32 bit integers

`u32(min=None, max=None)` matches 32 bit unsigned integers

`i64(min=None, max=None)` matches 64 bit integers

`u64(min=None, max=None)` matches 64 bit unsigned integers

`isstr(min=None, max=None)` matches `str` type

`isbytes(min=None, max=None)` matches `bytes` type

In the following functions `type` param is initialized to `None` indicating no type matching, otherwise it should be set to function matching internal type.

`islist(type=None, min=None, max=None)` matches `list` type

`isset(type=None, min=None, max=None)` matches `set` type

`isfrozenset(type=None, min=None, max=None)` matches `frozenset` type

`istuple(type=None, min=None, max=None)` matches `tuple` type

`Isodate()` matches to `str` or `bytes` type that is a valid iso8601 date

`Uri()` matches to `str` or `bytes` type that is a valid url

`Url()` matches to valid url with `https` or `http` scheme

`Http()` matches to valid url with `https` scheme

`Https()` matches to valid url with `http` scheme

`Hash(min=1, max=None)` matches to `str` or `bytes` type that consists of hexadecimal digits

`Md5()` matches valid `md5` hash

`Sha1()` matches valid `sha1` hash

`Sha256()` matches valid `sha256` hash

`Sha512()` matches valid `sha512` hash

## Expressions

Expressions are presented in tuple structures where the first element is the function and other elements serve as arguments in it.

Tuples in expressions will get evaluated into lambda expressions, that's why tuples cannot be used for arguments in any matching function, lists should be used instead.

Expressions are mostly present in `isdict` fields where they are inlined: `("field", str, 2, 3)` in this case expression starts after the first argument. Build in python types can be used as matching functions since they get replaced when evaluating by `replacements`  dictionary. In this case `isstr()` is called with `2` and `3` arguments.

`("field", list, int, 2)` evaluates to `islist` with `int` and `2` arguments. Note that `int` uses default arguments, if you want to pass arguments you'd have to pass it as lambda expression `("fields", list, lambda x, w: isint(x,w,5), 2)` but thanks to tuple evaluation you can just `("fields", list, (int, 5), 2)` which is equivalent.

You can add arguments to optional types in `("field", list, (Or, int, str), 2)` by `("field", list, (Or, (int, 5), str), 2)`

## FieldType

All type discoverers are derived from `FieldType()` class. New discoverers can be appended to `Scheme()` class as described in `types` section.

`FieldType` defines many methods but any discoverers should overwrite only 4 of them:

```python
class FieldType:
    self.typelist
    self.replacements
    self.state

    def conv(self, x) -> dict:
        return {}

    def func(self) -> Callable:
        return lambda: 0

    def args(self, pedantic: bool = False) -> list:
        return []

    def merge(self, dest: dict, src: dict):
        pass
```

`self.typelist` is list of other discoverers

`self.replacements` is a dictionary of replacements

`self.state` is a dictionary of state of current object, contains results of `conv()` method

`conv()` method returns state dictionary based on passed value. Discovery fails if `DictError()` exception is raised.

`func()` method returns matching function that will be called in scheme. Schemes can be converted to string representations, to do that returned function have to have `__name__` field set, meaning that they cannot be made by lambda expressions. Such schemes should also be used where functions are in the same namespace.

`args(self, pedantic: bool = False)` method returns a list of arguments to function returned from `func()`. `pedantic` param is used to decide how many arguments should be returned.

`merge(self, dest: dict, src: dict)` method merges `src` and `dest` states while storing results in `dest`.

For example here's definition of `TypeAny()` discoverer that while never failing, returns instance check for python objects:

```python
class TypeAny(FieldType):
    def conv(self, x) -> dict:
        return {"type": type(x)}

    def func(self) -> Callable:
        return Instance

    def args(self, pedantic: bool = False) -> list:
        return [self.state["type"]]
```
