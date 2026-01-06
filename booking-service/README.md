# 📅 Booking Service

Service untuk manajemen Pemesanan Tiket & Pembayaran.

- **Port Aplikasi**: `8001` (External) / `8000` (Internal)
- **Database**: SQLite (`bookings.db`) - File lokal
- **Integrasi**: Menghubungi `Event Service` dan `Ticket Service`

---

## 🛠️ Cara Install & Run (Manual)

### 1. Setup Environment
Buka terminal di folder `booking-service`:
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Jalankan Aplikasi
```bash
python app/main.py
```
*Akses di: [http://localhost:8001/graphql](http://localhost:8001/graphql)*

---

## 📝 API Usage

### 1. Create Booking
Membuat pesanan baru. Status awal adalah `PENDING`.
*Membutuhkan `eventId` dan `ticketTypeId` yang valid.*
```graphql
mutation {
  createBooking(input: {
    eventId: "<EVENT_ID>",
    ticketTypeId: "<TICKET_ID>",
    quantity: 2
  }) {
    id
    status
    totalPrice
  }
}
```

### 2. Confirm Payment
Mensimulasikan pembayaran sukses. Mengubah status menjadi `PAID` dan mengurangi stok tiket di Ticket Service.
```graphql
mutation {
  confirmPayment(id: "<BOOKING_ID>") {
    id
    status
    ticketTypeId
  }
}
```

### 3. Cancel Booking
Membatalkan pesanan.
```graphql
mutation {
  cancelBooking(id: "<BOOKING_ID>") {
    id
    status
  }
}
```

### 4. Get Booking Detail
```graphql
query {
  booking(id: "<BOOKING_ID>") {
    id
    status
    totalPrice
    ticketTypeId
    userId
  }
}
```

### 5. Get My Bookings
Melihat semua pesanan user yang sedang login.
```graphql
query {
  bookingsByUser(userId: "<USER_ID>") {
    id
    eventId
    status
    totalPrice
  }
}
```
