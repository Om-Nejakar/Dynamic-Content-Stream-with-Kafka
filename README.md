# 🚀 Project 2: Dynamic Content Stream with Kafka  

## 🧭 Overview  

In modern data-driven systems, content streams are **dynamic** — new data topics are created, evolve, and disappear continuously.  
Traditional Kafka setups often require **manual topic creation and configuration**, limiting scalability and responsiveness.  

This project simulates a **dynamic Kafka-based content streaming system** that automatically manages topics and subscriptions in real time.  
It integrates a **Kafka Broker**, a **multi-threaded Producer**, **dynamic Consumers**, and an **Admin + MySQL Control Plane** for topic lifecycle management.  

---

## 🎯 Objective  

To design a **real-time, adaptive content streaming platform** that integrates:  
- ✅ A **Kafka-based message broker system**  
- ✅ A **MySQL metadata registry** for topics and user subscriptions  
- ✅ **Dynamic topic creation** and management using the **Kafka Admin API**  
- ✅ **Multi-threaded producer** design for real-time ingestion  
- ✅ A **Flask-based Admin Control Plane & Web Interface**  

---

## 🏗️ System Architecture  
<img width="1348" height="801" alt="image" src="https://github.com/user-attachments/assets/714e36f6-3827-48f8-9c59-44f7b6c4d059" />



---

## ⚙️ Technology Stack  

| Component | Technology Used |
|------------|----------------|
| Programming Language | Python 3 |
| Message Broker | Apache Kafka |
| Database | MySQL |
| Web Framework | Flask |
| APIs / Libraries | kafka-python, mysql-connector-python, threading |
| Architecture | Multi-node distributed Kafka system |

---

## 🧩 Components and Responsibilities  

| Node | Component | Responsibilities |
|------|------------|------------------|
| **Node 1** | Producer | Multi-threaded producer with Publisher, Input Listener, and Topic Watcher threads. |
| **Node 2** | Kafka Broker | Central message hub that manages all topics and routing. |
| **Node 3** | Consumers | Dynamically subscribe/unsubscribe from approved topics and process messages. |
| **Node 4** | Admin & MySQL | Control plane for topic metadata, approval, and user-topic mapping. |

---

## 🛠️ Setup Instructions  

### 🧱 Prerequisites  

Install:
- Python 3.x  
- Apache Kafka  
- MySQL  
- pip and virtualenv  

---

### 1️⃣ Clone the Repository  

```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
```

### 2️⃣ Configure MySQL Database
```
mysql -u root -p
```
### 3️⃣ Start Kafka & Zookeeper (Node 2 – Broker)
```
cd /opt/kafka
bin/zookeeper-server-start.sh config/zookeeper.properties
bin/kafka-server-start.sh config/server.properties
```
config/server.properties : 
```
delete.topic.enable=true
auto.create.topics.enable=false
listeners=PLAINTEXT://192.168.196.62:9092
```
Describe topic : 
```
bin/kafka-topics.sh --describe --topic test-topic --bootstrap-server 192.168.196.62:9092
```
Listing Kafka Topics : 
```
/opt/kafka/bin/kafka-topics.sh --list --bootstrap-server 192.168.196.62:9092
```

### 4️⃣ Run the Admin Flask API (Node 4 – Control Plane)
```
cd admin
pip install -r requirements.txt
python3 app.py
```

### 5️⃣ Run the Producer (Node 1)
```
cd producer
source venv/bin/activate
python3 producer_main.py

```
### 6️⃣ Run the Consumer (Node 3)
```
cd consumer
source venv/bin/activate
pip3  install -r requirements.txt
python3 consumer_node.py
```

### 💡 Topic Lifecycle
| Step | Status     | Description                                 |
| ---- | ---------- | ------------------------------------------- |
| 1️⃣  | `pending`  | Topic requested by producer or user.        |
| 2️⃣  | `approved` | Admin approves in Flask API.                |
| 3️⃣  | `active`   | Producer creates topic via Kafka Admin API. |
| 4️⃣  | `inactive` | Admin deactivates; consumers unsubscribe.   |



---

## ✅ Flask Admin Backend Summary

### 🔐 Authentication & Session Handling

* Uses hardcoded admin credentials:
  `admin@stream.com` / `admin123`
* Session variable `logged_in=True` determines admin access
* `login_required` decorator protects all admin-only routes
* Authentication routes included:

  * `/login`
  * `/logout`
  * `/dashboard`

---

### 🖥️ Admin Views (Rendered HTML Pages)

| Route            | Method   | Description                                                  |
| ---------------- | -------- | ------------------------------------------------------------ |
| `/`              | GET      | Redirects to dashboard if logged in, otherwise to login page |
| `/login`         | GET/POST | Admin login page; validates hardcoded credentials            |
| `/logout`        | GET      | Logs out admin by clearing session                           |
| `/dashboard`     | GET      | Main admin landing page                                      |
| `/topics`        | GET      | Fetches and displays all topics with status & details        |
| `/subscriptions` | GET      | Lists all user subscriptions with joined topic names         |

---

### ✅ Topic Management Operations

| Route                    | Method | Description                                           |
| ------------------------ | ------ | ----------------------------------------------------- |
| `/approve/<topic_id>`    | GET    | Sets topic status to `approved` and updates timestamp |
| `/reject/<topic_id>`     | GET    | Sets topic status to `rejected`                       |
| `/deactivate/<topic_id>` | GET    | Marks topic as `inactive`                             |
| `/reactivate/<topic_id>` | GET    | Marks topic as `active`                               |

> All actions update the database directly and redirect back to `/topics`.

---

### 🗄️ Database Access

* Uses `get_db_connection()` helper for MySQL connections
* Dictionary-style cursor via `cursor(dictionary=True)`
* All cursor/connection instances are properly closed
* Performs SQL read/update queries against:

  * `topics`
  * `user_subscriptions`

---




