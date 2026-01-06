import asyncio
from app.schema.schema import schema

async def test_schema():
    query = """
    query {
        bookingsByUser(userId: "test_user") {
            id
            status
        }
    }
    """
    # Mock context with a dummy db session (won't be used deeply if we don't return data, 
    # but let's see if it errors out purely on schema structure)
    class MockDB:
        def execute(self, *args, **kwargs):
            raise NotImplementedError("DB not mocked fully")
            
    # We might need to mock get_bookings_by_user to avoid DB calls if we just want to verify schema definition.
    # However, let's try to just check if schema is valid.
    
    print("Schema is valid:", schema is not None)
    
    # Introspection query is a good test that doesn't hit the DB if resolvers aren't called for __schema
    introspection_query = """
    {
        __schema {
            types {
                name
            }
        }
    }
    """
    result = await schema.execute_async(introspection_query)
    if result.errors:
        print("Introspection Errors:", result.errors)
    else:
        print("Introspection Successful")

if __name__ == "__main__":
    asyncio.run(test_schema())
