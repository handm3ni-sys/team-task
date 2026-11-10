# Team Task & Note List — Cloud-Native Fullstack App + CI/CD

Tugas Kelompok UTS Cloud Computing (Panduan Ujian Chunin) — Telkom University

## Anggota Kelompok

| No | Nama | NIM |
|---|---|---|
| 1 | Liony Syafitri | 101012330035 |
| 2 | Amelya Fazrin | 101012330146 |
| 3 | Muhammad Hanif Rafsanjani | 101012330044 |
| 4 | Ziya Bahjatulloh | 101012300364 |

## Studi Kasus

**No. 6 — Papan Catatan Tugas Kelompok (Team Task & Note List)**
Aplikasi todo list sederhana untuk membagi tugas antar-anggota tim.

| Method | Endpoint | Fungsi |
|---|---|---|
| GET | `/tasks` | Menampilkan daftar tugas |
| POST | `/tasks` | Menambah tugas baru (`title`, `assignee`, `note`) |
| DELETE | `/tasks?index=X` | Menghapus / menyelesaikan tugas |

Error handling: `400` (JSON/field tidak valid), `404` (index/endpoint tidak ditemukan).

## Diagram Arsitektur

```
 Developer ──git push──> GitHub ──webhook (ngrok)──> Jenkins
                                                        │ deploy
                                                        ▼
 ┌──────────────────── app-net (custom bridge) ────────────────────┐
 │                                                                  │
 │  Browser ──:8081──> frontend (Nginx) ──/api/──> backend (app.py) │
 │                        │                          │              │
 │                  Bind Mount ./frontend     Named Volume          │
 │                                            team-task-data        │
 │                                            (tasks.json)          │
 └──────────────────────────────────────────────────────────────────┘
```

- **Frontend**: HTML + Vanilla JS (`fetch()`), dijalankan di Nginx dengan **Bind Mount** ke folder `frontend/` sehingga perubahan UI langsung terlihat tanpa rebuild image.
- **Backend**: Python `http.server` tanpa framework, data disimpan di `tasks.json` dalam **Named Volume** `team-task-data`.
- **Network**: kedua kontainer berada di **Custom Bridge Network** `app-net`; Nginx meneruskan `/api/` ke `http://backend:5000/` lewat DNS Docker (service name).

## Struktur Repositori

```
team-task/
├── backend/
│   ├── app.py
│   └── Dockerfile
├── frontend/
│   ├── index.html
│   └── nginx.conf
├── docker-compose.yml
├── Jenkinsfile
└── README.md
```

## Instalasi Lokal

Prasyarat: Docker Desktop & Git.

```bash
git clone https://github.com/handm3ni-sys/team-task.git
cd team-task
docker compose -p team-task up -d --build
```

Buka **http://localhost:8081**

> Catatan: path Bind Mount di `docker-compose.yml` memakai format Docker Desktop
> (`/run/desktop/mnt/host/c/...`) agar bisa dipakai dari dalam kontainer Jenkins.
> Sesuaikan dengan lokasi folder di laptop masing-masing.

### Uji Data Immunity (Named Volume)

```bash
docker rm -f task-backend
docker compose -p team-task up -d
```

Data tugas tetap ada karena tersimpan di Named Volume `team-task-data`.

## Setup Jenkins CI/CD

1. Jalankan Jenkins sebagai kontainer (akses Docker host lewat socket):
   ```bash
   docker run -d --name jenkins -p 9090:8080 -u root \
     -v jenkins_home:/var/jenkins_home \
     -v //var/run/docker.sock:/var/run/docker.sock \
     jenkins/jenkins:lts
   ```
2. Pasang Docker CLI & Compose di dalam kontainer Jenkins:
   ```bash
   docker exec jenkins bash -c "curl -fsSL https://get.docker.com | sh"
   ```
3. Buka **http://localhost:9090**, selesaikan setup, lalu buat **Pipeline** baru:
   - Trigger: centang **GitHub hook trigger for GITScm polling**
   - Definition: **Pipeline script from SCM** → Git → URL repo ini → branch `*/main`
4. Ekspos Jenkins ke internet: `ngrok http 9090`
5. Di GitHub repo → **Settings → Webhooks → Add webhook**:
   - Payload URL: `https://<url-ngrok>/github-webhook/`
   - Content type: `application/json`

### Stage Pipeline (Jenkinsfile)

| Stage | Fungsi |
|---|---|
| Checkout | Mengambil kode terbaru dari GitHub |
| Syntax Check | Memastikan `app.py` bebas syntax error |
| Build Image | `docker compose build` |
| Automated Deployment | Menghapus kontainer lama lalu `docker compose up -d` |
| Health Check | Memanggil `GET /tasks` dari dalam jaringan `app-net` |

Setiap `git push` ke branch `main` otomatis memicu pipeline lewat webhook.

## Video 

