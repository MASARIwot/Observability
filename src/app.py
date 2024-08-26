import sys
from flask import Flask
from flask_smorest import Api

from api import NS_TEST
from config import ConfigDocs
from telemetry import configure_opentelemetry  # Import the OpenTelemetry setup function


def register_blueprints(api):
    # Register the Blueprint with the API
    api.register_blueprint(NS_TEST)


def create_app():
    # Initialize Flask app
    app = Flask(__name__)

    # Configure Flask-Smorest
    app.config.from_object(ConfigDocs)

    # Initialize API with Flask-Smorest
    api = Api(app)
    # Register the Blueprints
    register_blueprints(api)
    # Configure OpenTelemetry
    configure_opentelemetry(app)
    print(app.url_map)
    return app

# app = create_app()

def main():
    # Check for command-line argument for port
    port = 5000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("Invalid port number. Defaulting to 5000.")
    create_app().run(port=port)


if __name__ == "__main__":
    # Run the Flask app
    main()
