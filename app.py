from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Oturum yönetimi için gizli anahtar

# 📌 Veritabanını başlatma
def init_db():
    conn = sqlite3.connect("tournament.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            gen TEXT NOT NULL,
            registered INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

@app.route("/")
def index():
    return render_template("index.html")

# 📌 Kullanıcı kayıt olma
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        gen = request.form["gen"]

        # 📌 "Gen" alanının 2 veya 3 haneli sayı olup olmadığını kontrol et
        if not gen.isdigit() or not (2 <= len(gen) <= 3):
            return "Gen sadece 2 veya 3 haneli rakamlardan oluşmalıdır!"

        conn = sqlite3.connect("tournament.db")
        c = conn.cursor()

        # 📌 Kullanıcı daha önce kayıt olmuş mu? (email veya kullanıcı adı kontrolü)
        c.execute("SELECT * FROM users WHERE email = ? OR username = ?", (email, username))
        existing_user = c.fetchone()

        if existing_user:
            conn.close()
            return "Bu kullanıcı adı veya e-posta adresi zaten kayıtlı!"

        # 📌 Kullanıcıyı kaydet
        c.execute("INSERT INTO users (username, email, gen, registered) VALUES (?, ?, ?, 1)", 
                  (username, email, gen))
        conn.commit()
        conn.close()
        return redirect(url_for("success"))

    return render_template("register.html")

@app.route("/success")
def success():
    return render_template("success.html")

# 📌 Yönetici giriş sayfası
@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # 📌 Yönetici bilgileri kontrolü
        if username == "admin" and password == "MAGICTR71814":
            session["admin"] = True
            return redirect(url_for("admin_panel"))

        return "Hatalı kullanıcı adı veya şifre!"

    return render_template("admin_login.html")

# 📌 Yönetici paneli - Kayıtlı kullanıcıları göster
@app.route("/admin/panel")
def admin_panel():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    conn = sqlite3.connect("tournament.db")
    c = conn.cursor()
    c.execute("SELECT id, username, email, gen FROM users")
    users = c.fetchall()
    conn.close()
    
    return render_template("admin_panel.html", users=users)

# 📌 Çıkış yapma
@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("index"))

if __name__ == "__main__":
    init_db()

    @app.route("/admin/reset_users", methods=["POST"])
    def reset_users():
        if not session.get("admin"):
            return redirect(url_for("admin_login"))

        conn = sqlite3.connect("tournament.db")
        c = conn.cursor()
        
        # 📌 Tüm kullanıcıları veritabanından sil
        c.execute("DELETE FROM users")
        conn.commit()
        conn.close()

        return redirect(url_for("admin_panel"))
    
    app.run(debug=True)
