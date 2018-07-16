import uuid


def check_uuid(suuid: str) -> bool:
    try:
        uuid.UUID(suuid)
        return True
    except (ValueError, TypeError):
        return False
