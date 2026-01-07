# EventHUB Microservices

EventHUB adalah sistem manajemen event terdistribusi yang terdiri dari beberapa microservices yang dikoordinasikan melalui sebuah API Gateway pusat.

## Arsitektur

Sistem ini terdiri dari beberapa layanan khusus:
- **API Gateway**: Titik masuk utama untuk semua permintaan, mengarahkan traffic ke layanan yang sesuai di belakangnya.
- **User Service**: Menangani pendaftaran pengguna, autentikasi (JWT), dan profil.
- **Event Service**: Mengelola pembuatan event, daftar event, detail event, dan integrasi dengan SpaceMaster.
- **Ticket Service**: Mengelola tipe tiket, ketersediaan kuota, dan harga.
- **Booking Service**: Mengatur proses pemesanan tiket dan pembayaran, terintegrasi dengan Event dan Ticket service.

## Teknologi Utama

- **Bahasa**: Python 3.9+
- **Framework**: FastAPI (Gateway/Booking), Flask (Event/Ticket/User)
- **Komunikasi**: GraphQL (Event/Ticket/User/Booking), REST (Gateway)
- **Database**: MySQL (Event/Ticket/User), SQLite (Booking - Async)
- **Orkestrasi**: Docker & Docker Compose

---

## Panduan Penggunaan (Quick Start)

### Prasyarat
- Pastikan **Docker** dan **Docker Compose** sudah terinstal di komputer Anda.

### Langkah-langkah Menjalankan
1. **Clone Repositori**:
   ```bash
   cd EventHUB
   ```

2. **Jalankan dengan Docker Compose**:
   Gunakan perintah berikut untuk membangun image dan menjalankan semua container sekaligus:
   ```bash
   docker compose up --build -d
   ```
   *Opsi `-d` menjalankan layanan di latar belakang (detached mode).*

3. **Verifikasi Layanan**:
   Pastikan semua container berjalan dengan status `Up`:
   ```bash
   docker compose ps
   ```

---

## Cara Mengakses Layanan (Gateway)

Semua permintaan disarankan melalui **API Gateway** yang berjalan di port **`8090`**.

- **Gateway Health Check**: `http://localhost:8090/health`
- **User GraphQL**: [http://localhost:8090/user/graphql](http://localhost:8090/user/graphql)
- **Event GraphQL**: [http://localhost:8090/event/graphql](http://localhost:8090/event/graphql)
- **Ticket GraphQL**: [http://localhost:8090/ticket/graphql](http://localhost:8090/ticket/graphql)
- **Booking GraphQL**: [http://localhost:8090/booking/graphql](http://localhost:8090/booking/graphql)

---

## Referensi API (GraphQL)

### 1. User Service
Endpoint: `/user/graphql`

| Tipe | Nama Operasi | Deskripsi |
|------|-------------|-----------|
| **Query** | `users` | Mengambil daftar semua user |
| **Query** | `user(id: ID!)` | Mengambil detail user (Admin only) |
| **Query** | `me(token: String!)` | Mengambil profil sendiri berdasarkan token |
| **Mutation** | `createUser` | Mendaftar user baru |
| **Mutation** | `login` | Masuk dan mendapatkan Access Token |
| **Mutation** | `updateUser` | Mengubah profil user sendiri |
| **Mutation** | `deleteUser` | Menghapus user (Admin only) |

#### Contoh: Update Profile
```graphql
mutation {
  updateUser(id: "USER_ID", name: "New Name", address: "New Address") {
    user {
      id
      name
      address
    }
  }
}
```

### 2. Event Service
Endpoint: `/event/graphql`

| Tipe | Nama Operasi | Deskripsi |
|------|-------------|-----------|
| **Query** | `events` | Mengambil semua event |
| **Query** | `event(id: ID!)` | Mengambil detail satu event |
| **Query** | `eventsByVenue(venueId: Int!)` | Mencari event berdasarkan venue |
| **Mutation** | `createEvent` | Membuat event baru (Admin, Validasi SpaceMaster) |
| **Mutation** | `updateEvent` | Mengubah detail atau jadwal event |

| **Mutation** | `blockSchedule` | Mencegah booking ruangan secara manual (Sync SpaceMaster) |

#### Contoh: Create Event
```graphql
mutation {
  createEvent(
    title: "Konser Akbar"
    description: "Festival Musik 2026"
    venueId: 1
    roomId: 101
    startTime: "2026-12-31T19:00:00"
    endTime: "2026-12-31T23:59:00"
  ) {
    event {
      id
      title
      status
    }
  }
}
```

### 3. Ticket Service
Endpoint: `/ticket/graphql`

| Tipe | Nama Operasi | Deskripsi |
|------|-------------|-----------|
| **Query** | `ticketTypesByEvent(eventId: ID!)` | Melihat tipe tiket untuk event tertentu |
| **Query** | `ticketType(id: ID!)` | Melihat detail satu tipe tiket |
| **Mutation** | `createTicketType` | Menambahkan tipe tiket ke event (Admin) |
| **Mutation** | `updateTicketType` | Mengubah harga atau kuota tiket |
| **Mutation** | `updateTicketSold` | Mengupdate jumlah terjual (Internal use) |
| **Mutation** | `deleteTicketType` | Menghapus tipe tiket |

#### Contoh: Create Ticket Type
```graphql
mutation {
  createTicketType(input: {
    eventId: "EVENT_ID"
    name: REGULAR
    price: 150000
    quota: 100
  }) {
    id
    name
    price
    quota
  }
}
```

### 4. Booking Service
Endpoint: `/booking/graphql`

| Tipe | Nama Operasi | Deskripsi |
|------|-------------|-----------|
| **Query** | `booking(id: ID!)` | Melihat detail booking |
| **Query** | `bookingsByUser(userId: ID!)` | Melihat history booking user |
| **Mutation** | `createBooking` | Membuat pesanan baru (Status: PENDING) |
| **Mutation** | `confirmPayment` | Konfirmasi pembayaran (Status: PAID) |
| **Mutation** | `cancelBooking` | Membatalkan pesanan (Admin Only, Returns Success/Message) |

#### Contoh: Alur Pemesanan Lengkap
**Langkah 1: Create Booking**
```graphql
mutation {
  createBooking(input: {
    eventId: "EVENT_ID"
    ticketTypeId: "TICKET_ID"
    quantity: 2
  }) {
    id
    totalPrice
    status
  }
}
```

**Langkah 2: Confirm Payment**
```graphql
mutation {
  confirmPayment(id: "BOOKING_ID_DARI_LANGKAH_1") {
    id
    status
    ticketTypeId
  }
}
```

---

## Akses Pengembangan (Direct Access)

- **User Service**: `http://localhost:8004`
- **Ticket Service**: `http://localhost:8003`
- **Event Service**: `http://localhost:8102`
- **Booking Service**: `http://localhost:8001`

---

