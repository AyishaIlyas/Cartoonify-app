from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import cv2
import numpy as np
import base64

app = Flask(__name__)
CORS(app)

# Configuration for SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cartoons.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the Cartoon model for SQLAlchemy
class Cartoon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_image = db.Column(db.Text, nullable=False)
    cartoon_image = db.Column(db.Text, nullable=False)

# Ensure creation of database tables within app context
with app.app_context():
    db.create_all()

# Function to cartoonify an image using OpenCV
def cartoonify(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)
    edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)
    color = cv2.bilateralFilter(image, 9, 300, 300)
    cartoon = cv2.bitwise_and(color, color, mask=edges)
    return cartoon

# Route to handle cartoonification POST requests
@app.route('/cartoonify', methods=['POST'])
def cartoonify_route():
    try:
        data = request.json
        img_data = base64.b64decode(data['image'])
        np_img = np.frombuffer(img_data, np.uint8)
        image = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
        cartoon = cartoonify(image)
        _, buffer = cv2.imencode('.jpg', cartoon)
        cartoon_base64 = base64.b64encode(buffer).decode('utf-8')

        # Save cartoon images to database
        new_cartoon = Cartoon(original_image=data['image'], cartoon_image=cartoon_base64)
        db.session.add(new_cartoon)
        db.session.commit()

        return jsonify({'cartoon': cartoon_base64})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Default route to handle undefined paths
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return jsonify({'error': 'Route not found'}), 404

# Run the Flask application if executed directly
if __name__ == '__main__':
    app.run(debug=True)

