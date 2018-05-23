import decimal
import uuid

from flask import json


class JSONDecimalEncoder(json.JSONEncoder):
    def iterencode(self, o, _one_shot=False):
        if isinstance(o, decimal.Decimal):
            # wanted a simple yield str(o) in the next line,
            # but that would mean a yield on the line with super(...),
            # which wouldn't work (see my comment below), so...
            return (str(o) for o in [o])
        elif isinstance(o, uuid.UUID):
            # wanted a simple yield str(o) in the next line,
            # but that would mean a yield on the line with super(...),
            # which wouldn't work (see my comment below), so...
            return (str(o) for o in [o])
        return super().iterencode(o, _one_shot)


def check_uuid(suuid: str) -> bool:
    try:
        uuid.UUID(suuid)
        return True
    except ValueError:
        return False
