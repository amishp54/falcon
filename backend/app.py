from typing import List
import falcon
import falcon.asgi
import falcon.asgi.ws as Websocket 
from falcon import media
import json
class ConnectionManager:
    def __init__(self):
        self.active_connections = []

    async def connect(self, ws :Websocket):
        await ws.accept()
        self.active_connections.append(ws)

    def disconnect(self,ws: Websocket):
        self.active_connections.remove(ws)

    async def send_personal_message(self, message: str, ws: Websocket): 
        await ws.send_text(message)

    async def broadcast(self, message: str,ws : Websocket):
        for connection in self.active_connections:
            if(connection!=ws):
                await connection.send_text(message)


manager = ConnectionManager()

# origins = [
#     "http://localhost:3000",
# ]
class HelloResource:
    async def on_get(self, req, resp,client_id):
        resp.status = falcon.HTTP_200
        resp.content_type = 'text/html'
        with open('D:\Downloads\Internship ass\\backend\index.html', 'rb') as f:
            resp.body = f.read()
        # resp.media ={'message': f'Hello,!'}

    # async def on_post(self, req, resp):
    #     userJson = await req.media
    #     users.update(userJson)
    #     resp.status = falcon.HTTP_200

    async def on_websocket(self, req, ws,client_id):
        try:
            await manager.connect(ws)
            while True:
                data = await ws.receive_text()
                await manager.send_personal_message((f"You wrote: {data}"),ws)
                await manager.broadcast((f"Client #{client_id} says: {data}"), ws)
        except falcon.WebSocketDisconnected:
            # await ws.send_text((f"{client_id} has left the chat"))
            await manager.disconnect(ws)


app = falcon.asgi.App()
app.add_route('/ws/{client_id}', HelloResource())