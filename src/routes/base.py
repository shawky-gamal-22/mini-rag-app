from fastapi import FastAPI, APIRouter, Depends
import os
from helpers.config import get_settings, Settings
from datetime import datetime
from time import sleep
import logging
from tasks.mail_service import send_email_report

logger = logging.getLogger("uvicorn.error")

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
        "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

@base_router.get("/send_reports")
async def  send_reports(app_settings: Settings = Depends(get_settings)):


    # ===== START ====== send reports
    task = send_email_report.delay(
        mail_wait_seconds=3
    )


    # ===== END ====== send reports


    return {
        "success": True,
        "task_id": task.id
    }
