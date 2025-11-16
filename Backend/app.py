from flask import Flask
from flask_cors import CORS
from auth_routes import auth_bp
from customer_routes import customer_bp
from datetime import timedelta

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Optional: Add session timeout
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

CORS(
    app,
    resources={r"/api/*": {"origins": "http://127.0.0.1:5500"}},
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization"]
)

# Register all blueprints
app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(customer_bp, url_prefix="/api/customer")

if __name__ == "__main__":
    app.run(debug=True)