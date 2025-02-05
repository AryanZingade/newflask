import os
<<<<<<< HEAD
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
=======
from flask import Flask, render_template, request
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from openai import AzureOpenAI
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

app = Flask(__name__)

# Azure Search Configuration
SEARCH_SERVICE_ENDPOINT = os.getenv("SEARCH_SERVICE_ENDPOINT")
SEARCH_ADMIN_KEY = os.getenv("SEARCH_ADMIN_KEY")
SEARCH_INDEX_NAME = os.getenv("SEARCH_INDEX_NAME")

# Azure OpenAI Configuration
client = AzureOpenAI(
    api_key=os.getenv("OPENAI_GPT_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("OPENAI_GPT_ENDPOINT")
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
        model='gpt-4o',
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": query}
        ],
        max_tokens=150,
        temperature=0,
        top_p=1,
    )
    
    return response.choices[0].message.content 

@app.route("/", methods=["GET", "POST"])
def index():
    gpt_response = ""
    search_results = []
    
    if request.method == "POST":
        query = request.form["query"]
        
        # Get search results
        search_results = get_search_results(query)

        # Extract context from the first search result
        search_context = search_results[0]["text"] if search_results else "No relevant search results found."
        
        # Get GPT response
        gpt_response = chat_with_gpt(query, search_context)

    return render_template("index.html", results=search_results, response=gpt_response)
>>>>>>> ef2cafa (second commit to app)

if __name__ == "__main__":
    app.run(debug=True)
