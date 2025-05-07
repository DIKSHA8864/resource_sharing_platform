from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate  # Import Flask-Migrate

# Initialize the database and migration tools
db = SQLAlchemy()
migrate = Migrate()  # Initialize Migrate

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'auth.login'  # This refers to the blueprint and function name
login_manager.login_message_category = 'info'

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # Initialize the app, db, login_manager, and migrate
    db.init_app(app)
    migrate.init_app(app, db)  # Initialize Migrate with app and db
    login_manager.init_app(app)

    # Import models (to ensure they are loaded for migrations)
    from .models import User

    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Import routes/blueprints
    from .routes import main as main_blueprint
    from .auth_routes import auth as auth_blueprint

    # Register blueprints for routes
    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint, url_prefix='/auth')  # ✅ Add URL prefix for auth

    return app
