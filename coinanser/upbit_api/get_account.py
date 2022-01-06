import jwt
import uuid
import hashlib
from urllib.parse import urlencode
import requests


from my_setting import config as my_config


access_key = my_config.UPBIT_ACCOUNT['access_key']
secret_key = my_config.UPBIT_ACCOUNT['secret_key']
server_url = my_config.UPBIT_ACCOUNT['server_url']


def get_authorize_token(payload_):
    jwt_token = jwt.encode(payload_, secret_key)
    authorize_token = 'Bearer {}'.format(jwt_token)
    return authorize_token


def get_query_payload(query_):
    query_string = urlencode(query_).encode()
    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()
    payload = {
        'access_key': access_key,
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512',
    }
    return payload


# 현재 자산
def account_all():
    payload = {
        'access_key': access_key,
        'nonce': str(uuid.uuid4()),
    }
    headers = {"Authorization": get_authorize_token(payload)}
    res = requests.get(server_url + "/v1/accounts", headers=headers)
    result = {j['currency']: j for j in res.json()}
    return result


# 보유 마켓
def account_market(market_):
    query = {
        'market': market_,
    }
    payload = get_query_payload(query)
    headers = {"Authorization": get_authorize_token(payload)}
    res = requests.get(server_url + "/v1/orders/chance", params=query, headers=headers)
    result = res.json()
    return result
# account_market('KRW-XRP')

