# 👤 User Service

Service untuk Autentikasi (JWT) & Manajemen User.

- **Port Aplikasi**: `8004` (External) / `3001` (Internal)
- **Port Database**: `3309` (Docker) / `3306` (Local)
- **Database Name**: `user_db`

---

## 🛠️ Cara Install & Run (Manual)

### 1. Setup
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run
```bash
python app.py
```
*Akses di: [http://localhost:8004/graphql](http://localhost:8004/graphql)*

---

## 📝 API Usage

### 1. Register
Mendaftar pengguna baru.
```graphql
mutation {
  createUser(name: "John Doe", email: "john@test.com", password: "password123") {
    user {
      id
      email
      name
    }
  }
}
```

### 2. Login
Mendapatkan Access Token untuk autentikasi.
```graphql
mutation {
  login(email: "john@test.com", password: "password123") {
    accessToken
    user {
      id
      role
    }
  }
}
```

### 3. Get My Profile
Melihat data diri sendiri (Memerlukan Token).
```graphql
query {
  me(token: "<ACCESS_TOKEN>") {
    id
    name
    email
    role
  }
}
```

### 4. Update User
Mengubah data profil (Hanya pemilik akun atau Admin).
```graphql
mutation {
  updateUser(id: "<USER_ID>", name: "New Name", address: "New Address") {
    user {
      id
      name
      address
    }
  }
}
```

### 5. Get All Users (Admin Only)
```graphql
query {
  users {
    id
    name
    email
    role
  }
}
```

### 6. Delete User (Admin Only)
```graphql
mutation {
  deleteUser(id: "<USER_ID>") {
    ok
  }
}
```
