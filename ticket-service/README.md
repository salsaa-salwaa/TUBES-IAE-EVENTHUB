# 🎫 Ticket Service

Service untuk manajemen Jenis Tiket & Kuota.

- **Port Aplikasi**: `8003` (External) / `4002` (Internal)
- **Port Database**: `3308` (Docker) / `3306` (Local)
- **Database Name**: `ticket_db`

---

## 🛠️ Cara Install & Run (Manual)

### 1. Buat Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Jalankan Aplikasi
```bash
python app.py
```
*Akses di: [http://localhost:8003/graphql](http://localhost:8003/graphql)*

---

## 📝 API Usage

### 1. Create Ticket Type (Admin)
Menambahkan tipe tiket baru ke sebuah event.
```graphql
mutation {
  createTicketType(input: {
    eventId: "<EVENT_ID>",
    name: REGULAR,
    price: 50000,
    quota: 100
  }) {
    id
    name
    price
    quota
  }
}
```

### 2. Get Tickets by Event
Melihat semua tipe tiket yang tersedia di event tertentu.
```graphql
query {
  ticketTypesByEvent(eventId: "<EVENT_ID>") {
    id
    name
    price
    quota
    sold
    status
  }
}
```

### 3. Get Ticket Detail
```graphql
query {
  ticketType(id: "<TICKET_ID>") {
    id
    name
    eventId
    price
    quota
  }
}
```

### 4. Update Ticket Type (Admin)
Mengupdate harga atau kuota tiket.
```graphql
mutation {
  updateTicketType(id: "<TICKET_ID>", input: {
    price: 60000,
    quota: 150
  }) {
    id
    price
    quota
  }
}
```

### 5. Delete Ticket Type (Admin)
Menghapus tipe tiket (Hanya jika belum ada yang terjual).
```graphql
mutation {
  deleteTicketType(id: "<TICKET_ID>") {
    ok
  }
}
```
