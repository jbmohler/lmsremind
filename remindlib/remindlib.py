##############################################################################
#       Copyright (C) 2010, Joel B. Mohler <joel@kiwistrawberry.us>
#
#  Distributed under the terms of the GNU General Public License (GPLv2 or later)
#                  http://www.gnu.org/licenses/
##############################################################################
import datetime
import re
import subprocess
import string
import sys
import email.Utils

todays_date = None
hit_list = []

class Reminder:
    def __init__(self,brief,memo):
        self.brief = brief
        if memo is not None:
            self.memo = memo.strip()
        else:
            self.memo = ""

    def __repr__(self):
        return "%s\n\n%s" % (self.brief, self.memo)

    def email(self,address):
        send = subprocess.Popen( ["/usr/sbin/sendmail", "-t"], stdin=subprocess.PIPE )
        send.stdin.write( "To: %s\n" % (address,) )
        #send.stdin.write( "From: lmsremind\n" )
        send.stdin.write( "Date: %s\n" % (email.Utils.formatdate(localtime=True)) )
        send.stdin.write( "X-Mailer: lmsremind\n" )
        send.stdin.write( "Subject: %s\n" % (self.brief,) )
        send.stdin.write( "\n%s\n" % (self.memo,) )
        send.stdin.close()

def ActOnHits(email):
    global hit_list
    for h in hit_list:
        if email:
            h.email(email)
        else:
            print h

def ReminderHit(brief,memo):
    global hit_list
    hit_list.append(Reminder(brief,memo))

def set_todays_date(date):
    assert(isinstance(date,datetime.date))
    global todays_date
    todays_date = date

def get_todays_date():
    global todays_date
    return todays_date

def str_to_month(s):
    s = s.lower()
    months = ["january","february","march","april","may","june","july","august","september","october","november","december"]
    for index,m in [(i,months[i]) for i in range(12)]:
        if m.startswith(s):
            return index + 1
    raise ValueError

def str_to_date_int(s):
    m = re.match("([a-zA-Z]*) ([0-9]+)(,|) ([0-9]+)",s)
    if m:
        return int(m.group(4)),str_to_month(m.group(1)),int(m.group(2))
    m = re.match("([a-zA-Z]*) ([0-9]+)",s)
    if m:
        return None,str_to_month(m.group(1)),int(m.group(2))
    m = re.match("([0-9]{4})-([0-9]{1,2})-([0-9]{1,2})",s)
    if m:
        return int(m.group(1)),int(m.group(2)),int(m.group(3))
    m = re.match("(-|\+)([0-9]+)",s)
    if m:
        if m.group(1)=='+':
            d = datetime.date.today() + datetime.timedelta(int(m.group(2)))
        elif m.group(1)=='-':
            d = datetime.date.today() - datetime.timedelta(int(m.group(2)))
        return d.year,d.month,d.day
    raise NotImplementedError
    return None,None,None

def str_to_date(s):
    year,month,day = str_to_date_int(s)
    if year is None:
        year = datetime.date.today().year
    if month is None:
        month = datetime.date.today().month
    if day is None:
        day = datetime.date.today().day
    return datetime.date(year,month,day)

class DateCondition:
    def __init__(self):
        raise NotImplementedError

    def matches(self,date):
        raise NotImplementedError

class SpecificDate(DateCondition):
    def __init__(self,year=None,month=None,day=None,dateStr=None):
        if dateStr is not None:
            self.date = str_to_date(s)
        else:
            self.date = datetime.date(year,month,day)

    def matches(self,date):
        assert(isinstance(date,datetime.date))
        return self.date == date

class DayOfWeek(DateCondition):
    def __init__(self,dow):
        if isinstance(dow,str):
            dow = dow.lower()
            dows = ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]
            for index,d in [(i,dows[i]) for i in range(7)]:
                if d.startswith(dow):
                    dow = index
        assert(type(dow) is int and 0<=dow<=6)
        self.dow = dow

    def matches(self,date):
        assert(isinstance(date,datetime.date))
        return self.dow == date.weekday()

class Recurring(DateCondition):
    def __init__(self,init_date,length):
        self.date = str_to_date(init_date)
        self.length = length

    def matches(self,date):
        assert(isinstance(date,datetime.date))
        return ((date - self.date).days % self.length) == 0

class PartialDate(DateCondition):
    def __init__(self,year,month,day):
        self.year = year
        self.month = month
        self.day = day

    def matches(self,date):
        assert(isinstance(date,datetime.date))
        if self.year is not None and self.year != date.year:
            return False
        if self.month is not None and self.month != date.month:
            return False
        if self.day is not None and self.day != date.day:
            return False
        return True

def parse_DateCondition(dc):
    if isinstance(dc,DateCondition):
        return dc
    elif isinstance(dc,str):
        return PartialDate(*str_to_date_int(dc))
    elif isinstance(dc,int):
        return PartialDate(None,None,dc)
    raise NotImplementedError

class Prior(DateCondition):
    def __init__(self,dc,days_prior):
        self.dc = parse_DateCondition(dc)
        assert(0<=days_prior<=366) # why more than a year?
        self.days_prior = days_prior

    def matches(self,date):
        assert(isinstance(date,datetime.date))
        for i in xrange(self.days_prior+1):
            if self.dc.matches(date + datetime.timedelta(i)):
                return True
        return False

class Post(DateCondition):
    def __init__(self,dc,days_post):
        self.dc = parse_DateCondition(dc)
        assert(0<=days_post<=366) # why more than a year?
        self.days_post = days_post

    def matches(self,date):
        assert(isinstance(date,datetime.date))
        for i in xrange(self.days_post+1):
            if self.dc.matches(date - datetime.timedelta(i)):
                return True
        return False

def Match(dc):
    if isinstance(dc,(list,tuple)):
        dc_list = dc
    else:
        dc_list = [dc]
    for dc in dc_list:
        dc = parse_DateCondition(dc)
        if dc.matches(todays_date):
            return dc # Once, we've been done, we quit
    return None

def Remind(dc,brief=None,memo=None):
    if Match(dc):
        ReminderHit(brief,memo)
