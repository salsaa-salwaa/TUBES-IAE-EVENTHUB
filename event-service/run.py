from flask import Flask, make_response
from flask_graphql import GraphQLView
from app.schema import schema
from app.graphiql_modern import MODERN_GRAPHIQL_HTML

app = Flask(__name__)

# GraphQL POST endpoint
app.add_url_rule(
    "/graphql",
    view_func=GraphQLView.as_view(
        "graphql",
        schema=schema,
        graphiql=False  # Disable default GraphiQL
    ),
    methods=['POST']
)

# Custom GraphiQL UI with header support
@app.route('/graphql', methods=['GET'])
def graphql_playground():
    return make_response(MODERN_GRAPHIQL_HTML)

import time
from app.database import engine, Base

# RETRY DATABASE CONNECTION
retries = 5
while retries > 0:
    try:
        # CREATE TABLES
        Base.metadata.create_all(bind=engine)
        print("✅ Database connected and tables created")
        break
    except Exception as e:
        retries -= 1
        print(f"❌ Database error: {e}. Retrying in 5s... ({retries} left)")
        time.sleep(5)
else:
    print("❌ Failed to connect to database after retries")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4001, debug=True)