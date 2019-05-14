import calendar
import logging
import uuid
from datetime import datetime

logger = logging.getLogger("rest utils")


def check_uuid(suuid: str) -> bool:
    try:
        uuid.UUID(suuid)
        return True
    except (ValueError, TypeError):
        return False


def random_with_n_digits(n):
    range_start = 10 ** (n - 1)
    range_end = (10 ** n) - 1
    from random import randint
    return randint(range_start, range_end)


def random_x(minX, maxX):
    import random
    return random.randint(minX, maxX)


def get_unixtime() -> int:
    d = datetime.utcnow()
    unixtime = calendar.timegm(d.utctimetuple())
    return unixtime


def gen_sec_token() -> str:
    token = ""
    ruuid = str(uuid.uuid4())
    ruuid = ruuid.replace("-", "")
    ruuid_len = len(ruuid)
    r4 = str(random_x(1, ruuid_len))
    token += ruuid

    unixtime = get_unixtime()
    unixtime_divided = int(unixtime) / int(r4)
    unixtime_divided_rounded = "%.10f" % (unixtime_divided)

    unixtime_divided_len = str(len(str(unixtime_divided_rounded)))
    if len(unixtime_divided_len) == 1:
        unixtime_divided_len = "0" + str(unixtime_divided_len)

    left_token = token[:int(r4)]
    center_token = str(unixtime_divided_rounded)
    right_token = token[int(r4):]
    token = left_token + center_token + right_token
    if len(r4) == 1:
        r4 = "0" + str(r4)
    token = str(r4) + str(unixtime_divided_len) + token

    return token


def check_sec_token(token) -> bool:
    if token is None:
        return False

    try:
        r4 = token[0:2]
        unixtime_len = token[2:4]

        if r4[0] == "0":
            r4 = int(r4[1])
        else:
            r4 = int(r4)

        if unixtime_len[0] == "0":
            unixtime_len = int(unixtime_len[1])
        else:
            unixtime_len = int(unixtime_len)

        token = token[4:]
        unixtime = str(token[int(r4):int(unixtime_len) + int(r4)])

        if unixtime.find(".") != -1:
            unixtime = float(unixtime)
        elif unixtime.find(",") != -1:
            unixtime = unixtime.replace(",", ".")
            unixtime = float(unixtime)
        else:
            unixtime = int(unixtime)
        unixtime = round(unixtime * int(r4))

        d = datetime.utcfromtimestamp(int(unixtime))
        now_d = datetime.utcnow()
        delta = now_d - d
        delta_list = divmod(delta.days * 86400 + delta.seconds, 60)
        # TODO think about minutes
        delta_minutes = delta_list[0]
        delta_seconds = delta_list[1]
        logger.debug(f"Difference between now date and token date is {delta_minutes} minutes and {delta_seconds} seconds")
        # return delta_minutes < 100
        return delta_minutes <= 1 and delta_seconds <= 41
    except ValueError:
        logger.error(f"ValueError to do security check for token={token}")
        return False
