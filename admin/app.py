from flask import Flask, render_template, redirect, request, session, url_for
from functools import wraps
from db_config import get_db_connection

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Required for session handling

# Hardcoded admin credentials
ADMIN_EMAIL = "admin@stream.com"
ADMIN_PASSWORD = "admin123"

# ==========================
# Authentication Helpers
# ==========================
def login_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return view_func(*args, **kwargs)
    return wrapper

# ==========================
# Auth Routes
# ==========================
@app.route('/')
def home():
    if session.get('logged_in'):
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password'].strip()

        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            error = "Invalid email or password."

    return render_template('login.html', error=error)


@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

# ==========================
# Admin Dashboard + Routes
# ==========================
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('index.html')


@app.route('/topics')
@login_required
def view_topics():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM topics ORDER BY id DESC")
    topics = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('topics.html', topics=topics)


@app.route('/subscriptions')
@login_required
def view_subscriptions():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT us.id, us.user_name, t.topic_name, us.subscribed_at
        FROM user_subscriptions us
        JOIN topics t ON us.topic_id = t.id
        ORDER BY us.subscribed_at DESC
    """)
    subs = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('subscriptions.html', subs=subs)


# ==========================
# Topic Management Routes
# ==========================
@app.route('/approve/<int:topic_id>')
@login_required
def approve_topic(topic_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE topics SET status=%s, last_updated=NOW() WHERE id=%s", ('approved', topic_id))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('view_topics'))


@app.route('/reject/<int:topic_id>')
@login_required
def reject_topic(topic_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE topics SET status=%s, last_updated=NOW() WHERE id=%s", ('rejected', topic_id))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('view_topics'))


@app.route('/deactivate/<int:topic_id>')
@login_required
def deactivate_topic(topic_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE topics SET status=%s, last_updated=NOW() WHERE id=%s", ('inactive', topic_id))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('view_topics'))


@app.route('/reactivate/<int:topic_id>')
@login_required
def reactivate_topic(topic_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE topics SET status=%s, last_updated=NOW() WHERE id=%s", ('active', topic_id))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('view_topics'))


# ==========================
# Run App
# ==========================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
