# app.py — Backend REST API "Team Task & Note List"
# Hanya pakai library bawaan Python, tanpa Flask/Django
import json
import os
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

# Folder data, nanti di-mount ke Named Volume "team-task-data"
DATA_DIR = os.environ.get("DATA_DIR", "/var/lib/backend_data")
DATA_FILE = os.path.join(DATA_DIR, "tasks.json")
PORT = 5000


def load_tasks():
    """Baca daftar tugas dari tasks.json (kalau belum ada, kembalikan list kosong)."""
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def save_tasks(tasks):
    """Simpan daftar tugas ke tasks.json."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)


class TaskHandler(BaseHTTPRequestHandler):
    def send_json(self, status, data):
        """Kirim respon JSON + header CORS (biar bisa dites dari browser)."""
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        """Preflight CORS dari browser."""
        self.send_json(204, {})

    def do_GET(self):
        """GET /tasks -> tampilkan semua tugas."""
        if urlparse(self.path).path != "/tasks":
            return self.send_json(404, {"error": "Endpoint tidak ditemukan"})
        self.send_json(200, load_tasks())

    def do_POST(self):
        """POST /tasks -> tambah tugas baru. Body: {"title","assignee","note"}"""
        if urlparse(self.path).path != "/tasks":
            return self.send_json(404, {"error": "Endpoint tidak ditemukan"})
        length = int(self.headers.get("Content-Length", 0))
        try:
            data = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            return self.send_json(400, {"error": "Body harus JSON yang valid"})
        # Validasi: title dan assignee wajib diisi
        if not isinstance(data, dict) or not data.get("title") or not data.get("assignee"):
            return self.send_json(400, {"error": "Field 'title' dan 'assignee' wajib diisi"})
        task = {
            "title": str(data["title"]),
            "assignee": str(data["assignee"]),
            "note": str(data.get("note", "")),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        tasks = load_tasks()
        tasks.append(task)
        save_tasks(tasks)
        self.send_json(201, {"message": "Tugas ditambahkan", "task": task})

    def do_DELETE(self):
        """DELETE /tasks?index=X -> hapus / selesaikan tugas ke-X."""
        url = urlparse(self.path)
        if url.path != "/tasks":
            return self.send_json(404, {"error": "Endpoint tidak ditemukan"})
        index = parse_qs(url.query).get("index", [None])[0]
        if index is None or not index.isdigit():
            return self.send_json(400, {"error": "Parameter 'index' wajib berupa angka"})
        tasks = load_tasks()
        i = int(index)
        if i >= len(tasks):
            return self.send_json(404, {"error": f"Tugas index {i} tidak ditemukan"})
        removed = tasks.pop(i)
        save_tasks(tasks)
        self.send_json(200, {"message": "Tugas dihapus", "task": removed})


if __name__ == "__main__":
    print(f"Backend jalan di port {PORT}, data di {DATA_FILE}")
    HTTPServer(("0.0.0.0", PORT), TaskHandler).serve_forever()