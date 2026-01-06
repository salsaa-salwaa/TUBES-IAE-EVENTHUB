# 📅 Event Service

Service untuk manajemen Data Event & Integrasi dengan SpaceMaster.

- **Port Aplikasi**: `8102` (External) / `4001` (Internal)
- **Port Database**: `3307` (Docker) / `3306` (Local)
- **Database Name**: `event_db`

---

## 🛠️ Cara Install & Run (Manual)

### 1. Buat Virtual Environment
Buka terminal di folder `event-service`:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Konfigurasi .env
Pastikan environment variables sesuai:
```bash
export DATABASE_URL="mysql+pymysql://root:root@localhost:3307/event_db"
export JWT_SECRET_KEY="dev-secret-123"
```

### 4. Jalankan Aplikasi
```bash
python run.py
```
*Akses di: [http://localhost:8102/graphql](http://localhost:8102/graphql)*

---

## 📝 API Usage

### 1. Read All Events
```graphql
query {
  events {
    id
    title
    status
    venueCapacity
    startTime
    endTime
  }
}
```

### 2. Read One Event
```graphql
query {
  event(id: "<EVENT_ID>") {
    id
    title
    description
    status
    venueId
    roomId
  }
}
```

### 3. Create Event (Admin Only)
Membuat event baru dengan validasi ruangan ke SpaceMaster.
```graphql
mutation {
  createEvent(
    title: "Tech Conference 2026"
    description: "Future of AI"
    venueId: 1
    roomId: 101
    startTime: "2026-10-10T09:00:00"
    endTime: "2026-10-10T17:00:00"
  ) {
    event {
      id
      title
      status
    }
  }
}
```

### 4. Update Event (Admin Only)
Mengubah detail event atau jadwal (akan re-validasi SpaceMaster).
```graphql
mutation {
  updateEvent(
    id: "<EVENT_ID>"
    title: "Updated Title"
    status: "ONGOING"
  ) {
    event {
      id
      title
      status
    }
  }
}
```

### 5. Delete Event (Admin Only)
Menghapus event (hanya jika status bukan ONGOING).
```graphql
mutation {
  deleteEvent(id: "<EVENT_ID>") {
    success
  }
}
```

### 6. Block Schedule (Manual Sync)
Melakukan blocking ruangan manual ke SpaceMaster tanpa membuat Event lengkap.
```graphql
mutation {
  blockSchedule(input: {
    roomId: 101
    startTime: "2026-12-01T08:00:00"
    endTime: "2026-12-01T12:00:00"
  }) {
    success
    message
  }
}
```
