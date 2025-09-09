from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
app = Flask(__name__)
app.jinja_env.globals.update(session=session)
try:
    import openai
except Exception:
    openai = None

from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "change_this_secret_in_prod")

# Konfigürasyon
DB_PATH = os.getenv("DB_PATH", "study_assistant.db")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

if openai and OPENAI_KEY:
    openai.api_key = OPENAI_KEY

# ----------------------
# Database helpers
# ----------------------
def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        summary TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        week_plan TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    
    conn.commit()
    conn.close()

# ----------------------
# AI helpers (with fallback)
# ----------------------
def ai_summarize(text):
    """Try OpenAI. If not available, use a simple heuristic fallback."""
    if openai and getattr(openai, 'api_key', None):
        try:
            resp = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes study notes concisely."},
                    {"role": "user", "content": f"Lütfen bu notu 2-3 cümleyle Türkçe olarak özetle:\n\n{text}"}
                ],
                max_tokens=150,
                temperature=0.2
            )
            return resp["choices"][0]["message"]["content"].strip()
        except Exception as e:
            return f"Özet oluşturulamadı (AI hatası): {e}"
    
    # Simple fallback: take first 2 sentences
    parts = [p.strip() for p in text.replace('\n', ' ').split('.') if p.strip()]
    return ('. '.join(parts[:2]) + ('.' if parts else ''))

def ai_generate_plan(details):
    """Generate study plan using AI or fallback"""
    if openai and getattr(openai, 'api_key', None):
        try:
            prompt = (
                "Haftanın 7 günü için, kullanıcının haftada 3 gün stajı olacak şekilde\n"
                "ders çalışabileceği, kısa ve uygulanabilir bir çalışma planı hazırla.\n"
                f"Kullanıcının verdiği detaylar: {details}\n"
                "Her günü ayrı satırda, Pazartesi'den Pazar'a kadar listele."
            )
            
            resp = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Sen çalışma planı hazırlayan yardımcı bir asistansın."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.3
            )
            return resp["choices"][0]["message"]["content"].strip()
        except Exception as e:
            return f"Plan oluşturulamadı (AI hatası): {e}"
    
    # Fallback plan
    return """PAZARTESİ: Staj günü - Akşam hafif tekrar (1 saat)
SALI: Yoğun çalışma günü (3-4 saat) - Ana konulara odaklan
ÇARŞAMBA: Staj günü - Akşam problem çözme (1-2 saat)
PERŞEMBE: Orta tempolu çalışma (2-3 saat) - Eksik konuları tamamla
CUMA: Staj günü - Akşam haftalık tekrar (1 saat)
CUMARTESİ: Yoğun çalışma günü (4-5 saat) - Proje ve ödevler
PAZAR: Hafta sonu değerlendirmesi ve önümüzdeki hafta planı (2-3 saat)"""

# ----------------------
# Routes
# ----------------------
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    notes = conn.execute('SELECT * FROM notes WHERE user_id = ? ORDER BY created_at DESC', 
                        (session['user_id'],)).fetchall()
    
    # Son kaydedilmiş planı getir
    plan_row = conn.execute('SELECT week_plan FROM plans WHERE user_id = ? ORDER BY created_at DESC LIMIT 1', 
                           (session['user_id'],)).fetchone()
    plan = plan_row['week_plan'] if plan_row else None
    
    conn.close()
    return render_template('index.html', notes=notes, plan=plan)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if not username or not password:
            flash('Kullanıcı adı ve parola gerekli!')
            return render_template('register.html')
        
        conn = get_db()
        try:
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                        (username, generate_password_hash(password)))
            conn.commit()
            flash('Kayıt başarılı! Giriş yapabilirsiniz.')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Bu kullanıcı adı zaten alınmış!')
        finally:
            conn.close()
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('index'))
        else:
            flash('Geçersiz kullanıcı adı veya parola!')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Başarıyla çıkış yaptınız.')
    return redirect(url_for('login'))

@app.route('/add', methods=['POST'])
def add_note():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    title = request.form['title']
    content = request.form['content']
    
    if not title or not content:
        flash('Başlık ve içerik gerekli!')
        return redirect(url_for('index'))
    
    # AI ile özet oluştur
    summary = ai_summarize(content)
    
    conn = get_db()
    conn.execute('INSERT INTO notes (user_id, title, content, summary) VALUES (?, ?, ?, ?)',
                (session['user_id'], title, content, summary))
    conn.commit()
    conn.close()
    
    flash('Not başarıyla eklendi ve özetlendi!')
    return redirect(url_for('index'))

@app.route('/generate_plan', methods=['POST'])
def generate_plan():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    details = request.form['details']
    
    if not details:
        flash('Plan detayları gerekli!')
        return redirect(url_for('index'))
    
    # AI ile plan oluştur
    plan = ai_generate_plan(details)
    
    conn = get_db()
    conn.execute('INSERT INTO plans (user_id, week_plan) VALUES (?, ?)',
                (session['user_id'], plan))
    conn.commit()
    conn.close()
    
    flash('Haftalık plan oluşturuldu!')
    return redirect(url_for('index'))

@app.route('/delete/<int:note_id>')
def delete_note(note_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    conn.execute('DELETE FROM notes WHERE id = ? AND user_id = ?', 
                (note_id, session['user_id']))
    conn.commit()
    conn.close()
    
    flash('Not silindi!')
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)