# This contains our frontend; since it is a bit messy to use the @app.route
# decorator style when using application factories, all of our routes are
# inside blueprints. This is the front-facing blueprint.
#
# You can find out more about blueprints at
# http://flask.pocoo.org/docs/blueprints/
# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_bootstrap import __version__ as FLASK_BOOTSTRAP_VERSION
from flask_nav.elements import Navbar, View, Subgroup, Link, Text, Separator
from markupsafe import escape
import dominate
from dominate.tags import img
import json
import datetime, time
import os, ast
from threading import Event

#from .forms import ChannelTesterForm
from .forms import PerfTesterForm, LoginForm, RegisterForm, ChannelTesterForm
from .nav import nav
from flask_table import Table, Col
from .table import *
#from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_user import UserManager, current_user,roles_required, login_required
from .users import User, UserRoles, Role, db
import candela_channel_tester 
from conf_template_updater import ConfUpdater

#TODO: Delete this test lines :
#from .arm import Arm
#user_manager = UserManager()

#db = SQLAlchemy()
frontend = Blueprint('frontend', __name__)
#login_manager = LoginManager()
#login_manager.login_view = "frontend.login"
#@login_manager.user_loader
#def load_user(user_id):
#    return User.query.get(int(user_id))
#branding2 = img(src='static/img/logo2.png')

# We're adding a navbar as well through flask-navbar. In our example, the
# navbar has an usual amount of Link-Elements, more commonly you will have a
# lot more View instances.
nav.register_element('frontend_top', Navbar(
 #   branding2,
    View(img(src='/static/img/logo_nav.png'), '.index'),
    View('Home', '.index'),
    View('Channel Tester', '.Channel_Tester'),
#    View('Debug-Info', 'debug.debug_root'),
    View('Results', '.Res_Table'),
    Subgroup(
        'Test Campaign',
        Text('Performances Test'),
        View('Channel Tester', '.Channel_Tester'),
        View('Perf Test', '.Perf_test'),
        Separator(),
        Text('Functionnal Test -- (Todo)'),
        Separator(),
        Text('Docs'),
        Link('Flask-Debug', 'https://github.com/mbr/flask-debug'),
        Link('Flask-Bootstrap', 'http://pythonhosted.org/Flask-Bootstrap'),
        Link('Getting started', 'http://getbootstrap.com/getting-started/'),
        Link('CSS', 'http://getbootstrap.com/css/'),
        Link('Components', 'http://getbootstrap.com/components/'),
        Link('Javascript', 'http://getbootstrap.com/javascript/'),
        Link('Customize', 'http://getbootstrap.com/customize/'), ),
    View('Login', '.login'),
    View('Logout', '.logout'),
    ))



# Our index-page just shows a quick explanation. Check out the template
# "templates/index.html" documentation for more details.
@frontend.route('/')
def index():
    return render_template('index.html')


# Shows a long signup form, demonstrating form rendering.
@frontend.route('/Channel_tester/', methods=('GET', 'POST'))
def Channel_Tester():
    form = ChannelTesterForm(csrf_enabled=False)
    print("CC , first Debug :",form.errors)

    if form.is_submitted():
        print "submitted"

    if form.validate():
        print "validated"

    if form.submit.data and request.method == 'POST' and form.validate_on_submit():
        # We don't have anything fancy in our application, so we are just
        # flashing a message when a user completes the form successfully.
        #
        # Note that the default flashed messages rendering allows HTML, so
        # we need to escape things if we input user values:
	
	#ICI je dois appeler ma classe et lui envoyer les donnes du form

	#test = CandelaChannelTester(form)
	#form.process()
	Config ={}
	Config['EUT'] = request.form['EUT']
	Config['test_id'] = request.form['test_id']
	Config['operator'] = request.form['operator']
	Config['htmode'] = request.form['htmode']
	Config['wifi_card'] = request.form['wifi_card']
	Config['channels'] = form.channels.data
	Config['attenuator'] = request.form['attenuator']
	Config['mode'] = request.form['mode']
	Config['prot'] = form.prot.data
	Config['tid_ap'] = request.form['tid_ap']
	Config['tid_client'] = request.form['tid_client']
	Config['tx_power'] = request.form['tx_power']
	Config['reboot'] = form.reboot.data
	Config['attn_list'] = form.attn_list.data
	Config['attn_duration'] = request.form['attn_duration']
	print Config
	print("CC", Config['EUT'])
	#a = candela_channel_tester.CandelaChannelTester(Config)
	#a.background_launcher()

	EUT = request.form['EUT']
	operator = request.form['operator']
	htmode = request.form['htmode']
	wifi_card = request.form['wifi_card']
	channels = form.channels.data
	attenuator = request.form['attenuator']

	print(type(form.EUT), type(form.EUT.data))
	print(str(form.EUT.data), "CC EUT Debug")
	print(form.EUT.data, "CC EUT Debug")
	#print(request.form['EUT'], "CC EUT Debug")
	print(form)
	

        flash('EUT: {0}  \nOperator {1} \nHT Mode : {2}, wifi_card : {3}, channels : {4} attenuator : {5} '
        .format(EUT, operator, htmode, wifi_card, form.channels.data,attenuator))
	
        #items = [Config('EUT', 'mode')]
	#items = [  
	#	dict(name=key, description=val) for key,val in Config.items()]
		
	items = [  
		dict(name='monimage', description=img(src="/static/img/accept.png")) ]

	# Populate the table

	table = ItemTable(items, classes=["table", "table-striped", "table-hover"])
	#arm = MaClass()


        # In a real application, you may wish to avoid this tedious redirect.
        #return render_template('res.html', Config=Config)
	print("Before Redirect", type(Config))
	return redirect(url_for('.Res_Table', Config=Config))
	#render_template('channel_tester.html', test=test)
    else:
    	flash('Error in the signup Form', 'error')
    print("CC , second Debug :",form.errors)
    return render_template('signup.html', form=form)


