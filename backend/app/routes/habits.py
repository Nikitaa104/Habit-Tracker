from flask import Blueprint, request, jsonify
from marshmallow import ValidationError

from app.schemas import HabitCreateSchema, HabitUpdateSchema
from app.services.habit_service import HabitService, HabitNotFoundError

habits_bp = Blueprint("habits", __name__)

_create_schema = HabitCreateSchema()
_update_schema = HabitUpdateSchema()


@habits_bp.route("", methods=["GET"])
def list_habits():
    include_archived = request.args.get("archived", "false").lower() == "true"
    habits = HabitService.list_habits(include_archived=include_archived)
    return jsonify([h.to_dict() for h in habits]), 200


@habits_bp.route("", methods=["POST"])
def create_habit():
    try:
        data = _create_schema.load(request.get_json(force=True) or {})
    except ValidationError as exc:
        return jsonify({"errors": exc.messages}), 422

    habit = HabitService.create_habit(**data)
    return jsonify(habit.to_dict()), 201


@habits_bp.route("/<int:habit_id>", methods=["GET"])
def get_habit(habit_id: int):
    try:
        habit = HabitService.get_habit(habit_id)
    except HabitNotFoundError as exc:
        return jsonify({"error": str(exc)}), 404
    return jsonify(habit.to_dict()), 200


@habits_bp.route("/<int:habit_id>", methods=["PATCH"])
def update_habit(habit_id: int):
    try:
        data = _update_schema.load(request.get_json(force=True) or {})
    except ValidationError as exc:
        return jsonify({"errors": exc.messages}), 422

    try:
        habit = HabitService.update_habit(habit_id, **data)
    except HabitNotFoundError as exc:
        return jsonify({"error": str(exc)}), 404

    return jsonify(habit.to_dict()), 200


@habits_bp.route("/<int:habit_id>", methods=["DELETE"])
def delete_habit(habit_id: int):
    try:
        HabitService.delete_habit(habit_id)
    except HabitNotFoundError as exc:
        return jsonify({"error": str(exc)}), 404
    return "", 204
