from flask import Flask, render_template, request, redirect, url_for, flash
from pymongo import MongoClient, DESCENDING
from dotenv import load_dotenv
from datetime import datetime
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import urllib.request
import urllib.parse

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "niranjan_secret_key")

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/infohub")
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client["infohub"]
    projects = db["projects"]
    messages = db["messages"]
    print("MongoDB Connected Successfully")
except Exception as e:
    print(f"MongoDB Connection Warning: {e}")
    db = None
    projects = None
    messages = None


def now():
    return datetime.now()


def format_date(value):
    if not value:
        return "Not available"
    if isinstance(value, datetime):
        return value.strftime("%d %b %Y, %I:%M %p")
    return str(value)


app.jinja_env.filters["format_date"] = format_date


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
    if projects is None:
        return
    try:
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
    except Exception as e:
        print(f"Error seeding projects: {e}")


# Run initial project seed on startup
seed_projects()


@app.context_processor
def inject_globals():
    return {
        "current_year": datetime.now().year
    }


# Main website pages
@app.route("/")
def home():
    featured_projects = []
    if projects is not None:
        try:
            featured_projects = list(projects.find().sort("created_at", DESCENDING).limit(2))
        except Exception:
            featured_projects = get_default_projects()[:2]
    return render_template("index.html", projects=featured_projects)


@app.route("/projects")
def all_projects():
    project_list = []
    if projects is not None:
        try:
            project_list = list(projects.find().sort("created_at", DESCENDING))
        except Exception:
            project_list = get_default_projects()
    return render_template("projects.html", projects=project_list)


@app.route("/about")
def about():
    return render_template("blog.html")


@app.route("/blog")
def blog():
    return render_template("about.html")


def send_contact_email(name, email, message_text, phone=""):
    smtp_user = os.getenv("MAIL_USERNAME")
    smtp_pass = os.getenv("MAIL_PASSWORD")
    smtp_server = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("MAIL_PORT", "465"))

    recipient = "niraaanjaaan@gmail.com"

    # 1. Try sending via SMTP if credentials are configured in .env
    if smtp_user and smtp_pass:
        try:
            msg = MIMEMultipart()
            msg["From"] = smtp_user
            msg["To"] = recipient
            msg["Subject"] = f"New Contact Message from {name} - InfoHub"
            body = f"Name: {name}\nSender Email: {email}\n\nMessage:\n{message_text}"
            msg.attach(MIMEText(body, "plain"))

            if smtp_port == 465:
                with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
                    server.login(smtp_user, smtp_pass)
                    server.send_message(msg)
            else:
                with smtplib.SMTP(smtp_server, smtp_port) as server:
                    server.starttls()
                    server.login(smtp_user, smtp_pass)
                    server.send_message(msg)
            print("Contact email sent via SMTP successfully.")
            return True
        except Exception as e:
            print(f"SMTP send failed: {e}")

    # 2. Fallback: FormSubmit API to niraaanjaaan@gmail.com
    try:
        payload = {
            "name": name,
            "email": email,
            "message": message_text,
            "_subject": f"New Contact Message from {name}",
            "_captcha": "false"
        }
        if phone:
            payload["phone"] = phone

        data = urllib.parse.urlencode(payload).encode("utf-8")
        req = urllib.request.Request(
            f"https://formsubmit.co/ajax/{recipient}",
            data=data,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req) as resp:
            print("FormSubmit API response:", resp.read().decode("utf-8"))
        return True
    except Exception as e:
        print(f"FormSubmit API request error: {e}")
        return False


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        message_text = request.form.get("message", "").strip()

        if messages is not None:
            try:
                messages.insert_one({
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "message": message_text,
                    "created_at": now()
                })
            except Exception as e:
                print(f"Failed to record message: {e}")

        # Send email to niraaanjaaan@gmail.com
        send_contact_email(name, email, message_text, phone)

        flash("Message sent successfully! Thank you for reaching out.", "success")
        return redirect(url_for("contact"))

    return render_template("contact.html")


# Redirect old legacy/static links to active Flask routes
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


@app.route("/login")
@app.route("/login.html")
@app.route("/register")
@app.route("/register.html")
@app.route("/logout")
def auth_redirect():
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
