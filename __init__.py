# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate
# from flask_login import LoginManager
# from werkzeug.security import generate_password_hash

# db = SQLAlchemy()
# migrate = Migrate()

# def create_app():
#     app = Flask(__name__)
#     app.secret_key = "your_secret_key"

#     # ---------- MySQL Connection ----------
#     app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:1234@localhost/pld_lab'

#     #app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+mysqlconnector://root:yourpassword@localhost/library_fine"
#     app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#     db.init_app(app)
#     migrate.init_app(app, db)

#     # ---------- Login Manager ----------
#     login_manager = LoginManager()
#     login_manager.login_view = "auth.login"
#     login_manager.init_app(app)

#     from app.models import User

#     @login_manager.user_loader
#     def load_user(user_id):
#         return User.query.get(int(user_id))

#     # ---------- Register Blueprints ----------
#     from app.routes.auth import auth_bp
#     from app.routes.tasks import task_bp

#     app.register_blueprint(auth_bp)
#     app.register_blueprint(task_bp)

#     # ---------- Create tables if not exist ----------
#     with app.app_context():
#         db.create_all()

#         # Create default admin user if missing
#         if not User.query.filter_by(username="admin").first():
#             admin = User(username="admin", is_admin=True)
#             admin.set_password("admin123")
#             db.session.add(admin)
#             db.session.commit()

#     return app
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from werkzeug.security import generate_password_hash
import os 

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    

    app.secret_key = os.urandom(24) 

    # ---------- MySQL Connection ----------
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:1234@localhost/pld_lab'

    #app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+mysqlconnector://root:yourpassword@localhost/library_fine"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)

    # ---------- Login Manager ----------
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # ---------- Register Blueprints ----------
    from app.routes.auth import auth_bp
    from app.routes.tasks import task_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(task_bp)

    # ---------- Create tables if not exist ----------
    with app.app_context():
        db.create_all()

        # Create default admin user if missing
        if not User.query.filter_by(username="admin").first():
            admin = User(username="admin", is_admin=True)
            admin.set_password("admin123")
            db.session.add(admin)
            db.session.commit()

    return app