import google.generativeai as genai

GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"

def initialize_gemini():
    if GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
        return None
    genai.configure(api_key=GEMINI_API_KEY)
    return genai.GenerativeModel('gemini-pro')

def get_chatbot_response(user_message, report_context=None):
    """
    Generate chatbot response based on user query and medical report context
    """
    try:
        model = initialize_gemini()
        
        if model is None:
            return get_default_chatbot_response(user_message)
        
        # Build context-aware prompt
        prompt = f"""You are a friendly and empathetic medical assistant chatbot. 
Your role is to help patients understand their medical reports and answer health-related questions.

IMPORTANT GUIDELINES:
- Be warm, empathetic, and patient-friendly
- Explain medical terms in simple language
- ALWAYS include a disclaimer that you're providing information, not medical diagnosis
- If the question requires immediate medical attention, urge them to see a doctor
- Be honest if you don't have enough information

"""
        
        if report_context:
            prompt += f"""
PATIENT'S MEDICAL REPORT CONTEXT:
{report_context}

"""
        
        prompt += f"""
PATIENT'S QUESTION: {user_message}

Please provide a helpful, empathetic response. Keep it concise (2-3 sentences) unless more detail is needed."""
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        print(f"Chatbot Error: {str(e)}")
        return get_default_chatbot_response(user_message)

def get_default_chatbot_response(user_message):
    """Fallback responses when Gemini API is not available"""
    user_message_lower = user_message.lower()
    
    # Check for emergency keywords
    emergency_keywords = ['emergency', 'urgent', 'severe', 'serious', 'critical', 'pain', 'chest']
    if any(keyword in user_message_lower for keyword in emergency_keywords):
        return "⚠️ Based on your question, I recommend consulting a healthcare professional immediately. If this is an emergency, please call emergency services or visit the nearest hospital. This chatbot provides general information only and cannot replace professional medical advice."
    
    # Check for specific questions
    if 'what' in user_message_lower and ('mean' in user_message_lower or 'is' in user_message_lower):
        return "I can help explain medical terms! However, to give you accurate information, I'd need access to your specific report values. Generally speaking, medical test results should be interpreted by your doctor who can consider your complete health history. Would you like to know about a specific parameter?"
    
    if 'should i' in user_message_lower or 'do i need' in user_message_lower:
        return "For personalized medical decisions, I always recommend consulting with a healthcare professional. They can review your complete medical history and provide guidance specific to your situation. Is there something specific from your report you'd like me to help explain?"
    
    if 'eat' in user_message_lower or 'food' in user_message_lower or 'diet' in user_message_lower:
        return "Diet recommendations depend on your specific health conditions. Generally, a balanced diet with fruits, vegetables, whole grains, and lean proteins is beneficial. For personalized dietary advice based on your medical report, please consult a doctor or dietitian. They can provide recommendations tailored to your needs."
    
    if 'thank' in user_message_lower or 'thanks' in user_message_lower:
        return "You're welcome! I'm here to help. Remember, I provide general information - always consult your healthcare provider for medical decisions. Feel free to ask if you have more questions! 😊"
    
    # Default response
    return "I'm here to help answer questions about your medical report! I can explain medical terms, discuss general health topics, and provide information. However, please remember that I'm not a substitute for professional medical advice. For specific medical decisions, always consult your healthcare provider. What would you like to know?"

def build_report_context(values, risk_level, risk_score):
    """Build context string from report data"""
    context = f"Risk Level: {risk_level}\n"
    context += f"Risk Score: {risk_score}/100\n\n"
    context += "Medical Values:\n"
    
    if values.get('hemoglobin') is not None:
        context += f"- Hemoglobin: {values['hemoglobin']} g/dL\n"
    if values.get('blood_sugar') is not None:
        context += f"- Blood Sugar: {values['blood_sugar']} mg/dL\n"
    if values.get('cholesterol') is not None:
        context += f"- Cholesterol: {values['cholesterol']} mg/dL\n"
    
    return context
