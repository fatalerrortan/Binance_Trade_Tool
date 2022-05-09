import os
import random
# from math import trunc
import aiohttp
from aiohttp import web
import asyncio
from aiofile import async_open
from app import trading, app_close
from App_Logging import getLogger
import threading
import json
# import webbrowser
# import socketio
# from Websocket import Websocket
# from multiprocessing import Process

logger = None
x = None
routes = web.RouteTableDef()
        
# @routes.get('/run')
# async def index(request):
#     return web.FileResponse('./index.html')

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

            req = json.loads(msg.data)
  
            if req["cmd"] == "detach":
                logger.info("[app] websocket connection closed")
                await ws.close()

            if req["cmd"] == "attach":               
                async with async_open(f"log/{req['run_id']}.log", 'r') as afp:
                    while True:
                        line = await afp.readline()
                        if len(line) == 0: 
                            await asyncio.sleep(15)
                            continue
                        await ws.send_str(line)

            # if req["cmd"] == "test": 
            #     await ws.send_json({"test":"test!!!"})

        elif msg.type == aiohttp.WSMsgType.ERROR:
            logger.error('[app] ws connection closed with exception %s' % ws.exception())

    logger.warning('[app] websocket connection closed')

    return ws

@routes.get('/stop')
async def stop(request):  
    del os.environ["run_id"]
    logger.warning('[app] the exit flag was set, the app will be closed in 1 min !!!')
    # app_close()
    return web.Response(text='{"status": "ok", "body": "[app] the exit flag was set, the app will be closed in 1 min !!!"}')

# sio = socketio.AsyncServer(async_mode="aiohttp")
app = web.Application()
app.add_routes(routes)
# sio.register_namesapce(Websocket("/ws"))

# @sio.event(namespace="/ws")
# def connect(sid, environ, auth):
#     pass
#     # raise ConnectionRefusedError('authentication failed')

# @sio.event(namespace="/ws")
# def disconnect(sid):
#     sio.emit('my event', {'data': 'foobar'}, room=111)
    
# @sio.event(namespace="/ws")
# async def attach(sid, data):
#     print(data)
#     sio.emit('test', {'data': 'foobar'})

# @sio.on('*')
# async def catch_all(event, sid, data):
#     """Catch-All Event Handlers
#     The connect and disconnect events have to be defined explicitly and are not invoked on a catch-all event handler.

#     Args:
#         event ([type]): [description]
#         sid ([type]): [description]
#         data ([type]): [description]
#     """
#     pass

# sio.attach(app)
# webbrowser.open_new("http://localhost:9898/run")
web.run_app(app, port = 9898)

