import hashlib
import json
import datetime



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
    #score = store.cache_get(key) or 0
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
    #store.cache_set(key, score,  60 * 60)
    return score


def get_interests(store, cid):
    #r = store.get("i:%s" % cid)
    r = {}
    return json.loads(r) if r else []
