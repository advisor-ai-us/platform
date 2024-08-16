from . import mental_health_bp
from .utils import get_system_prompt_with_latest_health_data, save_health_status
from flask import request, jsonify
from app import get_response_from_openai  # Assuming this is a global function

@mental_health_bp.route('/ai_request', methods=['POST'])
def ai_request_mental_health_advisor():
    data = request.get_json()
    userEmail = data.get('userEmail')
    message = data.get('message')
    display_on_page = data.get('display_on_page')

    text_sent_to_ai_in_the_prompt = get_system_prompt_with_latest_health_data(userEmail)
    text_sent_to_ai_in_the_prompt.append({"role": "user", "content": message})

    # Get OpenAI API key and model (you might need to adjust this based on your actual implementation)
    apiKey, model = get_user_openai_settings(userEmail)

    response = get_response_from_openai(apiKey, model, text_sent_to_ai_in_the_prompt)

    if isinstance(response, str):
        return jsonify({"error": "An error occurred while processing your request. Please try again later."}), 500

    if response.choices and response.choices[0].message.content:
        content = response.choices[0].message.content
        responseData = extract_json_from_text(content)

        if not responseData:
            return jsonify({"error": "Invalid response format"}), 500

        MsgForUser = responseData.get('MsgForUser', 'An error occurred. Please try again.')
        MsgForApplication = responseData.get('MsgForApplication', [])

        save_health_status(userEmail, MsgForApplication)

        return jsonify({
            "response": MsgForUser,
            "responseData": content,
            "model": model,
            "prompt_details": json.dumps(text_sent_to_ai_in_the_prompt),
        })

    return jsonify({"error": "Unexpected response format from OpenAI API"}), 500
