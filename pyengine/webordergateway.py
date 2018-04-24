import hive
import dfix
import websockets
import asyncio

async def fixserver(websocket, path):
    name = await websocket.recv()
    print("received message: " + name)
    if ';35=' in name:
        fixmsg = dfix.dfixformat(name)
        fixmsg = hive.fixgateway(name)
    else:
        fixmsg = "invalid message"
    await websocket.send(fixmsg)
    print("sending to client: " + fixmsg)

start_server = websockets.serve(fixserver, '127.0.0.1', 20001)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()