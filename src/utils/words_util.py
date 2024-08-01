def iid_context_to_values(iid, context: str) -> tuple:
    return (int_to_phonetic(iid), context)


def int_to_letter(num: int) -> str:
    num = int(num)
    if 0 <= num <= 25:
        return chr(num + 65)
    elif 65 <= num <= 90:
        return chr(num)
    elif 97 <= num <= 122:
        return chr(num - 32)
    else:
        raise ValueError(f"Invalid number: {num}")


def int_to_phonetic(num: int) -> str:
    num = int(num)
    if 0 <= num <= 25:
        return int_phonetic_dict[num]
    else:
        raise ValueError(f"Invalid number: {num}")


def letter_to_int(letter: str) -> int:
    letter = letter.upper()
    if "A" <= letter <= "Z":
        return ord(letter) - 65
    else:
        raise ValueError(f"Invalid letter: {letter}")


int_phonetic_dict = {
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


if __name__ == "__main__":
    print(letter_to_int("A"))
    print(letter_to_int("a"))
    print(letter_to_int("Z"))
    print(letter_to_int("z"))
