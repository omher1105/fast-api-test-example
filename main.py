import codecs
import json
import os
from typing import Union, Dict

import http3 as http3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from starlette.responses import FileResponse

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


class PayloadHttp(BaseModel):
    url: str
    filters: Union[Dict, None] = None


async def callback_http(payload: PayloadHttp):
    try:
        if len(payload.filters) > 3:
            raise HTTPException(status_code=400, detail="filters should not exceed more than 3 values!!")
        r = await client.get(payload.url, params=payload.filters)
        callback_serializable = r.json()
        return callback_serializable
    except BaseException as err:
        return err


@app.post("/fetch-http-resources/")
async def fetch_http_resources(payload: PayloadHttp):
    response = await callback_http(payload)
    return response


@app.post("/fetch-http-resources/download/")
async def fetch_http_resources(payload: PayloadHttp):
    try:
        response = await callback_http(payload)
        print(response)
        file_name = "test.txt"
        file_path = os.getcwd() + "/" + file_name
        with open(file_name, 'wb+') as f:
            json.dump(response, codecs.getwriter('utf-8')(f), ensure_ascii=False)
        return FileResponse(path=file_path, media_type='application/octet-stream', filename=file_name)
    except HTTPException as err:
        return err
