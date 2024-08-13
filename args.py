from sys import argv, stderr


class Args:
    DELIMITERS: set[str] = {".", ","}

    def __init__(self, args: list[str] | None = None):
        self._args: list[str] = args or argv[1:]
        self._preprocess()
        self._idx: int = 0
        self._n: int = len(self._args)

    def __str__(self) -> str:
        line: list[str] = []
        for i in range(self._n):
            if i > 0 and self._args[i] != ",":
                line.append(" ")
            line.append(self._args[i])

        return "".join(line)

    def __format__(self, spec: str) -> str:
        line: list[str] = []
        for i in range(self._n):
            if i > 0 and self._args[i] != ",":
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
                if s[r] in Args.DELIMITERS:
                    if r > l:
                        args.append(s[l:r])
                    args.append(s[r])
                    l = r = r + 1
                else:
                    r += 1

            if r > l:
                args.append(self._args[idx][l:r])

            idx += 1

        self._args = args

    def _err(self, msg: str):
        print(f"{msg}:", file=stderr)
        print(f"  {self:c}", file=stderr)
        exit(1)

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
        if self._at_end() or self._match_consume("."):
            return None

        return self._consume()

    def _get_multi(self) -> list[str]:
        if self._at_end() or self._match_consume("."):
            return []

        multi_args: list[str] = []
        if self._match(","):
            self._err("invalid multi arg")
        multi_args.append(self._consume())

        while not self._at_end() and not self._match_consume("."):
            if not self._match_consume(","):
                break

            if self._at_end() or self._match(",") or self._match("."):
                self._err("invalid multi arg")

            multi_args.append(self._consume())

        return multi_args

    def _get_long(self) -> str | None:
        long_arg: list[str] = []
        while not self._at_end():
            if self._match(","):
                if long_arg == []:
                    print("invalid long arg:", file=stderr)
                    print(f"  {self:c}", file=stderr)
                    exit(1)

                self._backtrack()
                long_arg.pop(-1)
                break

            elif self._match_consume("."):
                break

            else:
                long_arg.append(self._consume())

        if long_arg == []:
            return None
        return " ".join(long_arg)

    def _get_multi_long(self) -> list[str]:
        if self._at_end() or self._match_consume("."):
            return []

        multi_arg: list[str] = []
        long_arg: list[str] = []
        while not self._at_end() and not self._match(","):
            long_arg.append(self._consume())
        multi_arg.append(" ".join(long_arg))
        long_arg = []

        while not self._at_end() and not self._match_consume("."):
            if not self._match_consume(","):
                break

            if self._at_end() or self._match(",") or self._match("."):
                self._err("invalid multi long arg")

            while not self._at_end() and not self._match(","):
                long_arg.append(self._consume())
            multi_arg.append(" ".join(long_arg))
            long_arg = []

        return multi_arg

    def get(self, long: bool = False, multi: bool = False) -> str | list[str] | None:
        if not multi and not long:
            return self._get()

        if multi and not long:
            return self._get_multi()

        if not multi and long:
            return self._get_long()

        if multi and long:
            return self._get_multi_long()

        assert False
