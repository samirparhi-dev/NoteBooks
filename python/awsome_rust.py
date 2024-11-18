import requests
import toml
import json

print("Fetching top Rust repositories...")

#Load the GitHub Authentication from config.toml

config = toml.load("config.toml")
GITHUB_TOKEN = config["github"]["token"]
if not GITHUB_TOKEN:
    raise ValueError("GITHUB_TOKEN is not set in the `config.toml` file")

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# Function to fetch repositories with the Rust language
def fetch_repositories():
    url = "https://api.github.com/search/repositories"
    query = "language:rust"
    # params = {"q": query, "sort": "stars", "order": "desc", "per_page": 100}
    params = {"q": query, "sort": "stars", "per_page": 2000}
    
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
            return (rust_code / total_code) * 100 if total_code > 0 else 0

# Function to fetch the last commit date
def fetch_last_commit_date(repo_url):
    commits_url = f"{repo_url}/commits"
    response = requests.get(commits_url, headers=HEADERS)
    response.raise_for_status()
    commits = response.json()
    if commits:
        return commits[0]["commit"]["committer"]["date"]
    return "N/A"

# Main function to generate the TOML file
def generate_toml_file():
    repos = fetch_repositories()
    awesome_rust_repo_metadata = []
    
    for repo in repos:
        name = repo["name"]
        repo_description = repo["description"]
        url = repo["html_url"]
        avatar_url = repo["owner"]["avatar_url"]
        languages_url = repo["url"]
        rust_percentage = fetch_language_percentage(languages_url)
        forks_count= repo["forks_count"]
        open_issues = repo["open_issues"]
        git_url = repo["git_url"]
        last_updated = fetch_last_commit_date(repo["url"])

        if rust_percentage > 60:  # Filter based on Rust language percentage
            print(f"adding {name}")
            awesome_rust_repo_metadata.append({
                "name": name,
                "repo_description": repo_description,
                "url": url,
                "rustLangPercentage": rust_percentage,
                "lastUpdated": last_updated,
                "gitHubAvtarURL": avatar_url,
                "forks_count": forks_count,
                "open_issues": open_issues,
                "git_url": git_url
            })
    
    # Save to JSON file
    with open("repositories.json", "w") as json_file:
                json.dump({"repos": awesome_rust_repo_metadata}, json_file, indent=4)
    print("Json file generated successfully!")