from typing import Dict
from sanic import Sanic
from sanic.response import json, file
from sanic_cors import CORS
from gamestate import *
import utils

from os import path

app = Sanic("tworooms")
CORS(app)

games: Dict[str,GameRoom] = {}

# this will be replaced with redis for "production"
app.ctx.gamedata = {}

app.static("/assets", "/workspaces/tworooms/tworooms-vue/dist/assets")


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

    games[roomcode] = GameRoom(roomcode, request.json["playername"])
    current_game = games[roomcode]
    return json(
        {
            "roomcode": roomcode,
            "playerlist": [player.playername for player in current_game.players]
        })


@app.post("api/join/")
async def join_room_handler(request):
    roomcode = request.json['roomcode']
    playername = request.json['playername']

    current_game = games[roomcode]
    current_game.players.append(Player(playername))
    return json(
        {
            "roomcode": roomcode,
            "playerlist": [player.playername for player in current_game.players]
        }
    )

@app.websocket("ws/game/")
async def game_ws_handler(request, ws):
    pass
