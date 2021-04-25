from flask import Flask, request
import logging
import json

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

sessionStorage = {}
targets = {
    0: ['слона', 'слон'],
    1: ['кролика', 'кролик'],
}


@app.route('/post', methods=['POST'])
def main():
    logging.info(f'Request: {request.json!r}')

    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    handle_dialog(request.json, response)
    logging.info(f'Response:  {response!r}')
    return json.dumps(response)


def handle_dialog(req, res):
    user_id = req['session']['user_id']

    if req['session']['new']:
        sessionStorage[user_id] = {
            'suggests': [
                "Не хочу.",
                "Не буду.",
                "Отстань!",
            ],
            'target': 0,
        }
        res['response']['text'] = 'Привет! Купи слона!'
        res['response']['buttons'] = get_suggests(user_id)
        return

    success_words = [
        'куплю',
        'покупаю',
        'ладно',
        'хорошо'
    ]
    if any([i in success_words
            for i in req['request']['original_utterance'].lower().split()]):
        res['response']['text'] = targets[sessionStorage[
            user_id]['target']][0].capitalize()
        res['response']['text'] += ' можно найти на Яндекс.Маркете!'
        sessionStorage[user_id]['target'] += 1
        if sessionStorage[user_id]['target'] == 2:
            res['response']['end_session'] = True
        return

    res['response']['text'] = offer_elephant(
        req['request']['original_utterance'],
        sessionStorage[user_id]['target'])
    res['response']['buttons'] = get_suggests(user_id)


def offer_elephant(text, target_):
    return f"Все говорят '{text}', а ты купи {targets[target_][0]}!"


def get_suggests(user_id):
    session = sessionStorage[user_id]

    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests'][:2]
    ]

    session['suggests'] = session['suggests'][1:]
    sessionStorage[user_id] = session

    if len(suggests) < 2:
        suggests.append({
            "title": "Ладно",
            "url": "https://market.yandex.ru/search?text=" + targets[
                session['target']][1],
            "hide": True
        })

    return suggests


if __name__ == '__main__':
    app.run()
