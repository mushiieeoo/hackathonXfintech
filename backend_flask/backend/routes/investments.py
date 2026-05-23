from flask import Blueprint, request, jsonify

# Create a Blueprint named 'investments'
investments_bp = Blueprint('investments', __name__)

@investments_bp.route('/add', methods=['POST'])
def add_investment():
    """
    Endpoint to add a new stock or crypto asset.
    Expected JSON payload: {"ticker": "AAPL", "quantity": 10, "purchase_price": 150.50}
    """
    data = request.get_json()
    
    # Basic validation
    if not data or not all(k in data for k in ("ticker", "quantity", "purchase_price")):
        return jsonify({"error": "Missing ticker, quantity, or purchase_price"}), 400
        
    # In the future, we will use models/user.py to save this to MongoDB
    
    return jsonify({
        "status": "success",
        "message": f"Successfully added {data['quantity']} shares of {data['ticker']}",
        "data": data
    }), 201

@investments_bp.route('/portfolio', methods=['GET'])
def view_portfolio():
    """
    Endpoint to retrieve the user's investment portfolio.
    """
    # Dummy data for testing until the database is fully linked
    dummy_portfolio = {
        "stocks": [
            {"ticker": "AAPL", "quantity": 10, "current_value": 1750.00},
            {"ticker": "TSLA", "quantity": 5, "current_value": 1100.00}
        ],
        "crypto": [
            {"ticker": "BTC", "quantity": 0.5, "current_value": 32000.00}
        ]
    }
    
    return jsonify({
        "status": "success",
        "portfolio": dummy_portfolio
    }), 200