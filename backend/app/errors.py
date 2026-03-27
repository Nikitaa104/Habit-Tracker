from flask import Flask, jsonify
import logging

logger = logging.getLogger(__name__)


def register_error_handlers(app: Flask) -> None:

    @app.errorhandler(404)
    def not_found(exc):
        return jsonify({"error": "Resource not found."}), 404

    @app.errorhandler(405)
    def method_not_allowed(exc):
        return jsonify({"error": "Method not allowed."}), 405

    @app.errorhandler(400)
    def bad_request(exc):
        return jsonify({"error": "Bad request."}), 400

    @app.errorhandler(Exception)
    def unhandled(exc):
        logger.exception("Unhandled exception: %s", exc)
        return jsonify({"error": "An unexpected error occurred."}), 500
