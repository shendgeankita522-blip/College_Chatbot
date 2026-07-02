import sqlite3
import os

DB_FILE = os.path.join(os.path.dirname(__file__), "chatbot.db")

def get_connection():
    return sqlite3.connect(DB_FILE)

# ---------------- INIT DB ----------------
def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS faqs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        intent TEXT,
        question TEXT,
        answer TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        message TEXT,
        is_bot INTEGER
    )
    """)

    # USERS
    c.execute("SELECT * FROM users WHERE username='admin'")
    if not c.fetchone():
        c.execute("INSERT INTO users (username,password,role) VALUES ('admin','admin123','admin')")

    c.execute("SELECT * FROM users WHERE username='guest'")
    if not c.fetchone():
        c.execute("INSERT INTO users (username,password,role) VALUES ('guest','guest','user')")

    # FAQS
    c.execute("SELECT COUNT(*) FROM faqs")
    if c.fetchone()[0] == 0:
        faqs = [
    ("fees","what is fees","Fees is 50000 per year"),
    ("fees","how much is college fees","Fees is 50000 per year"),

    ("exam","when is exam","Exams start from June"),
    ("exam","exam date","Exams start from June"),

    ("hostel","is hostel available","Yes hostel is available"),
    ("hostel","hostel facility","Yes hostel is available"),

    ("admission","admission process","Apply online or visit office"),
    ("admission","how to take admission","Apply online or visit office"),

    ("timing","college timing","9 AM to 4 PM"),
    ("timing","what are college hours","9 AM to 4 PM"),

    ("library","is library available","Library is open 8 AM to 6 PM"),
    ("library","library timing","Library is open 8 AM to 6 PM"),

    ("placement","placement support","Placement support available"),

    ("scholarship","scholarship available","Scholarships available"),

    ("contact","college contact","Contact college office"),

    ("attendance","attendance rule","75% attendance required"),

    ("canteen","canteen available","Canteen available"),

    ("bus","bus facility","Bus facility available"),

    ("sports","sports facility","Sports available"),

    ("wifi","wifi available","WiFi available"),

    ("results","results","Results announced after exams"),

    ("internship","internship","Internship available")
]
        for f in faqs:
            c.execute("INSERT INTO faqs (intent,question,answer) VALUES (?,?,?)", f)

    conn.commit()
    conn.close()

# ---------------- LOGIN ----------------
def verify_user(u,p):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id,role FROM users WHERE username=? AND password=?", (u,p))
    user = c.fetchone()
    conn.close()
    return user

# ---------------- FAQ ----------------
def get_all_faqs():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT intent,question,answer FROM faqs")
    data = c.fetchall()
    conn.close()
    return data

# ---------------- CHAT ----------------
def log_chat(uid,msg,is_bot):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO chat_history (user_id,message,is_bot) VALUES (?,?,?)",
              (uid,msg,is_bot))
    conn.commit()
    conn.close()

def get_chat_history(uid):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT message,is_bot FROM chat_history WHERE user_id=?", (uid,))
    data = c.fetchall()
    conn.close()
    return data

def clear_chat_history(uid):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM chat_history WHERE user_id=?", (uid,))
    conn.commit()
    conn.close()

# ---------------- BOT (FIXED SMART MATCHING) ----------------
def bot_response(msg):
    faqs = get_all_faqs()
    msg = msg.lower().strip()

    best_answer = None
    best_score = 0

    msg_words = set(msg.split())

    for intent, q, a in faqs:
        q_words = set(q.lower().split())

        # keyword match
        common = msg_words.intersection(q_words)
        score = len(common)

        # intent boost
        if intent.lower() in msg:
            score += 2

        # exact phrase boost
        if q.lower() in msg:
            score += 3

        if score > best_score:
            best_score = score
            best_answer = a

    if best_score > 0:
        return best_answer

    return "Sorry, I couldn't understand. Try again with different words."

# ---------------- RUN DB ----------------
if __name__ == "__main__":
    init_db()
    print("Database created successfully ✔")