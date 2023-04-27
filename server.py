import datetime
import os
import werkzeug.utils
from flask import Flask, render_template, redirect, make_response, request, abort, jsonify, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_restful import Api
from data.lesson import Lesson
from forms.LessonForm import LessonForm
from forms.TaskForm import TaskForm
from forms.user import RegisterForm, LoginForm
from data.users import User
from data.chats import Chat
from data import db_session
from forms.SearchForm import SearchForm
from forms.ChatForm import ChatForm
from functions import check_password, crop_center
from tinydb import TinyDB
from PIL import Image
from data.task import Task

chats = TinyDB('chats_db.json')
app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


def main():
    db_session.global_init("db/Space.db")
    # app.register_blueprint(advertisement_api.blueprint)
    # api = Api(app)
    # api.add_resource(advertisement_resources.AdvertisementListResource, '/api/v2/advertisement')
    # api.add_resource(advertisement_resources.AdvertisementResource, '/api/v2/advertisement/<int:advertisement_id>')
    app.run()


@app.route("/", methods=['GET', 'POST'])
def index():
    form = SearchForm()
    if form.validate_on_submit():
        return redirect(f'/search/{form.search.data}')
    db_sess = db_session.create_session()
    lessons = []
    if current_user.is_authenticated:
        lessons = db_sess.query(Lesson).all()
    return render_template("index.html", lessons=lessons, search={'title': '',
                                                                  'author': ''},
                           form=form,
                           url='/')


@app.route("/search/<string:searchWord>", methods=['GET', 'POST'])
def search(searchWord):
    form = SearchForm()
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        lessons = db_sess.query(Lesson).filter(
            (Lesson.user == current_user) | (Lesson.is_private != True))
    else:
        lessons = db_sess.query(Lesson).filter(Lesson.is_private != True)
    text = ''
    if request.method == 'GET':
        text = searchWord
    if form.validate_on_submit():
        print(f'Поиск: {form.search.data}')
        text = form.search.data
    sp_char = '&'
    if sp_char in text:
        emailIndex = text.index(sp_char) + 1
        emailEndIndex = text[emailIndex:].find(' ') + len(text[:emailIndex])
        if emailEndIndex < len(text[:emailIndex]):
            emailEndIndex = len(text)
        emailAuthor = text[emailIndex:emailEndIndex]
        search = {'title': (' '.join((text[:emailIndex - 1] + text[emailEndIndex:]).split()).lower()),
                  'author': emailAuthor}
    else:
        search = {'title': text.lower(), 'author': ''}
    print('Поиск: ', search)
    return render_template('index.html',
                           form=form,
                           url_for=url_for,
                           search=search,
                           lessons=lessons,
                           url=f'/search/{searchWord}')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Такой пользователь уже есть")
        user = User()
        user.name = form.name.data
        user.email = form.email.data
        user.surname = form.surname.data
        user.age = form.age.data
        user.type = form.type.data
        user.tests = ''
        file = form.photo.data
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        new_user(user)
        if file:
            filename = werkzeug.utils.secure_filename(file.filename)
            user.avatar = f'static/users_data/{user.id}/avatar/{filename}'
        else:
            user.avatar = 'https://bootdey.com/img/Content/user_1.jpg'
        user.set_password(form.password.data)
        db_sess.merge(user)
        db_sess.commit()
        if file:
            filename = werkzeug.utils.secure_filename(file.filename)
            path = f'static/users_data/{user.id}/avatar/{filename}'
            file.save(path)
            image = Image.open(path)
            im_crop = crop_center(image)
            im_crop.save(path, quality=95)
        return redirect('/')
    return render_template('register.html', title='Регистрация', form=form)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html',
                           title='Авторизация',
                           form=form,
                           url='/login')


@app.route('/lesson', methods=['GET', 'POST'])
@login_required
def add_lesson():
    form = LessonForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        lesson = Lesson()
        lesson.title = form.title.data
        lesson.content = form.content.data
        lesson.is_private = form.is_private.data
        lesson.url_videos = form.url_videos.data
        user = db_sess.query(User).get(current_user.id)
        user.lesson.append(lesson)
        db_sess.merge(user)
        db_sess.commit()
        return redirect('/')
    return render_template('lesson.html',
                           title='Добавление новости',
                           form=form,
                           url='/advertisement')