@frontend.route('/Perf_test/', methods=('GET', 'POST'))
def Perf_test():
    form = PerfTesterForm(csrf_enabled=False)
    print("CC , first Debug :",form.errors)

    if form.is_submitted():
        print "submitted"

    if form.validate():
        print "validated"

    if form.validate_on_submit():
        # We don't have anything fancy in our application, so we are just
        # flashing a message when a user completes the form successfully.
        #
        # Note that the default flashed messages rendering allows HTML, so
        # we need to escape things if we input user values:
        flash('Operator : {0} EUT: {5} Htmode {1} eula : {2}, reboot : {4}, channels : {6} submit : {5} '
              .format(escape(form.email.data), escape(form.htmode.data), escape(form.eula.data), escape(form.EUT.data),escape(form.reboot.data),escape(form.submit.data), escape(form.channels.data)))

        # In a real application, you may wish to avoid this tedious redirect.
        return redirect(url_for('.index'))

    print("CC , second Debug :",form.errors)
    return render_template('signup.html', form=form)


@frontend.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
		flash('Successfully logged in')
                return redirect(url_for('.index'))

        return '<h1>Invalid username or password</h1>'
    return render_template('login.html', form=form)

@frontend.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
	print(type(form.role.data), type(datetime.datetime.utcnow()))
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password, email_confirmed_at=datetime.datetime.utcnow())
	new_user.roles.append(Role(name='Admin'))
        db.session.add(new_user)
        db.session.commit()

        return '<h1>New user has been created!</h1>'
        #return '<h1>' + form.username.data + ' ' + form.email.data + ' ' + form.password.data + '</h1>'

    return render_template('mysignup.html', form=form)
@frontend.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Goodbye') 
    return redirect(url_for('.index'))

STOP_EVENT = Event()

@frontend.route('/Results/', methods=('GET', 'POST'))
#@roles_required('Admin')
def Res_Table():
	# import things
#	Config ={}
#	Config['prot'] = ['TCP', 'UDP']
#	Config['sens'] = ['APtoClient', 'ClienttoAP'] 
#	Config['channels'] = ['1','2','3','4','5','6','7','8','9','10','11','12','13','100','112']

	Config = request.args["Config"]
	print(Config)
	print("Error ici")
	print(type(Config))
	Config = ast.literal_eval(Config)
	Config['countries'] = ["US"]
	Config['htmodes'] = ["vht80"]
	new_conf = ConfUpdater(Config, Config['htmodes'][0], Config['countries'][0]).get_conf()
	global thread
	thread = candela_channel_tester.CandelaChannelTester(new_conf, STOP_EVENT)
	thread.start()
	#a.background_launcher()

	items = []
	#for key, value in Config.iteritems() :

		#items.append(Item(key, value))
	print("Dans la page Res")
	print(type(items))
	# Populate the table
	#table = ItemTable(items, classes=["table", "table-striped", "table-hover"])
	#print(type(table))

	# Print the html
	#for f in os.listdir('.'):
	#	print(f)
	#for f in os.listdir('./sample_app/static/'):
	#	print(f)
	time.sleep(5)
	with open("/tmp/candela_channel/34_vht80_US/jsonfile.json", 'r+') as f:
        	json_data = json.loads(f.read())
		#print(json_data['channel']['TCP']['APtoClient'])
	 
    	return render_template('res.html',Config=Config, json_data=json_data)

@frontend.route('/Stop/', methods=('GET', 'POST'))
def Stop():
	STOP_EVENT.set()
	global thread
	thread.join()
	return "STOP", 9999
