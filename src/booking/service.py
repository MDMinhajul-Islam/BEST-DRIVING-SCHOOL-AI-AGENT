"""Stable tool contract, opaque scoped refs and durable multi-session orchestration."""
import hashlib,json,time,uuid
from src.booking.validators import BookingError,package_plan,date_bounds,customer_data,utc_stamp
from src.booking.normalizers import result,error
class BookingService:
 def __init__(self,adapter,store,test_email=None):self.adapter=adapter;self.store=store;self.mode=adapter.mode;self.test_email=test_email
 def _slot(self,ref,scope,package=None):
  with self.store.connect() as db:r=db.execute('SELECT * FROM slots WHERE ref=? AND scope=? AND mode=?',(ref,scope,self.mode)).fetchone()
  if not r or r['expires']<time.time() or (package is not None and r['package']!=package):raise BookingError('SLOT_UNAVAILABLE')
  return dict(r)|{'duration_minutes':r['duration']}
 def _appointment(self,ref,scope):
  r=self.store.get_appointment(ref,scope,self.mode)
  if not r:raise BookingError('BOOKING_NOT_FOUND')
  return r
 def _public(self,ref,data):return {'appointment_id':ref,'start':data['start'],'end':data['end'],'booking_status':'confirmed' if data['confirmed'] else data['status']}
 def check_availability(self,scope,package_id,preferred_date,session_duration_minutes=None,preferred_time_window=None,timezone='America/Chicago'):
  plan=package_plan(package_id)
  if not plan:return result(self.mode,package_id=package_id,scheduling_required=False,available_slots=[])
  if timezone!='America/Chicago':raise BookingError('VALIDATION_ERROR')
  date_bounds(preferred_date)
  if preferred_time_window not in (None,'morning','afternoon','evening'):raise BookingError('VALIDATION_ERROR')
  duration=plan[0] if session_duration_minutes is None else session_duration_minutes
  if type(duration) is not int or duration not in plan:raise BookingError('UNSUPPORTED_DURATION')
  slots=self.adapter.check_availability(package_id,preferred_date,session_duration_minutes=duration);out=[]
  for slot in slots:
   hour=utc_stamp(slot['start']).astimezone(__import__('zoneinfo').ZoneInfo('America/Chicago')).hour
   if preferred_time_window=='morning' and hour>=12:continue
   if preferred_time_window=='afternoon' and not 12<=hour<17:continue
   if preferred_time_window=='evening' and hour<17:continue
   with self.store.connect() as db:
    db.execute('INSERT OR IGNORE INTO slots VALUES(?,?,?,?,?,?,?,?)',(uuid.uuid4().hex,scope,self.mode,package_id,duration,slot['start'],slot['end'],time.time()+300))
    r=db.execute('SELECT ref FROM slots WHERE scope=? AND mode=? AND package=? AND duration=? AND start=?',(scope,self.mode,package_id,duration,slot['start'])).fetchone()
    db.execute('UPDATE slots SET expires=? WHERE ref=?',(time.time()+300,r['ref']))
   out.append({'slot_ref':r['ref'],'slot_id':r['ref'],**slot})
  return result(self.mode,package_id=package_id,timezone='America/Chicago',scheduling_required=True,session_plan=plan,session_count_required=len(plan),available_slots=out,slots=out)
 def _begin(self,scope,operation,payload):
  key=hashlib.sha256(json.dumps([scope,self.mode,operation,payload],sort_keys=True).encode()).hexdigest();old=self.store.claim(key,scope,self.mode,operation)
  if old:
   if old['result']:
    saved=json.loads(old['result'])
    # Never replay an old active confirmation after local cancellation/reschedule.
    for s in saved.get('sessions',[]):
     if s.get('appointment_id'):
      current=self._appointment(s['appointment_id'],scope);s.update(self._public(s['appointment_id'],current['data']))
    if saved.get('appointment_id'):
     current=self._appointment(saved['appointment_id'],scope);saved.update(self._public(saved['appointment_id'],current['data']));saved['booking_confirmed']=current['data']['confirmed']
    if saved.get('sessions'):
     saved['booking_confirmed']=all(s.get('booking_status')=='confirmed' for s in saved['sessions'])
     if not saved['booking_confirmed'] and saved.get('package_booking_status')=='confirmed':saved['package_booking_status']='cancelled' if all(s.get('booking_status')=='cancelled' for s in saved['sessions']) else 'partial'
    return key,saved
   return key,error('OUTCOME_UNKNOWN',self.mode)
  return key,None
 def create_booking(self,scope,package_id,slot_ids,customer):
  plan=package_plan(package_id)
  if not plan:raise BookingError('NOT_SCHEDULABLE')
  customer=customer_data(customer)
  if self.mode!='mock' and (not self.test_email or customer['email']!=self.test_email):raise BookingError('CUSTOMER_DATA_MISSING')
  if not isinstance(slot_ids,list) or not all(isinstance(s,str) for s in slot_ids) or len(slot_ids)!=len(plan) or len(set(slot_ids))!=len(plan):raise BookingError('VALIDATION_ERROR')
  key,old=self._begin(scope,'create',[package_id,slot_ids,customer])
  if old:return old
  target='package:'+scope+':'+self.mode+':'+package_id
  if not self.store.lock(target,key):
   out=error('OUTCOME_UNKNOWN',self.mode);self.store.finish(key,out);return out
  sessions=[]
  try:
   slots=[self._slot(ref,scope,package_id) for ref in slot_ids]
   if [s['duration_minutes'] for s in slots]!=plan:raise BookingError('UNSUPPORTED_DURATION')
   intervals=sorted((utc_stamp(s['start']),utc_stamp(s['end'])) for s in slots)
   if any(intervals[i][1]>intervals[i+1][0] for i in range(len(intervals)-1)):raise BookingError('VALIDATION_ERROR')
   # Validate every selection before any writes; capacity can still race afterwards.
   for slot in slots:
    day=utc_stamp(slot['start']).astimezone(__import__('zoneinfo').ZoneInfo('America/Chicago')).date().isoformat()
    available=self.adapter.check_availability(package_id,day,session_duration_minutes=slot['duration_minutes'])
    if not any(s['start']==slot['start'] and s['end']==slot['end'] for s in available):raise BookingError('SLOT_UNAVAILABLE')
   for idx,slot in enumerate(slots,1):
    self.store.audit('create_attempt',self.mode,package_id,idx,'pending')
    try:
     data=self.adapter.create_booking(package_id,slot,customer);ref=('MOCK-' if self.mode=='mock' else 'CAL-DEMO-')+uuid.uuid4().hex
     self.store.save_appointment(ref,scope,self.mode,package_id,idx,data);sessions.append({'index':idx,**self._public(ref,data)});self.store.audit('create_result',self.mode,package_id,idx,data['status'])
     if not data['confirmed']:break
    except BookingError as e:
     sessions.append({'index':idx,'status':'outcome_unknown' if e.code=='OUTCOME_UNKNOWN' else 'failed','error_code':e.code});self.store.audit('create_result',self.mode,package_id,idx,e.code);break
   complete=len(sessions)==len(plan) and all(s.get('booking_status')=='confirmed' for s in sessions)
   if complete:out=result(self.mode,package_id=package_id,booking_confirmed=True,package_booking_status='confirmed',sessions=sessions)
   else:out=error('PARTIAL_BOOKING' if any(s.get('appointment_id') for s in sessions) else sessions[-1].get('error_code','PROVIDER_UNAVAILABLE'),self.mode)|{'package_id':package_id,'package_booking_status':'partial' if any(s.get('appointment_id') for s in sessions) else ('outcome_unknown' if any(s.get('status')=='outcome_unknown' for s in sessions) else 'failed'),'sessions':sessions,'human_review_required':True}
   if len(plan)==1 and sessions and sessions[0].get('appointment_id'):out.update({k:v for k,v in sessions[0].items() if k!='index'})
  except BookingError as e:out=error(e.code,self.mode)
  self.store.finish(key,out)
  if not out.get('human_review_required') and out.get('error_code')!='OUTCOME_UNKNOWN':self.store.unlock(target,key)
  return out
 def find_booking(self,scope,appointment_id):
  r=self._appointment(appointment_id,scope);owner=uuid.uuid4().hex
  if not self.store.lock(appointment_id,owner):raise BookingError('OUTCOME_UNKNOWN')
  try:
   r=self._appointment(appointment_id,scope);data=self.adapter.find_booking(r['uid']);self.store.save_appointment(appointment_id,scope,self.mode,r['package'],r['idx'],data)
   return result(self.mode,booking_confirmed=data['confirmed'],**self._public(appointment_id,data))
  finally:self.store.unlock(appointment_id,owner)
 def _change(self,scope,appointment_id,operation,slot_ref=None):
  r=self._appointment(appointment_id,scope);key,old=self._begin(scope,operation,[appointment_id,slot_ref])
  if old:return old
  if not self.store.lock(appointment_id,key):
   out=error('OUTCOME_UNKNOWN',self.mode);self.store.finish(key,out);return out
  try:
   r=self._appointment(appointment_id,scope)
   if operation=='cancel':data=self.adapter.cancel_booking(r['uid'])
   else:
    slot=self._slot(slot_ref,scope,r['package'])
    if (utc_stamp(r['data']['end'])-utc_stamp(r['data']['start'])).total_seconds()!=slot['duration_minutes']*60:raise BookingError('UNSUPPORTED_DURATION')
    day=utc_stamp(slot['start']).astimezone(__import__('zoneinfo').ZoneInfo('America/Chicago')).date().isoformat()
    available=self.adapter.check_availability(r['package'],day,session_duration_minutes=slot['duration_minutes'])
    if not any(s['start']==slot['start'] and s['end']==slot['end'] for s in available):raise BookingError('SLOT_UNAVAILABLE')
    data=self.adapter.reschedule_booking(r['uid'],slot)
   self.store.save_appointment(appointment_id,scope,self.mode,r['package'],r['idx'],data);self.store.audit(operation,self.mode,r['package'],r['idx'],data['status'])
   out=result(self.mode,booking_confirmed=data['confirmed'],**self._public(appointment_id,data))
   if operation=='cancel':out['refund_issued']=False
  except BookingError as e:self.store.audit(operation,self.mode,r['package'],r['idx'],e.code);out=error(e.code,self.mode)
  self.store.finish(key,out)
  if out.get('error_code')!='OUTCOME_UNKNOWN':self.store.unlock(appointment_id,key)
  return out
 def reschedule_booking(self,scope,appointment_id,slot_ref):return self._change(scope,appointment_id,'reschedule',slot_ref)
 def cancel_booking(self,scope,appointment_id):return self._change(scope,appointment_id,'cancel')
