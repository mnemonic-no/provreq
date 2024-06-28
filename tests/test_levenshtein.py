import provreq.tools.libs.data as data


def test_levenshtein() -> None:

    d = data.levenshtein("test", "test")
    assert d == 0

    d = data.levenshtein("test", "tast")
    assert d == 1

    d = data.levenshtein("abcd", "efgh")
    assert d == 4

    d = data.levenshtein("abcd", "efghi")
    assert d == 5

    d = data.levenshtein("efghi", "abcd")
    assert d == 5
