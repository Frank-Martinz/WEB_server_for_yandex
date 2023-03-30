from flask import Flask, request, jsonify
import logging
import json
from geo import get_distance, get_geo_info

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(message)s')

sessionStorage = {}


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
    logging.info('Request: %r', response)
    return jsonify(response)


def handle_dialog(res, req):
    user_id = req['session']['user_id']
    if req['session']['new']:
        res['response']['text'] = \
            'Привет! Назови своё имя!'
        sessionStorage[user_id] = {
            'first_name': None
        }
        return
    if sessionStorage[user_id]['first_name'] is None:
        first_name = get_first_name(req)
        if first_name is None:
            res['response']['text'] = 'Не расслышала имя. Повтори, пожалуйста!'
        else:
            sessionStorage[user_id]['first_name'] = first_name
            sessionStorage[user_id]['guessed_cities'] = []
            res['response']['text'] = f'Приятно познакомиться, {first_name.title()}. Я Алиса. \n' \
                                      f'Я могу показать город или сказать расстояние между городами!\n' \
                                      f'Напиши название города, чтобы узнать в какой стране он находится, ' \
                                      f'или напиши название двух городов, чтобы узнать расстояние между ними'
    else:
        cities = get_cities(req)
        if not cities:
            res['response']['text'] = 'Ты не написал название не одного города!'
        elif len(cities) == 1:
            res['response']['text'] = 'Этот город в стране - ' + \
                                      get_geo_info(cities[0], 'country')
        elif len(cities) == 2:
            distance = get_distance(get_geo_info(
                cities[0], 'coordinates'), get_geo_info(cities[1], 'coordinates'))
            res['response']['text'] = 'Расстояние между этими городами: ' + \
                                      str(round(distance)) + ' км.'
        else:
            res['response']['text'] = 'Слишком много городов!'


def get_cities(req):
    cities = []
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.GEO':
            if 'city' in entity['value']:
                cities.append(entity['value']['city'])
    return cities


def get_first_name(req):
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.FIO':
            return entity['value'].get('first_name', None)


if __name__ == '__main__':
    app.run()
