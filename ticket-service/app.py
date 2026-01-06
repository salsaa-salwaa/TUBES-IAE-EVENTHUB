from flask import Flask
from flask_graphql import GraphQLView
from config import db, get_database_uri
from schema import schema

app = Flask(__name__)
from flask_cors import CORS
CORS(app, resources={r"/*": {"origins": "*"}}, allow_headers=["Content-Type", "Authorization"])

app.config["SQLALCHEMY_DATABASE_URI"] = get_database_uri()
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

from graphiql_modern import MODERN_GRAPHIQL_HTML
from flask import make_response

app.add_url_rule(
    "/graphql",
    view_func=GraphQLView.as_view(
        "graphql",
        schema=schema,
        graphiql=False
    ),
    methods=['POST']
)

@app.route("/graphql", methods=["GET"])
def graphql_playground():
    return make_response(MODERN_GRAPHIQL_HTML)

@app.route("/playground", methods=["GET"])
def playground():
    return make_response(MODERN_GRAPHIQL_HTML)


if __name__ == "__main__":
    import time
    with app.app_context():
        retries = 5
        while retries > 0:
            try:
                db.create_all()
                print("Database connected and tables created!")
                break
            except Exception as e:
                retries -= 1
                print(f"Database connection failed, retrying in 5s... ({retries} left)")
                print(f"Error: {e}")
                time.sleep(5)
        else:
            print("Failed to connect to database after retries")

    app.run(host="0.0.0.0", port=4002)
