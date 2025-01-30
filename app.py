import os
from flask import Flask, request, jsonify, render_template
from openai import AzureOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Fetch API credentials from .env
api_key = os.getenv("AZURE_OPENAI_API_KEY")
api_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_version = os.getenv("AZURE_OPENAI_API_VERSION")
deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")  # Ensure this is added in .env

# Initialize Azure OpenAI client
client = AzureOpenAI(
    api_key=api_key,
    azure_endpoint=api_endpoint,
    api_version=api_version
)

# Initialize Flask app
app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_query = request.form.get("query")  # Use .get() to prevent errors
        if user_query:
            response_text = generate_text(user_query)
            return render_template("index.html", query=user_query, response=response_text)
    return render_template("index.html")

def generate_text(prompt):
    try:
        response = client.chat.completions.create(
            model=deployment_name,  
            messages=[
                {"role": "system", "content": "You are an AI assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100
        )
        return response.choices[0].message.content  
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    app.run(debug=True)
