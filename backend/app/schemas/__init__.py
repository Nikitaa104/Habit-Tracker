import re
from datetime import date
from marshmallow import Schema, fields, validate, validates, ValidationError, pre_load


HEX_COLOR_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")


class HabitCreateSchema(Schema):
    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=120, error="Name must be 1–120 characters."),
    )
    description = fields.Str(
        load_default=None,
        validate=validate.Length(max=500, error="Description must be ≤ 500 characters."),
    )
    frequency = fields.Str(
        load_default="daily",
        validate=validate.OneOf(["daily", "weekly"], error="frequency must be 'daily' or 'weekly'."),
    )
    color = fields.Str(load_default="#6366f1")

    @validates("color")
    def validate_color(self, value: str):
        if not HEX_COLOR_RE.match(value):
            raise ValidationError("color must be a valid hex code, e.g. #6366f1.")

    @pre_load
    def strip_strings(self, data, **kwargs):
        return {
            k: v.strip() if isinstance(v, str) else v
            for k, v in data.items()
        }


class HabitUpdateSchema(HabitCreateSchema):
    name = fields.Str(
        load_default=None,
        validate=validate.Length(min=1, max=120),
    )
    archived = fields.Bool(load_default=None)


class CompletionCreateSchema(Schema):
    completed_on = fields.Date(load_default=None)
    note = fields.Str(
        load_default=None,
        validate=validate.Length(max=300, error="Note must be ≤ 300 characters."),
    )

    @validates("completed_on")
    def not_future(self, value: date):
        if value and value > date.today():
            raise ValidationError("completed_on cannot be a future date.")
