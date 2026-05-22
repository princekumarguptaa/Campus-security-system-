from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['ADMIN_PASSWORD'] = 'admin123' # Change this!

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
    data = request.json
    new_report = Report(
        id=f"r_{int(datetime.utcnow().timestamp() * 1000)}",
        type=data.get('type'),
        description=data.get('desc'),
        location=data.get('loc'),
        image_base64=data.get('image'),
        status='pending'
    )
    db.session.add(new_report)
    db.session.commit()
    return jsonify({"success": True}), 201

# API: Update report status (Admin)
@app.route('/api/reports/<id>', methods=['PATCH'])
def update_status(id):
    data = request.json
    report = Report.query.get_or_404(id)
    report.status = data.get('status')
    db.session.commit()
    return jsonify({"success": True})

# API: Admin Login
@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    data = request.json
    if data.get('password') == app.config['ADMIN_PASSWORD']:
        return jsonify({"success": True})
    return jsonify({"success": False, "message": "Invalid password"}), 401

if __name__ == '__main__':
   app.run(debug=True)
   
   from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['ADMIN_PASSWORD'] = 'admin123' # Change this!

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
    data = request.json
    new_report = Report(
        id=f"r_{int(datetime.utcnow().timestamp() * 1000)}",
        type=data.get('type'),
        description=data.get('desc'),
        location=data.get('loc'),
        image_base64=data.get('image'),
        status='pending'
    )
    db.session.add(new_report)
    db.session.commit()
    return jsonify({"success": True}), 201

# API: Update report status (Admin)
@app.route('/api/reports/<id>', methods=['PATCH'])
def update_status(id):
    data = request.json
    report = Report.query.get_or_404(id)
    report.status = data.get('status')
    db.session.commit()
    return jsonify({"success": True})

# API: Admin Login
@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    data = request.json
    if data.get('password') == app.config['ADMIN_PASSWORD']:
        return jsonify({"success": True})
    return jsonify({"success": False, "message": "Invalid password"}), 401

if __name__ == '__main__':
    app.run(debug=True)