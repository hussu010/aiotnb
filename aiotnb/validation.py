"""
The MIT License (MIT)

Copyright (c) 2021 AnonymousDapper
"""

from __future__ import annotations

__all__ = ("transform", "validate_with", "Validator", "Ignore", "Const", "Fn", "Type", "Maybe", "As", "Schema")

import logging
from functools import wraps
from typing import TYPE_CHECKING

from .errors import ValidatorException, ValidatorFailed, ValidatorTransformError

if TYPE_CHECKING:
    from typing import Any, Awaitable, Callable, Mapping, TypeVar

    from typing_extensions import ParamSpec

    _A = ParamSpec("_A")
    _M = TypeVar("_M", bound=Mapping[str, Any])


_log = logging.getLogger(__name__)


def transform(schema: Validator, data: Any) -> Any:
    is_ok = schema.validate(data)

    if not is_ok:
        raise ValidatorFailed(f"Had schema: {schema!r}\nHad data: {data!r}")

    return schema.transform(data)


def validate_with(schema: Validator):
    def deco(fn: Callable[_A, Awaitable[_M]]) -> Callable[_A, Awaitable[Any]]:
        @wraps(fn)
        async def inner(*args: _A.args, **kwargs: _A.kwargs) -> Any:
            result = await fn(*args, **kwargs)

            return transform(schema, result)

        return inner

    return deco


# Actual validator logic


class ArgsManager:
    types = {}
    tmp = []

    @classmethod
    def register_type(cls, type_, *args, **kwargs):
        cls.types[type_] = dict(args=args, kwargs=kwargs)

    @classmethod
    def has_type(cls, type_):
        return type_ in cls.types

    @classmethod
    def get_args(cls, type_):
        return cls.types[type_]["args"], cls.types[type_]["kwargs"]

    @classmethod
    def clear_type(cls, type_):
        cls.types[type_] = None

    @classmethod
    def temp(cls, type_, *args, **kwargs):
        cls.tmp.append(type_)
        cls.register_type(type_, *args, **kwargs)

        return cls()

    # @classmethod
    def __enter__(self):
        pass

    # @classmethod
    def __exit__(self, *args):
        cls = self.__class__
        tmp = cls.tmp.pop()
        cls.clear_type(tmp)


class Validator:
    validator: Any

    def __init__(self, validator: Any, *args: Any, **kwargs: Any):
        self.validator = validator
        self.args = args
        self.kwargs = kwargs

    def validate(self, data: Any) -> bool:
        return NotImplemented

    def transform(self, data: Any) -> Any:
        return NotImplemented

    def __repr__(self):
        return f"{self.__class__.__name__}[{self.validator!r}]"


# lower-level Validator helpers


class Ignore(Validator):
    def validate(self, data: Any) -> bool:
        return True

    def transform(self, data: Any) -> Any:
        return data


class Const(Validator):
    def validate(self, data: Any) -> bool:
        return data == self.validator

    def transform(self, data: Any) -> Any:
        if data == self.validator:
            return data

        else:
            raise ValidatorTransformError(f"expected constant value {self.validator!r}, got {data!r}")


class Fn(Validator):
    def validate(self, data: Any) -> bool:
        try:
            self.transform(data)

        except ValidatorException:
            return False

        return True

    def transform(self, data: Any) -> Any:
        try:
            val = self.validator(data)

        except ValidatorException as e:

            raise ValidatorTransformError(f"{self.validator.__name__} failed: Validator error: {e.message}") from e

        except Exception as e:
            raise ValidatorTransformError(f"{self.validator.__name__} failed: {e}") from e

        else:
            return val


# higher-level Validator helpers


class Type(Validator):
    def __init__(self, validator: Any, *args: Any, **kwargs: Any):
        self.is_strict = kwargs.pop("strict", False)
        super().__init__(validator, *args, **kwargs)

    def validate(self, data: Any) -> bool:
        try:
            self.transform(data)

        except ValidatorException:
            return False

        return True

    def transform(self, data: Any) -> Any:
        if self.is_strict:
            valid = type(data) == type(self.validator)
            message = f"value {data!r} should be of type {self.validator.__name__}, got {type(data).__name__}"
        else:
            valid = isinstance(data, self.validator)
            message = f"value {data!r} should be instance/subclass of {self.validator.__name__}, got {type(data).__name__} [{' -> '.join(x.__name__ for x in type(data).mro())}]"

        if valid:
            return data

        else:
            raise ValidatorTransformError(message)

    def __repr__(self):
        return f"{self.__class__.__name__}[{'*' if self.is_strict else ''}{self.validator.__name__}]"


