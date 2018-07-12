import json
import uuid
from datetime import datetime
from functools import singledispatch

# @singledispatch
# def to_serializable(val):
#     """Used by default."""
#     return str(val)
#
#
# @to_serializable.register(datetime)
# def ts_datetime(val):
#     """Used if *val* is an instance of datetime."""
#     return val.isoformat() + "Z"
#
#
# @to_serializable.register(uuid.UUID)
# def ts_uuid(val):
#     """Used if *val* is an instance of UUID."""
#     return str(val)
#
#
# @to_serializable.register(dict)
# def ts_dct(val):
#     """Used if *val* is an instance of dict."""
#     return json.dumps(val, default=to_serializable)


def check_uuid(suuid: str) -> bool:
    try:
        uuid.UUID(suuid)
        return True
    except (ValueError, TypeError):
        return False
