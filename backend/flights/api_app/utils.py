from datetime import datetime
from serializers import ValidationError

# Helper function to parse datetime objs, used in get_queryset() of FlightsViewSet
def parse_datetime_str(datetime_str: str) -> None | datetime:
    try:
        return datetime.strptime(datetime_str, "%d/%m/%Y %H:%M")
    except ValueError:
        pass
    try:
        return datetime.strptime(datetime_str, "%d/%m/%Y")
    except ValueError:
        pass
    return None

# Date strings converter to ISO format, which is save-able in DB & corresponds to DateTimeField()
def validate_datetime(self, value, default=None):
    if not value:
        return default

    try:
        return datetime.strptime(value, "%d/%m/%Y %H:%M").isoformat()
    except ValueError:
        raise ValidationError(
            "Invalid datetime format. Use the format DD/MM/YYYY HH:MM."
        )