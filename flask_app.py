from flask import Flask, request
import logging
import json
from requests import get

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)


sessionStorage = {}


def translate(text, lang):
    response = get('https://translate.yandex.net/api/v1.5/tr.json/translate',
                 {'key': 'trnsl.1.1.20200505T115405Z.e81ba43b2a560407.b24350720bd63bd44082ff3421f476145d467343',
                  'text': text, 'lang': lang}).json()
    return response['text'][0] if response['code'] == 200 else response['message']


def translate_phrase(req):
    if len(req['request']['command'].split()) > 1 and req['request']['command'].split()[0] == 'переведи':
        return ' '.join(req['request']['command'].split()[1:])


@app.route('/post', methods=['POST'])
def main():
    logging.info('Request: %r', request.json)
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(response, request.json)
    logging.info('Response: %r', response)
    return json.dumps(response)


def handle_dialog(res: dict, req: dict):
    user_id = req['session']['user_id']

    if req['session']['new']:
        res['response']['text'] = 'Правильные команды: "переведи слово <фраза>"'
        sessionStorage[user_id] = {'language': 'en'}
        return
    tran = translate_phrase(req)
    if translate is not None:
        res['response']['text'] = translate(tran, sessionStorage[user_id]['language'])
    else:
        res['response']['text'] = 'Я понимаю только "переведи слово <фраза>"'


if __name__ == '__main__':
    app.run()