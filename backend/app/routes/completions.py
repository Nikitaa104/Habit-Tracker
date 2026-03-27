from datetime import date

from flask import Blueprint, request, jsonify
from marshmallow import ValidationError

from app.schemas import CompletionCreateSchema
from app.services.habit_service import HabitService, HabitNotFoundError, DuplicateCompletionError

completions_bp = Blueprint("completions", __name__)

_completion_schema = CompletionCreateSchema()


@completions_bp.route("/<int:habit_id>/completions", methods=["GET"])
def list_completions(habit_id: int):
    try:
        completions = HabitService.list_completions(habit_id)
    except HabitNotFoundError as exc:
        return jsonify({"error": str(exc)}), 404
    return jsonify([c.to_dict() for c in completions]), 200


@completions_bp.route("/<int:habit_id>/completions", methods=["POST"])
def log_completion(habit_id: int):
    try:
        data = _completion_schema.load(request.get_json(force=True) or {})
    except ValidationError as exc:
        return jsonify({"errors": exc.messages}), 422

    try:
        completion = HabitService.log_completion(
            habit_id=habit_id,
            completed_on=data.get("completed_on"),
            note=data.get("note"),
        )
    except HabitNotFoundError as exc:
        return jsonify({"error": str(exc)}), 404
    except DuplicateCompletionError as exc:
        return jsonify({"error": str(exc)}), 409

    return jsonify(completion.to_dict()), 201


@completions_bp.route("/<int:habit_id>/completions/<string:date_str>", methods=["DELETE"])
def undo_completion(habit_id: int, date_str: str):
    try:
        target_date = date.fromisoformat(date_str)
    except ValueError:
        return jsonify({"error": "date must be in YYYY-MM-DD format."}), 400

    try:
        HabitService.undo_completion(habit_id=habit_id, target_date=target_date)
    except HabitNotFoundError as exc:
        return jsonify({"error": str(exc)}), 404

    return "", 204
