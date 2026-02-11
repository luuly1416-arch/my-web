from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

# ===== MODEL USER =====
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(200))
    role = db.Column(db.String(20), default="user")  # user hoặc admin
    score = db.Column(db.Integer, default=0)
    class_name = db.Column(db.String(50))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ===== TRANG CHỦ =====
@app.route("/")
def home():
    return render_template("index.html")

# ===== ĐĂNG KÝ =====
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        hashed_pw = generate_password_hash(request.form["password"])
        user = User(
            username=request.form["username"],
            email=request.form["email"],
            password=hashed_pw,
            class_name=request.form["class"]
        )
        db.session.add(user)
        db.session.commit()
        flash("Tạo tài khoản thành công!")
        return redirect(url_for("login"))
    return render_template("register.html")

# ===== ĐĂNG NHẬP =====
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(username=request.form["username"]).first()
        if user and check_password_hash(user.password, request.form["password"]):
            login_user(user)
            return redirect(url_for("dashboard"))
        flash("Sai tài khoản hoặc mật khẩu")
    return render_template("login.html")

# ===== DASHBOARD =====
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

# ===== ADMIN =====
@app.route("/admin")
@login_required
def admin():
    if current_user.role != "admin":
        return "Không có quyền!"
    users = User.query.all()
    return render_template("admin.html", users=users)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
