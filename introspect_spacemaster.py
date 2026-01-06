import requests
import json

url = "https://4639a4b9effa.ngrok-free.app/graphql"
headers = {
    "Content-Type": "application/json",
    "ngrok-skip-browser-warning": "true"
}

query = """
query {
  __type(name: "Room") {
    name
    fields {
      name
      type {
        name
        kind
        ofType {
          name
          kind
        }
      }
    }
  }
}
"""

try:
    response = requests.post(url, json={'query': query}, headers=headers)
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Error: {e}")
