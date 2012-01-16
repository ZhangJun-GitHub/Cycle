#====================================================
#        Cycle - calendar for women
#        Distributed under GNU Public License
# Original author: Oleg S. Gints
# Maintainer: Matt Molyneaux (moggers87+git@moggers87.co.uk)
# Home page: http://moggers.co.uk/cgit/cycle.git/about
#===================================================

import wx
import wx.calendar
import calendar
import operator
from dialogs import Note_Dlg

class Val:
    pass

MARK_BEGIN  = 1
MARK_FERT   = 1<<1
MARK_OVUL   = 1<<2
MARK_SAFESEX= 1<<3 #compat. with older versions
MARK_TODAY  = 1<<4
MARK_NOTE   = 1<<5
MARK_PROG   = 1<<6
MARK_LAST   = 1<<7 #last cycle, conception begin
MARK_BIRTH  = 1<<8
MARK_TABLET = 1<<9 #1-st hormonal tablet
MARK_T22_28 = 1<<10 #tablets 22-28 or pause 7 days
MARK_NEXT_TABLET = 1<<11

class Month_Cal(wx.calendar.CalendarCtrl):
    """Draws a single month"""
    def __init__(self, parent, id, date, pos=wx.DefaultPosition, size=wx.DefaultSize, style=0):
        style = wx.calendar.CAL_NO_YEAR_CHANGE | wx.calendar.CAL_NO_MONTH_CHANGE | wx.NO_BORDER
        if cycle.first_week_day == 0:
            style = style | wx.calendar.CAL_MONDAY_FIRST
        else:
            style = style | wx.calendar.CAL_SUNDAY_FIRST
        try:
            style = style | wx.calendar.CAL_SEQUENTIAL_MONTH_SELECTION
        except NameError:
            pass

        wx.calendar.CalendarCtrl.__init__(self, parent, id, date, pos, size, style)
        self.SetBackgroundColour(wx.WHITE)
        self.SetHeaderColours(wx.BLACK, wx.WHITE)
        if '__WXMSW__' in wx.PlatformInfo:
            font = self.GetFont()
            font.SetFaceName("MS Sans Serif")
            self.SetFont(font)

        self.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_KEY_UP, self.OnKey)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKey)
        self.date_click = wx.DateTime()

    def OnLeftDown(self, event):
        result, date, wday = self.HitTest(event.GetPosition())
        if result == wx.calendar.CAL_HITTEST_DAY:
            Val.frame.SetStatusText(info(date))

    def OnRightDown(self, event):
        result, date, wday = self.HitTest(event.GetPosition())
        if result == wx.calendar.CAL_HITTEST_DAY:
            self.date_click = date
            menu = wx.Menu()
            menu.Append(1, date.Format('%d %B'))
            menu.AppendSeparator()
            menu.AppendCheckItem(2, _('Beginning of cycle'))
            menu.Check(2, is_set_mark(date, MARK_BEGIN, date.GetYear()))
            menu.AppendCheckItem(5, _('1-st tablet'))
            menu.Check(5, is_set_mark(date, MARK_TABLET, date.GetYear()))
            if is_set_mark(date, MARK_BEGIN, date.GetYear()):
                menu.AppendCheckItem(3, _('Conception'))
                menu.Check(3, is_set_mark(date, MARK_LAST, date.GetYear()))
            menu.AppendCheckItem(4, _('Note'))
            menu.Check(4, is_set_mark(date, MARK_NOTE, date.GetYear()))

            self.Bind(wx.EVT_MENU, self.OnBegin, id=2)
            self.Bind(wx.EVT_MENU, self.OnLast, id=3)
            self.Bind(wx.EVT_MENU, self.OnNote, id=4)
            self.Bind(wx.EVT_MENU, self.OnTablet, id=5)
            self.PopupMenu(menu, event.GetPosition())
            menu.Destroy()

    def OnBegin(self, event):
        if self.date_click in cycle.begin:
            cycle.begin.remove(self.date_click)
            if self.date_click in cycle.last:
                cycle.last.remove(self.date_click)
            remove_mark(self.date_click, MARK_BEGIN, self.date_click.GetYear())
            remove_mark(self.date_click, MARK_LAST, self.date_click.GetYear())
        else:
            cycle.begin.append(self.date_click)
            cycle.begin.sort()
            add_mark(self.date_click, MARK_BEGIN, self.date_click.GetYear())
        Val.Cal.Draw_Mark()

    def OnLast(self, event):
          if self.date_click in cycle.begin:
            if self.date_click in cycle.last:
                cycle.last.remove(self.date_click)
                remove_mark(self.date_click, MARK_LAST, self.date_click.GetYear())
            else:
                cycle.last.append(self.date_click)
                cycle.last.sort()
                add_mark(self.date_click, MARK_LAST, self.date_click.GetYear())
            Val.Cal.Draw_Mark()

    def OnNote(self, event):
        txt = get_note(self.date_click)
        dlg = Note_Dlg(self, self.date_click.Format('%d %B'), txt)
        ret = dlg.ShowModal()
        note = dlg.Get_Txt()
        dlg.Destroy()
        if ret == wx.ID_OK:
            add_note(self.date_click, note )
            add_mark(self.date_click, MARK_NOTE, self.date_click.GetYear())
        elif ret == False:
            remove_note(self.date_click)
            remove_mark(self.date_click, MARK_NOTE, self.date_click.GetYear())
        elif ret == wx.ID_CANCEL:
            return
        Val.Cal.Draw_Mark()

    def OnTablet(self, event):
        if self.date_click in cycle.tablet:
            cycle.tablet.remove(self.date_click)
            remove_mark(self.date_click, MARK_TABLET, self.date_click.GetYear())
        else:
            cycle.tablet.append(self.date_click)
            cycle.tablet.sort()
            add_mark(self.date_click, MARK_TABLET, self.date_click.GetYear())
        Val.Cal.Draw_Mark()

    def OnKey(self, event):
        code = event.GetKeyCode()
        if code in (WXK_LEFT, WXK_RIGHT, WXK_UP, WXK_DOWN):
            pass
        else:
            event.Skip()

