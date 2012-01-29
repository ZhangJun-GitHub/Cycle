#====================================================
#        Cycle - calendar for women
#        Distributed under GNU Public License
# Original author: Oleg S. Gints
# Maintainer: Matt Molyneaux (moggers87+git@moggers87.co.uk)
# Home page: http://moggers.co.uk/cgit/cycle.git/about
#===================================================    

## READ ##
# http://eli.thegreenplace.net/2010/06/25/aes-encryption-of-files-in-python-with-pycrypto/
# http://www.python.org/dev/peps/pep-0272/
# and then touch this code

import wx
import os, os.path , cPickle
import cal_year
import hashlib
from Crypto.Cipher import AES

try:
    import rotor
except:
    import p_rotor as rotor

FILE_FORMATS = ['AES1']

def Save_Cycle(name, password, file):
    """ Save the contents of our document to disk.
    """
    objSave = []
    objSave.append(['period', cal_year.cycle.period])
    objSave.append(['by_average', cal_year.cycle.by_average])
    objSave.append(['disp', cal_year.cycle.disp])
    objSave.append(['first_week_day', cal_year.cycle.first_week_day])
    objSave.append(['note', cal_year.cycle.note])
    for d in cal_year.cycle.begin:
        objSave.append(['begin', [d.GetDay(), d.GetMonth(), d.GetYear()]])
   
    for d in cal_year.cycle.last:
        objSave.append(['last', [d.GetDay(), d.GetMonth(), d.GetYear()]])
        
    for d in cal_year.cycle.tablet:
        objSave.append(['tablet', [d.GetDay(), d.GetMonth(), d.GetYear()]])

    for d in cal_year.cycle.colour_set.keys():
        objSave.append(['colour', [d, cal_year.cycle.colour_set[d].Get()] ])

    data = cPickle.dumps(objSave, cPickle.HIGHEST_PROTOCOL)
    data = data + (16 - len(data) % 16) * chr(16 - len(data) % 16) # 16 is our blocksize

    iv = os.urandom(16)
    key = hashlib.sha256(password).digest()
    encr = AES.new(key, AES.MODE_CBC, iv)
    data = encr.encrypt(data)
    data = cPickle.dumps({'username': name, 'iv': iv, 'data': data, 'format': 'AES1'}, cPickle.HIGHEST_PROTOCOL)

    p, f_name = get_f_name(file)
    if not os.path.exists(p):
        os.mkdir(p, 0700)
    f = open(f_name, "wb")
    f.write(data)
    f.close()

def Load_Cycle(name, password, file):
    p, f_name = get_f_name(file)
    if not os.path.isfile(f_name):
        return False

    data = open(f_name, "rb").read()

    try:
        tmp = load_dict_format(data, password)
    except:
        tmp = load_legacy(data, password)

    if tmp is False:
        return False
    else:
        data = tmp

    try:
        objLoad = cPickle.loads(data)
    except cPickle.UnpicklingError:
        return False

    set_color_default()

    for type, d in objLoad:
        if type == 'period':
            cal_year.cycle.period = int(d)
        elif type == 'by_average':
            cal_year.cycle.by_average = int(d)
        elif type == 'disp':
            cal_year.cycle.disp = int(d)
        elif type == 'first_week_day':
            cal_year.cycle.first_week_day = int(d)
        elif type == 'begin':
            dt = wx.DateTimeFromDMY(d[0], d[1], d[2])
            cal_year.cycle.begin.append(dt)
        elif type == 'last':
            dt = wx.DateTimeFromDMY(d[0], d[1], d[2])
            cal_year.cycle.last.append(dt)
        elif type == 'tablet':
            dt=wx.DateTimeFromDMY(d[0], d[1], d[2])
            cal_year.cycle.tablet.append(dt)
        elif type == 'note':
            cal_year.cycle.note=d.copy()
        elif type == 'colour': # d=['item', (r,g,b)]
            c = wx.Colour(d[1][0], d[1][1], d[1][2])
            if cal_year.cycle.colour_set.has_key(d[0]):
                cal_year.cycle.colour_set[d[0]] = c
            else:
                cal_year.cycle.colour_set.update({d[0]:c})
    return True

def load_legacy(data, password):
    #clean me up!
    if data[:9] == "UserName=":
        #second format, username precedes pickle
        n = data.find("===") + len("===")
        data = data[n:]

    m = hashlib.md5(password)
    rt = rotor.newrotor(m.digest())
    data = rt.decrypt(data)

    if data[0:5] != 'Cycle': # print 'Password is invalid'
        return False
    data = data[5:] #remove control word 'Cycle'

    return data

def load_dict_format(data, password):
    data = cPickle.loads(data)
    if data['format'] not in FILE_FORMATS:
        return False

    iv = data['iv']
    key = hashlib.sha256(password).digest()
    encr = AES.new(key, AES.MODE_CBC, iv)
    data = encr.decrypt(data['data'])
    data = data[0:-ord(data[-1])]    

    return data

#---------------------------------------------------------------------------
def get_users():
    """Get list of users"""
    magic_str = 'UserName='
    users = [] #array of (user, file) name
    p, f_name = get_f_name()
    if os.path.exists(p):
        files = os.listdir(p)
        for f in files:
            fd = open(os.path.join(p, f), "rb")
            try:
                data = cPickle.loads(fd.read())
            except:
                fd.seek(0)
                data = fd.read(len(magic_str))

            if 'username' in data:
                users.append((data['username'], f))
            elif data == magic_str:
                data = fd.read()
                n = data.find("===") #find end string
                if n is not -1:
                    users.append((cPickle.loads(data[:n]), f))
            else: #old format
                users.append((f, f))
        users.sort()
    return users

#-------------------------------------------------------
def get_new_file_name():
    """Generate filename for user"""
    while True:
        random_chars = "".join(chr(random.randint(0,255)) for i in xrange(4))
        random_chars = base64.urlsafe_b64encode(random_chars)
        p, random_chars = get_f_name(random_chars)
        if not os.path.isfile(random_chars):
            return random_chars

#-------------------------------------------------------
def get_f_name(name=""):
    """Get path for filename, then return directory path and full path.

    I think."""
    p = os.path.expanduser("~/.cycle")
    f_name = os.path.join(p, name)

    return p, f_name

#-------------------------------------------------------
def set_color_default():
    cal_year.cycle.colour_set = {'begin':wx.NamedColour('RED'),
        'prog begin':wx.NamedColour('PINK'),
        'conception':wx.NamedColour('MAGENTA'),
        'fertile':wx.NamedColour('GREEN YELLOW'),
        'ovule':wx.NamedColour('SPRING GREEN'),
        '1-st tablet':wx.NamedColour('GOLD'),
        'pause':wx.NamedColour('LIGHT BLUE'),
        'next 1-st tablet':wx.NamedColour('PINK')}


