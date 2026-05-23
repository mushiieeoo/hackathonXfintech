from flask import Flask, jsonify
from db import db # <-- Importing the database connection from our new file

# Import your routing blueprints
from routes.accounts import accounts_bp
from routes.investments import investments_bp
from routes.ai import ai_bp

app = Flask(__name__)

# Register Blueprints 
app.register_blueprint(accounts_bp, url_prefix='/accounts')
app.register_blueprint(investments_bp, url_prefix='/investments')
app.register_blueprint(ai_bp, url_prefix='/ai')

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "success",
        "message": "Welcome to the portfoAI Backend!"
    }), 200

if __name__ == '__main__':
    print("Starting server... Database connection is active.")
    app.run(debug=True, host='0.0.0.0', port=5000)