class Cal_Year(wx.ScrolledWindow):
    """This class seems to bring everything together"""
    def __init__(self, parent):
        wx.ScrolledWindow.__init__(self, parent, -1)
        self.SetBackgroundColour(wx.NamedColour('LIGHT BLUE'))

        today = wx.DateTime_Today()
        self.year = today.GetYear()

        self.day_of_year = []
        self.month = []
        Val.Cal = self
        self.Init_Year()

    def Inc_Year(self):
        self.year += 1
        self.Draw_Year()
        reset_mark(self.year)
        self.Draw_Mark()

    def Dec_Year(self):
        self.year -= 1
        self.Draw_Year()
        reset_mark(self.year)
        self.Draw_Mark()

    def Set_Year(self, year):
        self.year = year
        self.Draw_Year()
        reset_mark(self.year)
        self.Draw_Mark()

    def Init_Year(self):
        """Draw calendar"""
        month = 0
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(wx.StaticLine(self, -1, style=wx.LI_HORIZONTAL), 0, wx.EXPAND )
        for y in xrange(3):
            row_box = wx.BoxSizer(wx.HORIZONTAL)
            for x in xrange(4):
                date = wx.DateTimeFromDMY(1, month, self.year)
                id = wx.NewId()
                self.month.append(Month_Cal(self, id, date))
                row_box.Add(self.month[month], 0, wx.ALL, 5)
                month += 1
            box.Add(row_box, 0, wx.LEFT | wx.RIGHT, 10)

        self.SetAutoLayout(True)
        self.SetSizer(box)
        box.Fit(self)
        w = box.GetSize().GetWidth()
        h = box.GetSize().GetHeight()
        Val.frame.SetSize(wx.Size(w + 10, h + 90))
        self.SetScrollbars(20, 20, w / 20, h / 20)

    def Draw_Year(self):
        """Redraw calendar for a new year"""
        Val.frame.SetTitle(cycle.name + " - " + str(self.year))
        for month.nth in self.month:
            month.EnableYearChange(True)
            month.EnableMonthChange(True)

            date = month.getDate()
            date.SetYear(self.year)
            month.SetDate(date)

            month.EnableYearChange(False)
            month.EnableMonthChange(False)

            month.Refresh()

    def Draw_Mark(self):
        #TODO: use somonth. better variable names
        font_normal = self.month[1].GetFont()
        font_normal.SetUnderlined(False)
        font_underline = self.month[1].GetFont()
        font_underline.SetUnderlined(True)

        today = wx.DateTime_Today()
        if self.year == today.GetYear():
            add_mark(today, MARK_TODAY, self.year)

        calc_fert(self.year)
        calc_tablet(self.year)
        k = 1
        for m in xrange(12):
            sel_hide = True #need hide selection
            for d in xrange(1, wx.DateTime_GetNumberOfDaysInMonth(m, self.year) + 1):
                can_hide = True
                lab = cycle.mark.get(k, 0)
                at = self.month[m].GetAttr(d)
                if at is None :
                    at = wx.calendar.CalendarDateAttr(wx.BLACK)
                    self.month[m].SetAttr(d, at)

                #reset attributes
                at.SetBorder(wx.calendar.CAL_BORDER_NONE)
                at.SetBackgroundColour(wx.WHITE)
                at.SetTextColour(wx.BLACK)
                at.SetFont(font_normal)

                current_date = wx.DateTimeFromDMY(d, m, self.year)

                if not current_date.IsWorkDay(): #mark weekend
                    at.SetTextColour(wx.NamedColour('firebrick'))

                if lab & MARK_BEGIN:
                    at.SetBackgroundColour(cycle.colour_set['begin'])
                    at.SetTextColour(wx.WHITE)

                if lab & MARK_PROG:
                    at.SetBackgroundColour(cycle.colour_set['prog begin'])
                    at.SetTextColour(wx.BLACK)

                if lab & MARK_FERT and (cycle.disp == 0):
                    at.SetBackgroundColour(cycle.colour_set['fertile'])

                if lab & MARK_OVUL and (cycle.disp == 0):
                    at.SetBackgroundColour(cycle.colour_set['ovule'])

                if lab & MARK_TODAY :
                    at.SetBorderColour(wx.NamedColour('NAVY'))
                    at.SetBorder(wx.calendar.CAL_BORDER_SQUARE)
                    can_hide = False

                if lab & MARK_LAST :
                    at.SetBackgroundColour(cycle.colour_set['conception'])

                if lab & MARK_NOTE:
                    at.SetFont(font_underline)
                    can_hide = False

                if lab & MARK_BIRTH :
                   at.SetBackgroundColour(cycle.colour_set['ovule'])

                if lab & MARK_TABLET :
                    at.SetBackgroundColour(cycle.colour_set['1-st tablet'])

                if lab & MARK_T22_28 :
                    at.SetBackgroundColour(cycle.colour_set['pause'])

                if lab & MARK_NEXT_TABLET :
                    at.SetBackgroundColour(cycle.colour_set['next 1-st tablet'])

                if sel_hide and can_hide:
                    #we can hide selection when don't use border and underlined
                    sel_hide = False
                    self.month[m].SetDate(current_date)
                    self.month[m].SetHighlightColours(at.GetTextColour(),
                                at.GetBackgroundColour())

                k += 1

        # so visual refresh is more fast
        for m in self.month:
            m.Refresh()

