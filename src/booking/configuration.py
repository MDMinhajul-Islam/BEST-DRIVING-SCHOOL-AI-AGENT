"""Safe startup configuration: credentials alone never enable Cal.com."""
import os,json
from config.settings import ROOT
from src.booking.store import Store
from src.booking.service import BookingService
from src.booking.calcom_adapter import CalComBookingAdapter
from src.booking.mock_adapter import PersistentMockBookingAdapter
def configured_service(env=None):
 env=os.environ if env is None else env
 mode=env.get('BOOKING_MODE','mock')
 if mode not in ('mock','calcom_test','calcom_live'):raise ValueError('Invalid booking mode')
 if env.get('CALCOM_API_BASE_URL','https://api.cal.com')!='https://api.cal.com':raise ValueError('Only verified Cal.com API origin supported')
 if env.get('CALCOM_TIMEZONE','America/Chicago')!='America/Chicago':raise ValueError('Business timezone must be America/Chicago')
 if mode=='calcom_live' and env.get('CALCOM_LIVE_ENABLED')!='true':raise ValueError('Live Cal.com mode requires explicit enablement')
 path=env.get('BOOKING_DB_PATH',str(ROOT/'runtime/booking.sqlite3'));store=Store(path)
 if mode=='mock':adapter=PersistentMockBookingAdapter(store)
 else:
  if env.get('BOOKING_PROVIDER','calcom')!='calcom' or not env.get('CALCOM_API_KEY'):raise ValueError('Cal.com configuration incomplete')
  mapping=json.loads((ROOT/'config/calcom.example.json').read_text(encoding='utf-8'))['event_types']
  for key,suffix in [('driving_standard','DRIVING_120'),('driving_remainder','DRIVING_60'),('road_test','ROAD_TEST_30')]:
   value=env.get('CALCOM_EVENT_TYPE_'+suffix)
   if value:mapping[key]['event_type_id']=int(value)
  adapter=CalComBookingAdapter(env['CALCOM_API_KEY'],mapping,mode,env.get('CALCOM_WRITE_ENABLED')=='true')
 return BookingService(adapter,store,env.get('CALCOM_TEST_EMAIL'))
