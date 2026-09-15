"""Admin-configured internal calendar provider. Empty configuration means no slots."""
import json,uuid
from datetime import datetime,timedelta,timezone,time as clock
from zoneinfo import ZoneInfo
from src.booking.validators import BookingError,date_bounds,utc_stamp,package_plan
from src.booking.normalizers import stamp

ZONE=ZoneInfo('America/Chicago')
def now():return datetime.now(timezone.utc).isoformat()

class InternalBookingAdapter:
 mode='internal'
 def __init__(self,store):self.store=store;self._sync_catalog()
 def _sync_catalog(self):
  from config.settings import ROOT
  catalog=json.loads((ROOT/'data/structured/package_catalog.json').read_text(encoding='utf-8'))
  with self.store.connect() as db:
   for p in catalog:
    try:plan=package_plan(p['package_id']);auto=bool(plan)
    except BookingError:plan=None;auto=False
    db.execute('INSERT INTO internal_services VALUES(?,?,?,?,?) ON CONFLICT(package_id) DO UPDATE SET name=excluded.name,session_plan=excluded.session_plan,auto_schedulable=excluded.auto_schedulable',(p['package_id'],p['package_name'],json.dumps(plan) if plan is not None else None,int(auto),'canonical package catalog'))
 def _rules(self,db,package_id,day):
  return db.execute("SELECT * FROM availability_rules WHERE active=1 AND capacity>0 AND package_id IN (?, '*') AND weekday=? AND effective_start<=? AND (effective_end IS NULL OR effective_end>=?) ORDER BY package_id DESC,start_time",(package_id,day.weekday(),day.isoformat(),day.isoformat())).fetchall()
 def _blocked(self,db,package_id,start,end):
  return bool(db.execute("SELECT 1 FROM blackouts WHERE active=1 AND package_id IN (?, '*') AND start<? AND end>?",(package_id,stamp(end),stamp(start))).fetchone())
 def _count(self,db,start,end,exclude=None):
  return db.execute("SELECT count(*) FROM internal_sessions WHERE status='accepted' AND start<? AND end>? AND uid!=?",(stamp(end),stamp(start),exclude or '')).fetchone()[0]
 def _rule_slots(self,rule,day,duration):
  sh,sm=map(int,rule['start_time'].split(':'));eh,em=map(int,rule['end_time'].split(':'))
  cur=datetime.combine(day,clock(sh,sm),ZONE);limit=datetime.combine(day,clock(eh,em),ZONE);step=timedelta(minutes=duration)
  while cur+step<=limit:yield cur.astimezone(timezone.utc),(cur+step).astimezone(timezone.utc);cur+=step
 def _available_db(self,db,package_id,start,end,exclude=None):
  local=start.astimezone(ZONE);duration=int((end-start).total_seconds()/60)
  if self._blocked(db,package_id,start,end):return False
  for rule in self._rules(db,package_id,local.date()):
   if any(a==start and b==end for a,b in self._rule_slots(rule,local.date(),duration)) and self._count(db,start,end,exclude)<rule['capacity']:return True
  return False
 def check_availability(self,package_id,preferred_date,location_id=None,session_duration_minutes=120):
  if location_id is not None:raise BookingError('VALIDATION_ERROR')
  date_bounds(preferred_date);day=datetime.strptime(preferred_date,'%Y-%m-%d').date();out={}
  with self.store.connect() as db:
   for rule in self._rules(db,package_id,day):
    for start,end in self._rule_slots(rule,day,session_duration_minutes):
     if self._available_db(db,package_id,start,end):out[stamp(start)]={'start':stamp(start),'end':stamp(end),'duration_minutes':session_duration_minutes,'timezone':'America/Chicago'}
  return [out[k] for k in sorted(out)]
 def create_group(self,package_id,slots,customer,scope):
  group='IG-'+uuid.uuid4().hex;created=now();items=[]
  with self.store.connect() as db:
   db.execute('BEGIN IMMEDIATE')
   for slot in slots:
    start,end=utc_stamp(slot['start']),utc_stamp(slot['end'])
    if not self._available_db(db,package_id,start,end):raise BookingError('SLOT_UNAVAILABLE')
   db.execute('INSERT INTO booking_groups VALUES(?,?,?,?,?,?,?,?)',(group,scope,package_id,customer['name'],customer['email'],'confirmed',created,created))
   for idx,slot in enumerate(slots,1):
    uid='IS-'+uuid.uuid4().hex;ref='INTERNAL-'+uuid.uuid4().hex
    data={'provider_uid':uid,'start':slot['start'],'end':slot['end'],'status':'accepted','confirmed':True,'booking_group_id':group}
    db.execute('INSERT INTO internal_sessions(uid,group_id,appointment_ref,package_id,start,end,status,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?)',(uid,group,ref,package_id,slot['start'],slot['end'],'accepted',created,created))
    db.execute('INSERT INTO appointments VALUES(?,?,?,?,?,?,?)',(ref,scope,self.mode,package_id,idx,uid,json.dumps(data)));items.append(data|{'appointment_ref':ref})
   db.execute('INSERT INTO internal_history VALUES(?,?,?,?,?,?)',(uuid.uuid4().hex,created,'booking_created','booking_group',group,json.dumps({'package_id':package_id,'session_count':len(items)})))
  return group,items
 def create_booking(self,package_id,slot,customer):return self.create_group(package_id,[slot],customer,'adapter')[1][0]
 def find_booking(self,provider_uid):
  with self.store.connect() as db:r=db.execute('SELECT * FROM internal_sessions WHERE uid=?',(provider_uid,)).fetchone()
  if not r:raise BookingError('BOOKING_NOT_FOUND')
  return {'provider_uid':r['uid'],'start':r['start'],'end':r['end'],'status':r['status'],'confirmed':r['status']=='accepted','booking_group_id':r['group_id']}
 def reschedule_booking(self,provider_uid,slot):
  at=now()
  with self.store.connect() as db:
   db.execute('BEGIN IMMEDIATE');r=db.execute('SELECT * FROM internal_sessions WHERE uid=?',(provider_uid,)).fetchone()
   if not r or r['status']!='accepted':raise BookingError('BOOKING_NOT_FOUND')
   start,end=utc_stamp(slot['start']),utc_stamp(slot['end'])
   if (end-start).total_seconds()!=(utc_stamp(r['end'])-utc_stamp(r['start'])).total_seconds():raise BookingError('UNSUPPORTED_DURATION')
   if not self._available_db(db,r['package_id'],start,end,provider_uid):raise BookingError('SLOT_UNAVAILABLE')
   old={'start':r['start'],'end':r['end']};db.execute('UPDATE internal_sessions SET start=?,end=?,updated_at=? WHERE uid=?',(slot['start'],slot['end'],at,provider_uid))
   db.execute('INSERT INTO internal_history VALUES(?,?,?,?,?,?)',(uuid.uuid4().hex,at,'session_rescheduled','session',provider_uid,json.dumps(old|{'new_start':slot['start'],'new_end':slot['end']})))
  return self.find_booking(provider_uid)
 def cancel_booking(self,provider_uid):
  at=now()
  with self.store.connect() as db:
   db.execute('BEGIN IMMEDIATE');r=db.execute('SELECT * FROM internal_sessions WHERE uid=?',(provider_uid,)).fetchone()
   if not r:raise BookingError('BOOKING_NOT_FOUND')
   if r['status']=='accepted':
    db.execute("UPDATE internal_sessions SET status='cancelled',cancelled_at=?,updated_at=? WHERE uid=?",(at,at,provider_uid));db.execute('INSERT INTO internal_history VALUES(?,?,?,?,?,?)',(uuid.uuid4().hex,at,'session_cancelled','session',provider_uid,'{}'))
    left=db.execute("SELECT count(*) FROM internal_sessions WHERE group_id=? AND status='accepted'",(r['group_id'],)).fetchone()[0]
    if not left:db.execute("UPDATE booking_groups SET status='cancelled',updated_at=? WHERE id=?",(at,r['group_id']))
  return self.find_booking(provider_uid)