#-------------------- work with cycle -------------------
class cycle:
    begin = []
    last = []
    tablet = []
    period = 28
    mark = {}
    passwd = "123"
    name = "empty"
    file = "empty"
    by_average = False
    disp = 0
    first_week_day = 0
    note = {}
    colour_set = {}

def min_max(i):
    """Return length max and min of 6 last cycles
    from i item cycle.begin"""

    if len(cycle.begin) < 2 or i == 0:
        return cycle.period, cycle.period

    last_6 = []
    for k in xrange(i, 0, -1):
        span = (cycle.begin[k] - cycle.begin[k - 1] + wx.TimeSpan.Hours(1)).GetDays()
        if 20 < span <36:
            last_6.append(span)
            if len(last_6) >= 6:
                break

    if cycle.by_average and len(last_6) != 0:
        s = float(reduce(operator.add, last_6)) # sum of last_6
        cycle.period = int(round(s / len(last_6), 0))

    if last_6 == []:
        return cycle.period, cycle.period
    return min(last_6), max(last_6)


def calc_fert(year):
    for k in cycle.mark.keys():
        cycle.mark[k] = cycle.mark[k] & ~MARK_FERT & \
        ~MARK_OVUL & ~MARK_PROG & ~MARK_SAFESEX & ~MARK_BIRTH & \
        ~MARK_T22_28 & ~MARK_NEXT_TABLET

    if cycle.begin == []: return

    year_begin = wx.DateTimeFromDMY(1, 0, year)
    year_end = wx.DateTimeFromDMY(31, 11, year)
    for d in cycle.begin:
        i = cycle.begin.index(d)
        if i < len(cycle.begin)-1:
            if (cycle.begin[i + 1] - cycle.begin[i] + wx.TimeSpan.Hours(1)).GetDays() < 21:
                continue

        min, max = min_max(i)
        begin = d + wx.DateSpan.Days(min - 18) # begin fertile
        end = d + wx.DateSpan.Days(max - 11) # end fertile
        ovul = end-wx.DateSpan.Days(((max - 11) - (min - 18)) / 2) #day of ovul
        if year_begin <= ovul <= year_end:
            add_mark(ovul, MARK_OVUL, year)

        start = d + wx.DateSpan_Day()
        if i < len(cycle.begin) - 1:
            last_cycle = (cycle.begin[i + 1] - cycle.begin[i] + wx.TimeSpan.Hours(1)).GetDays()
            if last_cycle > 35:
                stop = d + wx.DateSpan.Days(35)
            else:
                stop = cycle.begin[i + 1] - wx.DateSpan_Day()
        else:
            stop = d + wx.DateSpan.Days(cycle.period - 1)

        if (stop < year_begin or start > year_end) and (d not in cycle.last):
            continue
        f = start
        while f.IsBetween(start, stop):
            if f.IsBetween(begin, end):
                add_mark(f, MARK_FERT, year)
            f = f + wx.DateSpan_Day()

        if d in cycle.last: # calc birthday
            birth = d + wx.DateSpan.Days(280 + cycle.period - 28)
            if i < len(cycle.begin) - 1: # not last item
                if birth < cycle.begin[i + 1]:
                    add_mark(birth, MARK_BIRTH, year)
            else: #last item
                add_mark(birth, MARK_BIRTH, year)
                return

    # prognosis to future cycles
    cycle.prog_begin = []
    d = d + wx.DateSpan.Days(cycle.period)
    while d.GetYear() <= year:
        if cycle.tablet != [] and cycle.tablet[-1] <= d and \
            cycle.begin[-1] <= cycle.tablet[-1]: return
        if d.GetYear() == year:
            #            cycle.prog_begin.append(d)
            add_mark(d, MARK_PROG, year)

        begin = d + wx.DateSpan.Days(min - 18)
        end = d + wx.DateSpan.Days(max - 11)
        ovul = end - wx.DateSpan.Days(((max - 11) - (min - 18)) / 2) #day of ovul
        if year_begin <= ovul <= year_end:
            add_mark(ovul, MARK_OVUL, year)

        start = d + wx.DateSpan.Day()
        stop =d + wx.DateSpan.Days(cycle.period - 1)
        d = d + wx.DateSpan.Days(cycle.period)

        if stop < year_begin or start > year_end:
            continue

        f = start
        while f.IsBetween(start, stop):
            if f.IsBetween(begin, end):
                add_mark(f, MARK_FERT, year)
            f = f + wx.DateSpan_Day()

