import functools
import logging

from flask import session, request
from flask_login import current_user
from flask_socketio import SocketIO, emit, join_room, disconnect

#
# This variable keeps track of the workers associated with each client. It is
# structued as follows:

# user_id ( Girder user id )
#  |
#  +--- worker_id (the uuid for this worker)
#        |
#        +--- pipelines ( list of pipelines that this worker can support )
#        |
#        +--- ranks ( dict the key is the rank and the value is the sid for the rank )
#
logger = logging.getLogger('stemserver')
workers = {}

def auth_required(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            disconnect()
        else:
            return f(*args, **kwargs)
    return wrapped

def current_room():
    return current_user.girder_user['login']

def init(socketio):
    @socketio.on('connect', namespace='/stem')
    def connect():
        if current_user.is_authenticated:
            logger.debug('Client connected')
            join_room(current_room())
            user_id = current_user.girder_user['_id']
            user_workers = workers.setdefault(user_id, {})
            emit('stem.workers', user_workers)
        else:
            return False

    @socketio.on('stem.pipeline.create', namespace='/stem')
    @auth_required
    def create(params):
        user_id = current_user.girder_user['_id']
        worker_id = params['workerId']
        logger.debug('stem.pipeline.create: %s' % params)
        # Send to all worker ranks
        for sid in workers[user_id][worker_id]['ranks'].values():
            emit('stem.pipeline.create', params, room=sid, include_self=False)

    @socketio.on('stem.pipeline.created', namespace='/stem')
    @auth_required
    def created(params):
        logger.debug('stem.pipeline.created: %s' % params)

        emit('stem.pipeline.created', params, room=current_room(), include_self=False)

    @socketio.on('stem.pipeline.execute', namespace='/stem')
    @auth_required
    def execute(params):
        logger.debug('stem.pipeline.execute: %s' % params)

        user_id = current_user.girder_user['_id']
        worker_id = params['workerId']
        # Send to all worker ranks
        for sid in workers[user_id][worker_id]['ranks'].values():
            emit('stem.pipeline.execute', params, room=sid, include_self=False)

    @socketio.on('stem.pipeline.executed', namespace='/stem')
    @auth_required
    def executed(params):
        logger.debug('stem.pipeline.executed.')
        emit('stem.pipeline.executed', params, room=current_room(), include_self=False)

    @socketio.on('stem.pipeline.delete', namespace='/stem')
    @auth_required
    def delete(params):
        logger.debug('stem.pipeline.delete: %s' % params)

        emit('stem.pipeline.delete', params, room=current_room(), include_self=False)

    @socketio.on('stem.worker_connected', namespace='/stem')
    @auth_required
    def worker_connected(data):
        logger.debug('stem.worker_connected: %s' % data)
        user_id = current_user.girder_user['_id']
        user_workers = workers.setdefault(user_id, {})
        worker_id = data['id']
        rank = data['rank']
        user_worker = user_workers.setdefault(worker_id, {})
        client_id = request.sid
        ranks = user_worker.setdefault('ranks', {})

        if 'pipelines' in data:
            user_worker['pipelines'] = data['pipelines']

        ranks[rank] = client_id

        emit('stem.workers', user_workers, room=current_room())

    @socketio.on('stem.bright', namespace='/stem')
    @auth_required
    def bright(data):
        emit('stem.bright', data, room=current_room(), include_self=False)

    @socketio.on('stem.dark', namespace='/stem')
    @auth_required
    def dark(data):
        emit('stem.dark', data, room=current_room(), include_self=False)

    @socketio.on('stem.size', namespace='/stem')
    @auth_required
    def size(data):
        emit('stem.size', data, room=current_room(), include_self=False)

    @socketio.on('disconnect', namespace='/stem')
    @auth_required
    def disconnect():
        logger.debug('Client disconnected')
        user_id = current_user.girder_user['_id']
        client_id = request.sid
        user_workers = workers.setdefault(user_id, set())
        if client_id in user_workers:
            user_workers.remove(client_id)
            emit('stem.workers', list(user_workers), room=current_room())
