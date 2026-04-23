"""
Infant Jesus Church, Kallettumkara
Flask Application Server (SQLite Edition)
"""

import os
import json
from datetime import datetime
from functools import wraps
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, session, jsonify, abort
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# ── App Configuration ──────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "kallettumkara-church-secret-2026")

# SQLite Configuration
basedir = os.path.abspath(os.path.dirname(__file__))

# Railway persistent volume support
volume_path = os.environ.get("RAILWAY_VOLUME_MOUNT_PATH")
if volume_path:
    db_path = os.path.join(volume_path, "church.db")
else:
    db_path = os.path.join(basedir, "church.db")

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///" + db_path)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ── Models ──────────────────────────────────────────────────────────
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class MassTiming(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(200))
    category = db.Column(db.String(20)) # Weekday, Sunday

class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    expiry = db.Column(db.DateTime, nullable=False)
    pdf_url = db.Column(db.String(500))

class ParishCouncil(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(500))
    phone = db.Column(db.String(20))

class PrayerRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120))
    intention = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ── Helpers ─────────────────────────────────────────────────────────
def login_required(f):
    """Decorator to protect admin routes."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if "admin_logged_in" not in session:
            flash("Please log in to access the admin dashboard.", "warning")
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated

def seed_database():
    """Seed initial data if tables are empty."""
    # --- Admin user ---
    if Admin.query.count() == 0:
        admin = Admin(
            username="admin",
            password=generate_password_hash("admin123")
        )
        db.session.add(admin)

    # --- Mass Timings ---
    if MassTiming.query.count() == 0:
        timings = [
            MassTiming(day="Monday",    time="06:30 AM", description="Holy Qurbana (Syro-Malabar Rite)", category="Weekday"),
            MassTiming(day="Tuesday",   time="06:30 AM", description="Holy Qurbana", category="Weekday"),
            MassTiming(day="Wednesday", time="06:30 AM", description="Holy Qurbana & Novena", category="Weekday"),
            MassTiming(day="Thursday",  time="06:30 AM", description="Holy Qurbana", category="Weekday"),
            MassTiming(day="Friday",    time="06:30 AM", description="Holy Qurbana & Way of the Cross", category="Weekday"),
            MassTiming(day="Saturday",  time="06:30 AM", description="Holy Qurbana", category="Weekday"),
            MassTiming(day="Sunday",    time="06:00 AM", description="First Holy Qurbana", category="Sunday"),
            MassTiming(day="Sunday",    time="08:00 AM", description="Second Holy Qurbana (Main)", category="Sunday"),
            MassTiming(day="Sunday",    time="10:00 AM", description="Third Holy Qurbana", category="Sunday"),
            MassTiming(day="Sunday",    time="05:00 PM", description="Evening Holy Qurbana & Catechism", category="Sunday"),
        ]
        db.session.add_all(timings)

    # --- Announcements ---
    if Announcement.query.count() == 0:
        announcements = [
            Announcement(
                title="Annual Parish Feast",
                content="The annual feast will be celebrated on January 20th with solemnity.",
                date=datetime(2026, 1, 15),
                expiry=datetime(2026, 1, 25)
            ),
            Announcement(
                title="Sunday School Admissions Open",
                content="Admissions for the new academic year of Sunday School (Catechism) are now open.",
                date=datetime(2026, 4, 1),
                expiry=datetime(2026, 5, 31)
            ),
            Announcement(
                title="Parish Pilgrimage to Arthunkal",
                content="A parish pilgrimage to Arthunkal is being organised for May 15th.",
                date=datetime(2026, 4, 20),
                expiry=datetime(2026, 5, 20)
            ),
        ]
        db.session.add_all(announcements)

    # --- Parish Council ---
    if ParishCouncil.query.count() == 0:
        members = [
            ParishCouncil(name="Rev. Fr. Jose Pallikkunnu", role="Parish Priest", image_url="/static/images/vicar.jpg", phone="+91 79091 51122"),
            ParishCouncil(name="Rev. Fr. Paul Antony",      role="Assistant Vicar", image_url="/static/images/assistant.jpg", phone="+91 480 2881 002"),
        ]
        db.session.add_all(members)

    db.session.commit()

# ── Public Routes ───────────────────────────────────────────────────
@app.route("/")
def home():
    """Home page with announcements marquee & daily mass widget."""
    today_name = datetime.utcnow().strftime("%A")
    daily_masses = MassTiming.query.filter_by(day=today_name).all()
    sunday_masses = MassTiming.query.filter_by(category="Sunday").all()
    announcements = Announcement.query.filter(Announcement.expiry >= datetime.utcnow()).order_by(Announcement.date.desc()).limit(10).all()
    parish_council = ParishCouncil.query.limit(6).all()
    
    return render_template(
        "index.html",
        daily_masses=daily_masses,
        sunday_masses=sunday_masses,
        announcements=announcements,
        parish_council=parish_council,
        today=today_name,
    )

@app.route("/history")
def history():
    return render_template("history.html")

@app.route("/spiritual-life")
def spiritual_life():
    weekday = MassTiming.query.filter_by(category="Weekday").all()
    sunday = MassTiming.query.filter_by(category="Sunday").all()
    return render_template("spiritual_life.html", weekday=weekday, sunday=sunday)

@app.route("/about")
def about():
    council = ParishCouncil.query.all()
    return render_template("about.html", council=council)

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/parish")
def parish():
    council = ParishCouncil.query.all()
    return render_template("parish.html", council=council)

@app.route("/catechism")
def catechism():
    return render_template("catechism.html")

@app.route("/family-units")
def family_units():
    return render_template("family_units.html")

@app.route("/associations")
def associations():
    return render_template("associations.html")

@app.route("/bulletin")
def bulletin():
    return render_template("bulletin.html")

@app.route("/gallery")
def gallery():
    return render_template("gallery.html")

@app.route("/prayer-request", methods=["POST"])
def prayer_request():
    req = PrayerRequest(
        name=request.form.get("name", "Anonymous"),
        email=request.form.get("email", ""),
        intention=request.form.get("intention", "")
    )
    db.session.add(req)
    db.session.commit()
    flash("Your prayer intention has been received. God bless you!", "success")
    return redirect(url_for("home") + "#prayer")

# ── API (Multilingual data) ────────────────────────────────────────
@app.route("/api/translations/<lang>")
def translations(lang):
    data_path = os.path.join(app.root_path, "data", f"{lang}.json")
    if not os.path.exists(data_path):
        abort(404)
    with open(data_path, "r", encoding="utf-8") as f:
        return jsonify(json.load(f))

# ── Admin Routes ────────────────────────────────────────────────────
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = Admin.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session["admin_logged_in"] = True
            session["admin_user"] = username
            flash("Welcome back!", "success")
            return redirect(url_for("admin_dashboard"))
        flash("Invalid credentials.", "danger")
    return render_template("admin/login.html")

@app.route("/admin/logout")
def admin_logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))

@app.route("/admin")
@login_required
def admin_dashboard():
    stats = {
        "masses": MassTiming.query.count(),
        "announcements": Announcement.query.count(),
        "council": ParishCouncil.query.count(),
        "prayers": PrayerRequest.query.count(),
    }
    recent_prayers = PrayerRequest.query.order_by(PrayerRequest.created_at.desc()).limit(5).all()
    return render_template("admin/dashboard.html", stats=stats, prayers=recent_prayers)

# ── Admin CRUD: Mass Timings ───────────────────────────────────────
@app.route("/admin/mass-timings")
@login_required
def admin_mass_timings():
    timings = MassTiming.query.all()
    return render_template("admin/mass_timings.html", timings=timings)

@app.route("/admin/mass-timings/add", methods=["POST"])
@login_required
def admin_add_mass():
    m = MassTiming(
        day=request.form["day"],
        time=request.form["time"],
        description=request.form["description"],
        category=request.form["category"]
    )
    db.session.add(m)
    db.session.commit()
    flash("Mass timing added.", "success")
    return redirect(url_for("admin_mass_timings"))

@app.route("/admin/mass-timings/delete/<int:id>")
@login_required
def admin_delete_mass(id):
    m = MassTiming.query.get_or_404(id)
    db.session.delete(m)
    db.session.commit()
    flash("Mass timing removed.", "success")
    return redirect(url_for("admin_mass_timings"))

# ── Admin CRUD: Announcements ──────────────────────────────────────
@app.route("/admin/announcements")
@login_required
def admin_announcements():
    items = Announcement.query.order_by(Announcement.date.desc()).all()
    return render_template("admin/announcements.html", items=items)

@app.route("/admin/announcements/add", methods=["POST"])
@login_required
def admin_add_announcement():
    a = Announcement(
        title=request.form["title"],
        content=request.form["content"],
        expiry=datetime.strptime(request.form["expiry"], "%Y-%m-%d"),
        pdf_url=request.form.get("pdf_url", "")
    )
    db.session.add(a)
    db.session.commit()
    flash("Announcement published.", "success")
    return redirect(url_for("admin_announcements"))

@app.route("/admin/announcements/delete/<int:id>")
@login_required
def admin_delete_announcement(id):
    a = Announcement.query.get_or_404(id)
    db.session.delete(a)
    db.session.commit()
    flash("Announcement removed.", "success")
    return redirect(url_for("admin_announcements"))

# ── Admin CRUD: Parish Council ─────────────────────────────────────
@app.route("/admin/parish-council")
@login_required
def admin_parish_council():
    members = ParishCouncil.query.all()
    return render_template("admin/parish_council.html", members=members)

@app.route("/admin/parish-council/add", methods=["POST"])
@login_required
def admin_add_council():
    p = ParishCouncil(
        name=request.form["name"],
        role=request.form["role"],
        image_url=request.form.get("image_url", ""),
        phone=request.form.get("phone", "")
    )
    db.session.add(p)
    db.session.commit()
    flash("Council member added.", "success")
    return redirect(url_for("admin_parish_council"))

@app.route("/admin/parish-council/delete/<int:id>")
@login_required
def admin_delete_council(id):
    p = ParishCouncil.query.get_or_404(id)
    db.session.delete(p)
    db.session.commit()
    flash("Council member removed.", "success")
    return redirect(url_for("admin_parish_council"))

# ── Boot ────────────────────────────────────────────────────────────
with app.app_context():
    db.create_all()
    seed_database()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
