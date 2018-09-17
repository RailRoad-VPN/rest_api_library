import calendar
import uuid
from datetime import datetime


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
    # print('---------------- gen token')
    token = ""
    ruuid = str(uuid.uuid4())
    ruuid = ruuid.replace("-", "")
    ruuid_len = len(ruuid)
    r4 = str(random_x(1, ruuid_len))
    token += ruuid
    unixtime = get_unixtime()
    # print("Unix time:" + str(unixtime))
    # print("Unix time len:" + str(len(str(unixtime))))
    unixtime_divided = "%.5f" % (int(unixtime) / int(r4))
    # print("Unix time divided:" + str(unixtime_divided))
    unixtime_divided_len = str(len(str(unixtime_divided)))
    if len(unixtime_divided_len) == 1:
        unixtime_divided_len = "0" + str(unixtime_divided_len)
    # print("Unix time rounded len:" + unixtime_divided_len )
    left_token = token[:int(r4)]
    center_token = str(unixtime_divided)
    right_token = token[int(r4):]
    token = left_token + center_token + right_token
    if len(r4) == 1:
        r4 = "0" + str(r4)
    token = str(r4) + str(unixtime_divided_len) + token
    # print("Random number:" + str(r4))
    # print("Token: " + str(token))
    return token


def check_sec_token(token) -> bool:
    if token is None:
        return False
    # print('---------------- check token')
    r4 = token[0:2]
    unixtime_len = token[2:4]
    # print("Raw number: " + str(r4))
    # print("Raw unixtime_len: " + str(unixtime_len))
    if r4[0] == "0":
        r4 = int(r4[1])
    else:
        r4 = int(r4)
    if unixtime_len[0] == "0":
        unixtime_len = int(unixtime_len[1])
    else:
        unixtime_len = int(unixtime_len)
    # print("Parsed number: " + str(r4))
    # print("Parsed unixtime_len: " + str(unixtime_len))

    token = token[4:]
    unixtime = token[int(r4):int(unixtime_len) + int(r4)]
    if str(unixtime).find("."):
        unixtime = float(unixtime)
    else:
        unixtime = int(unixtime)
    # print("Raw unixtime: " + str(unixtime))
    unixtime = round(unixtime * int(r4))
    # print("Parsed unixtime: " + str(unixtime))

    d = datetime.utcfromtimestamp(int(unixtime))
    now_d = datetime.utcnow()
    delta = now_d - d
    delta_list = divmod(delta.days * 86400 + delta.seconds, 60)
    # TODO think about minutes
    delta_minutes = delta_list[0]
    delta_seconds = delta_list[1]
    print(f"Difference between now date and token date is {delta_minutes} minutes and {delta_seconds} seconds")
    return delta_seconds < 5
