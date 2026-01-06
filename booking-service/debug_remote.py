import requests
import json

# URL from .env (hardcoded for debug script based on what we know)
URL = "http://localhost:4001/graphql"

def debug_event(event_id):
    query = """
    query GetEvent($id: ID!) {
        event(id: $id) {
            id
            name
        }
    }
    """
    variables = {"id": event_id}
    
    print(f"Sending request to {URL}...")
    print(f"Query: {query}")
    print(f"Variables: {variables}")
    
    try:
        response = requests.post(
            URL,
            json={"query": query, "variables": variables},
            timeout=5
        )
        print(f"Status Code: {response.status_code}")
        print("Response Body:")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_event("cee1ebfe-76a3-4a7d-8f20-ba7160d1e0e3")
