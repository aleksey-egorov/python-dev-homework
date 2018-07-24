import hashlib
import json
import datetime
import random


class ScoringError(Exception):
    def __init__(self, error):
        self.message = "Scoring error - {}".format(error)


def get_score(store, phone, email, birthday=None, gender=None, first_name=None, last_name=None):

    def convert_birthday(birthday):
        try:
            dt = datetime.datetime.strptime(birthday, '%d.%m.%Y')
            return dt.strftime("%Y%m%d")
        except:
            return ""

    key_parts = [
        first_name or "",
        last_name or "",
        #birthday.strftime("%Y%m%d") if birthday is not None else "",
        convert_birthday(birthday) or ""
    ]
    key = "uid:" + hashlib.md5("".join(key_parts).encode('utf-8')).hexdigest()

    # try get from cache,
    # fallback to heavy calculation in case of cache miss
    store.set_mode('cache')
    score = store.storage.get(key)
    if score == None:
        score = 0
        if score:
            return score
        if phone:
            score += 1.5
        if email:
            score += 1.5
        if birthday and gender:
            score += 1.5
        if first_name and last_name:
            score += 0.5
        # cache for 60 minutes
        store.storage.set(key, score,  60 * 60)
    else:
        score = float(score)
    return score


def get_interests(store, cid):

    key = "i:%s" % cid
    store.set_mode('persistent')
    inter_resp = store.storage.get(key)

    if inter_resp == None:
        interests_list = ["cars", "pets", "travel", "hi-tech", "sport", "music", "books", "tv", "cinema", "geek", "otus"]
        interests = random.sample(interests_list, 2)
        store.storage.set(key, json.dumps(interests))
    else:
        inter_str = inter_resp.decode('utf-8')
        try:
            interests = json.loads(inter_str)
        except Exception as err:
            raise ScoringError(err)

    return interests


