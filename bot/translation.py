import requests
import json

URL_AUTH = 'https://developers.lingvolive.com/api/v1.1/authenticate'
URL_TRANSLATE = 'https://developers.lingvolive.com/api/v1/Minicard'
KEY = 'ODAzNmY2ZDMtODEwZS00OTBmLWI3ZjgtMzg3YzA3ZWI0Nzk5OmNmNmE0OGIzNzJjZjQ4NGJiODk4NmI4NzJhMWVjMjQw'


def get_auth_token(key: str, url_auth: str) -> str:
    headers_auth = {'Authorization': 'Basic ' + key}
    auth = requests.post(url=url_auth, headers=headers_auth)
    if auth.status_code == 200:
        cur_token = auth.text
        return cur_token
    else:
        return 'Error - ' + str(auth.status_code)


def get_a_word_translation(cur_token: str, url_tr: str, word: str, srcLang: int, dstLang: int) -> str:
    headers_translate = {
        'Authorization': 'Bearer ' + cur_token
    }
    params = {
        'text': word,
        'srcLang': srcLang,
        'dstLang': dstLang
    }
    req = requests.get(
        url_tr, headers=headers_translate, params=params)
    if req.status_code == 200:
        res = req.json()
        try:
            value = res['Translation']['Translation']
            return value
        except TypeError:
            if res == 'Incoming request rate exceeded for 50000 chars per day pricing tier':
                return res
            else:
                return 'No translation available'
    else:
        return 'Error!' + str(req.status_code)


def start(word: str, srcLang: int, dstLang: int) -> str:
    token = get_auth_token(key=KEY, url_auth=URL_AUTH)
    ru_translation = get_a_word_translation(cur_token=token, url_tr=URL_TRANSLATE, word=word.lower(),
                                            srcLang=srcLang, dstLang=dstLang)
    if ru_translation == 'Incoming request rate exceeded for 50000 chars per day pricing tier':
        return 'Error: Unable to get the translation. Try again'
    elif not ru_translation:
        return 'Error: Unable to get the translation. Try again'
    return ru_translation

