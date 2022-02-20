import os
import random
# from math import trunc
from aiohttp import web
import aiohttp
import asyncio
from aiofile import async_open
from app import trading, app_close
from App_Logging import getLogger
import threading


# from multiprocessing import Process

logger = None
x = None
routes = web.RouteTableDef()
        

@routes.post('/app')
async def run(request):

    global x, logger

    if os.getenv("run_id"):
        return web.Response(text='{"status": "error", "body": "[app] the Run with ID: %s is already running now!!!"}' % (os.getenv("run_id")))

    run_id = str(random.randint(1000, 9999))
    os.environ["run_id"] = run_id
    logger = getLogger('server.py', run_id)
    
    
    data = await request.post()
    logger.info("[app] app is launching!!!") 
    logger.info(f"[app] --- run id ---: {run_id}") 
    
    try:
        # data["client_id"] = client_id
        x = threading.Thread(target=thread, args=(data,))
        x.start()
    except Exception:
        return web.Response(text='{"status": "error", "body": "[app] launching error!!!"}')
  
    # await trading(data)
    return web.Response(text='{"status": "ok", "body": "[app] app is launching!!!", "run_id": "%s"}' % (run_id))

def thread(data):
    asyncio.run(trading(data))

@routes.get('/ws')
async def websocket_handler(request):

    ws = web.WebSocketResponse()
    await ws.prepare(request)

    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            if msg.data == "detach":
                await ws.close()
            if msg.data == "attach":               
                async with async_open("app.log", 'r') as afp:
                    while True:
                        line = await afp.readline()
                        if len(line) == 0: 
                            await asyncio.sleep(15)
                            continue
                        await ws.send_str(line)

        elif msg.type == aiohttp.WSMsgType.ERROR:
            logger.error('ws connection closed with exception %s' %
                  ws.exception())

    logger.warning('websocket connection closed')

    return ws

@routes.get('/stop')
async def stop(request):  
    del os.environ["run_id"]
    logger.warning('[app] the exit flag was set, the app will be closed in 1 min !!!')
    # app_close()
    return web.Response(text='{"status": "ok", "body": "[app] the exit flag was set, the app will be closed in 1 min !!!"}')
    
app = web.Application()
app.add_routes(routes)
web.run_app(app, port = 9898)