import os
from flask import Flask, request, jsonify, render_template
from openai import AzureOpenAI
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

# Load environment variables
load_dotenv()

# Fetch API credentials from .env
api_key = os.getenv("AZURE_OPENAI_API_KEY")
api_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_version = os.getenv("AZURE_OPENAI_API_VERSION")
deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")  # Ensure this is added in .env

# Azure Search Configuration
SEARCH_SERVICE_ENDPOINT = os.getenv("SEARCH_SERVICE_ENDPOINT")
SEARCH_ADMIN_KEY = os.getenv("SEARCH_ADMIN_KEY")
SEARCH_INDEX_NAME = os.getenv("SEARCH_INDEX_NAME")

# Initialize Azure OpenAI client
client = AzureOpenAI(
    api_key=api_key,
    azure_endpoint=api_endpoint,
    api_version=api_version
)

# Initialize Search Client
search_client = SearchClient(
    endpoint=SEARCH_SERVICE_ENDPOINT,
    index_name=SEARCH_INDEX_NAME,   
    credential=AzureKeyCredential(SEARCH_ADMIN_KEY)
)

def get_search_results(query):
    """Retrieve search results from Azure Search."""
    results = search_client.search(search_text=query)
    chunks = [{"title": result.get("title", "No Title"), "text": result.get("text", "No Text Available")} for result in results]
    return chunks

def chat_with_gpt(query, search_context):
    """Retrieve GPT response using search results as context."""
    system_message = f"You are an AI assistant. Use the following search results to provide relevant information:\n\n{search_context}"

    response = client.chat.completions.create(
        model=deployment_name,  
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": query}
        ],
        max_tokens=150,
        temperature=0,
        top_p=1,
    )
    
    return response.choices[0].message.content 

# Initialize Flask app
app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    gpt_response = ""
    search_results = []
    
    if request.method == "POST":
        query = request.form.get("query")  # Use .get() to prevent errors
        
        if query:
            # Get search results
            search_results = get_search_results(query)

            # Extract context from the first search result
            search_context = search_results[0]["text"] if search_results else "No relevant search results found."

            # Get GPT response
            gpt_response = chat_with_gpt(query, search_context)

    return render_template("index.html", results=search_results, response=gpt_response)

if __name__ == "__main__":
    app.run(debug=True)
