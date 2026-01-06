import requests
from app.config import settings

def get_event_details(event_id: str):
    # Assuming Event Service could be the same endpoint or we need a new env var.
    # For now, let's try to query the same endpoint or fallback to mock if url is not distinct.
    # Actually, usually getting event details is needed.
    
    query = """
    query GetEvent($id: ID!) {
        event(id: $id) {
            id
            title
            description
        }
    }
    """
    variables = {"id": event_id}
    
    try:
        response = requests.post(
            settings.EVENT_SERVICE_URL,
            json={"query": query, "variables": variables},
            timeout=5
        )
        response.raise_for_status()
        data = response.json()
        
        if "data" in data and data["data"].get("event"):
            return data["data"]["event"]
            
        return None
        
    except Exception as e:
        print(f"Connection failed ({e}). Using MOCK data for Event.")
        return {
            "id": event_id,
            "name": "Simulated Event (Offline Mode)",
            "description": "This is a mock event because connection failed."
        }
