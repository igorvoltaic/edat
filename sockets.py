#!/usr/bin/env python

import asyncio
import json
import logging
import websockets
from django.apps import apps
from django.conf import settings
from dotenv import load_dotenv
from asgiref.sync import sync_to_async
from celery.result import AsyncResult

load_dotenv()
apps.populate(settings.INSTALLED_APPS)

from apps.datasets.models import Plot
from apps.datasets.dtos import PlotTaskStatusDTO
from helpers.exceptions import FileAccessError, PlotRenderError

logging.basicConfig()

TASKS = set()


@sync_to_async
def get_tasks():
    return [p.task_id for p in Plot.objects.all()]  # type: ignore


# async def get_result():
#     await AsyncResult.th


@sync_to_async
def get_status(task_id: str) -> PlotTaskStatusDTO:
    task = AsyncResult(task_id)
    try:
        return PlotTaskStatusDTO(
            id=task_id,
            result=task.result,
            ready=task.ready()
        )
    except (FileNotFoundError, FileExistsError, OSError) as err:
        raise FileAccessError("Cannot find plot image file") from err


async def task_status(websocket, path):
    async for message in websocket:
        data = json.loads(message)
        try:
            if data["action"] == "status":
                status = await get_status(data["task_id"])  # type: ignore
                await websocket.send(
                    json.dumps({
                        'type': 'status',
                        'result': status.dict()
                    })
                )
            elif data["action"] == "all":
                for task in await get_tasks():
                    isReady = await result(task)
                    await websocket.send(
                        json.dumps({
                            'type': 'all',
                            'result': isReady
                        })
                    )
            elif data["action"] == "echo":
                await websocket.send(message)
            else:
                logging.error("unsupported event: {}", data)
                await websocket.send(
                    json.dumps({
                        "error": "unsupported event",
                        'detail': data
                    })
                )
        except FileAccessError as err:
            await websocket.send(
                json.dumps({
                    'type': 'error',
                    'detail': err.message
                })
            )
        except PlotRenderError as err:
            await websocket.send(
                json.dumps({
                    'type': 'error',
                    'detail': err.message
                })
            )

start_server = websockets.serve(task_status, "localhost", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
