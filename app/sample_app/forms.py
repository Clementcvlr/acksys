from flask_wtf import FlaskForm
from wtforms.fields import *
from wtforms.validators import Required, Email


class ChannelTesterForm(FlaskForm):
#    test_id = IntegerField(u'Test identifier', validators=[Required()])
    test_title = "Channel Tester"
    test_description = "Description de l'essai...."
    test_id = TextField(u'Test ID')
    EUT = TextField(u'EUT IP adress', default='192.168.100.20')
    operator = TextField(u'Operator')
#    birthday = DateField(u'Your birthday')

#    a_float = FloatField(u'A floating point number')
#    a_decimal = DecimalField(u'Another floating point number')
    htmode = SelectField(u'HT Mode ', choices=[('ht20', 'HT20'), ('ht40+', 'HT40 Above'), ('ht40-', 'HT40 Below'), ('ht80', 'HT80')], default='ht80')
    wifi_card = SelectField(u'Wifi Card ', coerce=str, choices=[('1', 'WiFi1'), ('2', 'Wifi2'), ('3', 'Wifi3')], default = '1')
    channels_list = [('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10'), ('11', '11'), ('12', '12'), ('13', '13'), ('36', '36'), ('40', '40'), ('44', '44'), ('48', '48'), ('52', '52'), ('56', '56'), ('60', '60'), ('64', '64'), ('100', '100'), ('104', '104'), ('108', '108'), ('112', '112'), ('116', '116'), ('120', '120'), ('124', '124'), ('128', '128'), ('132', '132'), ('136', '136'), ('140', '140'), ('149', '149'), ('153', '153'), ('157', '157'), ('161', '161'), ('165', '165')]
    channels = SelectMultipleField(choices = channels_list, coerce = str, default = ['149'])
    attenuator = SelectField(u'Attenuator', coerce = str, choices=[('39', '39'), ('46', '46'), ('47', '47')], default='46')
    mode = SelectField(u'Mode ', coerce = str, choices=[('AP', 'Access Point'), ('Client', 'Client')], default='AP')
    prot = SelectField(u'Protocole ', coerce = str, choices=[('TCP', 'TCP'), ('UDP', 'UDP'), ('Both', 'Both')], default='Both')
    attn_list = SelectMultipleField(u'Attnuation Steps', choices = [('150', '150'), ('200', '200'), ('250', '250'), ('300', '300'), ('350', '350'), ('400', '400'), ('450', '450'), ('500', '500'), ('550', '550'), ('600', '600'), ('650', '650'), ('700', '700'), ('750', '750'), ('800', '800'), ('850', '850')], coerce = str, default = ['350'])
    attn_duration = IntegerField(u'Attenuator step duration (s)', default='300')
    
    tid_ap = SelectField(u'TID Candela - AP', coerce = str, choices=[('TID_1-1-1-3', 'TID_1-1-1-3')], default = 'TID_1-1-1-3')
    tid_client = SelectField(u'TID Candela - Client', coerce = str, choices=[('TID_1-1-2-3', 'TID_1-1-2-3')], default = 'TID_1-1-2-3')
    tx_power = IntegerField(u'Tx Power (dBm)', default='10')
#    a_integer = IntegerField(u'An integer')

#    now = DateTimeField(u'Current time',
                #        description='...for no particular reason')
    sample_file = FileField(u'Config File')
    eula = BooleanField('wlan1')
    reboot = BooleanField ('Reboot')
    submit = SubmitField(u'Start the test')
"""
        EUT = TextField('EUT:' )
        HTMODE = ['HT20Mhz','HT40Mhz Above', 'HT40Mhz Below', 'HT80Mhz (ac only)']
        availables_prots = ['UDP', 'TCP' ]
        WIFI_CARDS = ['1', '2', '3']
        ATTENUATORS = ['39', '46', '47']
        MODES = ['Access Point', 'Client']
        CHANNELS = ['1','2','3','4','5','6','7','8','9','10','11','12','13','36','40','44','48','52','56','60','64']
"""


class PerfTesterForm(FlaskForm):
    test_title = "Perf Test"
    test_description = "Description de l'essai...."
#    test_id = IntegerField(u'Test identifier', validators=[Required()])
    EUT = TextField('EUT IP adress')
    email = TextField(u'Operator')
#    birthday = DateField(u'Your birthday')

#    a_float = FloatField(u'A floating point number')
#    a_decimal = DecimalField(u'Another floating point number')
    htmode = SelectField(u'HT Mode ', choices=[('ht20', 'HT20'), ('ht40+', 'HT40 Above'), ('ht40-', 'HT40 Below'), ('ht80', 'HT80')])
    wifi_card = SelectField(u'Wifi Card ', choices=[('1', 'WiFi1'), ('2', 'Wifi2'), ('3', 'Wifi3')])
    channels_list = [('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10'), ('11', '11'), ('12', '12'), ('13', '13'), ('36', '36'), ('40', '40'), ('44', '44'), ('48', '48'), ('52', '52'), ('56', '56'), ('60', '60'), ('64', '64'), ('100', '100'), ('104', '104'), ('108', '108'), ('112', '112'), ('116', '116'), ('120', '120'), ('124', '124'), ('128', '128'), ('132', '132'), ('136', '136'), ('140', '140'), ('149', '149'), ('153', '153'), ('157', '157'), ('161', '161'), ('165', '165')]
    channels = SelectMultipleField(choices = channels_list, default = ['149'])
    attenuator = SelectField(u'Attenuator', choices=[('39', '39'), ('46', '46'), ('47', '47')])
    mode = SelectField(u'Mode ', choices=[('AP', 'Access Point'), ('Client', 'Client')])
#    a_integer = IntegerField(u'An integer')

#    now = DateTimeField(u'Current time',
                #        description='...for no particular reason')
    eula = BooleanField('wlan1')
    reboot = BooleanField ('Reboot')
    submit = SubmitField(u'Start the test')
"""
        EUT = TextField('EUT:' )
        HTMODE = ['HT20Mhz','HT40Mhz Above', 'HT40Mhz Below', 'HT80Mhz (ac only)']
        availables_prots = ['UDP', 'TCP' ]
        WIFI_CARDS = ['1', '2', '3']
        ATTENUATORS = ['39', '46', '47']
        MODES = ['Access Point', 'Client']
        CHANNELS = ['1','2','3','4','5','6','7','8','9','10','11','12','13','36','40','44','48','52','56','60','64']
"""


class LoginForm(FlaskForm):
    username = StringField('username', validators=[Required()])
    password = PasswordField('password', validators=[Required()])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    email = StringField('email', validators=[Required(), Email(message='Invalid email')])
    username = StringField('username', validators=[Required()])
    password = PasswordField('password', validators=[Required()])
    role = StringField('username', validators=[Required()])

