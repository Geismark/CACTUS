def int_to_letter(num):
    num = int(num)
    if 0 <= num <= 25:
        return chr(num + 65)
    elif 65 <= num <= 90:
        return chr(num)
    elif 97 <= num <= 122:
        return chr(num - 32)
    else:
        raise ValueError(f"Invalid number: {num}")