def calc_tablet(year):
    """calculation result of using hormonal tablets"""
    if cycle.tablet == []:
        return
    year_begin = wx.DateTimeFromDMY(1, 0, year)
    year_end = wx.DateTimeFromDMY(31, 11, year)
    for d in cycle.tablet:
        i = cycle.tablet.index(d)
        if i < len(cycle.tablet) - 1:
            if (cycle.tablet[i + 1] - cycle.tablet[i] + wx.TimeSpan.Hours(1)).GetDays() < 28:
                #incorrect using - must more 28 days
                continue
        for k in xrange(28):
            remove_mark(d + wx.DateSpan.Days(k), MARK_PROG | MARK_FERT |
            MARK_NEXT_TABLET | MARK_OVUL | MARK_SAFESEX | MARK_BIRTH, year)
        for k in xrange(21, 28):
            add_mark(d + wx.DateSpan.Days(k), MARK_T22_28, year)
        add_mark(d + wx.DateSpan.Days(28), MARK_NEXT_TABLET, year)

def add_mark(date, mark, year):
    if date.GetYear() == year:
        day = date.GetDayOfYear()
        cycle.mark[day] = cycle.mark.get(day, 0) | mark

def remove_mark(date, mark, year):
    if date.GetYear() == year:
        k = date.GetDayOfYear()
        cycle.mark[k] = cycle.mark.get(k, 0) & ~mark

