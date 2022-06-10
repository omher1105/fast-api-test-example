import http3 as http3
from fastapi import FastAPI

from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from starlette.staticfiles import StaticFiles

app = FastAPI(docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory="static"), name="static")

client = http3.AsyncClient()


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )


@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()


@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
        redoc_js_url="/static/redoc.standalone.js",
    )


MICROSERVICES_URL_API = 'https://financialmodelingprep.com/api/v3/'
API_KEY = 'e0446b98ba66087e1491c21caf98f336'

AVAILABLE_STOCKS = ['AAPL', 'GOOGL', 'GOOGL', 'AMZN', 'TSLA', 'FB', 'TWTR', 'UBER', 'LYFT', 'SNAP', 'SHOP']


async def amount_by_material(material: str):
    api_url = f"{MICROSERVICES_URL_API}quote-short/{material}"
    price = 0
    try:
        r = await client.get(api_url, params={'apikey': API_KEY})
        materials_serializable = r.json()
        for material in materials_serializable:
            price += float(material['price']) or 0
        return price
    except:
        print({'error': f'problem occurred {api_url}'})
        return price


@app.get("/amount-by-materials/{materials}")
async def amount_by_materials_all(params: str):
    try:
        total = 0
        materials = params.split(',') if params else AVAILABLE_STOCKS
        for material in materials:
            price_by_material = await amount_by_material(material)
            total += price_by_material
        return {'total': "{:.2f}".format(total)}
    except BaseException as err:
        return err
