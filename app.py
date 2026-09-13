from flask import Flask, render_template, request, jsonify, session, Response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from camera import generate_frames
import os

from chatbot import get_ai_response

app = Flask(__name__)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['ADMIN_PASSWORD'] = os.getenv('ADMIN_PASSWORD')

if not app.config['ADMIN_PASSWORD']:
    raise ValueError("ADMIN_PASSWORD is missing from .env")


app.secret_key = os.getenv('SECRET_KEY')

if not app.secret_key:
    raise ValueError("SECRET_KEY is missing from .env")

db = SQLAlchemy(app)

# Database Model
class Report(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    image_base64 = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='pending')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "desc": self.description,
            "loc": self.location,
            "image": self.image_base64,
            "status": self.status,
            "time": self.timestamp.isoformat()
        }

# Create database tables
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

# API: Get all reports
@app.route('/api/reports', methods=['GET'])
def get_reports():
    reports = Report.query.order_by(Report.timestamp.desc()).all()
    return jsonify([r.to_dict() for r in reports])

# API: Submit a report
@app.route('/api/reports', methods=['POST'])
def submit_report():

    data = request.get_json(silent=True) or {}

    report_type = data.get('type', '').strip()
    description = data.get('desc', '').strip()
    location = data.get('loc', '').strip()
    image = data.get('image')

    # Required fields
    if not report_type or not description or not location:
        return jsonify({
            "success": False,
            "message": "Type, description and location are required."
        }), 400

    # Allowed report types
    allowed_types = ['fight', 'medical', 'theft', 'other']

    if report_type not in allowed_types:
        return jsonify({
            "success": False,
            "message": "Invalid report type."
        }), 400

    # Length validation
    if len(description) > 5000:
        return jsonify({
            "success": False,
            "message": "Description is too long."
        }), 400

    if len(location) > 200:
        return jsonify({
            "success": False,
            "message": "Location is too long."
        }), 400

    new_report = Report(
        id=f"r_{int(datetime.utcnow().timestamp() * 1000)}",
        type=report_type,
        description=description,
        location=location,
        image_base64=image,
        status='pending'
    )

    db.session.add(new_report)
    db.session.commit()

    return jsonify({
        "success": True
    }), 201

# API: Update report status (Admin)
@app.route('/api/reports/<id>', methods=['PATCH'])
def update_status(id):

    # Check admin login
    if not session.get('admin_logged_in'):
        return jsonify({
            "success": False,
            "message": "Unauthorized"
        }), 401

    data = request.get_json(silent=True) or {}

    status = data.get('status')

    # Validate status
    if status not in ['pending', 'resolved']:
        return jsonify({
            "success": False,
            "message": "Invalid status."
        }), 400

    report = Report.query.get_or_404(id)

    report.status = status

    db.session.commit()

    return jsonify({
        "success": True
    })

# AI Chatbot Route
@app.route('/chat', methods=['POST'])
def chat():

    try:

        data = request.get_json(silent=True) or {}

        user_message = data.get('message', '').strip()

        if not user_message:
            return jsonify({
                "response": "Please enter a message."
            }), 400

        if len(user_message) > 1000:
            return jsonify({
                "response": "Message is too long. Please keep it under 1000 characters."
            }), 400

        ai_response = get_ai_response(user_message)

        return jsonify({
            "response": ai_response
        }), 200

    except Exception as e:

        print("CHATBOT ERROR:", str(e))

        return jsonify({
            "response": "Sorry, the AI assistant is temporarily unavailable."
        }), 500

# API: Admin Login
@app.route('/api/admin/login', methods=['POST'])
def admin_login():

    data = request.get_json(silent=True) or {}

    password = data.get('password', '')

    if password == app.config['ADMIN_PASSWORD']:

        session['admin_logged_in'] = True

        return jsonify({
            "success": True
        })

    return jsonify({
        "success": False,
        "message": "Invalid password"
    }), 401

@app.route('/video_feed')
def video_feed():
    return Response(
        generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


if __name__ == '__main__':
    app.run(debug=True)