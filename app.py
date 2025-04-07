from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini
try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel('gemini-1.5-pro-latest')
except Exception as e:
    print(f"Error configuring Gemini: {str(e)}")
    exit(1)
 
app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    try:
        # Get form data
        user_input = request.form.get("user_input", "").strip()
        word_count = request.form.get("word_count", "200")
        tone = request.form.get("tone", "professional")
        
        if not user_input:
            return jsonify({"error": "Please enter a topic"}), 400

        # Create precise prompt
        prompt = f"""Write a {word_count}-word {tone} about: "{user_input}".
        
        Structure:
        1. Engaging introduction
        2. 2-3 subheadings with detailed content
        3. Practical examples
        4. Concise conclusion
        
        Important:
        - Use only plain text (no markdown, asterisks or special formatting)
        - Never include phrases like "here's a blog post" or disclaimers
        """
        
        # Generate content
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.7,
                "max_output_tokens": 2000
            }
        )
        
        # Extract text safely
        if not response.candidates:
            return jsonify({"error": "No response generated"}), 400
            
        if hasattr(response.candidates[0].content, 'parts'):
            generated_text = response.candidates[0].content.parts[0].text
        else:
            generated_text = response.text
            
        return jsonify({"content": generated_text})

    except Exception as e:
        return jsonify({"error": f"Generation failed: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
