"""Only safe explicit provider results cross the adapter boundary."""
from src.booking.validators import BookingError,utc_stamp
def stamp(dt):return dt.isoformat().replace('+00:00','Z')
def provider(mode):return mode if mode in ('mock','internal') else 'calcom'
def result(mode,**fields):return {'success':True,'mode':mode,'booking_provider':provider(mode),'production':False,'synthetic':mode=='mock','demo':True,'booking_confirmed':False,**fields}
def error(code,mode):
 messages={'SLOT_UNAVAILABLE':'That time is no longer available. Please check other times.','OUTCOME_UNKNOWN':'The result is uncertain; staff must reconcile it before another attempt.','PARTIAL_BOOKING':'Some sessions were accepted; staff must review the remaining sessions.','AUTHENTICATION_FAILURE':'The booking request could not be authorized.','PACKAGE_REQUIRES_REVIEW':'This package needs staff scheduling review.','NOT_SCHEDULABLE':'This self-paced course does not need an appointment.'}
 return {'success':False,'mode':mode,'booking_provider':provider(mode),'production':False,'demo':True,'booking_confirmed':False,'error_code':code,'user_safe_message':messages.get(code,'The scheduling request could not be completed safely.')}
def provider_booking(payload,expected_start=None,duration=None):
 if not isinstance(payload,dict) or payload.get('status')!='success' or not isinstance(payload.get('data'),dict):raise BookingError('PROVIDER_UNAVAILABLE')
 data=payload['data'];uid=data.get('uid');state=data.get('status')
 if not isinstance(uid,str) or not uid or len(uid)>200 or state not in ('accepted','pending','cancelled','rejected'):raise BookingError('OUTCOME_UNKNOWN')
 try:start=utc_stamp(data.get('start'));end=utc_stamp(data.get('end'))
 except BookingError:raise BookingError('OUTCOME_UNKNOWN')
 if end<=start or (duration is not None and (end-start).total_seconds()!=duration*60) or (expected_start is not None and start!=utc_stamp(expected_start)):raise BookingError('OUTCOME_UNKNOWN')
 return {'provider_uid':uid,'start':stamp(start),'end':stamp(end),'status':state,'confirmed':state=='accepted'}
