from flask import Flask, render_template, request, redirect, session, url_for, flash, send_from_directory
from pymongo import MongoClient, DESCENDING
from flask import send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from datetime import datetime
from bson.objectid import ObjectId
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "infohub_secret_key")

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/infohub")
client = MongoClient(MONGO_URI)
db = client["infohub"]
print("MongoDB Connected Successfully")
users = db["users"]
projects = db["projects"]
admin_logs = db["admin_logs"]
messages = db["messages"]

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "iamniranjanxyz27@gmail.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")
ADMIN_NAME = os.getenv("ADMIN_NAME", "Niranjan")
ADMIN_PHONE = os.getenv("ADMIN_PHONE", "+91 7418203404")
ADMIN_LOCATION = os.getenv("ADMIN_LOCATION", "India")
ADMIN_WEBSITE = os.getenv("ADMIN_WEBSITE", "https://www.infohub.net.in")
ADMIN_ROLE = os.getenv("ADMIN_ROLE", "Administrator")


def now():
    return datetime.now()


def format_date(value):
    if not value:
        return "Not available"
    if isinstance(value, datetime):
        return value.strftime("%d %b %Y, %I:%M %p")
    return str(value)


app.jinja_env.filters["format_date"] = format_date


def is_admin_logged_in():
    return session.get("admin") is True


def get_default_projects():
    return [
        {
            "title": "AI Tools Directory",
            "description": "A clean directory of useful AI tools arranged in one simple platform for students, creators, and developers.",
            "tech": "HTML, CSS, JavaScript",
            "link": "#",
            "image": "/static/images/aitools.webp",
            "status": "Live",
            "created_at": now()
        },
        {
            "title": "Nexus UI",
            "description": "A modern UI library containing ready-made templates and modern frontend components to build pages faster.",
            "tech": "HTML, CSS, JavaScript",
            "link": "/static/nexus_ui/index.html",
            "image": "/static/images/nexus.jpg",
            "status": "Live",
            "created_at": now()
        },
        {
            "title": "Smart GOV",
            "description": "A career development website for students.",
            "tech": "Python, Flask, HTML, CSS, JavaScript, MongoDB",
            "link": "#",
            "image": "/static/images/smartgov.png",
            "status": "Live",
            "created_at": now()
        },
        {
            "title": "EBuy",
            "description": "A hyperlocal multi-vendor e-commerce marketplace connecting customers, local shops, delivery partners, and administrators on a single real-time platform.",
            "tech": "Python, Flask, Socket.IO, PostgreSQL",
            "link": "#",
            "image": "/static/images/ebuy.jpg",
            "status": "Live",
            "created_at": now()
        }
    ]


def seed_projects():
    if projects.count_documents({}) == 0:
        projects.insert_many(get_default_projects())
    else:
        if not projects.find_one({"title": "EBuy"}):
            projects.insert_one({
                "title": "EBuy",
                "description": "A hyperlocal multi-vendor e-commerce marketplace connecting customers, local shops, delivery partners, and administrators on a single real-time platform.",
                "tech": "Python, Flask, Socket.IO, PostgreSQL",
                "link": "#",
                "image": "/static/images/ebuy.jpg",
                "status": "Live",
                "created_at": now()
            })


@app.before_request
def before_request():
    seed_projects()


@app.context_processor
def inject_globals():
    return {
        "admin_logged_in": is_admin_logged_in(),
        "current_year": datetime.now().year
    }


# Main website pages
@app.route("/")
def home():
    featured_projects = list(projects.find().sort("created_at", DESCENDING).limit(2))
    return render_template("index.html", projects=featured_projects)


@app.route("/projects")
def all_projects():
    all_projects = list(projects.find().sort("created_at", DESCENDING))
    return render_template("projects.html", projects=all_projects)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/blog")
def blog():
    return render_template("blog.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        messages.insert_one({
            "name": request.form.get("name", "").strip(),
            "email": request.form.get("email", "").strip(),
            "phone": request.form.get("phone", "").strip(),
            "message": request.form.get("message", "").strip(),
            "created_at": now()
        })
        flash("Message sent successfully.", "success")
        return redirect(url_for("contact"))

    return render_template("contact.html")


# Redirect old .html links to Flask routes
@app.route("/index.html")
def index_html():
    return redirect(url_for("home"))


@app.route("/projects.html")
def projects_html():
    return redirect(url_for("all_projects"))


@app.route("/about.html")
def about_html():
    return redirect(url_for("about"))


@app.route("/blog.html")
def blog_html():
    return redirect(url_for("blog"))


@app.route("/contact.html")
def contact_html():
    return redirect(url_for("contact"))


@app.route("/login.html")
def login_html():
    return redirect(url_for("login"))


@app.route("/register.html")
def register_html():
    return redirect(url_for("register"))


