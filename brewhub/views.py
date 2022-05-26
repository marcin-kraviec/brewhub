from flask import Blueprint, render_template
from brewhub import RegistrationForm, LoginForm

views = Blueprint('views', __name__)


@views.route('/')
def home():
    return render_template('index.html')


@views.route('/test')
def test():
    return render_template('test.html')


@views.route('/register', methods=['GET', 'POST'])
def register():
    ages = list(range(18,100))
    username = None
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        form.username.data = ''
    return render_template('register.html', ages=ages, username=username, form=form)


@views.route('/login')
def login():
    form = LoginForm()
    return render_template('login.html', form=form)
