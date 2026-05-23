from flask import Blueprint, request, jsonify
from db import db
from models.user import User

accounts_bp = Blueprint('accounts', __name__)

# For testing purposes, we will hardcode a "demo user" email 
# until you add a login system later.
DEMO_USER_EMAIL = "demo@example.com"

@accounts_bp.route('/add', methods=['POST'])
def add_account():
    """Endpoint to add a new fiat account."""
    data = request.get_json()
    
    if not data or 'account_name' not in data or 'balance' not in data:
        return jsonify({"error": "Missing account_name or balance"}), 400
        
    # 1. Format the new account using your User model
    new_account = User.add_fiat_account(data['account_name'], data['balance'])
    
    # 2. Update the user's document in MongoDB by $pushing the new account into the array
    # If the user doesn't exist yet, 'upsert=True' will automatically create them!
    result = db.users.update_one(
        {"email": DEMO_USER_EMAIL}, 
        {"$push": {"fiat_accounts": new_account}}, 
        upsert=True
    )
    
    return jsonify({
        "status": "success",
        "message": f"Successfully added {data['account_name']}",
        "database_acknowledged": result.acknowledged
    }), 201

@accounts_bp.route('/view', methods=['GET'])
def view_accounts():
    """Endpoint to retrieve all fiat accounts from the database."""
    # 1. Find the demo user in the database
    user = db.users.find_one({"email": DEMO_USER_EMAIL})
    
    # 2. If the user exists, get their accounts. Otherwise, return an empty list.
    accounts = user.get("fiat_accounts", []) if user else []
    
    # 3. Clean up the ObjectId so it can be converted to JSON safely
    for acc in accounts:
        acc["_id"] = str(acc.get("_id", "")) # Safely handle missing internal IDs
    
    return jsonify({
        "status": "success",
        "accounts": accounts
    }), 200