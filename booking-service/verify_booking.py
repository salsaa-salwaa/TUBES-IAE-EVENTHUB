import requests
import time
import subprocess
import sys
import os

# Start server
print("Starting server...")
server_process = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "app.main:app", "--port", "8001"],
    cwd=os.getcwd(),
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

time.sleep(5) # Wait for server to start

BASE_URL = "http://127.0.0.1:8001"
GRAPHQL_URL = f"{BASE_URL}/graphql"
HEADERS = {"Authorization": "Bearer testuser123"}

def run_query(query, variables=None):
    response = requests.post(
        GRAPHQL_URL,
        json={"query": query, "variables": variables},
        headers=HEADERS
    )
    if response.status_code != 200:
        print(f"Error: {response.text}")
        return None
    return response.json()

try:
    # 1. Create Booking
    print("Testing createBooking...")
    mutation = """
    mutation CreateBooking($input: CreateBookingInput!) {
        createBooking(input: $input) {
            id
            eventId
            userId
            ticketTypeId
            quantity
            totalPrice
            status
        }
    }
    """
    variables = {
        "input": {
            "eventId": "1",
            "ticketTypeId": "1",
            "quantity": 2
        }
    }
    
    result = run_query(mutation, variables)
    print("Create Result:", result)
    
    if "errors" in result:
        print("Create Booking Failed")
        # Don't exit yet, try reading logs
    else:
        booking = result["data"]["createBooking"]
        booking_id = booking["id"]
        assert booking["quantity"] == 2
        assert booking["totalPrice"] == 200.0
        assert booking["status"] == "PENDING"
        print("Create Booking Success")

        # 2. Get Booking
        print("Testing booking(id)...")
        query = """
        query GetBooking($id: Int!) {
            booking(id: $id) {
                id
                status
            }
        }
        """
        result = run_query(query, {"id": int(booking_id)})
        print("Get Result:", result)
        assert result["data"]["booking"]["id"] == booking_id
        print("Get Booking Success")

        # 3. Cancel Booking
        print("Testing cancelBooking...")
        mutation = """
        mutation CancelBooking($id: Int!) {
            cancelBooking(id: $id) {
                id
                status
            }
        }
        """
        result = run_query(mutation, {"id": int(booking_id)})
        print("Cancel Result:", result)
        assert result["data"]["cancelBooking"]["status"] == "CANCELLED"
        print("Cancel Booking Success")

except Exception as e:
    print(f"Test Failed: {e}")

finally:
    print("Stopping server...")
    server_process.terminate()
    server_process.wait()
    print("Server stopped.")
