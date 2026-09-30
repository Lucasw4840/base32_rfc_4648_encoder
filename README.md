# base32_rfc_4648_encoder

A small, dependency-free Python library for Base32 encoding and decoding that strictly follows RFC 4648. Two functions, `encode` and `decode`, are the entire API.

```python
from base32_rfc_4648_encoder import encode, decode

text = encode(b"foobar")      # 'MZXW6YTBOI======'
bytes_ = decode(text)          # b'foobar'
```

## Why this exists

Python's standard library already ships a compliant Base32 codec in `base64.b32encode` / `base64.b32decode`. The problem is not correctness, it is that those functions are easy to misuse: they accept `bytes` where a caller meant `str`, their handling of lower-case input depends on a `casefold` flag, and whitespace or incorrect padding can produce surprising results. This library wraps them with a deliberately small surface and strict rules so the behaviour is predictable.

The trade-off is strictness over convenience. There is no option to skip padding, no option to allow whitespace, and no option to use the base32hex alphabet. If you need those, use `base64` directly.

## Behaviour you will hit

- `encode` always returns upper-case ASCII and always pads the output to a multiple of eight characters.
- `decode` accepts lower-case and mixed-case input, but rejects every character outside the RFC 4648 alphabet, including spaces, newlines, `-`, and `_`. It does not strip whitespace. Incorrect padding length raises `ValueError`.
- `encode` takes `bytes` or `bytearray` and returns `str`. Passing `str` raises `TypeError`; if you have text, encode it to UTF-8 first.
- `decode` takes `str` and returns `bytes`. Passing `bytes` raises `TypeError`; decode it to ASCII first.

## Exported names

- `encode(data: bytes) -> str`
- `decode(text: str) -> bytes`