# Auth
@app.route("/register", methods=["GET", "POST"])
def register():
    if is_admin_logged_in():
        return redirect(url_for("admin_dashboard"))
    if session.get("user"):
        return redirect(url_for("home"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")

        if users.find_one({"email": email}):
            flash("This email is already registered.", "error")
            return redirect(url_for("register"))

        users.insert_one({
            "name": name,
            "email": email,
            "phone": phone,
            "password": generate_password_hash(password),
            "created_at": now(),
            "last_login": None
        })

        flash("Account created. Please login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if is_admin_logged_in():
        return redirect(url_for("admin_dashboard"))
    if session.get("user"):
        return redirect(url_for("home"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        # Admin login
        if ADMIN_EMAIL and email == ADMIN_EMAIL.lower() and password == ADMIN_PASSWORD:
            session.clear()
            session["admin"] = True
            session["admin_email"] = ADMIN_EMAIL
            session["admin_name"] = ADMIN_NAME
            session.permanent = True

            admin_logs.insert_one({
                "email": ADMIN_EMAIL,
                "login_time": now()
            })

            response = redirect(url_for("admin_dashboard"))
            response.set_cookie("admin_logged_in", "true", max_age=30*24*60*60)
            response.set_cookie("user_name", ADMIN_NAME, max_age=30*24*60*60)
            return response

        # Normal user login
        user = users.find_one({"email": email})
        if user and check_password_hash(user["password"], password):
            session.clear()
            session["user"] = str(user["_id"])
            session["user_name"] = user.get("name", "User")
            session.permanent = True

            users.update_one(
                {"_id": user["_id"]},
                {"$set": {"last_login": now()}}
            )

            response = redirect(url_for("home"))
            response.set_cookie("user_logged_in", "true", max_age=30*24*60*60)
            response.set_cookie("user_name", user.get("name", "User"), max_age=30*24*60*60)
            return response

        flash("Invalid email or password.", "error")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    response = redirect(url_for("home"))
    response.delete_cookie("admin_logged_in")
    response.delete_cookie("user_logged_in")
    response.delete_cookie("user_name")
    return response


# Admin dashboard
@app.route("/admin/dashboard")
def admin_dashboard():
    if not is_admin_logged_in():
        return redirect(url_for("login"))

    last_login_log = admin_logs.find_one(
        {"email": ADMIN_EMAIL},
        sort=[("login_time", -1)]
    )

    last_login_time = last_login_log.get("login_time") if last_login_log else None

    total_users = users.count_documents({})
    total_projects = projects.count_documents({})
    total_messages = messages.count_documents({})

    project_list = list(projects.find().sort("created_at", DESCENDING))

    return render_template(
        "admin/dashboard.html",
        total_users=total_users,
        total_projects=total_projects,
        total_messages=total_messages,
        admin_email=ADMIN_EMAIL,
        admin_name=ADMIN_NAME,
        admin_location=ADMIN_LOCATION,
        admin_website=ADMIN_WEBSITE,
        last_login=last_login_time,
        projects=project_list
    )


@app.route("/admin/add-project", methods=["GET", "POST"])
def add_project():
    if not is_admin_logged_in():
        return redirect(url_for("login"))

    if request.method == "POST":
        projects.insert_one({
            "title": request.form.get("title", "").strip(),
            "description": request.form.get("description", "").strip(),
            "tech": request.form.get("tech", "").strip(),
            "link": request.form.get("link", "").strip() or "#",
            "image": request.form.get("image", "").strip() or "/static/images/project-placeholder.svg",
            "status": request.form.get("status", "Live").strip(),
            "created_at": now()
        })

        flash("Project added successfully.", "success")
        return redirect(url_for("admin_dashboard"))

    return render_template("admin/add_project.html")


@app.route("/admin/edit-project/<project_id>", methods=["GET", "POST"])
def edit_project(project_id):
    if not is_admin_logged_in():
        return redirect(url_for("login"))

    project = projects.find_one({"_id": ObjectId(project_id)})
    if not project:
        flash("Project not found.", "error")
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":
        projects.update_one(
            {"_id": ObjectId(project_id)},
            {"$set": {
                "title": request.form.get("title", "").strip(),
                "description": request.form.get("description", "").strip(),
                "tech": request.form.get("tech", "").strip(),
                "link": request.form.get("link", "").strip() or "#",
                "image": request.form.get("image", "").strip() or "/static/images/project-placeholder.svg",
                "status": request.form.get("status", "Live").strip(),
                "updated_at": now()
            }}
        )

        flash("Project updated successfully.", "success")
        return redirect(url_for("admin_dashboard"))

    return render_template("admin/edit_project.html", project=project)



if __name__ == "__main__":
    app.run(debug=True)