@app.route('/lesson/<int:lesson_id>', methods=['GET', 'POST'])
def lesson_page(lesson_id):
    db_sess = db_session.create_session()
    lesson = db_sess.query(Lesson).get(lesson_id)
    url_videos = [url.replace(' ', '').replace('https://youtu.be/', '') for url in lesson.url_videos.split(',')]
    for ind in range(len(url_videos)):
        if url_videos[ind] == '':
            url_videos.pop(ind)
    if lesson:
        return render_template('lesson_page.html', lesson=lesson,
                               url_for=url_for, url_videos=url_videos)
    else:
        return redirect('/')


@app.route('/chat/<int:_id>', methods=['GET', 'POST'])
@login_required
def WrIte_MeSSage(_id):
    form = ChatForm()
    sess = db_session.create_session()
    if _id != 0:
        res = sess.query(Chat).filter((Chat.user_id1 == min(current_user.id, _id)) &
                                      (Chat.user_id2 == max(current_user.id, _id))).first()
        if res:
            chat_id = res.id
        else:
            chat = Chat()
            chat.user_id1 = min(current_user.id, _id)
            chat.user_id2 = max(current_user.id, _id)
            sess.add(chat)
            sess.commit()
            chat_id = chat.id
        other = sess.query(User).filter(User.id == _id).first()
        table = chats.table(str(chat_id))
    else:
        table = chats.table(str(0))
        other = None
    previous = [(i.user_id1, i.id) if i.user_id1 != current_user.id else (i.user_id2, i.id) for i
                in sess.query(Chat).filter((Chat.user_id1 == current_user.id) |
                                           (Chat.user_id2 == current_user.id)).all()]
    lm = {}
    for i in previous:
        messages = chats.table(i[1])
        for j in messages:
            if j['id'] == i[0]:
                lm[i[0]] = j['text']
                break
    previous = [sess.query(User).filter(User.id == i[0]).first() for i in previous]
    if request.method == 'POST':
        if form.message.data:
            table.insert({'id': current_user.id, 'text': form.message.data,
                          'time': datetime.datetime.now().strftime('"%m-%d-%Y %H:%M"')})
        return redirect(f'/chat/{_id}')
    return render_template('chat_room.html', messages=table.all(), cur=current_user,
                           other=other, form=form, previous=previous, id=_id, lm=lm)


@app.route('/lesson/edit/<int:lesson_id>', methods=['GET', 'POST'])
@login_required
def edit_advertisement(lesson_id):
    form = LessonForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        lesson = db_sess.query(Lesson).filter(Lesson.id == lesson_id,
                                              Lesson.user == current_user).first()
        if lesson:
            form.title.data = lesson.title
            form.content.data = lesson.content
            form.is_private.data = lesson.is_private
            form.url_videos.data = lesson.url_videos
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        lesson = db_sess.query(Lesson).filter(Lesson.id == lesson_id,
                                              Lesson.user == current_user).first()
        if lesson:
            lesson.title = form.title.data
            lesson.content = form.content.data
            lesson.is_private = form.is_private.data
            lesson.url_videos = form.url_videos.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('lesson.html',
                           title='Редактирование урока',
                           form=form)


@app.route('/lesson_delete/<int:lesson_id>', methods=['GET', 'POST'])
@login_required
def advertisement_delete(lesson_id):
    db_sess = db_session.create_session()
    lesson = db_sess.query(Lesson).filter(Lesson.id == lesson_id,
                                          Lesson.user == current_user).first()
    if lesson:
        db_sess.delete(lesson)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/settings')
def settings():
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(current_user.id)
    return render_template('settings.html', user=user, url='/settings')


@app.route('/settings/edit', methods=['GET', 'POST'])
def edit_user():
    form = RegisterForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        user = db_sess.query(User).get(current_user.id)
        if user:
            form.email.data = user.email
            form.name.data = user.name
            form.surname.data = user.surname
            form.age.data = user.age
        else:
            abort(404)
    if request.method == "POST":
        db_sess = db_session.create_session()
        user = db_sess.query(User).get(current_user.id)
        user1 = db_sess.query(User).filter(User.email == form.email.data).first()
        if user1:
            if user1.id != current_user.id:
                return render_template('edit_user.html', title='Редактирование профиля', form=form,
                                       message="Такой пользователь уже есть")
        """try:
            check_password(form.password.data, form.password_again.data)
        except Exception as error:
            return render_template('register.html', title='Редактирование профиля', form=form,
                                   message=error.__str__())"""
        if user:
            user.email = form.email.data
            user.set_password(form.password.data)
            user.name = form.name.data
            user.surname = form.surname.data
            user.age = form.age.data
            file = form.photo.data
            if file:
                filename = werkzeug.utils.secure_filename(file.filename)
                path = f'static/users_data/{user.email}/avatar/{filename}'
                if user.avatar:
                    del_path = user.avatar
                    os.remove(del_path)
                file.save(path)
                user.avatar = f'static/users_data/{user.email}/avatar/{filename}'
                image = Image.open(path)
                im_crop = crop_center(image)
                im_crop.save(path, quality=95)
            elif not user.avatar:
                user.avatar = 'https://bootdey.com/img/Content/user_1.jpg'
            db_sess.commit()
            return redirect('/settings')
        else:
            abort(404)
    return render_template('edit_user.html',
                           title='Редактирование профиля',
                           form=form,
                           url='')


