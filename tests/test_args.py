from args import Args


def test_0():
    args = Args([""])
    assert args.get() is None


def test_1():
    args = Args(["a"])
    assert args.get() == "a"
    assert args.get() is None


def test_2():
    args = Args(["ab"])
    assert args.get() == "ab"
    assert args.get() is None


def test_3():
    args = Args(["a", "b"])
    assert args.get() == "a"
    assert args.get() == "b"
    assert args.get() is None


def test_4():
    args = Args(["a.b"])
    assert args.get() == "a"
    assert args.get() == "b"
    assert args.get() is None


def test_5():
    args = Args(["a.", "b"])
    assert args.get() == "a"
    assert args.get() == "b"
    assert args.get() is None


def test_6():
    args = Args(["a", ".b"])
    assert args.get() == "a"
    assert args.get() == "b"
    assert args.get() is None


def test_7():
    args = Args(["a", ".", "b"])
    assert args.get() == "a"
    assert args.get() == "b"
    assert args.get() is None


def test_8():
    args = Args(["a b"])
    assert args.get(long=True) == "a b"
    assert args.get() is None


def test_9():
    args = Args(["a b", "c"])
    assert args.get(long=True) == "a b c"
    assert args.get() is None


def test_10():
    args = Args(["a b", ".c"])
    assert args.get(long=True) == "a b"
    assert args.get() == "c"
    assert args.get() is None


def test_11():
    args = Args(["a", ",b", ",c"])
    assert args.get(multi=True) == ["a", "b", "c"]
    assert args.get() is None


def test_12():
    args = Args(["a,b"])
    assert args.get(multi=True) == ["a", "b"]
    assert args.get() is None


def test_13():
    args = Args(["a,b.c,", "d"])
    assert args.get(multi=True) == ["a", "b"]
    assert args.get(multi=True) == ["c", "d"]
    assert args.get() is None


def test_14():
    args = Args(["a b,c d"])
    assert args.get(long=True, multi=True) == ["a b", "c d"]
    assert args.get() is None


def test_15():
    args = Args(["a b,c d", ".", "e, f g"])
    assert args.get(long=True, multi=True) == ["a b", "c d"]
    assert args.get(long=True, multi=True) == ["e", "f g"]
    assert args.get() is None


def test_16():
    args = Args(["a.b-c.d .. e-f.g"], delimiters=Args.Delimiters(comma="-", dot=".."))
    assert args.get(long=True, multi=True) == ["a.b", "c.d"]
    assert args.get(long=True, multi=True) == ["e", "f.g"]
    assert args.get() is None
