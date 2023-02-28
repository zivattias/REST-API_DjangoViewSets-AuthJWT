from datetime import datetime

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