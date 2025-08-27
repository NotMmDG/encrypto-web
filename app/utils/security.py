from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from env import settings
import random
import bcrypt
from fastapi import HTTPException, status
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
import base64
from collections import Counter
import heapq
import struct

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)
def get_password_hash(password: str) -> str:
    hashed = pwd_context.hash(password)
    print(f"Hashing password: {password} -> {hashed}")
    return hashed

def verify_password(plain_password: str, hashed_password: str) -> bool:
    result = pwd_context.verify(plain_password, hashed_password)
    print(f"Verifying password: {plain_password} with hash: {hashed_password} -> {result}")
    return result

# JWT settings
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        return user_id
    except JWTError:
        raise credentials_exception
def generate_password(length=12):
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return "".join(random.choice(chars) for _ in range(length))

def encrypt_file(data, password):
    salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = kdf.derive(password.encode())
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(data) + encryptor.finalize()
    return salt + iv + encrypted_data

def decrypt_file(data, password):
    salt = data[:16]
    iv = data[16:32]
    encrypted_data = data[32:]
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = kdf.derive(password.encode())
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    return decryptor.update(encrypted_data) + decryptor.finalize()
class _HuffNode:
    __slots__ = ("freq", "sym", "left", "right")
    def __init__(self, freq, sym=None, left=None, right=None):
        self.freq = freq
        self.sym = sym
        self.left = left
        self.right = right
    # heapq needs this
    def __lt__(self, other):
        return self.freq < other.freq


def _build_huff_tree(freqs: dict) -> Optional[_HuffNode]:
    """
    Build a Huffman tree from {byte: frequency}.
    """
    heap = []
    for sym, f in freqs.items():
        heapq.heappush(heap, _HuffNode(f, sym=sym))

    if not heap:
        return None

    if len(heap) == 1:
        # Edge case: only one unique symbol -> make a 2-node tree
        only = heapq.heappop(heap)
        dummy = _HuffNode(0, sym=only.sym)
        return _HuffNode(only.freq, left=only, right=dummy)

    while len(heap) > 1:
        a = heapq.heappop(heap)
        b = heapq.heappop(heap)
        heapq.heappush(heap, _HuffNode(a.freq + b.freq, left=a, right=b))
    return heap[0]


def _build_code_table(node: _HuffNode, prefix: str = "", table=None) -> dict:
    """
    Create {byte: 'bitstring'} mapping.
    """
    if table is None:
        table = {}

    # Leaf
    if node.sym is not None and node.left is None and node.right is None:
        table[node.sym] = prefix or "0"  # ensure at least one bit if single-symbol
        return table

    _build_code_table(node.left, prefix + "0", table)
    _build_code_table(node.right, prefix + "1", table)
    return table


def huffman_compress(data: bytes) -> bytes:
    """
    Compress 'data' with Huffman coding.

    Output format (big-endian):
    - magic: b'HUFF1' (5 bytes)
    - orig_len: uint64
    - num_symbols: uint16  (<= 256)
    - repeated num_symbols times: (symbol: uint8, freq: uint64)
    - pad_bits: uint8  (how many 0-bits were padded at end)
    - payload: packed bits
    """
    magic = b"HUFF1"

    if not data:
        # empty payload
        return magic + struct.pack(">QH", 0, 0) + bytes([0])

    freqs = Counter(data)
    root = _build_huff_tree(freqs)
    codes = _build_code_table(root)

    # Build bitstring
    bits = "".join(codes[b] for b in data)
    pad_bits = (8 - (len(bits) % 8)) % 8
    bits += "0" * pad_bits

    # Pack bits to bytes
    out = bytearray()
    for i in range(0, len(bits), 8):
        out.append(int(bits[i:i+8], 2))

    # Header
    num = len(freqs)
    header = magic + struct.pack(">QH", len(data), num)
    for sym, f in freqs.items():
        header += struct.pack(">BQ", sym, f)
    header += struct.pack(">B", pad_bits)

    return header + bytes(out)


def huffman_decompress(blob: bytes) -> bytes:
    """
    Reverse of huffman_compress().
    """
    magic = b"HUFF1"
    if len(blob) < len(magic) + 8 + 2 + 1:
        raise ValueError("Invalid Huffman blob: too short")

    if blob[:5] != magic:
        raise ValueError("Invalid Huffman blob: bad magic")

    idx = 5
    orig_len, num_symbols = struct.unpack(">QH", blob[idx:idx+10])
    idx += 10

    freqs = {}
    for _ in range(num_symbols):
        sym, f = struct.unpack(">BQ", blob[idx:idx+9])
        idx += 9
        freqs[sym] = f

    pad_bits = struct.unpack(">B", blob[idx:idx+1])[0]
    idx += 1
    payload = blob[idx:]

    if num_symbols == 0:
        return b""

    # Single-symbol shortcut
    if len(freqs) == 1:
        sym = next(iter(freqs.keys()))
        return bytes([sym]) * orig_len

    # Rebuild tree
    root = _build_huff_tree(freqs)

    # Bytes -> bitstring
    if not payload:
        return b""
    bitstring = "".join(f"{b:08b}" for b in payload)
    if pad_bits:
        bitstring = bitstring[:-pad_bits]

    # Decode
    out = bytearray()
    node = root
    for bit in bitstring:
        node = node.left if bit == "0" else node.right
        # leaf
        if node.sym is not None and node.left is None and node.right is None:
            out.append(node.sym)
            if len(out) == orig_len:
                break
            node = root

    return bytes(out)
