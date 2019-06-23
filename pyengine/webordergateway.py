import hive
import dfix
import websockets
import asyncio

async def fixserver(websocket, path):
    while True:
        name = await websocket.recv()
        print("received message: " + name)
        if ';35=' in name:
            fixmsg = dfix.dfixformat(name)
            parsed = dfix.parsefix(fixmsg)
            sendercomp = parsed.get('49')
            targetcomp = parsed.get('56')
            print("processing FIX message from sender " + sendercomp + " to target " + targetcomp)
            fixmsg = hive.fixgateway(name)
        else:
            fixmsg = "invalid message"
        await websocket.send(fixmsg)
        print("sending to client: " + fixmsg)

start_server = websockets.serve(fixserver, '127.0.0.1', 20001)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()