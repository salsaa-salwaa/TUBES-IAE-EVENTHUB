import jwt

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc2Njk0OTMxMSwianRpIjoiYjNlNGFkNzMtMDU0MS00YzJmLTlkY2EtZGI3YTk2ZmI5NWYxIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjQiLCJuYmYiOjE3NjY5NDkzMTEsImV4cCI6MTc2NzAzNTcxMX0.youd6HRUbYaQhLYOyqEffng2aRgT8wcwgExAP1Cn7yY"

try:
    # Decode header to check algorithm
    header = jwt.get_unverified_header(token)
    print("Header:", header)
    
    # Decode payload without verification
    payload = jwt.decode(token, options={"verify_signature": False})
    print("Payload:", payload)
    
    # Try verifying with the configured secret
    secret = "dev-secret-123"
    try:
        jwt.decode(token, secret, algorithms=["HS256"])
        print("SUCCESS: Token verified with 'dev-secret-123'")
    except Exception as e:
        print(f"FAILED: Verification failed with 'dev-secret-123': {e}")

except Exception as e:
    print(f"Error inspecting token: {e}")