class Maybe(Validator):
    def __init__(self, validator: Any, *args: Any, **kwargs: Any):
        super().__init__(Schema(validator).resolve(), *args, **kwargs)

    def validate(self, data: Any) -> bool:
        if data is None:
            return True

        return self.validator.validate(data)

    def transform(self, data: Any) -> Any:
        if data is None:
            return None

        return self.validator.transform(data)


class As(Validator):
    def __init__(self, validator: Any, transformer: Any, *args, **kwargs):
        self.transformer = transformer
        self._transformer_name = transformer.__name__ if hasattr(transformer, "__name__") else repr(transformer)

        self.unpack_params = kwargs.pop("unpack_args", True)

        super().__init__(Schema(validator).resolve(), *args, **kwargs)

    def validate(self, data: Any) -> bool:
        return self.validator.validate(data)

    def transform(self, data: Any) -> Any:
        new_data = self.validator.transform(data)
        result = None

        if ArgsManager.has_type(self.transformer):
            args, kwargs = ArgsManager.get_args(self.transformer)

        else:
            args, kwargs = [], {}

        try:
            if callable(self.transformer):
                if self.unpack_params:
                    type_ = _priority(data)
                    if type_ == DICT:
                        result = self.transformer(*args, **new_data, **kwargs)
                    elif type_ == ITER:
                        result = self.transformer(*new_data, *args, **kwargs)

                if not result:
                    result = self.transformer(new_data, *args, **kwargs)

            elif hasattr(self.transformer, "transform"):
                if self.unpack_params:
                    type_ = _priority(data)
                    if type_ == DICT:
                        result = self.transformer.transform(*args, **new_data, **kwargs)
                    elif type_ == ITER:
                        result = self.transformer.transform(*new_data, *args, **kwargs)

                if not result:
                    result = self.transformer.transform(new_data, *args, **kwargs)

            else:
                raise ValidatorTransformError(
                    f"transformer {self._transformer_name} has no candidate for conversion (is not callable, has no transform method)"
                )

            return result

        except Exception as e:
            raise ValidatorTransformError(
                f"failed to convert {type(data).__name__} with {self._transformer_name}: {e}"
            ) from e

    def __repr__(self):
        return f"{self.__class__.__name__}[{self.validator!r} -> {self._transformer_name}]"


# Priority code is adapted from schema package
IGNORE, VALUE, CALLABLE, VALIDATOR, TYPE, DICT, ITER = range(7)


def _priority(item: Any) -> int:
    if type(item) in (list, tuple, set, frozenset):
        return ITER

    if type(item) is dict:
        return DICT

    if issubclass(type(item), type):
        return TYPE

    if issubclass(type(item), Validator):
        return VALIDATOR

    if callable(item):
        return CALLABLE

    if item is Ellipsis:
        return IGNORE

    return VALUE


def _priority_by_key(item: Any):
    if isinstance(item, Maybe):
        return _priority(item.validator) + 0.5

    return _priority(item)


# Main validator entry


