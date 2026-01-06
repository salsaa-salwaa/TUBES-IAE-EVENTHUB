from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_restx import Api, Resource, fields
from flask_migrate import Migrate
from models import db, User
from config import Config
import bcrypt
from werkzeug.exceptions import BadRequest
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import os

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)
# Allow CORS for all domains on all routes, specifically for Authorization header
CORS(app, resources={r"/*": {"origins": "*"}}, allow_headers=["Content-Type", "Authorization"])

from flask_graphql import GraphQLView
from schema import schema


# JWT Setup (still needed for Token generation)
jwt = JWTManager(app)

from graphiql_modern import MODERN_GRAPHIQL_HTML
from flask import make_response

# GraphQL Endpoint
# GraphQL Endpoint (POST only for processing)
app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view(
        'graphql',
        schema=schema,
        graphiql=False
    ),
    methods=['POST']
)

# Custom GraphiQL UI (Universal) - Served on GET /graphql
@app.route('/graphql', methods=['GET'])
def graphql_playground():
    return make_response(MODERN_GRAPHIQL_HTML)

@app.route('/playground')
def playground():
    return make_response(MODERN_GRAPHIQL_HTML)

# Root endpoint check
@app.route('/')
def index():
    return "User Service (GraphQL) is running! Go to /graphql"

if __name__ == '__main__':
    import time
    import pymysql

    with app.app_context():
        retries = 5
        while retries > 0:
            try:
                db.create_all()
                print("Database connected and tables created!")
                
                # Check for existing admin
                admin = User.query.filter_by(email="admin@example.com").first()
                if not admin:
                     hashed_pw = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                     new_admin = User(
                         name="Super Admin",
                         email="admin@example.com",
                         password=hashed_pw,
                         role="ADMIN",
                         phone_number="0000000000",
                         address="Admin HQ"
                     )
                     db.session.add(new_admin)
                     db.session.commit()
                     print("Default Admin created: admin@example.com / admin123")
                else:
                     print("Admin already exists.")
                break
            except Exception as e:
                retries -= 1
                print(f"Database connection failed, retrying in 5s... ({retries} left)")
                print(f"Error: {e}")
                time.sleep(5)
        else:
            print("Failed to connect to database after retries")
    print(f"User Service running on http://localhost:{Config.PORT}")
    print(f"GraphiQL Interface: http://localhost:{Config.PORT}/graphql")
    app.run(host='0.0.0.0', port=Config.PORT, debug=True)