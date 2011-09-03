#====================================================
#        Cycle - calendar for women
#        Distributed under GNU Public License
# Author: Oleg S. Gints (altgo@users.sourceforge.net)
# Home page: http://cycle.sourceforge.net
#===================================================    
"""READ
http://eli.thegreenplace.net/2010/06/25/aes-encryption-of-files-in-python-with-pycrypto/
http://www.python.org/dev/peps/pep-0272/
and then remove this comment
"""

import warnings
# deprecated since release 2.3
warnings.filterwarnings("ignore",
                        category=DeprecationWarning,
                        message='.*rotor module', module=__name__)

import wx
import os, os.path , cPickle
import cal_year
import hashlib
from Crypto.Cipher import AES

try:
    import rotor
except:
    import p_rotor as rotor

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
        objSave.append(['begin',[d.GetDay(), d.GetMonth(), d.GetYear()]])
   
    for d in cal_year.cycle.last:
        objSave.append(['last',[d.GetDay(), d.GetMonth(), d.GetYear()]])
        
    for d in cal_year.cycle.tablet:
        objSave.append(['tablet',[d.GetDay(), d.GetMonth(), d.GetYear()]])

    for d in cal_year.cycle.colour_set.keys():
        objSave.append(['colour', [d, cal_year.cycle.colour_set[d].Get()] ])

    data = cPickle.dumps( objSave, pickle.HIGHEST_PROTOCOL )
    data = data + (16 - len(data) % 16) * chr(16 - len(data) % 16) # 16 is our blocksize

    iv = os.urandom(16)
    key = hashlib.sha256(password).digest()
    encr = AES.new(key, AES.MODE_CBC, iv)
    data = AES.encrypt( data )
    data = cPickle.dumps( { 'username': name, 'iv': iv, 'data': data, 'format': 'AES1' }, pickle.HIGHEST_PROTOCOL )

    p, f_name=get_f_name(file)
    if not os.path.exists(p):
        os.mkdir(p,0700)
    f=open(f_name,"wb")
    f.write(data)
    f.close()

def Load_Cycle(name, password, file):
    #TODO: detect if new AES or old rotor was used for save
    #depad aes data = data[ 0:-ord(data[-1]) ]
    p, f_name=get_f_name(file)
    if os.path.isfile(f_name):
        return True

    data = open( f_name, "rb" )

    if data[:9] == "UserName=":
        # second format, username precedes pickle
        n = data.find("===")+len("===")
        data = load_legacy( data[n:], password )
    else:
        try:
            data = cPickle.loads(data) #data is third format 
        except cPickle.UnpicklingError:
            #must be first format
            data = load_legacy( data, password )

        objLoad = cPickle.loads( data )
        data.close()
        set_color_default()

        for type, d in objLoad:
            if type=='period':
                cal_year.cycle.period=int(d)
            elif type=='by_average':
                cal_year.cycle.by_average=int(d)
            elif type=='disp':
                cal_year.cycle.disp=int(d)
            elif type=='first_week_day':
                cal_year.cycle.first_week_day=int(d)
            elif type=='begin':
                dt=wx.DateTimeFromDMY(d[0], d[1], d[2])
                cal_year.cycle.begin.append(dt)
            elif type=='last':
                dt=wx.DateTimeFromDMY(d[0], d[1], d[2])
                cal_year.cycle.last.append(dt)
            elif type=='tablet':
                dt=wx.DateTimeFromDMY(d[0], d[1], d[2])
                cal_year.cycle.tablet.append(dt)
            elif type=='note':
                cal_year.cycle.note=d.copy()
            elif type=='colour': # d=['item', (r,g,b)]
                c = wx.Colour(d[1][0], d[1][1], d[1][2])
                if cal_year.cycle.colour_set.has_key(d[0]):
                    cal_year.cycle.colour_set[d[0]] = c
                else:
                    cal_year.cycle.colour_set.update({d[0]:c})

            return True

def load_legacy( data, password ):
    #clean me up!
        m=hashlib.md5(password)
        rt=rotor.newrotor(m.digest())
        tmp=rt.decrypt(tmp)
        if tmp[0:5]!='Cycle':
            #            print 'Password is invalid'
            return False
        tmp=tmp[5:] #remove control word 'Cycle'



#-------------------------------------------------------
def get_f_name(name=""):
    if '__WXMSW__' in wx.PlatformInfo:
        p=os.path.join(os.getcwd(),"data")
    else:
        p=os.path.expanduser("~/.cycle")
    f_name=os.path.join(p,name)

    return p, f_name

#-------------------------------------------------------
def set_color_default():
    cal_year.cycle.colour_set={'begin':wx.NamedColour('RED'),
        'prog begin':wx.NamedColour('PINK'),
        'conception':wx.NamedColour('MAGENTA'),
        'safe sex':wx.NamedColour('WHEAT'),
        'fertile':wx.NamedColour('GREEN YELLOW'),
        'ovule':wx.NamedColour('SPRING GREEN'),
        '1-st tablet':wx.NamedColour('GOLD'),
        'pause':wx.NamedColour('LIGHT BLUE'),
        'next 1-st tablet':wx.NamedColour('PINK')}


