from fastapi import FastAPI, HTTPException, Body, Request
import json


app = FastAPI()
beers = {}


@app.on_event("startup")
async def startup_event():
    global beers
    try:
        with open("data.json", "r+") as file:
            beers = json.load(file)
    except:
        beers = {}


@app.on_event("shutdown")
def shutdown_event():
    with open("data.json", "w+") as outfile:
        json.dump(beers, outfile)


@app.get("/beers/{isbn}")
async def get_beer(isbn: str):
    if isbn in beers:
        return beers[isbn]
    raise HTTPException(status_code=404, detail=f"Beer {isbn} not found")


@app.get("/beers")
async def list_beers(req: Request):
    beer_list = list(beers.values())
    for filter_name in ['name', 'brand', 'isbn', 'price']:
        filter_value = req.query_params.get(f'filter[{filter_name}]')
        if filter_value is not None:
            filtered_beer_list = []
            filter_values = filter_value.split(',')
            for _beer in beer_list:
                if str(_beer[filter_name]) in filter_values:
                    filtered_beer_list.append(_beer)
            beer_list = filtered_beer_list
    return beer_list


@app.post("/beers")
async def create_beer(name: str = Body(2000), brand: str = Body(2000), price: float = Body(2000), isbn: int = Body(2000)):
    if not name or not brand or not price or not isbn:
        raise HTTPException(status_code=400, detail="Item not found")
    else:
        new_beer = {
            'name': name,
            'brand': brand,
            'price': price,
            'isbn': isbn
        }
        beers[str(isbn)] = new_beer
        raise HTTPException(status_code=204)


@app.patch("/beers/{isbn}")
async def update_beer(isbn: str, name: str = Body(''), brand: str = Body(''), price: float = Body('')):
    if isbn in beers:
        if name:
            beers[isbn]["name"] = name
        if brand:
            beers[isbn]["brand"] = brand
        if name:
            beers[isbn]["price"] = price
        raise HTTPException(status_code=204)
    raise HTTPException(status_code=400)


@app.delete("/beers/{isbn}")
async def delete_beer(isbn: str):
    if isbn in beers:
        del beers[isbn]
        raise HTTPException(status_code=204)
    raise HTTPException(status_code=404, detail="Item not found")