def is_set_mark(date, mark, year):
    if date.GetYear() == year:
        k = date.GetDayOfYear()
        return cycle.mark.get(k, 0) & mark
    else:
        return False

def reset_mark(year):
    cycle.mark.clear()
    for k in cycle.begin:
        if k.GetYear() == year:
            add_mark(k, MARK_BEGIN, year)
    for k in cycle.last:
        if k.GetYear() == year:
            add_mark(k, MARK_LAST, year)
    for k in cycle.tablet:
        if k.GetYear() == year:
            add_mark(k, MARK_TABLET, year)
    for k in cycle.note.keys():
        if str(year) == k[0:4]:
            d = wx.DateTimeFromDMY(int(k[6:8]), int(k[4:6]) - 1, int(k[0:4]))
            add_mark(d, MARK_NOTE, year)

def info(day):
    s = day.Format('%d %B')
    if cycle.tablet != []:
        for d in cycle.tablet:
            if day.IsBetween(d, d + wx.DateSpan.Days(28)):
                t = (day - d + wx.TimeSpan.Hours(1)).GetDays() + 1
                s += " - "
                if t <= 28:
                    s += _('tablet N ') + str(t)
                if 22 <= t <= 28:
                    s += _(' or pause')
                if t == 29:
                    s += _('next 1-st tablet')
                return s

    if cycle.begin == []:
        return s
    if day < cycle.begin[0]:
        return s

    find = 0
    gestation = 0
    for d in cycle.begin:
        if day < d:
            find = 1
            break

    if find == 0:
        if d in cycle.last:
            gestation = 1
            d2 = d
        else:
            while d <= day:
                if cycle.tablet != [] and cycle.tablet[-1] <= d and \
                   cycle.begin[-1] <= cycle.tablet[-1]:
                    return s
                d = d + wx.DateSpan.Days(cycle.period)
            find = 2

    if find == 1:
        i = cycle.begin.index(d)
        d2 = cycle.begin[i - 1]
        if d2 in cycle.last:
            gestation = 1
    elif find == 2:
        d2 = d - wx.DateSpan.Days(cycle.period)

    if gestation:
        k = (day - d2 + wx.TimeSpan.Hours(1)).GetDays() + 1
        w = (k - 1) / 7
        s += " - " + str(k) + _('% day of gestation, ') + str(w)

        if w == 1:
            s += _('1 week')
        else:
            s += _('% weeks')

        s += ' + ' + str(k - w * 7)

        if (k - w * 7) == 1:
            s += _('1 day')
        else:
            s += _('% days')
    else:
        p = (d - d2 + wx.TimeSpan.Hours(1)).GetDays()
        k = (day - d2 + wx.TimeSpan.Hours(1)).GetDays() + 1

        d = d - wx.DateSpan.Day()
    s += " - " + _('%s day of period from %s to %s') % (str(k), d2.Format('%d %b'), d.Format('%d %b')) + ' ' + _('length %s days') % (str(p))
    return s

#-------------------- Note --------------------
def add_note(date, txt):
    d = date.Format('%Y%m%d')
    cycle.note[d] = txt

