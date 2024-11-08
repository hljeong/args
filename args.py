from typing import Iterable, cast
from sys import argv, stderr
from rich import print
from dataclasses import dataclass

from menu.menu import Menu, select


def err(msg: str, do_exit: bool = True):
    print(f"[red]{msg}[/red]", file=stderr)
    if do_exit:
        exit(1)


class Args:
    @dataclass
    class Delimiters:
        comma: str = ","
        dot: str = "."

        def __post_init__(self):
            assert self.comma != self.dot

        def __iter__(self):
            return iter({self.comma, self.dot})

    DEFAULT_DELIMITERS: Delimiters = Delimiters()

    def __init__(
        self, args: list[str] | None = None, delimiters: Delimiters = DEFAULT_DELIMITERS
    ):
        self._args: list[str] = args or argv[1:]
        self._delimiters: Args.Delimiters = delimiters
        self._preprocess()
        self._idx: int = 0
        self._n: int = len(self._args)

    def __str__(self) -> str:
        line: list[str] = []
        for i in range(self._n):
            if i > 0 and self._args[i] != self._delimiters.comma:
                line.append(" ")
            line.append(self._args[i])

        return "".join(line)

    def __format__(self, spec: str) -> str:
        line: list[str] = []
        for i in range(self._n):
            if i > 0 and self._args[i] != self._delimiters.comma:
                line.append(" ")
            if spec == "c" and i == self._idx:
                line.append(f"[{self._args[i]}]")
            else:
                line.append(self._args[i])

        if self._at_end():
            line.append("[]")

        return "".join(line)

    def _preprocess(self):
        args: list[str] = []
        idx: int = 0
        n: int = len(self._args)
        while idx < n:
            l: int = 0
            r: int = 0
            s: str = self._args[idx]
            m: int = len(s)
            while r < m:
                if s[r:].startswith(self._delimiters.comma) or s[r:].startswith(
                    self._delimiters.dot
                ):
                    if len(arg := s[l:r].strip()) > 0:
                        args.append(arg)
                    if s[r:].startswith(self._delimiters.comma):
                        args.append(self._delimiters.comma)
                        l = r = r + len(self._delimiters.comma)
                    else:
                        args.append(self._delimiters.dot)
                        l = r = r + len(self._delimiters.dot)
                else:
                    r += 1

            if len(arg := s[l:r].strip()) > 0:
                args.append(arg)

            idx += 1

        self._args = args

    def _err(self, msg: str):
        err(f"{msg}:\n  {self:c}")

    def _at_start(self) -> bool:
        # sanity check
        assert 0 <= self._idx <= self._n
        return self._idx == 0

    def _at_end(self) -> bool:
        # sanity check
        assert 0 <= self._idx <= self._n
        return self._idx == self._n

    def _peek(self) -> str:
        assert not self._at_end()
        return self._args[self._idx]

    def _advance(self):
        assert not self._at_end()
        self._idx += 1

    def _backtrack(self):
        assert not self._at_start()
        self._idx -= 1

    def _match(self, s: str) -> bool:
        return self._peek() == s

    def _consume(self) -> str:
        arg: str = self._peek()
        self._advance()
        return arg

    def _match_consume(self, s: str) -> bool:
        match: bool
        if match := self._match(s):
            self._advance()
        return match

    def _get(self) -> str | None:
        if self._at_end() or self._match_consume(self._delimiters.dot):
            return None

        arg = self._consume()
        if not self._at_end():
            self._match_consume(self._delimiters.dot)
        return arg

    def _get_multi(self) -> list[str]:
        if self._at_end() or self._match_consume(self._delimiters.dot):
            return []

        multi_args: list[str] = []
        if self._match(self._delimiters.comma):
            self._err("invalid multi arg")
        multi_args.append(self._consume())

        while not self._at_end() and not self._match_consume(self._delimiters.dot):
            if not self._match_consume(self._delimiters.comma):
                break

            if (
                self._at_end()
                or self._match(self._delimiters.comma)
                or self._match(self._delimiters.dot)
            ):
                self._err("invalid multi arg")

            multi_args.append(self._consume())

        return multi_args

    def _get_long(self) -> str | None:
        long_arg: list[str] = []
        while not self._at_end():
            if self._match(self._delimiters.comma):
                if long_arg == []:
                    self._err("invalid long arg")

                self._backtrack()
                long_arg.pop(-1)
                break

            elif self._match_consume(self._delimiters.dot):
                break

            else:
                long_arg.append(self._consume())

        return None if long_arg == [] else " ".join(long_arg)

    def _get_multi_long(self) -> list[str]:
        if self._at_end() or self._match_consume(self._delimiters.dot):
            return []

        multi_args: list[str] = []
        long_arg: list[str] = []
        while not self._at_end() and not self._match(self._delimiters.comma):
            long_arg.append(self._consume())
        if long_arg == []:
            self._err("invalid multi long arg")
        multi_args.append(" ".join(long_arg))
        long_arg = []

        while not self._at_end() and not self._match_consume(self._delimiters.dot):
            if not self._match_consume(self._delimiters.comma):
                break  # todo: is this possible to hit?

            if (
                self._at_end()
                or self._match(self._delimiters.comma)
                or self._match(self._delimiters.dot)
            ):
                self._err("invalid multi long arg")

            long_arg.append(self._consume())
            while (
                not self._at_end()
                and not self._match(self._delimiters.comma)
                and not self._match(self._delimiters.dot)
            ):
                long_arg.append(self._consume())
            multi_args.append(" ".join(long_arg))
            long_arg = []

        if not self._at_end():
            self._match_consume(self._delimiters.dot)
        return multi_args

    def get(self, multi: bool = False, long: bool = False) -> str | list[str] | None:
        if not multi and not long:
            return self._get()

        if multi and not long:
            return self._get_multi()

        if not multi and long:
            return self._get_long()

        if multi and long:
            return self._get_multi_long()

        assert False

    def get_or_select(
        self,
        choices: Iterable[str],
        multi: bool = False,
        long: bool = False,
        menu_mode: object = Menu.SINGLE,
        menu_prompt: str | None = None,
        menu_use_descriptions: bool = False,
        check_validity: bool = True,
        exit_on_none: bool = True,
    ) -> str | list[str] | None:
        assert multi ^ (
            menu_mode == Menu.SINGLE
        ), "menu mode must be consistent with multi flag"

        arg: str | list[str] | None = self.get(multi=multi, long=long)

        if arg is None or multi and arg == []:
            arg = select(
                choices,
                mode=menu_mode,
                prompt=menu_prompt,
                use_descriptions=menu_use_descriptions,
            )

            if arg is None and exit_on_none:
                exit(1)

        elif check_validity:
            if multi:
                invalid_args: list[str] = [arg_ for arg_ in arg if arg_ not in choices]
                if invalid_args:
                    err(
                        f"invalid arg{'' if len(invalid_args) == 1 else 's'}: {', '.join(arg)} (select from: {', '.join(choices)})"
                    )

            elif cast(str, arg) not in choices:
                err(f"invalid arg: {arg} (select from: {', '.join(choices)})")

        return arg
