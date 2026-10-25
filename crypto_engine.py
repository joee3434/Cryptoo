import math
import string

ALPHABET = string.ascii_uppercase


def default_key_hint(algorithm):
    return {
        "Caesar Cipher": "Integer shift, e.g. 3",
        "Vigenère Cipher": "English keyword, e.g. LEMON",
        "Playfair Cipher": "Keyword, e.g. MONARCHY",
        "Hill Cipher": "2x2 matrix values, e.g. 3,3,2,5",
    }.get(algorithm, "")


def _caesar(text, shift):
    out = []
    for ch in text:
        if "a" <= ch <= "z":
            out.append(chr((ord(ch) - 97 + shift) % 26 + 97))
        elif "A" <= ch <= "Z":
            out.append(chr((ord(ch) - 65 + shift) % 26 + 65))
        else:
            out.append(ch)
    return "".join(out)


def _keyword_shifts(key):
    key = "".join(ch for ch in key.upper() if ch in ALPHABET)
    if not key:
        raise ValueError("Enter an English-letter keyword, for example LEMON.")
    return [ord(ch) - 65 for ch in key]


def _vigenere(text, key, decrypt=False):
    shifts = _keyword_shifts(key)
    out, idx = [], 0
    direction = -1 if decrypt else 1
    for ch in text:
        if ch.isascii() and ch.isalpha():
            base = 65 if ch.isupper() else 97
            shift = shifts[idx % len(shifts)] * direction
            out.append(chr((ord(ch) - base + shift) % 26 + base))
            idx += 1
        else:
            out.append(ch)
    return "".join(out)


def _clean_letters(text):
    return "".join(ch for ch in text.upper() if ch in ALPHABET).replace("J", "I")


def _playfair_square(key):
    key_letters = _clean_letters(key)
    if not key_letters:
        raise ValueError("Playfair key must contain English letters.")
    seq = []
    for ch in key_letters + ALPHABET.replace("J", ""):
        if ch not in seq:
            seq.append(ch)
    square = [seq[i:i + 5] for i in range(0, 25, 5)]
    positions = {square[r][c]: (r, c) for r in range(5) for c in range(5)}
    return square, positions


def _playfair_prepare(text):
    letters = _clean_letters(text)
    pairs = []
    i = 0
    while i < len(letters):
        a = letters[i]
        if i + 1 >= len(letters):
            b = "X" if a != "X" else "Q"
            i += 1
        elif letters[i + 1] == a:
            b = "X" if a != "X" else "Q"
            i += 1
        else:
            b = letters[i + 1]
            i += 2
        pairs.append((a, b))
    return pairs


def _playfair(text, key, decrypt=False):
    square, pos = _playfair_square(key)
    if decrypt:
        letters = _clean_letters(text)
        if len(letters) % 2:
            raise ValueError("Playfair ciphertext must contain an even number of letters.")
        pairs = [(letters[i], letters[i + 1]) for i in range(0, len(letters), 2)]
    else:
        pairs = _playfair_prepare(text)
    step = -1 if decrypt else 1
    result = []
    for a, b in pairs:
        r1, c1 = pos[a]
        r2, c2 = pos[b]
        if r1 == r2:
            result.extend([square[r1][(c1 + step) % 5], square[r2][(c2 + step) % 5]])
        elif c1 == c2:
            result.extend([square[(r1 + step) % 5][c1], square[(r2 + step) % 5][c2]])
        else:
            result.extend([square[r1][c2], square[r2][c1]])
    return "".join(result)


def _hill_matrix(key):
    try:
        values = [int(x.strip()) % 26 for x in key.split(",")]
    except Exception as exc:
        raise ValueError("Hill key must be four comma-separated integers, e.g. 3,3,2,5.") from exc
    if len(values) != 4:
        raise ValueError("Hill key must have exactly four values, e.g. 3,3,2,5.")
    a, b, c, d = values
    det = (a * d - b * c) % 26
    if math.gcd(det, 26) != 1:
        raise ValueError("Invalid Hill key: determinant must be coprime with 26. Try 3,3,2,5.")
    return values, det


def _mod_inverse(value, modulus):
    for i in range(modulus):
        if (value * i) % modulus == 1:
            return i
    raise ValueError("Matrix determinant has no modular inverse.")


def _hill(text, key, decrypt=False):
    values, det = _hill_matrix(key)
    a, b, c, d = values
    if decrypt:
        inv_det = _mod_inverse(det, 26)
        # Inverse of [[a,b],[c,d]] modulo 26
        a, b, c, d = (d * inv_det) % 26, (-b * inv_det) % 26, (-c * inv_det) % 26, (a * inv_det) % 26

    # Hill works on letters; retain punctuation and spaces in their original positions.
    chars = list(text)
    positions = [i for i, ch in enumerate(chars) if ch in string.ascii_letters]
    letters = [chars[i].upper() for i in positions]
    if len(letters) % 2:
        if decrypt:
            raise ValueError("Hill ciphertext must have an even number of letters.")
        letters.append("X")
        positions.append(None)
    result = []
    for i in range(0, len(letters), 2):
        x, y = ord(letters[i]) - 65, ord(letters[i + 1]) - 65
        result.extend([chr((a * x + b * y) % 26 + 65), chr((c * x + d * y) % 26 + 65)])
    for idx, pos in enumerate(positions):
        if pos is not None:
            original = chars[pos]
            chars[pos] = result[idx].lower() if original.islower() else result[idx]
    # If an X padding character was added, append it to the output.
    if len(result) > len(positions):
        chars.append(result[-1])
    return "".join(chars)


def encrypt_text(algorithm, text, key=""):
    if algorithm == "Caesar Cipher":
        try:
            shift = int(key or "3")
        except ValueError as exc:
            raise ValueError("Caesar key must be an integer, e.g. 3.") from exc
        return _caesar(text, shift)
    if algorithm == "Vigenère Cipher":
        return _vigenere(text, key)
    if algorithm == "Playfair Cipher":
        return _playfair(text, key, False)
    if algorithm == "Hill Cipher":
        return _hill(text, key, False)
    raise ValueError("Unknown algorithm selected.")


def decrypt_text(algorithm, text, key=""):
    if algorithm == "Caesar Cipher":
        try:
            shift = int(key or "3")
        except ValueError as exc:
            raise ValueError("Caesar key must be an integer, e.g. 3.") from exc
        return _caesar(text, -shift)
    if algorithm == "Vigenère Cipher":
        return _vigenere(text, key, True)
    if algorithm == "Playfair Cipher":
        return _playfair(text, key, True)
    if algorithm == "Hill Cipher":
        return _hill(text, key, True)
    raise ValueError("Unknown algorithm selected.")
