from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

from app.config import config_by_name

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_name: str = "development") -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Register blueprints
    from app.routes.habits import habits_bp
    from app.routes.completions import completions_bp
    from app.routes.health import health_bp

    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(habits_bp, url_prefix="/api/habits")
    app.register_blueprint(completions_bp, url_prefix="/api/habits")

    # Register global error handlers
    from app.errors import register_error_handlers
    register_error_handlers(app)

    return app
