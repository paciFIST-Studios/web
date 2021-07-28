
posts = [
    {
        'author': 'Ellie Love',
        'title': 'test post',
        'content': 'first post content',
        'date_posted': '20210724'
    },
    {
        'author': 'Ellie Love 2',
        'title': 'test post 2',
        'content': 'first post content 2',
        'date_posted': '20210724'
    }
]


@app.route('/')
def home():
    return render_template('home.html', posts=posts, title=None)


@app.route('/about')
def about():
    return render_template('about.html', title='Sexy')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for "{ form.username.data }."', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@blog.com' and form.password.data == 'admin0':
            flash(f'Welcome back { form.email.data }', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login unsuccessful.  Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)
