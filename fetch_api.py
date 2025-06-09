import requests

def fetch_neighbors_securely():
    url = "https://adventure-time.hackclub.dev/api/getNeighborsSecurely"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None