def get_note(date):
    d = date.Format('%Y%m%d')
    return cycle.note.get(d, "")

def remove_note(date):
    d = date.Format('%Y%m%d')
    if cycle.note.has_key(d):
        del cycle.note[d]

#-------------------- Report --------------------
def report_year(year):
    """Create a HTML document that can be used by wxHtmlEasyPrinting"""
    if cycle.first_week_day == 0:
        calendar.setfirstweekday(calendar.MONDAY)
        days = range(1, 7) + [0]
    else:
        calendar.setfirstweekday(calendar.SUNDAY)
        days = range(7)
    #sp = ' '
    s = '<html><body><H3 align=center>%s</H3><pre>' % year
    dn = ''
    for i in days:
        dn += '%.2s ' % wx.DateTime_GetWeekDayName(i, wx.DateTime.Name_Abbr)
    dn = dn[:-1]
    dn = '%s  %s  %s<br>\n' % (dn, dn, dn)  # week days names
    for m in xrange(0, 12, 3):
        s += '<br>\n%s  %s  %s<br>\n' % (
            wx.DateTime_GetMonthName(m).center(20),
            wx.DateTime_GetMonthName(m + 1).center(20),
            wx.DateTime_GetMonthName(m + 2).center(20))
        s += dn
        data = []
        h = 0
        for k in xrange(m + 1, m + 4):
            cal = calendar.monthcalendar(year, k)
            data.append( calendar.monthcalendar(year, k) )
            if h < len(cal):
                h = len(cal)
        for i in xrange(h):
            d_str = ''
            for n in xrange(3):
                for k in xrange(7):
                    if i < len(data[n]):
                        day_of_month = data[n][i][k]
                        if day_of_month:
                            d = wx.DateTimeFromDMY(day_of_month, m+n, year)
                            if is_set_mark(d, MARK_BEGIN, d.GetYear()):
                                d_str += '<u>%2s</u> ' % day_of_month
                            else:
                                d_str += '%2s ' % day_of_month
                        else:
                            d_str += '   '
                    else:
                        d_str += '   '
                d_str += ' '
            s += d_str[:-2] +'<br>\n'

    s += '</pre></body></html>'
    return s

def report_year_ical(year, fileobj):
    """Export year as an iCal file"""
    import socket
    hostname = socket.gethostname()

    def get_string(mark):
        if mark & MARK_LAST: return _("Conception")
        elif mark & MARK_BEGIN: return _("Beginning of cycle")
        elif mark & MARK_PROG: return _("Probable beginning of cycle")
        elif mark & MARK_TABLET: return _("1-st tablet")
        elif mark & MARK_OVUL: return _("Ovulation")
        elif mark & MARK_BIRTH: return _("Birth")
        else: return ""

    def make_event(description, mark, date):
        date2 = date + wx.TimeSpan.Days(1)
        datestr = "%04d%02d%02d" % (
            date.GetYear(), date.GetMonth() + 1, date.GetDay())
        datestr2 = "%04d%02d%02d" % (
            date2.GetYear(), date2.GetMonth() + 1, date2.GetDay())
        uid = "UID:cycle-%d-%sZ@%s" % (mark, datestr, hostname)
        return ["BEGIN:VEVENT", uid,
                "DTSTART;VALUE=DATE:" + datestr,
                "DTEND;VALUE=DATE:" + datestr2,
                "SUMMARY:" + description,
                "DESCRIPTION:" + description,
                "CLASS:PUBLIC",
                "END:VEVENT"]

    s = ["BEGIN:VCALENDAR",
         "CALSCALE:GREGORIAN",
         "PRODID:-//Cycle//NONSGML Cycle//EN",
         "VERSION:2.0"]

    days = cycle.mark.items()
    days.sort()
    for day, marks in days:
        if get_string(marks):
            d = wx.DateTime()
            d.SetYear(year)
            d.SetToYearDay(day)
            s.extend(make_event(get_string(marks), marks, d))

    s.append("END:VCALENDAR")

    print >>fileobj, "\n".join(s)


