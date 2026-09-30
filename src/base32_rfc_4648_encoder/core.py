"""Base32 encoding and decoding per RFC 4648.

This implementation uses Python's built-in :mod:`base64` module, which already
provides a compliant RFC 4648 Base32 codec. We expose two small wrapper
functions, ``encode`` and ``decode``, so callers get a single, unambiguous
surface area: upper-case output, strict padding on encode, and strict
validation on decode.

Design decisions (all stated plainly so the behaviour is predictable):

* Encoding always returns UPPER-case ASCII. RFC 4648 Section 3.2 notes that
  encoders MUST produce upper-case and decoders MUST treat upper and lower as
  equivalent. We honour both.
* Encoding always appends the correct number of ``=`` padding characters so
  the output length is a multiple of eight. There is no "no padding" option.
* Decoding rejects non-alphabet bytes (including whitespace and newlines)
  rather than silently stripping them, because silent data mutation is a
  recurring source of security bugs. ``base64.b32decode`` with its default
  ``casefold=False`` still accepts lower-case, which RFC 4648 requires, but it
  raises on characters outside the alphabet.
* Decoding requires correct padding length. RFC 4648 Section 3.1.2 describes
  the exact padding rules; ``base64.b32decode`` enforces them when
  ``map01=None`` and we keep that default.

The return types are deliberately plain ``str`` for the encoded form and
``bytes`` for the decoded form, matching how RFC 4648 is most commonly used in
application code: Base32 text is for humans and transport, the decoded value
is raw bytes.
"""

from __future__ import annotations

import base64


_BASE32_ALPHABET = b"ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"


def encode(data: bytes) -> str:
    """Encode ``data`` as a Base32 string per RFC 4648.

    The output is always upper-case ASCII and always padded with ``=`` so its
    length is a multiple of eight. ``data`` must be :class:`bytes` (or a
    :class:`bytearray`); passing :class:`str` raises :class:`TypeError` because
    silently encoding text would hide a caller bug (the caller should pick an
    encoding such as UTF-8 first).

    :param data: The raw bytes to encode.
    :returns: The Base32 representation as a :class:`str`.
    :raises TypeError: If ``data`` is not :class:`bytes` or :class:`bytearray`.
    """
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError(
            "encode() expects bytes or bytearray, got "
            f"{type(data).__name__}; if you have text, encode it (e.g. "
            "text.encode('utf-8')) before calling encode()."
        )
    encoded = base64.b32encode(bytes(data))
    # b32encode already returns upper-case ASCII; decoding as ASCII keeps the
    # contract explicit and would surface any surprise from a future stdlib
    # change rather than silently producing mojibake.
    return encoded.decode("ascii")


def decode(text: str) -> bytes:
    """Decode a Base32 string per RFC 4648.

    Lower-case input is accepted (RFC 4648 Section 3.2 requires decoders to
    treat upper and lower as equivalent) and converted to upper-case before
    handing off to :func:`base64.b32decode`. Any character outside the Base32
    alphabet (including whitespace, newlines, and ``-``/``_`` from other
    alphabets) causes :class:`ValueError`. Incorrect padding length also causes
    :class:`ValueError`.

    ``text`` must be :class:`str`. Passing :class:`bytes` is rejected with
    :class:`TypeError` so callers decide explicitly how to obtain text.

    :param text: The Base32 string to decode.
    :returns: The decoded raw bytes.
    :raises TypeError: If ``text`` is not :class:`str`.
    :raises ValueError: If ``text`` is not valid padded Base32.
    """
    if not isinstance(text, str):
        raise TypeError(
            "decode() expects str, got "
            f"{type(text).__name__}; if you have bytes, decode them (e.g. "
            "b.decode('ascii')) before calling decode()."
        )
    # Normalise to upper-case so b32decode's casefold path is not needed; this
    # keeps the alphabet check strict while still honouring the RFC's
    # case-insensitivity requirement.
    upper = text.upper()
    # Map any non-alphabet characters to make the subsequent check cheap and
    # explicit, then let b32decode raise a precise ValueError with the
    # standard message. We do not strip whitespace on purpose: accepting
    # whitespace would let a copy-paste with a trailing newline silently
    # succeed, but it would also let a truncated paste silently succeed in
    # some padding configurations, which is worse.
    for ch in upper:
        if ch != "=" and ch not in _BASE32_ALPHABET.decode("ascii"):
            raise ValueError(
                f"Non-alphabet character {ch!r} in Base32 input."
            )
    return base64.b32decode(upper)