@app.route('/settings/delete', methods=['GET', 'POST'])
def delete_user():
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(current_user.id)
    db_sess.delete(user)
    db_sess.commit()
    return redirect('/')


@app.route('/tasks')
def tasks():
    db_sess = db_session.create_session()
    if current_user.type == 2:
        _tasks = db_sess.query(Task).filter(Task.user == current_user).all()
    else:
        _tasks = []
        for task_id in [int(i) for i in current_user.tests.split(',')]:
            task = db_sess.query(Task).get(task_id)
            _tasks.append(task)
    return render_template('task.html', tasks=_tasks, url='/tasks')


@app.route('/tasks/create', methods=['GET', 'POST'])
def add_task():
    if current_user.type == 2:
        form = TaskForm()
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            task = Task()
            task.title = form.title.data
            task.url = form.url.data
            user = db_sess.query(User).get(current_user.id)
            user.tasks.append(task)
            db_sess.merge(user)
            db_sess.commit()
            return redirect('/tasks')
        return render_template('create_task.html', url='/tasks/create', form=form)
    return 'Доступ закрыт'


@app.route('/tasks/<int:task_id>/edit', methods=['GET', 'POST'])
def edit_task(task_id):
    form = TaskForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        task = db_sess.query(Task).filter(Task.id == task_id and Task.user == current_user).first()
        if task:
            form.title.data = task.title
            form.url.data = task.url
        else:
            abort(404)
    if request.method == "POST":
        db_sess = db_session.create_session()
        task = db_sess.query(Task).get(task_id)
        if task:
            task.title = form.title.data
            task.url = form.url.data
            db_sess.commit()
            return redirect('/tasks')
        else:
            abort(404)
    return render_template('create_task.html',
                           title='Редактирование теста',
                           form=form,
                           url='')


@app.route('/tasks/<int:task_id>/delete', methods=['GET', 'POST'])
def delete_task(task_id):
    db_sess = db_session.create_session()
    task = db_sess.query(Task).filter(Task.id == task_id and Task.user == current_user).first()
    db_sess.delete(task)
    db_sess.commit()
    return redirect('/tasks')


@app.route('/tasks/<int:task_id>/appoint', methods=['GET', 'POST'])
def appoint_task(task_id):
    db_sess = db_session.create_session()
    task = db_sess.query(Task).filter(Task.id == task_id and Task.user == current_user).first()
    users = db_sess.query(User).filter(User.type == 1).all()
    return render_template('appoint_page.html', task=task, users=users, title='Учинеки', str=str)


@app.route('/tasks/<int:task_id>/appoint/<int:user_id>', methods=['GET', 'POST'])
def add_task_study(task_id, user_id):
    if current_user.type == 2:
        db_sess = db_session.create_session()
        user = db_sess.query(User).get(user_id)
        if user.tests:
            user.tests += f',{task_id}'
        else:
            user.tests = f'{task_id}'
        db_sess.merge(user)
        db_sess.commit()
        return redirect(f'/tasks/{task_id}/appoint')
    else:
        return 'Доступ закрыт'


@app.route('/tasks/<int:task_id>/open', methods=['GET', 'POST'])
def open_task(task_id):
    if str(task_id) in current_user.tests.split(','):
        db_sess = db_session.create_session()
        task = db_sess.query(Task).get(task_id)
        return render_template('task_page.html', task=task)
    else:
        return 'Доступ закрыт'


@app.route("/authors")
def authors():
    return render_template("authors.html", url='/authors')


@app.errorhandler(404)
def not_found(error):
    print(error)
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(_):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


def new_user(user):
    try:
        os.mkdir('static/users_data/' + str(user.id))
        os.mkdir('static/users_data/' + str(user.id) + '/files')
        os.mkdir('static/users_data/' + str(user.id) + '/avatar')
    except FileExistsError:
        pass


if __name__ == '__main__':
    main()
