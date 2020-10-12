from flask import Flask, jsonify, request, Response
import json
import atexit

app = Flask(__name__)

if __name__ == '__app__':
    app.run(debug=True)

beers = {}


@app.before_first_request
def on_run_app():
    global beers
    try:
        with open("data.json", "r+") as file:
            beers = json.load(file)
    except:
        beers = {}


def on_exit_app():
    with open("data.json", "w+") as outfile:
        json.dump(beers, outfile)


atexit.register(on_exit_app)


@app.route('/beers')
def list_beer():
    beer_list = list(beers.values())
    for filter_name in ['name', 'brand', 'isbn', 'price']:
        filter_value = request.args.get(f'filter[{filter_name}]')

        # if filter not given, nothing to filter, continue
        if not filter_value:
            continue

        # do the filtering
        filtered_beer_list = []
        filter_values = filter_value.split(',')
        for _beer in beer_list:
            if _beer[filter_name] in filter_value:
                filtered_beer_list.append(_beer)

        # filtered list is now the "main" list
        beer_list = filtered_beer_list

    return jsonify(beer_list)


@app.route('/beers', methods=['POST'])
def create_beer():
    if validate_beer_object():
        new_beer = {
            'name': request.json['name'],
            'brand': request.json['brand'],
            'price': request.json['price'],
            'isbn': request.json['isbn']
        }
        beers[str(request.json['isbn'])] = new_beer
        return Response('', status=201)
    else:
        return Response('', status=400)


def validate_beer_object():
    if "name" in request.json and "brand" in request.json and "price" in request.json and "isbn" in request.json:
        return True
    return False


@app.route('/beers/<string:isbn>')
def get_beer(isbn):
    if isbn in beers:
        return jsonify(beers[isbn])
    return Response('', status=404)


@app.route('/beers/<string:isbn>', methods=['PATCH'])
def update_beer(isbn):
    new_beer = request.get_json()
    beer_to_edit = {}
    if "name" in new_beer:
        beer_to_edit["name"] = new_beer['name']
    if "brand" in new_beer:
        beer_to_edit["brand"] = new_beer['brand']
    if "price" in new_beer:
        beer_to_edit["price"] = new_beer['price']
    if isbn in beers:
        beers[isbn].update(beer_to_edit)
        return Response("", status=204)
    return Response('', status=404)


@app.route('/beers/<string:isbn>', methods=['DELETE'])
def delete_beer(isbn):
    if isbn in beers:
        del beers[isbn]
        return Response("", status=204)
    return Response('', status=404)


app.run(port=5000)
