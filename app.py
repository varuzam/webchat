from flask import Flask, request, render_template, redirect, url_for, flash
from flask_login import LoginManager, login_required, logout_user, login_user, current_user
from flask_socketio import SocketIO, emit, join_room, leave_room
from time import time
from typing import Dict
from models import db, User, ChatRoom, msg_history

app = Flask(__name__)
app.config.from_object('config')

if app.config['DEBUG']:
    from flask_debugtoolbar import DebugToolbarExtension
    DebugToolbarExtension(app)

db.init_app(app)
sio = SocketIO(app)

login = LoginManager(app)

@login.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@login.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for('login'))

#
# FLASK HTTP ########################
#
@app.route('/')
@login_required
def index():
    return render_template('index.html', title='Home',
                                         username=current_user.username,
                                         chats=ChatRoom.query.all())

@app.route('/register', methods=['POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User(username=request.form['username'], password=request.form['password'], email=request.form['email'])
    db.session.add(user)
    try:
        db.session.commit()
    except:
        flash('Invalid data. Probably such username or email exists', 'danger')
    flash('User has been registered. Log in now.', 'success')
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        authenticated_user = User.query.filter_by(username=request.form['username'], password=request.form['password']).first()
        if authenticated_user:
            if login_user(authenticated_user):
                return redirect(url_for('index'))
            else:
                flash('Is user disabled?', 'warning')
        else:
            flash('Invalid login', 'danger')
            redirect(url_for('login'))
    return render_template('login.html', title='Login')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/chat')
@login_required
def chat():
    return redirect(url_for('index'))


@app.route('/chat/create', methods=['POST'])
@login_required
def chat_create():
    room = ChatRoom(name='#'+request.form['name'], desc=request.form['desc'], user_id=current_user.id)
    db.session.add(room)
    try:
        db.session.commit()
        return redirect(url_for('chat') + '/' + str(room.id))
    except:
        flash('Something is wrong. Try again', 'danger')
        return redirect(url_for('index'))

@app.route('/chat/delete/<int:room_id>')
@login_required
def chat_delete(room_id):
    room = ChatRoom.query.get(room_id)
    if room and room.user_id == current_user.id:
        db.session.delete(room)
        db.session.commit()
        msg_history.pop(room_id, None)
        flash('Chat has been deleted', 'success')
    else:
        flash('Insufficient privileges', 'warning')
    return redirect(url_for('index'))

@app.route('/chat/<int:room_id>')
@login_required
def chat_room(room_id):
    # check if room_id exists
    if not ChatRoom.query.get(room_id):
        flash('Chat does not exist', 'warning')
        return redirect(url_for('index'))
    if room_id not in msg_history:
        msg_history[room_id] = []
    return render_template('chat.html', title='Chat', msg_history=msg_history[room_id],
                                        chats=ChatRoom.query.all())

#
# SocketIO PART #######################
#
@sio.on('join')
def handle_join(data):
    if not current_user.is_authenticated:
        return
    join_room(data['room_id'])
    emit('message', {'user': current_user.username, 'msg': 'has joined', 'time': time()},
                    include_self=False, room=data['room_id'])


@sio.on('leave')
def handle_leave(data):
    if not current_user.is_authenticated:
        return
    leave_room(data['room_id'])
    emit('message', {'user': current_user.username, 'msg': 'has left', 'time': time()},
                    room=data['room_id'])


@sio.on('message')
def handle_message(data: Dict[str, str]):  # data must be {"room_id": room_id, "msg": msg }
    print(data, request.sid)
    if not current_user.is_authenticated:
        return
    msg_history[int(data['room_id'])].append({'user': current_user.username,
                                      'msg': data['msg'],
                                      'time': time()})
    user_sid = request.sid if request.sid else 0
    emit('message', {'user_sid': user_sid, 'user': current_user.username, 'msg': data['msg'], 'time': time()},
                    room=data['room_id'])


if __name__ == '__main__':
    sio.run(app)
