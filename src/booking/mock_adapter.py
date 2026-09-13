"""Duration-aware persistent demo implementation, reusing the existing mock lineage."""
import uuid
from datetime import timedelta
from zoneinfo import ZoneInfo
from src.booking.adapters import MockBookingAdapter
from src.booking.validators import BookingError,date_bounds,utc_stamp
from src.booking.normalizers import stamp
class PersistentMockBookingAdapter(MockBookingAdapter):
 mode='mock'
 def __init__(self,store):self.store=store
 def _busy(self,start,end,exclude=None):
  with self.store.connect() as db:return bool(db.execute("SELECT 1 FROM mock_provider WHERE status='accepted' AND start<? AND end>? AND uid!=?",(end,start,exclude or '')).fetchone())
 def check_availability(self,package_id,preferred_date,location_id=None,session_duration_minutes=120):
  if location_id is not None:raise BookingError('VALIDATION_ERROR')
  start,_=date_bounds(preferred_date);local=start.astimezone(ZoneInfo('America/Chicago'));result=[]
  for hour in [9,12,15,18]:
   a=stamp(local.replace(hour=hour).astimezone(__import__('datetime').timezone.utc));b=stamp(utc_stamp(a)+timedelta(minutes=session_duration_minutes))
   if not self._busy(a,b):result.append({'start':a,'end':b,'duration_minutes':session_duration_minutes})
  return result
 def create_booking(self,package_id,slot,customer):
  uid='MOCK-'+uuid.uuid4().hex
  with self.store.connect() as db:
   db.execute('BEGIN IMMEDIATE')
   if db.execute("SELECT 1 FROM mock_provider WHERE status='accepted' AND start<? AND end>?",(slot['end'],slot['start'])).fetchone():raise BookingError('SLOT_UNAVAILABLE')
   db.execute('INSERT INTO mock_provider VALUES(?,?,?,?)',(uid,slot['start'],slot['end'],'accepted'))
  return {'provider_uid':uid,'start':slot['start'],'end':slot['end'],'status':'accepted','confirmed':True}
 def find_booking(self,provider_uid):
  with self.store.connect() as db:r=db.execute('SELECT * FROM mock_provider WHERE uid=?',(provider_uid,)).fetchone()
  if not r:raise BookingError('BOOKING_NOT_FOUND')
  return {'provider_uid':r['uid'],'start':r['start'],'end':r['end'],'status':r['status'],'confirmed':r['status']=='accepted'}
 def reschedule_booking(self,provider_uid,slot):
  with self.store.connect() as db:
   db.execute('BEGIN IMMEDIATE');r=db.execute('SELECT * FROM mock_provider WHERE uid=?',(provider_uid,)).fetchone()
   if not r or r['status']!='accepted':raise BookingError('BOOKING_NOT_FOUND')
   if db.execute("SELECT 1 FROM mock_provider WHERE status='accepted' AND uid!=? AND start<? AND end>?",(provider_uid,slot['end'],slot['start'])).fetchone():raise BookingError('SLOT_UNAVAILABLE')
   db.execute('UPDATE mock_provider SET start=?,end=? WHERE uid=?',(slot['start'],slot['end'],provider_uid))
  return self.find_booking(provider_uid)
 def cancel_booking(self,provider_uid):
  with self.store.connect() as db:
   r=db.execute('SELECT * FROM mock_provider WHERE uid=?',(provider_uid,)).fetchone()
   if not r:raise BookingError('BOOKING_NOT_FOUND')
   db.execute("UPDATE mock_provider SET status='cancelled' WHERE uid=?",(provider_uid,))
  return self.find_booking(provider_uid)
