"""TCP authentication server using Windows Winsock via ctypes."""
import ctypes
import json
import os
import sqlite3

try:
    from werkzeug.security import generate_password_hash, check_password_hash
except ImportError:
    import hashlib
    import hmac

    def generate_password_hash(password: str) -> str:
        salt = os.urandom(16).hex()
        key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000).hex()
        return f"pbkdf2:sha256:{salt}:{key}"

    def check_password_hash(p_hash: str, password: str) -> bool:
        if p_hash.startswith("pbkdf2:sha256:"):
            parts = p_hash.split(":")
            if len(parts) == 4:
                _, _, salt, key = parts
                test_key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000).hex()
                return hmac.compare_digest(key, test_key)
        return False

if os.name != "nt":
    raise OSError("This server requires Windows.")

DB_NAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dataBase.db")
HOST = "127.0.0.1"
PORT = 5000

ws = ctypes.WinDLL("Ws2_32.dll")
SOCKET = ctypes.c_size_t
INVALID_SOCKET = ctypes.c_size_t(-1).value

class SockAddrIn(ctypes.Structure):
    _fields_ = [
        ("sin_family", ctypes.c_ushort),
        ("sin_port", ctypes.c_ushort),
        ("sin_addr", ctypes.c_uint32),
        ("sin_zero", ctypes.c_ubyte * 8),
    ]

ws.WSAStartup.argtypes = [ctypes.c_ushort, ctypes.c_void_p]
ws.WSAStartup.restype = ctypes.c_int
ws.WSACleanup.restype = ctypes.c_int
ws.socket.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int]
ws.socket.restype = SOCKET
ws.bind.argtypes = [SOCKET, ctypes.POINTER(SockAddrIn), ctypes.c_int]
ws.listen.argtypes = [SOCKET, ctypes.c_int]
ws.accept.argtypes = [SOCKET, ctypes.c_void_p, ctypes.c_void_p]
ws.accept.restype = SOCKET
ws.recv.argtypes = [SOCKET, ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
ws.recv.restype = ctypes.c_int
ws.send.argtypes = [SOCKET, ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
ws.send.restype = ctypes.c_int
ws.closesocket.argtypes = [SOCKET]
ws.htons.argtypes = [ctypes.c_ushort]
ws.htons.restype = ctypes.c_ushort
ws.inet_addr.argtypes = [ctypes.c_char_p]
ws.inet_addr.restype = ctypes.c_uint32


def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        """)


def handle_request(data):
    action = data.get("action")
    username = data.get("username") or ""
    password = data.get("password") or ""

    if action not in ("login", "register"):
        return {"code": 400, "status": "error", "message": "Unknown action"}

    if not isinstance(username, str) or not isinstance(password, str):
        return {"code": 400, "status": "error", "message": "Invalid input"}

    username = username.strip()
    if not username or not password:
        return {"code": 400, "status": "error", "message": "Missing username or password"}

    try:
        with sqlite3.connect(DB_NAME) as conn:
            if action == "register":
                hashed = generate_password_hash(password)
                conn.execute(
                    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    (username, hashed)
                )
                print(f"[+] Registered: {username}")
                return {"code": 200, "status": "success", "message": "Account created successfully!"}

            row = conn.execute(
                "SELECT password_hash FROM users WHERE username = ?",
                (username,)
            ).fetchone()

        if row and check_password_hash(row[0], password):
            print(f"[+] Login successful: {username}")
            return {"code": 200, "status": "success", "message": "Login successful!"}

        return {"code": 401, "status": "error", "message": "Invalid username or password"}

    except sqlite3.IntegrityError:
        return {"code": 409, "status": "error", "message": "Username already exists"}
    except sqlite3.Error:
        return {"code": 500, "status": "error", "message": "Database error"}


def send_json(client, data):
    payload = (json.dumps(data) + "\n").encode("utf-8")
    sent = 0

    while sent < len(payload):
        chunk = payload[sent:]
        buffer = ctypes.create_string_buffer(chunk)
        result = ws.send(
            client,
            ctypes.cast(buffer, ctypes.c_void_p),
            len(chunk),
            0
        )
        if result <= 0:
            break
        sent += result


def start_server():
    # WSAStartup needs a valid memory buffer for WSADATA.
    wsa_data = ctypes.create_string_buffer(512)
    result = ws.WSAStartup(0x0202, ctypes.cast(wsa_data, ctypes.c_void_p))
    if result != 0:
        raise OSError(f"WSAStartup failed: {result}")

    server = None
    try:
        init_db()
        server = ws.socket(2, 1, 6)
        if server == INVALID_SOCKET:
            raise OSError("Could not create socket")

        address = SockAddrIn()
        address.sin_family = 2
        address.sin_port = ws.htons(PORT)
        address.sin_addr = ws.inet_addr(HOST.encode("ascii"))

        if ws.bind(server, ctypes.byref(address), ctypes.sizeof(address)) != 0:
            raise OSError("Bind failed: port may already be in use")

        if ws.listen(server, 5) != 0:
            raise OSError("Listen failed")

        print(f"[+] Server listening on {HOST}:{PORT}")

        while True:
            client = ws.accept(server, None, None)
            if client == INVALID_SOCKET:
                continue

            try:
                received_data = bytearray()

                while len(received_data) < 65536:
                    buffer = ctypes.create_string_buffer(4096)
                    count = ws.recv(client, ctypes.cast(buffer, ctypes.c_void_p), 4096, 0)
                    if count <= 0:
                        break

                    received_data.extend(buffer.raw[:count])
                    if b"\n" in received_data:
                        break

                if received_data:
                    request_line = bytes(received_data).split(b"\n", 1)[0]
                    request = json.loads(request_line.decode("utf-8"))

                    if isinstance(request, dict):
                        response = handle_request(request)
                    else:
                        response = {
                            "code": 400,
                            "status": "error",
                            "message": "Invalid request"
                        }

                    send_json(client, response)

            except (ValueError, UnicodeDecodeError):
                send_json(client, {
                    "code": 400,
                    "status": "error",
                    "message": "Invalid JSON"
                })
            finally:
                ws.closesocket(client)

    finally:
        if server is not None:
            ws.closesocket(server)
        ws.WSACleanup()


if __name__ == "__main__":
    try:
        start_server()
    except KeyboardInterrupt:
        print("\n[+] Server stopped")
    except OSError as error:
        print(f"[-] Server error: {error}")
