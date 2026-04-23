"""
Infant Jesus Church, Kallettumkara
Flask Application Server (MongoDB Edition)
"""

import os
import json
import uuid
from datetime import datetime
from functools import wraps
from bson import ObjectId
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, session, jsonify, abort
)
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# ── App Configuration ──────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "kallettumkara-church-secret-2026")

# Upload Configuration
UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB max
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# MongoDB Configuration
app.config["MONGO_URI"] = os.environ.get(
    "MONGO_URI", "mongodb://localhost:27017/kallettumkara_church"
)
mongo = PyMongo(app)


# ── Helpers ─────────────────────────────────────────────────────────
class JSONEncoder(json.JSONEncoder):
    """Custom encoder for ObjectId and datetime."""
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)

app.json_encoder = JSONEncoder


def login_required(f):
    """Decorator to protect admin routes."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if "admin_logged_in" not in session:
            flash("Please log in to access the admin dashboard.", "warning")
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_upload(file_field):
    """Save an uploaded file and return its URL path, or empty string."""
    file = request.files.get(file_field)
    if file and file.filename and allowed_file(file.filename):
        ext = file.filename.rsplit(".", 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        return f"/static/uploads/{filename}"
    return ""

def seed_database():
    """Seed initial data if collections are empty."""
    # --- Admin user ---
    if mongo.db.admins.count_documents({}) == 0:
        mongo.db.admins.insert_one({
            "username": "admin",
            "password": generate_password_hash("admin123"),
            "created_at": datetime.utcnow()
        })

    # --- Mass Timings ---
    if mongo.db.mass_timings.count_documents({}) == 0:
        timings = [
            {"day": "Monday",    "time": "06:30 AM", "description": "Holy Qurbana (Syro-Malabar Rite)", "category": "Weekday"},
            {"day": "Tuesday",   "time": "06:30 AM", "description": "Holy Qurbana", "category": "Weekday"},
            {"day": "Wednesday", "time": "06:30 AM", "description": "Holy Qurbana & Novena", "category": "Weekday"},
            {"day": "Thursday",  "time": "06:30 AM", "description": "Holy Qurbana", "category": "Weekday"},
            {"day": "Friday",    "time": "06:30 AM", "description": "Holy Qurbana & Way of the Cross", "category": "Weekday"},
            {"day": "Saturday",  "time": "06:30 AM", "description": "Holy Qurbana", "category": "Weekday"},
            {"day": "Sunday",    "time": "06:00 AM", "description": "First Holy Qurbana", "category": "Sunday"},
            {"day": "Sunday",    "time": "08:00 AM", "description": "Second Holy Qurbana (Main)", "category": "Sunday"},
            {"day": "Sunday",    "time": "10:00 AM", "description": "Third Holy Qurbana", "category": "Sunday"},
            {"day": "Sunday",    "time": "05:00 PM", "description": "Evening Holy Qurbana & Catechism", "category": "Sunday"},
        ]
        mongo.db.mass_timings.insert_many(timings)

    # --- Announcements ---
    if mongo.db.announcements.count_documents({}) == 0:
        announcements = [
            {
                "title": "Annual Parish Feast",
                "content": "The annual feast will be celebrated on January 20th with solemnity.",
                "date": datetime(2026, 1, 15),
                "expiry": datetime(2026, 1, 25),
                "pdf_url": ""
            },
            {
                "title": "Sunday School Admissions Open",
                "content": "Admissions for the new academic year of Sunday School (Catechism) are now open.",
                "date": datetime(2026, 4, 1),
                "expiry": datetime(2026, 5, 31),
                "pdf_url": ""
            },
            {
                "title": "Parish Pilgrimage to Arthunkal",
                "content": "A parish pilgrimage to Arthunkal is being organised for May 15th.",
                "date": datetime(2026, 4, 20),
                "expiry": datetime(2026, 5, 20),
                "pdf_url": ""
            },
        ]
        mongo.db.announcements.insert_many(announcements)

    # --- Parish Council ---
    if mongo.db.parish_council.count_documents({}) == 0:
        members = [
            {"name": "Rev. Fr. Jose Pallikkunnu", "role": "Parish Priest", "image_url": "/static/images/vicar.jpg", "phone": "+91 79091 51122"},
            {"name": "Rev. Fr. Paul Antony",      "role": "Assistant Vicar", "image_url": "/static/images/assistant.jpg", "phone": "+91 480 2881 002"},
        ]
        mongo.db.parish_council.insert_many(members)

    # --- Prayer Requests ---
    if mongo.db.prayer_requests.count_documents({}) == 0:
        mongo.db.prayer_requests.create_index("created_at")

    # --- Family Units ---
    if mongo.db.family_units.count_documents({}) == 0:
        unit_names = [
            "St. John", "St. George", "Mariyam Thresia", "Christhuraja", "St. James",
            "Jesus Christ", "St. Mary's", "Maria", "Holy Family", "St. Joseph",
            "Francis Xavier", "St. Sebastian", "St. Antony", "Infant Jesus", "Thiruhridayam",
            "St. Alphonsa", "St. Paul", "St. Raphel", "Mother Theresa", "St. Peter",
            "Maria Goretti", "Vellamkanni Matha", "Cherupushpam", "Chavara Kuriakose", "St. Thomas"
        ]
        units = []
        for i, name in enumerate(unit_names, 1):
            units.append({
                "unit_number": i,
                "name": name,
                "show_photo": True,
                "president": {"name": "—", "phone": "—", "address": "—", "image_url": ""},
                "secretary": {"name": "—", "phone": "—", "address": "—", "image_url": ""},
                "treasurer": {"name": "—", "phone": "—", "address": "—", "image_url": ""},
                "families": []
            })
        mongo.db.family_units.insert_many(units)


# ── Public Routes ───────────────────────────────────────────────────
@app.route("/")
def home():
    """Home page with announcements marquee & daily mass widget."""
    today_name = datetime.utcnow().strftime("%A")
    daily_masses = list(mongo.db.mass_timings.find({"day": today_name}))
    sunday_masses = list(mongo.db.mass_timings.find({"category": "Sunday"}))
    announcements = list(
        mongo.db.announcements.find({"expiry": {"$gte": datetime.utcnow()}})
        .sort("date", -1)
        .limit(10)
    )
    parish_council = list(mongo.db.parish_council.find().limit(6))
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
    weekday = list(mongo.db.mass_timings.find({"category": "Weekday"}))
    sunday = list(mongo.db.mass_timings.find({"category": "Sunday"}))
    return render_template("spiritual_life.html", weekday=weekday, sunday=sunday)


@app.route("/about")
def about():
    council = list(mongo.db.parish_council.find())
    return render_template("about.html", council=council)


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/parish")
def parish():
    council = list(mongo.db.parish_council.find())
    return render_template("parish.html", council=council)


@app.route("/catechism")
def catechism():
    return render_template("catechism.html")


@app.route("/family-units")
def family_units():
    units = list(mongo.db.family_units.find().sort("unit_number", 1))
    return render_template("family_units.html", units=units)


@app.route("/family-units/<unit_id>")
def family_unit_detail(unit_id):
    """Full page view for a single family unit showing all families."""
    unit = mongo.db.family_units.find_one({"_id": ObjectId(unit_id)})
    if not unit:
        abort(404)
    return render_template("family_unit_detail.html", unit=unit)


@app.route("/family-units/<unit_id>/member/<int:member_index>")
def family_member_detail(unit_id, member_index):
    """Full detail view for a single family member."""
    unit = mongo.db.family_units.find_one({"_id": ObjectId(unit_id)})
    if not unit or member_index < 0 or member_index >= len(unit.get("families", [])):
        abort(404)
    member = unit["families"][member_index]
    return render_template("family_member_detail.html", unit=unit, member=member, member_index=member_index)


@app.route("/institutions")
def institutions():
    return render_template("institutions.html")


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
    data = {
        "name": request.form.get("name", "Anonymous"),
        "email": request.form.get("email", ""),
        "intention": request.form.get("intention", ""),
        "created_at": datetime.utcnow(),
    }
    mongo.db.prayer_requests.insert_one(data)
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
        user = mongo.db.admins.find_one({"username": username})
        if user and check_password_hash(user["password"], password):
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
        "masses": mongo.db.mass_timings.count_documents({}),
        "announcements": mongo.db.announcements.count_documents({}),
        "council": mongo.db.parish_council.count_documents({}),
        "prayers": mongo.db.prayer_requests.count_documents({}),
    }
    recent_prayers = list(
        mongo.db.prayer_requests.find().sort("created_at", -1).limit(5)
    )
    return render_template("admin/dashboard.html", stats=stats, prayers=recent_prayers)


# ── Admin CRUD: Mass Timings ───────────────────────────────────────
@app.route("/admin/mass-timings")
@login_required
def admin_mass_timings():
    timings = list(mongo.db.mass_timings.find())
    return render_template("admin/mass_timings.html", timings=timings)


@app.route("/admin/mass-timings/add", methods=["POST"])
@login_required
def admin_add_mass():
    mongo.db.mass_timings.insert_one({
        "day": request.form["day"],
        "time": request.form["time"],
        "description": request.form["description"],
        "category": request.form["category"],
    })
    flash("Mass timing added.", "success")
    return redirect(url_for("admin_mass_timings"))


@app.route("/admin/mass-timings/delete/<id>")
@login_required
def admin_delete_mass(id):
    mongo.db.mass_timings.delete_one({"_id": ObjectId(id)})
    flash("Mass timing removed.", "success")
    return redirect(url_for("admin_mass_timings"))


# ── Admin CRUD: Announcements ──────────────────────────────────────
@app.route("/admin/announcements")
@login_required
def admin_announcements():
    items = list(mongo.db.announcements.find().sort("date", -1))
    return render_template("admin/announcements.html", items=items)


@app.route("/admin/announcements/add", methods=["POST"])
@login_required
def admin_add_announcement():
    mongo.db.announcements.insert_one({
        "title": request.form["title"],
        "content": request.form["content"],
        "date": datetime.utcnow(),
        "expiry": datetime.strptime(request.form["expiry"], "%Y-%m-%d"),
        "pdf_url": request.form.get("pdf_url", ""),
    })
    flash("Announcement published.", "success")
    return redirect(url_for("admin_announcements"))


@app.route("/admin/announcements/delete/<id>")
@login_required
def admin_delete_announcement(id):
    mongo.db.announcements.delete_one({"_id": ObjectId(id)})
    flash("Announcement removed.", "success")
    return redirect(url_for("admin_announcements"))


# ── Admin CRUD: Parish Council ─────────────────────────────────────
@app.route("/admin/parish-council")
@login_required
def admin_parish_council():
    members = list(mongo.db.parish_council.find())
    return render_template("admin/parish_council.html", members=members)


@app.route("/admin/parish-council/add", methods=["POST"])
@login_required
def admin_add_council():
    mongo.db.parish_council.insert_one({
        "name": request.form["name"],
        "role": request.form["role"],
        "image_url": request.form.get("image_url", ""),
        "phone": request.form.get("phone", ""),
    })
    flash("Council member added.", "success")
    return redirect(url_for("admin_parish_council"))


# ── Admin CRUD: Family Units ───────────────────────────────────────
@app.route("/admin/family-units")
@login_required
def admin_family_units():
    units = list(mongo.db.family_units.find().sort("unit_number", 1))
    return render_template("admin/family_units.html", units=units)


@app.route("/admin/family-units/<unit_id>")
@login_required
def admin_family_unit_edit(unit_id):
    unit = mongo.db.family_units.find_one({"_id": ObjectId(unit_id)})
    if not unit:
        abort(404)
    return render_template("admin/family_unit_edit.html", unit=unit)


@app.route("/admin/family-units/<unit_id>/toggle-photo")
@login_required
def admin_toggle_photo(unit_id):
    """Toggle profile photo visibility on the public page."""
    unit = mongo.db.family_units.find_one({"_id": ObjectId(unit_id)})
    if unit:
        new_val = not unit.get("show_photo", True)
        mongo.db.family_units.update_one(
            {"_id": ObjectId(unit_id)},
            {"$set": {"show_photo": new_val}}
        )
        status = "ON" if new_val else "OFF"
        flash(f"Profile photos are now {status} for this unit.", "success")
    return redirect(url_for("admin_family_unit_edit", unit_id=unit_id))

@app.route("/admin/family-units/<unit_id>/update-leadership", methods=["POST"])
@login_required
def admin_update_leadership(unit_id):
    unit = mongo.db.family_units.find_one({"_id": ObjectId(unit_id)})
    if not unit:
        abort(404)

    # Upload images (keep existing if no new file)
    pres_img = save_upload("president_image") or unit.get("president", {}).get("image_url", "")
    sec_img = save_upload("secretary_image") or unit.get("secretary", {}).get("image_url", "")
    tres_img = save_upload("treasurer_image") or unit.get("treasurer", {}).get("image_url", "")

    mongo.db.family_units.update_one(
        {"_id": ObjectId(unit_id)},
        {"$set": {
            "president": {
                "name": request.form.get("president_name", "—"),
                "phone": request.form.get("president_phone", "—"),
                "address": request.form.get("president_address", "—"),
                "image_url": pres_img,
            },
            "secretary": {
                "name": request.form.get("secretary_name", "—"),
                "phone": request.form.get("secretary_phone", "—"),
                "address": request.form.get("secretary_address", "—"),
                "image_url": sec_img,
            },
            "treasurer": {
                "name": request.form.get("treasurer_name", "—"),
                "phone": request.form.get("treasurer_phone", "—"),
                "address": request.form.get("treasurer_address", "—"),
                "image_url": tres_img,
            },
        }}
    )
    flash("Leadership updated.", "success")
    return redirect(url_for("admin_family_unit_edit", unit_id=unit_id))


@app.route("/admin/family-units/<unit_id>/add-family", methods=["POST"])
@login_required
def admin_add_family(unit_id):
    family_img = save_upload("image_file")
    family = {
        "name": request.form["name"],
        "phone": request.form.get("phone", ""),
        "address": request.form.get("address", ""),
        "email": request.form.get("email", ""),
        "image_url": family_img,
        "visible": True,
    }
    mongo.db.family_units.update_one(
        {"_id": ObjectId(unit_id)},
        {"$push": {"families": family}}
    )
    flash("Family added.", "success")
    return redirect(url_for("admin_family_unit_edit", unit_id=unit_id))


@app.route("/admin/family-units/<unit_id>/toggle-family/<int:index>")
@login_required
def admin_toggle_family(unit_id, index):
    """Toggle visibility of a family member on the public page."""
    unit = mongo.db.family_units.find_one({"_id": ObjectId(unit_id)})
    if unit and 0 <= index < len(unit.get("families", [])):
        families = unit["families"]
        families[index]["visible"] = not families[index].get("visible", True)
        mongo.db.family_units.update_one(
            {"_id": ObjectId(unit_id)},
            {"$set": {"families": families}}
        )
        status = "shown" if families[index]["visible"] else "hidden"
        flash(f"Family is now {status} on the website.", "success")
    return redirect(url_for("admin_family_unit_edit", unit_id=unit_id))


@app.route("/admin/family-units/<unit_id>/delete-family/<int:index>")
@login_required
def admin_delete_family(unit_id, index):
    unit = mongo.db.family_units.find_one({"_id": ObjectId(unit_id)})
    if unit and 0 <= index < len(unit.get("families", [])):
        families = unit["families"]
        families.pop(index)
        mongo.db.family_units.update_one(
            {"_id": ObjectId(unit_id)},
            {"$set": {"families": families}}
        )
        flash("Family removed.", "success")
    return redirect(url_for("admin_family_unit_edit", unit_id=unit_id))


# ── Boot ────────────────────────────────────────────────────────────
with app.app_context():
    seed_database()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
