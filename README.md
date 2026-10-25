# CRYPTOO — Cryptography Workstation

A desktop educational application built with Python, CustomTkinter, and SQLite.

## Ciphers
- Caesar Cipher — integer shift key, default 3.
- Vigenère Cipher — English-letter keyword, e.g. `LEMON`.
- Playfair Cipher — keyword, e.g. `MONARCHY`. I and J share a square cell; output is letters only and filler letters may be inserted.
- Hill Cipher — 2x2 matrix key as four comma-separated integers, e.g. `3,3,2,5`. The determinant must be invertible modulo 26.

## Install on Ubuntu

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip python3-tk -y
cd ~/Downloads/Cryptoo_Pro
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

If the project was extracted to a nested folder, `cd` into the folder containing `main.py` and `requirements.txt` before installing/running.

## Notes
These are classical educational ciphers and are not suitable for protecting real confidential data. Hill encryption pads an odd number of letters with X; Playfair removes spaces and punctuation and combines I/J. Some padding characters may need manual removal after decryption.
