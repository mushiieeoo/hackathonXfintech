from flask import Blueprint, request, jsonify

# Create a Blueprint named 'ai'
ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/chat', methods=['POST'])
def chat_with_ai():
    """
    Endpoint to handle user conversations with the AI financial assistant.
    Expected JSON payload: {"message": "How is my Apple stock doing?"}
    """
    data = request.get_json()
    
    if not data or 'message' not in data:
        return jsonify({"error": "Missing message content"}), 400
        
    user_message = data['message']
    
    # In the future, we will pass this message to the OpenAI or Gemini API
    # along with the user's portfolio data from MongoDB to get a personalized response.
    
    # Dummy response for now
    dummy_ai_response = f"I see you asked about: '{user_message}'. I am an AI assistant, but my API key is not connected yet!"
    
    return jsonify({
        "status": "success",
        "response": dummy_ai_response
    }), 200