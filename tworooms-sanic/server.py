from typing import Dict
from sanic import Sanic, Request, Websocket
from sanic.response import json as jsonresponse, file
from sanic_cors import CORS
import json
from uuid import uuid4 as uuid

from gamestate import *
import utils

from os import path

app = Sanic("tworooms")
CORS(app)

games: Dict[str,GameRoom] = {}
users: Dict[str, tuple[str, str]]

# this will be replaced with redis for "production"
app.ctx.gamedata = {}

app.static("/assets", "/workspaces/tworooms/tworooms-vue/dist/assets")

@app.middleware("request")
async def player_room_middleware(request):
    if request.json:
        roomcode = request.json['roomcode'] if 'roomcode' in request.json.keys() else None
        playername = request.json['playername'] if 'playername' in request.json.keys() else None
        game = None
        if roomcode:
            game = games[roomcode] if roomcode in games.keys() else None
            request.ctx.game = game
        if playername and game:
            playermatch = [player for player in game.players if player.playername == playername]
            player = playermatch if len(playermatch) > 0 else None
            request.ctx.player = player

async def get_app(request, ext=None):
    return await file(location="/workspaces/tworooms/tworooms-vue/dist/index.html")

app.add_route(get_app, "/<ext>/")
app.add_route(get_app, "/")


@app.post("api/create/")
async def create_room_handler(request):
    # create a game, generate a room code
    roomcode = utils.generate_access_code()
    while roomcode in games.keys():
        roomcode = utils.generate_access_code

    playername = request.json["playername"]
    games[roomcode] = GameRoom(roomcode, playername)
    current_game = games[roomcode]
    response = jsonresponse(
        {
            "roomcode": roomcode,
            "playerlist": [player.playername for player in current_game.players]
        })

    identifier = uuid()
    response.cookies['session'] = identifier
    users[identifier] = (roomcode, playername)
    return response


@app.post("api/join/")
async def join_room_handler(request):
    roomcode = request.json['roomcode']
    playername = request.json['playername']

    current_game = games[roomcode]
    current_game.players.append(Player(playername))
    return jsonresponse(
        {
            "roomcode": roomcode,
            "playerlist": [player.playername for player in current_game.players]
        }
    )

@app.websocket("ws/game/")
async def game_ws_handler(request: Request, ws: Websocket):
    # associate this websocket with its game/player
    game = request.ctx.game
    player = request.ctx.player

    while True:
        # if host handle host-specific messages

        # handle everything else
        message = await ws.recv()
        print(message)
        await ws.send("hello")
        