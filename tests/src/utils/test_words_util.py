import pytest

from src.utils.words_util import *


test_phonetic_dict = {
    0: "Alpha",
    1: "Bravo",
    2: "Charlie",
    3: "Delta",
    4: "Echo",
    5: "Foxtrot",
    6: "Golf",
    7: "Hotel",
    8: "India",
    9: "Juliett",
    10: "Kilo",
    11: "Lima",
    12: "Mike",
    13: "November",
    14: "Oscar",
    15: "Papa",
    16: "Quebec",
    17: "Romeo",
    18: "Sierra",
    19: "Tango",
    20: "Uniform",
    21: "Victor",
    22: "Whiskey",
    23: "X-ray",
    24: "Yankee",
    25: "Zulu",
}


# ========================= iid_context_to_values =========================
def test_iid_context_to_values():
    context = "test abc"
    for iid in range(26):
        assert iid_context_to_values(iid, context) == (test_phonetic_dict[iid], context)


# ========================= int_to_letter =========================
def test_int_to_letter_give_correct_response():
    # "0" -> "a" is desired, as that is how the WORDS selection is saved
    a_starting_values = [0, 65, 97]
    for i in range(26):
        assert int_to_letter(a_starting_values[0] + i) == chr(i + 65)
        assert int_to_letter(a_starting_values[1] + i) == chr(i + 65)
        assert int_to_letter(a_starting_values[2] + i) == chr(i + 65)


def test_int_to_letter_raises_error():
    out_of_bound_list = [-1, 26, 95, 123, 2048]
    for i in out_of_bound_list:
        with pytest.raises(ValueError):
            int_to_letter(i)


# ========================= int_to_phonetic =========================
def test_int_to_phonetic_give_correct_response():
    for i in range(26):
        assert int_to_phonetic(i) == int_phonetic_dict[i] == test_phonetic_dict[i]


def test_int_to_phonetic_raises_error():
    bounds = [-1, 26, 70, 100]
    for i in bounds:
        with pytest.raises(ValueError):
            int_to_phonetic(i)


# ========================= letter_to_int =========================
def test_letter_to_int_gives_correct_response():
    for i in range(26):
        assert letter_to_int(chr(i + 65)) == i
        assert letter_to_int(chr(i + 97)) == i


def test_letter_to_int_raises_error_int():
    bounds = [-1, 26, 64, 70, 91, 96, 100, 123, 125]
    for i in bounds:
        with pytest.raises(AttributeError):
            letter_to_int(i)


def test_letter_to_int_raises_error_str_not_char():
    # non-letter characters
    bounds = ["@", "[", "`", "{", " "]
    for i in bounds:
        with pytest.raises(ValueError):
            letter_to_int(i)
    # empty string
    with pytest.raises(ValueError):
        letter_to_int("")
    # multiple characters
    multiple = ["aa", "AB", "aB", "Bc", "zZ", "Zz"]
    for str in multiple:
        with pytest.raises(ValueError):
            letter_to_int(str)


# ========================= int_phonetic_dict =========================
def test_int_phonetic_dict():
    assert int_phonetic_dict == test_phonetic_dict
