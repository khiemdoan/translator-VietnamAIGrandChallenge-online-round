import logging

import socketio
import tornado.web
from googletrans import Translator
from tornado.ioloop import IOLoop
from tornado.options import define, options, parse_command_line

logger = logging.getLogger(__name__)
translator = Translator()

define("port", default=8888, help="run on the given port", type=int)
define("debug", default=False, help="run in debug mode")

sio = socketio.AsyncServer(async_mode='tornado')


@sio.event
async def connect(sid, environ):
    logger.info('A client has connected: %s', sid)


@sio.event
def disconnect(sid):
    logger.info('A client has disconnected: %s', sid)


@sio.on('chat message')
async def on_message(sid, message):
    message = message.get('data', '')
    await sio.emit('chat message', {'from': 'me', 'data': message}, room=sid)

    translated = translator.translate(message, src='en', dest='vi')
    await sio.emit('chat message', {'from': 'bot', 'data': translated.text}, room=sid)

    logger.info('%s - "%s" - "%s"', sid, message, translated.text)


def main():
    parse_command_line()
    app = tornado.web.Application(
        [
            (r'/socket.io/', socketio.get_tornado_handler(sio)),
            (r'/(.*)', tornado.web.StaticFileHandler, {'path': 'public', 'default_filename': 'index.html'}),
        ],
        debug=options.debug,
    )
    app.listen(options.port)
    IOLoop.current().start()


if __name__ == "__main__":
    main()
