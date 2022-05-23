from flask import Blueprint, render_template
from brewhub import RegistrationForm

views = Blueprint('views', __name__)


@views.route('/')
def home():
    return render_template('index.html')


@views.route('/test')
def test():
    return render_template('test.html')


@views.route('/register', methods=['GET', 'POST'])
def register():
    username = None
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        form.username.data = ''
    return render_template('register.html', username=username, form=form)


@views.route('/login')
def login():
    return render_template('login.html')
