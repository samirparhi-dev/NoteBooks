import requests
import toml

# GitHub API token
GITHUB_TOKEN = input("Please enter your Github API token: ")

# GitHub API headers
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# Function to fetch repositories with a specific tag and Rust language
def fetch_repositories():
    url = "https://api.github.com/search/repositories"
    query = "language:rust+is:public+has:tag"
    params = {"q": query, "sort": "stars", "order": "desc", "per_page": 100}
    
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    return response.json()["items"]

# Function to fetch the language breakdown for a repository
def fetch_language_percentage(repo_url):
    response = requests.get(f"{repo_url}/languages", headers=HEADERS)
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
    repo_metadata = []
    
    for repo in repos:
        name = repo["name"]
        url = repo["html_url"]
        avatar_url = repo["owner"]["avatar_url"]
        languages_url = repo["url"]
        rust_percentage = fetch_language_percentage(languages_url)
        
        if rust_percentage > 60:  # Filter based on Rust language percentage
            last_updated = fetch_last_commit_date(repo["url"])
            repo_metadata.append({
                "name": name,
                "url": url,
                "rustLangPercentage": f"{rust_percentage:.2f}%",
                "lastUpdated": last_updated,
                "gitHubAvtarURL": avatar_url
            })
    
    # Save to TOML file
    config = {"awsome_repo_metadata": repo_metadata}
    with open("awsome-rust-repo-config.toml", "w") as toml_file:
        toml.dump(config, toml_file)

    print("TOML file generated successfully!")

# Run the script
if __name__ == "__main__":
    generate_toml_file()
