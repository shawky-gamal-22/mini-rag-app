from fastapi import FastAPI, APIRouter, Depends
import os
from helpers.config import get_settings, Settings


base_router=APIRouter(
    prefix="/api/v1",
    tags=["api_v1"],
)

@base_router.get("/")
async def welcome(app_settings: Settings = Depends(get_settings)):
    #app_settings = get_settings() using Depends here tell fastapi that this function depends on the get_settings function so it will be called automatically before this function is called


    app_name = app_settings.APP_NAME
    app_version= app_settings.APP_VERSION

    return {
        "app_name": app_name,
        "app_version": app_version,
    }