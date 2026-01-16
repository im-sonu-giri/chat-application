# Real-Time Chat Application (Django + WebSockets)

A **real-time chat application** developed using **Django**, **Django Channels**, and **WebSockets**, designed to demonstrate asynchronous backend development, real-time communication, and scalable system architecture.

This project focuses on **how modern messaging systems work internally**, including persistent connections, event-driven communication, and concurrent user handling.

---

## Project Overview

Traditional HTTP-based applications rely on request–response cycles, which are inefficient for real-time communication.  
This project solves that limitation by implementing **WebSocket-based bidirectional communication**, enabling instant message delivery without page refresh or polling.

The application is built using **ASGI architecture**, allowing Django to handle both HTTP and WebSocket protocols in a single backend system.

---

##  Objectives of the Project

- Understand **real-time communication concepts**
- Implement **WebSocket connections** using Django Channels
- Learn **asynchronous programming** in Django
- Build a scalable and maintainable chat backend
- Simulate features used in real-world messaging platforms

---

## Key Features

### 🔐 Authentication & User Management
- Secure user registration and login system
- Messages are associated with authenticated users
- Session-based access control

### Real-Time Messaging
- Instant message delivery using WebSockets
- Bi-directional communication between client and server
- No page reloads or API polling required

### ⚡ Asynchronous Backend
- Uses **AsyncWebsocketConsumer** for non-blocking operations
- Handles multiple concurrent users efficiently
- Improves performance compared to synchronous views

### Message Persistence
- Messages are stored in the database
- Chat history remains available after reconnecting
- Supports future analytics or moderation features

###  WebSocket Routing
- Dedicated WebSocket routing configuration
- Clean separation between HTTP routes and socket events
- Easy to extend for group or room-based chats

---

## Technology Stack

### Backend
- **Python**
- **Django**
- **Django Channels**
- **ASGI (Daphne)**

### Frontend
- **HTML**
- **CSS**
- **JavaScript**
- Native **WebSocket API**

### Database
- **PostgreSQL** 



---

## Installation & Setup

### Clone Repository
git clone https://github.com/im-sonu-giri/chat-application.git



### Create a Virtual Environment
python -m venv chatvenv
source chatvenv/bin/activate

### Install Dependencies
pip install -r requirements.txt
### create dotenv file 

### Apply Database Migrations
python manage.py migrate

### Run the Server
daphne -p 8000 chatsystem.asgi:application
npm run dev



