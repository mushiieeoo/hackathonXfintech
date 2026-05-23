from datetime import datetime
from bson.objectid import ObjectId

class User:
    """
    A class to represent the User document structure in MongoDB.
    Instead of an ORM, we define a helper to generate the document dictionary.
    """
    
    @staticmethod
    def create_user_schema(username, email, password_hash):
        """
        Returns a dictionary formatted for MongoDB insertion.
        Notice how accounts and investments are embedded directly within the user document.
        """
        return {
            "username": username,
            "email": email,
            "password": password_hash,
            "created_at": datetime.utcnow(),
            "fiat_accounts": [], # Will hold embedded dictionaries of bank savings 
            "investments": {
                "stocks": [],    # Will hold embedded dictionaries of stock portfolios
                "crypto": []     # Will hold embedded dictionaries of crypto assets
            },
            "ai_chat_history": [] # Stores previous context for the AI financial assistant
        }

    @staticmethod
    def add_fiat_account(account_name, balance):
        """Helper to structure a new fiat account entry."""
        return {
            "account_id": str(ObjectId()),
            "name": account_name,
            "balance": balance,
            "last_updated": datetime.utcnow()
        }
        
    @staticmethod
    def add_investment(asset_ticker, quantity, purchase_price):
        """Helper to structure a new investment entry."""
        return {
            "investment_id": str(ObjectId()),
            "ticker": asset_ticker,
            "quantity": quantity,
            "purchase_price": purchase_price,
            "last_updated": datetime.utcnow()
        }