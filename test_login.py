import requests

url = "http://localhost:8004/graphql"
query = """
mutation {
  login(email: "admin@example.com", password: "admin123") {
    accessToken
    user {
      id
      email
    }
  }
}
"""

try:
    response = requests.post(url, json={'query': query})
    print(response.status_code)
    print(response.text)
except Exception as e:
    print(f"Error: {e}")