class Schema(Validator):
    def __init__(self, validator: Any, *args: Any, **kwargs: Any):
        self.validator = validator

        self.args = args
        self.kwargs = kwargs

        self.result = None
        self.valid = None
        self.resolved = False

    def resolve(self) -> Validator:
        self.resolved = True
        validator = self.validator

        type_ = _priority(validator)

        if type_ == IGNORE:
            # print(f"[debug] got object: {validator!r} as IGNORE")

            return self

        if type_ == VALUE:
            # print(f"[debug] got object: {validator!r} as VALUE")

            return Const(validator)

        if type_ == CALLABLE:
            # print(f"[debug] got {validator!r} as CALLABLE")

            return Fn(validator)

        if type_ == VALIDATOR:
            # print(f"[debug] got {validator!r} as VALIDATOR")

            return validator

        if type_ == TYPE:
            # print(f"[debug] got {validator!r} as TYPE")

            return Type(validator)

        if type_ == DICT:
            # print(f"[debug] got {validator!r} as DICT")

            keys = sorted(validator, key=_priority_by_key)

            self.validator = {key: Schema(validator[key], *self.args, **self.kwargs).resolve() for key in keys}

            return self

        if type_ == ITER:
            # print(f"[debug] got {validator!r} as ITER")

            self.validator = [Schema(v, *self.args, **self.kwargs).resolve() for v in validator]

            return self

        raise ValidatorException(f"Encountered unknown validator type: {validator!r} ({type(validator).__name__}")

    def validate(self, data: Any) -> bool:
        if not self.resolved:
            self.resolve()

        validator = self.validator

        type_ = _priority(validator)

        if type_ == IGNORE:
            # print(f"[debug] got object: {validator!r} : {data!r} as IGNORE")

            return True

        if type_ == VALUE:
            # print(f"[debug] got object: {validator!r} : {data!r} as VALUE")

            return Const(validator).validate(data)

        if type_ == CALLABLE:
            # print(f"[debug] got {validator!r} : {data!r} as CALLABLE")

            return Fn(validator).validate(data)

        if type_ == VALIDATOR:
            # print(f"[debug] got {validator!r} : {data!r} as VALIDATOR")

            return validator.validate(data)

        if type_ == TYPE:
            # print(f"[debug] got {validator!r} : {data!r} as TYPE")

            return Type(validator).validate(data)

        if type_ == DICT:
            # print(f"[debug] got {validator!r} : {data!r} as DICT")

            if type(data) is dict:
                visited_keys = set()

                keys = sorted(validator, key=_priority_by_key, reverse=True)

                # ordered_data = sorted(data.items(), key=lambda v: type(v[1]) is dict)

                for key in keys:
                    if key in data:
                        result = validator[key].validate(data[key])

                        if not result:
                            return False

                    # Handle key-optional validator here
                    visited_keys.add(key)

                if visited_keys != set(keys):
                    return False

                return True

            return False

        if type_ == ITER:
            # print(f"[debug] got {validator!r} : {data!r} as ITER")

            if len(validator) == 1:  # homogenous sequence
                inner_validator = validator[0]

                return all(type(data)(inner_validator.validate(x) for x in data))

            else:  # heterogenous sequence
                return all(type(data)(v.validate(d) for v, d in zip(validator, data)))

        raise ValidatorException(f"Encountered unknown validator type: {validator!r} ({type(validator).__name__}")

    def transform(self, data: Any) -> Any:
        if not self.resolved:
            self.resolve()

        validator = self.validator

        type_ = _priority(validator)

        if type_ == IGNORE:
            # print(f"[debug] got object: {validator!r} : {data!r} as IGNORE")

            return data

        if type_ == VALUE:
            # print(f"[debug] got object: {validator!r} : {data!r} as VALUE")

            return Const(validator).transform(data)

        if type_ == CALLABLE:
            # print(f"[debug] got {validator!r} : {data!r} as CALLABLE")

            return Fn(validator).transform(data)

        if type_ == VALIDATOR:
            # print(f"[debug] got {validator!r} : {data!r} as VALIDATOR")

            return validator.transform(data)

        if type_ == TYPE:
            # print(f"[debug] got {validator!r} : {data!r} as TYPE")

            return Type(validator).transform(data)

        if type_ == DICT:
            # print(f"[debug] got {validator!r} : {data!r} as DICT")

            if type(data) is dict:
                visited_keys = set()
                new = {}
                keys = sorted(validator, key=_priority_by_key, reverse=True)

                # ordered_data = sorted(data.items(), key=lambda v: type(v[1]) is dict)

                for key in keys:
                    if key in data:
                        # Handle key-optional validator here
                        visited_keys.add(key)

                        new[key] = validator[key].transform(data[key])

                    else:
                        raise ValidatorTransformError(f"missing required key {key!r} in {data!r}")

                required_keys = set(keys)
                if self.kwargs.get("ignore_extra_keys", False):
                    required_keys = required_keys | set(data.keys())

                if visited_keys > required_keys:
                    print(f"more keys visited than required - {visited_keys} : {required_keys}")

                elif visited_keys < required_keys:
                    raise ValidatorTransformError(f"missing keys in validator: {required_keys - visited_keys}")

                return new

            raise ValidatorTransformError(f"expected dict for validator, got {type(data).__name__}")

        if type_ == ITER:
            # print(f"[debug] got {validator!r} : {data!r} as ITER")

            if len(validator) == 1:  # homogenous sequence
                inner_validator = validator[0]

                return type(data)(inner_validator.transform(x) for x in data)

            else:  # heterogenous sequence
                return type(data)(v.transform(d) for v, d in zip(validator, data))

        raise ValidatorException(f"Encountered unknown validator type: {validator!r} ({type(validator).__name__}")
