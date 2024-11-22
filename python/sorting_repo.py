import json
repo_file = "awsome-rust-repos-list.json"
# Load JSON data from the file
with open(repo_file, "r") as file:
    data = json.load(file)

# Sorting the repositories by 'forks_count' in descending order
print(f"adding {len(data)} repos")