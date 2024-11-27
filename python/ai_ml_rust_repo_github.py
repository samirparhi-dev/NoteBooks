import requests
import toml
import json
from datetime import datetime

print("Fetching top AI ML Rust repositories...")

#Load the GitHub Authentication from config.toml

config = toml.load("config.toml")
GITHUB_TOKEN = config["github"]["token"]
if not GITHUB_TOKEN:
    raise ValueError("GITHUB_TOKEN is not set in the `config.toml` file")

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

keywords = [
    "nlp", "machine-learning", "natural-language-processing",
    "deep-learning", "tensorflow","transformer", 
    "speech-recognition", "seq2seq", "flax", "pretrained-models", 
    "language-models", "encoder-decoder-model", "encoder-decoder","llm", "nlp"
]

# Function to fetch repositories with the Rust language
def fetch_repositories():
    url = "https://api.github.com/search/repositories"
    query = "language:rust"
    params = {"q": query, "sort": "stargazers_count", "order": "desc", "per_page": 20000}
    
    response = requests.get(url, params=params, headers=HEADERS)
    response.raise_for_status()
    return response.json()["items"]

# Function to fetch the language breakdown for a repository
def fetch_language_percentage(repo_url):
        lang_url= f"{repo_url}/languages"
        response = requests.get(lang_url, headers=HEADERS)
        if repo_url != "https://api.github.com/repos/rust-lang/rust/languages":
            response.raise_for_status()
            data = response.json()
            rust_code = data.get("Rust", 0)
            total_code = sum(data.values())
            percentage = (rust_code / total_code) * 100
            trimmed_percentage = float(str(percentage)[:str(percentage).find('.') + 2])
            return trimmed_percentage if trimmed_percentage > 0 else 0

# Function to fetch the last commit date
def fetch_last_commit_date(repo_url):
    commits_url = f"{repo_url}/commits"
    response = requests.get(commits_url, headers=HEADERS)
    response.raise_for_status()
    commits = response.json()
    if commits:
        return commits[0]["commit"]["committer"]["date"]
    return "N/A"
def format_date(utc_date_str):
    # Parse the ISO 8601 UTC date string
    utc_date = datetime.strptime(utc_date_str, "%Y-%m-%dT%H:%M:%SZ")
    # Format the date to "18-nov-2024"
    formatted_date = utc_date.strftime("%d-%b-%Y").lower()
    return formatted_date
# Main function to generate the TOML file
def generate_json_file():
    keywords = [
        "nlp", "machine-learning", "natural-language-processing", "deep-learning", "tensorflow", "pytorch", "transformer", "speech-recognition", "seq2seq", "flax", "pretrained-models", "language-models", "encoder-decoder-model", "encoder-decoder","vector-database", "vector-search", "vector-search-engine", "mlops", "approximate-nearest-neighbor-search","embeddings-similarity","hacktoberfest","hnsw","image-search","knn-algorithm","machine-learning","matching","ai","ai-ml", "ml", "nearest-neighbor-search", "neural-network", "neural-search", "recommender-system", "search", "search-engine", "similarity-search",
    ]
    keywords_set = set(keyword.lower() for keyword in keywords)

    repos = fetch_repositories()
    sorted_repos = sorted(repos, key=lambda x: x["forks_count"], reverse=True)
    print(f"Adding {len(sorted_repos)} repos...")
    
    ai_ml_rust_awesome_rust_repo_metadata = []
    
    for repo in sorted_repos:
        topics_set = set(topic.lower() for topic in repo.get("topics", []))  # Fixed the generator expression
        common_keywords = keywords_set.intersection(topics_set)
        if common_keywords:
            name = repo["name"]
            repo_description = repo.get("description", "No description provided")
            url = repo["html_url"]
            avatar_url = repo["owner"]["avatar_url"]
            languages_url = repo["url"]
            rust_percentage = fetch_language_percentage(languages_url)
            forks_count = repo["forks_count"]
            open_issues = repo["open_issues"]
            git_url = repo["git_url"]
            last_updated = format_date(fetch_last_commit_date(repo["url"]))
            topic=repo["topics"]

            # Handle license and spdx_id safely
            try:
                license = repo["license"]["name"]
                spdx_id = repo["license"]["spdx_id"]
            except (TypeError, KeyError):
                license = "Unknown"
                spdx_id = "Unknown"
            if spdx_id=="NOASSERTION": spdx_id="Unknown"
            stargazers_count = repo["stargazers_count"]

            if rust_percentage:  # Filter based on Rust language percentage
                
                excluded_rust_list=["rust-analyzer", "Rust", "rust"]
                if name not in excluded_rust_list:
                    print(f"Adding {name}")
                    ai_ml_rust_awesome_rust_repo_metadata.append({
                        "name": name,
                        "repo_description": repo_description,
                        "url": url,
                        "rustLangPercentage": rust_percentage,
                        "lastUpdated": last_updated,
                        "gitHubAvtarURL": avatar_url,
                        "forks_count": forks_count,
                        "open_issues": open_issues,
                        "git_url": git_url,
                        "repo_license": license,
                        "repo_spdx_id": spdx_id,
                        "github_stars": stargazers_count,
                        "topic":topic
                    })
    # Save to JSON file
    with open("ai-ml-awsome-rust-repos-list.json", "w") as json_file:
                json.dump({"repos": ai_ml_rust_awesome_rust_repo_metadata}, json_file, indent=4)
    print("Json file generated successfully!")