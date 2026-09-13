"""Cal.com API v2 scheduling provider for internship demo, never school production."""
from urllib.parse import quote
from datetime import timedelta
import requests
from src.booking.validators import BookingError,utc_stamp,date_bounds,EVENTS
from src.booking.normalizers import stamp,provider_booking
VERSIONS={'slots':'2024-09-04','bookings':'2026-02-25','event_types':'2024-06-14'}
class CalComBookingAdapter:
 def __init__(self,key,event_types,mode='calcom_test',writes_enabled=False,client=None):
  if mode not in ('calcom_test','calcom_live'):raise ValueError('Invalid Cal.com mode')
  self.key=key;self.event_types=event_types;self.mode=mode;self.writes_enabled=writes_enabled;self.client=client or requests
 def _request(self,method,path,kind='bookings',**kwargs):
  if not self.key:raise BookingError('AUTHENTICATION_FAILURE')
  if method!='GET' and not self.writes_enabled:raise BookingError('WRITES_DISABLED')
  try:
   r=self.client.request(method,'https://api.cal.com/v2/'+path,headers={'Authorization':'Bearer '+self.key,'cal-api-version':VERSIONS[kind],'Content-Type':'application/json'},timeout=(5,15),allow_redirects=False,**kwargs)
   if r.status_code in (401,403):raise BookingError('AUTHENTICATION_FAILURE')
   if r.status_code==409:raise BookingError('SLOT_UNAVAILABLE')
   if r.status_code>=500:raise BookingError('OUTCOME_UNKNOWN' if method!='GET' else 'PROVIDER_UNAVAILABLE')
   if r.status_code not in (200,201):raise BookingError('PROVIDER_REJECTED')
   body=r.json()
   if not isinstance(body,dict) or body.get('status')!='success':raise BookingError('OUTCOME_UNKNOWN' if method!='GET' else 'PROVIDER_UNAVAILABLE')
   return body
  except (requests.Timeout,requests.ConnectionError):raise BookingError('OUTCOME_UNKNOWN' if method!='GET' else 'PROVIDER_UNAVAILABLE')
  except (requests.RequestException,ValueError):raise BookingError('OUTCOME_UNKNOWN' if method!='GET' else 'PROVIDER_UNAVAILABLE')
 def event_id(self,duration):
  cfg=self.event_types.get(EVENTS.get(duration),{})
  if cfg.get('duration_minutes')!=duration or type(cfg.get('event_type_id')) is not int or cfg['event_type_id']<=0:raise BookingError('EVENT_TYPE_NOT_CONFIGURED')
  return cfg['event_type_id']
 def _verify_event(self,duration):
  eid=self.event_id(duration);body=self._request('GET','event-types/'+str(eid),'event_types');event=body.get('data')
  if not isinstance(event,dict) or event.get('id')!=eid or event.get('lengthInMinutes')!=duration or event.get('price') not in (None,0) or event.get('recurrence') or event.get('isInstantEvent') or event.get('seatsPerTimeSlot'):raise BookingError('EVENT_TYPE_NOT_CONFIGURED')
  if duration==30 and (event.get('slotInterval')!=30 or event.get('beforeEventBuffer',0)!=0 or event.get('afterEventBuffer',0)!=0):raise BookingError('EVENT_TYPE_NOT_CONFIGURED')
  for field in event.get('bookingFields',[]):
   if field.get('required') and field.get('slug') not in ('name','email'):raise BookingError('EVENT_TYPE_NOT_CONFIGURED')
  return eid
 def check_availability(self,package_id,preferred_date,location_id=None,session_duration_minutes=120):
  if location_id is not None:raise BookingError('VALIDATION_ERROR')
  eid=self._verify_event(session_duration_minutes);start,end=date_bounds(preferred_date)
  body=self._request('GET','slots','slots',params={'eventTypeId':eid,'start':stamp(start),'end':stamp(end-timedelta(seconds=1)),'timeZone':'America/Chicago','format':'range'})
  data=body.get('data')
  if not isinstance(data,dict):raise BookingError('PROVIDER_UNAVAILABLE')
  slots={}
  for ranges in data.values():
   if not isinstance(ranges,list):raise BookingError('PROVIDER_UNAVAILABLE')
   for slot in ranges:
    if not isinstance(slot,dict):raise BookingError('PROVIDER_UNAVAILABLE')
    try:a=utc_stamp(slot.get('start'));b=utc_stamp(slot.get('end'))
    except BookingError:raise BookingError('PROVIDER_UNAVAILABLE')
    if (b-a).total_seconds()!=session_duration_minutes*60 or not start<=a<end:raise BookingError('PROVIDER_UNAVAILABLE')
    slots[stamp(a)]={'start':stamp(a),'end':stamp(b),'duration_minutes':session_duration_minutes}
  return [slots[k] for k in sorted(slots)]
 def create_booking(self,package_id,slot,customer):
  eid=self._verify_event(slot['duration_minutes'])
  try:body=self._request('POST','bookings',json={'eventTypeId':eid,'start':slot['start'],'attendee':{**customer,'timeZone':'America/Chicago'},'metadata':{'project':'BDS AI TEST'}})
  except BookingError as e:
   if e.code=='PROVIDER_REJECTED':
    from zoneinfo import ZoneInfo
    day=utc_stamp(slot['start']).astimezone(ZoneInfo('America/Chicago')).date().isoformat()
    try:
     remaining=self.check_availability(package_id,day,session_duration_minutes=slot['duration_minutes'])
     if not any(s['start']==slot['start'] for s in remaining):raise BookingError('SLOT_UNAVAILABLE')
    except BookingError as check:
     if check.code=='SLOT_UNAVAILABLE':raise
   raise e
  return provider_booking(body,slot['start'],slot['duration_minutes'])
 def find_booking(self,provider_uid):
  data=provider_booking(self._request('GET','bookings/'+quote(provider_uid,safe='')))
  if data['provider_uid']!=provider_uid:raise BookingError('PROVIDER_UNAVAILABLE')
  return data
 def reschedule_booking(self,provider_uid,slot):return provider_booking(self._request('POST','bookings/'+quote(provider_uid,safe='')+'/reschedule',json={'start':slot['start'],'reschedulingReason':'BDS AI TEST'}),slot['start'],slot['duration_minutes'])
 def cancel_booking(self,provider_uid):
  body=self._request('POST','bookings/'+quote(provider_uid,safe='')+'/cancel',json={'cancellationReason':'BDS AI TEST'})
  normalized=provider_booking(body)
  if normalized['status']!='cancelled':raise BookingError('OUTCOME_UNKNOWN')
  return normalized
