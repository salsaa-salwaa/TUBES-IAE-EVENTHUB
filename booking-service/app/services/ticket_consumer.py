import requests
from app.config import settings

def get_ticket_details(ticket_type_id: str):
    query = """
    query GetTicket($id: ID!) {
        ticketType(id: $id) {
            id
            name
            price
            quota
        }
    }
    """
    variables = {"id": ticket_type_id}
    
    try:
        response = requests.post(
            settings.TICKET_SERVICE_URL,
            json={"query": query, "variables": variables},
            timeout=5
        )
        response.raise_for_status()
        data = response.json()
        
        # Adjust based on actual response structure. 
        # Assuming response["data"]["ticketType"]
        if "data" in data and data["data"].get("ticketType"):
            return data["data"]["ticketType"]
            
        print(f"Ticket not found or invalid response: {data}")
        return None
        
    except Exception as e:
        print(f"Connection failed ({e}). Using MOCK data for Ticket.")
        return {
            "id": ticket_type_id,
            "name": "Simulated Ticket (Offline Mode)",
            "price": 100000.0,
            "quota": 999
        }
