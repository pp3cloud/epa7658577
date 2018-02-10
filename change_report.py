########################################
# change report:
#$ heroku config:set OPER=28
#$ heroku config:set START_DATE=2017,12,1,0,0,0
#$ hb
# ~ $ ./manage.py shell
# In[1]: exec(open('change_report.py').read())
########################################
from nutr.models import POC
from collections import Counter
import sys, os, pytz
from dateutil.parser import parse
import pytz
from datetime import datetime, timezone, timedelta
from itertools import groupby
from operator import itemgetter
# to python, POC.audit_log.values() is a list of dicts
# each row in the table is a dict, where the key is the name of the field
# and the value is the value

def summary(data, key=itemgetter(0), value=itemgetter(1)):
    for k, group in groupby(data, key):
        yield (k, sum(value(row) for row in group))


type(POC.audit_log.values())


list_to_be_sorted=POC.audit_log.values()

#rg1 = sys.argv[1]
#PER=os.getenv('OPER',27)
OPER = os.environ["OPER"]
from pytz import timezone
import pytz
gmt = timezone('GMT')
#rint("gmt: ",gmt)
START_DATE = os.getenv('START_DATE','2017,12,4,0,0,0')
COUNTNO = os.getenv('COUNTNO','1180,1311,1265')
#rint('START_DATE: ',START_DATE)
list = [int(k) for k in START_DATE.split(',')]
try:
  list2 = [int(k) for k in COUNTNO.split(',')]
except:
  list2 = []
dt=datetime(2017,12,4,6,0,0)
dt=datetime(list[0], list[1], list[2], list[3], list[4], list[5])
#rint('dt: ',dt)
start_date = gmt.localize(dt)
#rint('start_date: ',start_date)
newlist = sorted(list_to_be_sorted, key=lambda k: k['action_date']) 
#ewlist = sorted(list_to_be_sorted, key=lambda k: k['action_user_id']) 
#rint('newlist: ',newlist)
summ_list=[]
cnt=Counter()
for n in newlist:
  summ_list.append((n['created_by_id'], 1))
  #rint("n['action_date']>start_date",n['action_date']>start_date)
  #rint("str(n['created_by_id']): ",str(n['created_by_id']))
  #rint("str(OPER): ",str(OPER))
  #rint("str(n['created_by_id'])==str(OPER): ",str(n['created_by_id'])==str(OPER))
  #rint("start_date<n['action_date']: ",start_date<n['action_date'])
  #f start_date<n['action_date'] and str(n['created_by_id'])==str(OPER):
  if start_date<n['action_date']:
    #rint('type(list2[0]): ',type(list2[0]))
    #rint('type(list2[1]): ',type(list2[1]))
    #rint('type(list2[2]): ',type(list2[2]))
    #rint('len(list2): ',len(list2))
    #rint("type(n['tag_id']): ",type(n['tag_id']))
    if len(list2)==0 or n['tag_id'] in list2:
      if str(n['created_by_id'])==str(OPER) or not str(OPER):
        cnt[n['created_by_id']]+=1
        print ("%7d       %s       %10s       %s      	%d" %  (n['id'], n['action_type'], n['created_by_id'], n['action_date'], n['tag_id']))
"""
print("len(summ_list): ",len(summ_list))
for oper, total in summary(summ_list, key=itemgetter(0)):
    print ("%10s: %d" % (oper, total))
"""
print("Operator count:")
for key in cnt:
    try:
      print ("%5d     %5d" % (key,cnt[key]))
    except:
      pass
