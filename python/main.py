import requests
# from awsome_repos import generate_json_file
# from ai_tool_collections import generate_json_file
from ai_ml_rust_repo_github import generate_json_file

# Example usage
if __name__ == "__main__":
    try:
        generate_json_file()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")