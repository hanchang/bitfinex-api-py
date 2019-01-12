"""
Module used as a interfeace to describe a generick websocket client
"""

import asyncio
import websockets
import json

from pyee import EventEmitter
from ..utils.CustomLogger import CustomLogger


class AuthError(Exception):
    """
    Thrown whenever there is a problem with the authentication packet
    """
    pass


def is_json(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError as e:
        return False
    return True


class GenericWebsocket:
    """
    Websocket object used to contain the base functionality of a websocket.
    Inlcudes an event emitter and a standard websocket client.
    """

    def __init__(self, host, logLevel='INFO', loop=None):
        self.host = host
        self.logger = CustomLogger('BfxWebsocket', logLevel=logLevel)
        self.loop = loop or asyncio.get_event_loop()
        self.events = EventEmitter(
            scheduler=asyncio.ensure_future, loop=self.loop)
        self.ws = None

    def run(self):
        """
        Run the websocket connection indefinitely
        """
        self.loop.run_until_complete(self._main(self.host))

    def get_task_executable(self):
        """
        Get the run indefinitely asyncio task
        """
        return self._main(self.host)

    async def _main(self, host):
        self.ws = await websockets.connect(host)
        self.logger.info("Websocket connected to {}".format(self.host))
        while True:
            if not self.ws.open:
                self.logger.info("Websocket disconnected, reconnecting...")
                self.ws = await websockets.connect(host)

            await asyncio.sleep(0)
            message = await self.ws.recv()
            await self.on_message(message)

    def remove_all_listeners(self, event):
        """
        Remove all listeners from event emitter
        """
        self.events.remove_all_listeners(event)

    def on(self, event, func=None):
        """
        Add a new event to the event emitter
        """
        if not func:
            return self.events.on(event)
        self.events.on(event, func)

    def once(self, event, func=None):
        """
        Add a new event to only fire once to the event
        emitter
        """
        if not func:
            return self.events.once(event)
        self.events.once(event, func)

    def _emit(self, event, *args, **kwargs):
        self.events.emit(event, *args, **kwargs)

    async def on_error(self, error):
        """
        On websocket error print and fire event
        """
        self.logger.error(error)
        self.events.emit('error', error)

    async def on_close(self):
        """
        On websocket close print and fire event
        """
        self.logger.info("Websocket closed.")
        await self.ws.close()
        self._emit('done')

    async def on_open(self):
        """
        On websocket open
        """
        pass

    async def on_message(self, message):
        """
        On websocket message
        """
        pass
