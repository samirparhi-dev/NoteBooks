import requests
import toml
import json
from datetime import datetime

print("Fetching AI ML Collection")

#Load the Hugging Face Authentication from config.toml

config = toml.load("config.toml")

HF_TOKEN = config["hf"]["token"]
if not HF_TOKEN:
    raise ValueError("HF_TOKEN is not set in the `config.toml` file")

HEADERS = {
    "Authorization": f"Bearer {HF_TOKEN}"
}

# Function to fetch models from Huggingface
def fetch_repositories():
    # load_tools_names = toml.load("ai-tool-list.toml")
    # toolname = load_tools_names["tools"]["name"]
    hf_url = "https://huggingface.co/api/models"
    params={"sort":"downloads","limit":500,"full":"True","config":"True"}
    
    response = requests.get(hf_url, params=params, headers=HEADERS)
    print(response)
    response.raise_for_status()
    return response.json()

def get_spdx_url(license_name):
    url = "https://api.opensource.org/licenses/"
    response = requests.get(url)
    if response.status_code == 200:
        licenses = response.json()
        for license in licenses:
            if license_name.lower() == license["id"].lower():
                return license["links"]["url"]
        return "License not found."
    else:
        return f"Failed to fetch data. Status code: {response.status_code}"

def format_date(utc_date_str):
    try:
        # Format string to handle optional milliseconds
        if "." in utc_date_str:
            utc_date_str = utc_date_str.split(".")[0] + "Z"  # Remove milliseconds
        utc_date = datetime.strptime(utc_date_str, "%Y-%m-%dT%H:%M:%SZ")
        return utc_date
    except ValueError as e:
        print(f"Error parsing date: {e}")
        return None

# Main function to generate the JSON file

def generate_json_file():
    repos = fetch_repositories()
    print(f"adding {len(repos)} repos")
    ai_tool_tool_collection = []
    
    for repo in repos:
        name = repo["id"]
        author = repo.get("author", "Unknown")
        likes = repo.get("likes", 0)
        downloads = repo.get("downloads", 0)
        
        # Convert last updated date to datetime object
        last_updated = repo["lastModified"]
        converted_date = format_date(last_updated)
        
        # Handle license and spdx_id safely
        try:
            license = repo["tags"]["license"]
            license_URL = get_spdx_url(license)
        except (TypeError, KeyError):
            license = "Unknown"
            license_URL = "Unknown"
        
        if license_URL == "NOASSERTION":
            license_URL = "Unknown"
        formatted_date = converted_date.strftime("%d %b %Y") if converted_date else "Unknown"
        
        print(f"adding {name}")
        ai_tool_tool_collection.append({
            "name": name,
            "author": author,
            "likes": likes,
            "downloads": downloads,
            "lastUpdated": formatted_date,
            "license": license,
            "license_URL": license_URL,
        })
    
    # Save to JSON file
    with open("awsome-AI-ML-tools-collection.json", "w") as json_file:
        json.dump(ai_tool_tool_collection, json_file, indent=4)
    print("Json file generated successfully!")