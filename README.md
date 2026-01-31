AttendSure

# AttendSure

A web-based attendance system with location verification and low manual effort.

## Features
- Teacher-controlled attendance sessions
- Geo-fencing (latitude, longitude, radius)
- Attendance code verification
- Device/session fingerprint evidence
- Role-based access (teacher/student)

## Tech Stack
- Backend: Flask, SQLAlchemy, MySQL
- Frontend: React (CRA)
- Auth: Flask sessions (cookies)

## Setup Instructions

### Backend
1. Create virtual environment
2. Install requirements
3. Set .env (DATABASE_URL, SECRET_KEY)
4. Run migrations
5. Start Flask server

### Frontend
1. npm install
2. npm start

## Demo Flow
Teacher:
- Login
- Create class
- Start attendance
- View records

Student:
- Login
- Enroll
- Submit attendance

## Security & Design Notes
- No biometric data used
- Evidence-based attendance verification
- Tradeoffs explained



# AttendSure ✅ (Full-Stack Attendance System)

AttendSure is a web-based attendance system that reduces manual effort and disputes by combining:

- Teacher-controlled attendance sessions
- Location verification using a geo-fence (lat/long + radius)
- Attendance code validation
- Evidence logging (device signature + IP prefix) for anomaly/dispute support  
  *(not biometric — browsers cannot access raw biometrics)*

Repo structure: `backend/`, `frontend/`, `docs/` :contentReference[oaicite:1]{index=1}

---

## Tech Stack

### Backend
- Flask
- SQLAlchemy ORM
- MySQL
- Flask-Migrate (migrations)
- Flask session cookies (auth)
- Werkzeug password hashing

### Frontend
- React (Create React App)
- Mantine UI (`@mantine/core`, `@mantine/hooks`)
- React Router DOM

---

## Features

### Teacher
- Sign up / login
- Create class (with geo-fence)
- Start attendance session (code + time window)
- End attendance session
- View attendance records for a session

### Student
- Sign up / login
- Enroll into class
- View active session for a class
- Submit attendance (code + GPS location + evidence fields)

---

## Database Schema

See: `docs/database-schema.md`

Tables:
- `users`
- `classes`
- `enrollments`
- `attendance_sessions`
- `attendance_records`

---

## Setup Instructions

### Prerequisites
- Python 3.x
- Node.js + npm
- MySQL running locally or remotely

---

## Clone the repository
```
git clone https://github.com/Anshulsharma24092004/AttendSure.git
cd AttendSure
```
---

## Backend Setup (Flask)

### 1) Create & activate virtual environment
From project root:

```
cd backend
python -m venv venv
```

# Windows (PowerShell):

```
venv\Scripts\Activate.ps1
```

# Windows (CMD):

```
venv\Scripts\activate
```

### 2) Install backend dependencies

```
pip install -r requirements.txt
```

### 3) Create .env in backend/

Example:

DATABASE_URL=mysql+pymysql://USER:PASSWORD@localhost:3306/attendsure
SECRET_KEY=your_secret_key_here


### 4) Run migrations

```
flask db upgrade
```

### 5) Run backend server

```
flask run
```


# Backend runs on:

http://127.0.0.1:5000

## Frontend Setup (React)

### 1) Install frontend dependencies

From project root:

```
cd frontend
npm install
```

2) Start frontend

```
npm start
````

# Frontend runs on:

http://localhost:3000

# Proxy / cookies

Frontend uses CRA proxy to talk to backend (so requests can be:
fetch("/auth/login"))

# Cookies are enabled using:

```
credentials: "include"
```

## Demo Flow (Recommended)
### Teacher

- `Sign up teacher → /signup (role: teacher)`

- `Login → /login`

- `Create class (name + lat + long + radius)`

- `Start attendance (code + start/end)`

- `View records (initially 0)`

- `End attendance`

### Student

- `Sign up student → /signup (role: student)`

- `Login → /login`

- `Enroll into class (enter class_id)`

- `Select class → check active session`

- `Enter code → capture GPS → submit attendance`

### Verify

- `Back in teacher dashboard → View records → shows student submission.`