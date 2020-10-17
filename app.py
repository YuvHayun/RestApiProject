from fastapi import FastAPI, HTTPException, Body, Request
import json
from pydantic import BaseModel
import uvicorn
from fastapi.encoders import jsonable_encoder

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
async def on_exit_app():
    with open("data.json", "w+") as outfile:
        json.dump(beers, outfile)


class Beer(BaseModel):
    name: str
    brand: str
    price: float
    isbn: int


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
async def create_beer(beer: Beer):
    if not beer.name or not beer.brand or not beer.price or not beer.isbn:
        raise HTTPException(status_code=400, detail="Item not found")
    update_item_encoded = jsonable_encoder(beer)
    beers[str(update_item_encoded.isbn)] = update_item_encoded
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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)