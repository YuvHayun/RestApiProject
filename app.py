from fastapi import FastAPI, HTTPException, Request
import json
from pydantic import BaseModel
from typing import Optional
import uvicorn
import aiofiles

app = FastAPI()
beers = {}


@app.on_event("startup")
async def startup_event():
    global beers
    try:
        async with aiofiles.open("data.json", mode='r+') as file:
            beers_string = await file.read()
        beers = json.loads(beers_string)
    except Exception as exc:
        print(exc)
        beers = {}


@app.on_event("shutdown")
async def on_exit_app():
    dict_to_save = {}
    for beer_name, beer in beers.items():
        dict_to_save[beer_name] = beer.dict()
    async with aiofiles.open("data.json", "w+") as outfile:
        beers_to_save = json.dumps(dict_to_save)
        await outfile.write(beers_to_save)


class Beer(BaseModel):
    name: Optional[str] = None
    brand: Optional[str] = None
    price: Optional[float] = None
    isbn: Optional[int] = None


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


@app.post("/beers", status_code=201)
async def create_beer(beer: Beer):
    if not beer.name or not beer.brand or not beer.price or not beer.isbn:
        raise HTTPException(status_code=400, detail="Not a beer model")
    beers[str(beer.isbn)] = beer


@app.patch("/beers/{isbn}")
async def update_beer(isbn: str, beer: Beer):
    if isbn not in beers:
        raise HTTPException(status_code=404, detail="Item not found")
    if beer.name:
        beers[isbn]["name"]: beer.name
    if beer.brand:
        beers[isbn]["brand"]: beer.brand
    if beer.name:
        beers[isbn]["price"]: beer.price


@app.delete("/beers/{isbn}")
async def delete_beer(isbn: str):
    if isbn not in beers:
        raise HTTPException(status_code=404, detail="Item not found")
    del beers[isbn]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)