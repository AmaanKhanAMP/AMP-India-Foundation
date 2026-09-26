"""AMP India Foundation — Flask API application factory."""

from pathlib import Path

from flask import Flask, jsonify

from config import Config
from extensions import db, migrate, cors


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    upload_root = Path(app.root_path) / "uploads"
    upload_root.mkdir(parents=True, exist_ok=True)
    app.config["UPLOAD_FOLDER"] = str(upload_root)

    db.init_app(app)
    migrate.init_app(app, db)

    # CORS: explicit origins only (never "*"). JWT auth uses Authorization
    # header, so credentials are off by default — set CORS_SUPPORTS_CREDENTIALS
    # if you later need cookie-based cross-origin auth.
    cors.init_app(
        app,
        resources={
            r"/api/*": {
                "origins": app.config["CORS_ORIGINS"],
                "methods": ["GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
                "expose_headers": ["Content-Type"],
                "supports_credentials": app.config["CORS_SUPPORTS_CREDENTIALS"],
                "send_wildcard": False,
                "always_send": True,
            }
        },
    )

    # Models must be imported so Flask-Migrate can detect them
    from models import contact_message  # noqa: F401
    from models import cms_models  # noqa: F401
    from models import chat_message  # noqa: F401

    from routes.health_routes import health_bp
    from routes.contact_routes import contact_bp
    from routes.auth_routes import auth_bp
    from routes.content_routes import admin_content_bp, public_content_bp
    from routes.upload_routes import upload_bp
    from routes.admin_contact_routes import admin_contact_bp
    from routes.dashboard_routes import dashboard_bp
    from routes.chat_routes import chat_bp
    from routes.chatbot_sync_routes import chatbot_sync_bp
    from routes.section_visibility_routes import admin_sections_bp, public_sections_bp
    from routes.layout_routes import admin_layout_bp, public_layout_bp

    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(contact_bp, url_prefix="/api/contact")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(admin_content_bp, url_prefix="/api/admin/content")
    app.register_blueprint(public_content_bp, url_prefix="/api/content")
    app.register_blueprint(upload_bp, url_prefix="/api/admin/upload")
    app.register_blueprint(admin_contact_bp, url_prefix="/api/admin/contact")
    app.register_blueprint(dashboard_bp, url_prefix="/api/admin/dashboard")
    app.register_blueprint(chat_bp, url_prefix="/api/chat")
    app.register_blueprint(chatbot_sync_bp, url_prefix="/api/admin/chatbot")
    app.register_blueprint(admin_sections_bp, url_prefix="/api/admin/sections")
    app.register_blueprint(public_sections_bp, url_prefix="/api/sections")
    app.register_blueprint(admin_layout_bp, url_prefix="/api/admin/layout")
    app.register_blueprint(public_layout_bp, url_prefix="/api/layout")

    # Warm the chatbot knowledge cache once at startup (Phase 2)
    try:
        from services.knowledge_loader import load_knowledge

        load_knowledge()
    except Exception:
        # Non-fatal — first chat request will retry loading
        pass

    @app.get("/uploads/<path:filepath>")
    def serve_uploads(filepath):
        from utils.uploads import send_cached_upload

        return send_cached_upload(app.config["UPLOAD_FOLDER"], filepath)

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({"success": False, "message": "Resource not found."}), 404

    @app.errorhandler(500)
    def server_error(_error):
        return jsonify({"success": False, "message": "Internal server error."}), 500

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
