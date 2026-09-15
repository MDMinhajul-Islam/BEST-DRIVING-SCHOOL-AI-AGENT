import unittest, tempfile, json
from pathlib import Path
from unittest.mock import Mock
from concurrent.futures import ThreadPoolExecutor
import requests
from fastapi.testclient import TestClient
from src.booking.store import Store
from src.booking.service import BookingService
from src.booking.mock_adapter import PersistentMockBookingAdapter
from src.booking.calcom_adapter import CalComBookingAdapter, VERSIONS
from src.booking.validators import BookingError, package_plan, date_bounds, utc_stamp
from src.booking.normalizers import provider_booking
from src.booking.configuration import configured_service
from src.routes.booking import create_app

SCOPE='DEMO-SCOPE-000001'
CUSTOMER={'name':'BDS AI TEST Fixture','email':'fixture@example.com'}
ROAD='road_test_road_test_only'
ROOT=Path(__file__).resolve().parents[1]

class CalcomIntegrationTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
  self.path=Path(self.temp.name)/'booking.sqlite3';self.store=Store(self.path)
  self.adapter=PersistentMockBookingAdapter(self.store);self.service=BookingService(self.adapter,self.store)
  self.client=TestClient(create_app(self.service,'s'*32));self.headers={'X-Retell-Tool-Secret':'s'*32,'X-Booking-Scope':SCOPE}
  self.mapping={k:{'duration_minutes':d,'event_type_id':d} for d,k in [(120,'driving_standard'),(60,'driving_remainder'),(30,'road_test')]}
 def slots(self,pid=ROAD,day='2035-10-01',duration=None):
  return self.service.check_availability(SCOPE,pid,day,session_duration_minutes=duration)['available_slots']
 def booking(self):return self.service.create_booking(SCOPE,ROAD,[self.slots()[0]['slot_ref']],CUSTOMER)
 def cal(self,duration=30,state='accepted',code=201):
  c=Mock();a=CalComBookingAdapter('PRIVATE-KEY',self.mapping,writes_enabled=True,client=c)
  def request(method,url,**kwargs):
   r=Mock();r.status_code=200 if method=='GET' else code
   if '/event-types/' in url:r.json.return_value={'status':'success','data':{'id':duration,'lengthInMinutes':duration,'price':0,'slotInterval':30,'bookingFields':[]}}
   elif url.endswith('/slots'):r.json.return_value={'status':'success','data':{'2035-10-01':[{'start':'2035-10-01T14:00:00Z','end':f'2035-10-01T{14+duration//60:02d}:{duration%60:02d}:00Z'}]}}
   else:r.json.return_value={'status':'success','data':{'uid':'provider-private-uid','status':state,'start':'2035-10-01T14:00:00Z','end':f'2035-10-01T{14+duration//60:02d}:{duration%60:02d}:00Z'}}
   return r
  c.request.side_effect=request;return a,c
 def test_package_plans(self):
  rules=json.loads((ROOT/'data/structured/internal_business_scheduling_rules.json').read_text())
  for pid,p in rules['package_plans'].items():self.assertEqual(package_plan(pid),p['session_plan_minutes'])
  self.assertEqual(package_plan(ROAD),[30])
 def test_online_and_unknown_packages(self):
  catalog=json.loads((ROOT/'data/structured/package_catalog.json').read_text())
  online=next(p['package_id'] for p in catalog if p['program_id']=='adult_online')
  self.assertFalse(self.service.check_availability(SCOPE,online,'2035-10-01')['scheduling_required'])
  with self.assertRaises(BookingError):package_plan('invented')
 def test_unresolved_packages_blocked(self):
  catalog=json.loads((ROOT/'data/structured/package_catalog.json').read_text())
  rules=json.loads((ROOT/'data/structured/internal_business_scheduling_rules.json').read_text())
  for p in catalog:
   if p['program_id']!='adult_online' and p['package_id'] not in rules['package_plans'] and p['package_id']!=ROAD:
    with self.assertRaises(BookingError) as e:package_plan(p['package_id'])
    self.assertEqual(e.exception.code,'PACKAGE_REQUIRES_REVIEW')
 def test_timezone_and_dst(self):
  start,end=date_bounds('2035-03-11');self.assertEqual((end-start).total_seconds(),23*3600)
  with self.assertRaises(BookingError):utc_stamp('2035-10-01T09:00:00')
 def test_secret_required(self):
  self.assertEqual(self.client.post('/api/booking/find',json={'appointment_id':'x'}).status_code,401)
  with self.assertRaises(ValueError):create_app(self.service,'short')
 def test_scope_required(self):
  self.assertEqual(self.client.post('/api/booking/find',headers={'X-Retell-Tool-Secret':'s'*32},json={'appointment_id':'x'}).status_code,401)
 def test_health_minimal(self):self.assertEqual(self.client.get('/api/health').json(),{'status':'ok','service':'best-driving-school-booking-api','provider':'mock','timezone':'America/Chicago'})
 def test_request_validation(self):
  r=self.client.post('/api/booking/find',headers=self.headers,json={'appointment_id':'x','provider_uid':'private'})
  self.assertEqual(r.json()['error_code'],'VALIDATION_ERROR')
  self.assertEqual(self.client.post('/api/booking/find',headers=self.headers,content='x'*65537).status_code,413)
 def test_retell_envelope(self):
  r=self.client.post('/api/booking/check-availability',headers=self.headers,json={'name':'check_availability','call':{'transcript':'discard'},'args':{'package_id':ROAD,'preferred_date':'2035-10-01'}})
  self.assertTrue(r.json()['success']);self.assertNotIn('discard',r.text)
 def test_five_operations_restart_and_replay(self):
  b=self.booking();ref=b['appointment_id'];self.assertTrue(b['booking_confirmed']);self.assertTrue(ref.startswith('MOCK-'))
  restarted=BookingService(PersistentMockBookingAdapter(Store(self.path)),Store(self.path))
  self.assertTrue(restarted.find_booking(SCOPE,ref)['booking_confirmed'])
  next_slot=restarted.check_availability(SCOPE,ROAD,'2035-10-02')['available_slots'][0]['slot_ref']
  moved=restarted.reschedule_booking(SCOPE,ref,next_slot);self.assertEqual(moved['start'],'2035-10-02T14:00:00Z')
  self.assertFalse(restarted.cancel_booking(SCOPE,ref)['booking_confirmed'])
  replay=restarted.reschedule_booking(SCOPE,ref,next_slot);self.assertEqual(replay['booking_status'],'cancelled')
 def test_create_retry_no_duplicate(self):
  slot=self.slots()[0]['slot_ref'];a=self.service.create_booking(SCOPE,ROAD,[slot],CUSTOMER);b=self.service.create_booking(SCOPE,ROAD,[slot],CUSTOMER)
  self.assertEqual(a,b)
  with self.store.connect() as db:self.assertEqual(db.execute('SELECT count(*) FROM mock_provider').fetchone()[0],1)
 def test_scope_isolation(self):
  b=self.booking()
  with self.assertRaises(BookingError):self.service.find_booking('OTHER-SCOPE-00001',b['appointment_id'])
  with self.assertRaises(BookingError):self.service.find_booking(SCOPE,'provider-private-uid')
 def test_scoped_slots(self):
  out=self.service.create_booking('OTHER-SCOPE-00001',ROAD,[self.slots()[0]['slot_ref']],CUSTOMER)
  self.assertEqual(out['error_code'],'SLOT_UNAVAILABLE')
 def test_multisession_prevalidation(self):
  pid=next(k for k in json.loads((ROOT/'data/structured/internal_business_scheduling_rules.json').read_text())['package_plans'] if len(package_plan(k))==3)
  refs=[s['slot_ref'] for s in self.slots(pid)[:3]];refs[-1]='unknown'
  self.assertFalse(self.service.create_booking(SCOPE,pid,refs,CUSTOMER)['success'])
  with self.store.connect() as db:self.assertEqual(db.execute('SELECT count(*) FROM mock_provider').fetchone()[0],0)
 def test_partial_no_rollback_and_locked(self):
  pid=next(k for k in json.loads((ROOT/'data/structured/internal_business_scheduling_rules.json').read_text())['package_plans'] if len(package_plan(k))==3)
  refs=[s['slot_ref'] for s in self.slots(pid)[:3]];original=self.adapter.create_booking;calls=[]
  def create(*args):
   calls.append(1)
   if len(calls)==2:raise BookingError('SLOT_UNAVAILABLE')
   return original(*args)
  self.adapter.create_booking=create;out=self.service.create_booking(SCOPE,pid,refs,CUSTOMER)
  self.assertEqual(out['error_code'],'PARTIAL_BOOKING');self.assertTrue(out['human_review_required']);self.assertFalse(out['booking_confirmed'])
  with self.store.connect() as db:self.assertEqual(db.execute('SELECT count(*) FROM mock_provider WHERE status="accepted"').fetchone()[0],1);self.assertEqual(db.execute('SELECT count(*) FROM locks').fetchone()[0],1)
 def test_uncertain_write_no_retry(self):
  refs=[self.slots()[0]['slot_ref']];self.adapter.create_booking=Mock(side_effect=BookingError('OUTCOME_UNKNOWN'))
  self.service.create_booking(SCOPE,ROAD,refs,CUSTOMER);self.service.create_booking(SCOPE,ROAD,refs,CUSTOMER)
  self.assertEqual(self.adapter.create_booking.call_count,1)
 def test_concurrent_capacity(self):
  refs=[self.slots()[0]['slot_ref']]
  with ThreadPoolExecutor(2) as pool:out=list(pool.map(lambda n:self.service.create_booking(SCOPE,ROAD,refs,{'name':'BDS AI TEST '+str(n),'email':'fixture@example.com'}),range(2)))
  self.assertEqual(sum(x['booking_confirmed'] for x in out),1)
 def test_audit_no_customer_or_key(self):
  self.booking()
  with self.store.connect() as db:rows=[dict(r) for r in db.execute('SELECT * FROM audit')]
  self.assertTrue(rows);self.assertNotIn(CUSTOMER['email'],json.dumps(rows));self.assertNotIn(CUSTOMER['name'],json.dumps(rows))
 def test_endpoint_versions_and_slot_ranges(self):
  a,c=self.cal();slots=a.check_availability(ROAD,'2035-10-01',session_duration_minutes=30);self.assertEqual(slots[0]['duration_minutes'],30)
  calls=c.request.call_args_list;self.assertEqual(calls[0].kwargs['headers']['cal-api-version'],VERSIONS['event_types']);self.assertEqual(calls[1].kwargs['headers']['cal-api-version'],VERSIONS['slots']);self.assertFalse(calls[1].kwargs['allow_redirects'])
 def test_create_explicit_success_and_minimal_attendee(self):
  a,c=self.cal();slot=a.check_availability(ROAD,'2035-10-01',session_duration_minutes=30)[0];self.assertTrue(a.create_booking(ROAD,slot,CUSTOMER)['confirmed'])
  kw=c.request.call_args.kwargs;self.assertEqual(kw['headers']['cal-api-version'],VERSIONS['bookings']);self.assertEqual(set(kw['json']['attendee']),{'name','email','timeZone'})
 def test_pending_never_confirmed(self):
  a,c=self.cal(state='pending');slot=a.check_availability(ROAD,'2035-10-01',session_duration_minutes=30)[0];self.assertFalse(a.create_booking(ROAD,slot,CUSTOMER)['confirmed'])
 def test_conflict_safe_error(self):
  a,c=self.cal(code=409);slot=a.check_availability(ROAD,'2035-10-01',session_duration_minutes=30)[0]
  with self.assertRaises(BookingError) as e:a.create_booking(ROAD,slot,CUSTOMER)
  self.assertEqual(e.exception.code,'SLOT_UNAVAILABLE')
 def test_timeout_write_unknown(self):
  a,c=self.cal();c.request.side_effect=requests.Timeout('PRIVATE-KEY')
  with self.assertRaises(BookingError) as e:a._request('POST','bookings')
  self.assertEqual(e.exception.code,'OUTCOME_UNKNOWN')
 def test_malformed_provider_write_unknown(self):
  with self.assertRaises(BookingError) as e:provider_booking({'status':'success','data':{'uid':'x','status':'accepted','start':'bad','end':'bad'}})
  self.assertEqual(e.exception.code,'OUTCOME_UNKNOWN')
 def test_unconfigured_event_no_network(self):
  a,c=self.cal();a.event_types['road_test']['event_type_id']=None
  with self.assertRaises(BookingError):a.check_availability(ROAD,'2035-10-01',session_duration_minutes=30)
  c.request.assert_not_called()
 def test_write_gate(self):
  a,c=self.cal();a.writes_enabled=False
  with self.assertRaises(BookingError) as e:a._request('POST','bookings')
  self.assertEqual(e.exception.code,'WRITES_DISABLED');c.request.assert_not_called()
 def test_key_alone_stays_mock(self):
  s=configured_service({'CALCOM_API_KEY':'PRIVATE-KEY','BOOKING_DB_PATH':str(self.path)})
  self.assertEqual(s.mode,'mock')
 def test_provider_must_match_mode(self):
  with self.assertRaises(ValueError):configured_service({'BOOKING_PROVIDER':'calcom','BOOKING_MODE':'mock','BOOKING_DB_PATH':str(self.path)})
 def test_live_requires_explicit_gate(self):
  with self.assertRaises(ValueError):configured_service({'BOOKING_MODE':'calcom_live','CALCOM_API_KEY':'PRIVATE-KEY','BOOKING_DB_PATH':str(self.path)})
 def test_cal_test_customer_allowlist(self):
  a,c=self.cal();s=BookingService(a,self.store,'different@example.com')
  with self.assertRaises(BookingError):s.create_booking(SCOPE,ROAD,['opaque'],CUSTOMER)
  c.request.assert_not_called()
 def test_cal_find_reschedule_cancel(self):
  a,c=self.cal();slot=a.check_availability(ROAD,'2035-10-01',session_duration_minutes=30)[0]
  self.assertTrue(a.find_booking('provider-private-uid')['confirmed'])
  self.assertTrue(a.reschedule_booking('provider-private-uid',slot)['confirmed'])
  self.assertTrue(c.request.call_args.args[1].endswith('/reschedule'))
  a,c=self.cal(state='cancelled');self.assertFalse(a.cancel_booking('provider-private-uid')['confirmed'])
  self.assertTrue(c.request.call_args.args[1].endswith('/cancel'))
 def test_payment_and_extra_fields_blocked(self):
  for change in [{'price':10},{'bookingFields':[{'slug':'license','required':True}]},{'beforeEventBuffer':5}]:
   a,c=self.cal();r=Mock(status_code=200);r.json.return_value={'status':'success','data':{'id':30,'lengthInMinutes':30,'price':0,'slotInterval':30,**change}};c.request.side_effect=None;c.request.return_value=r
   with self.assertRaises(BookingError):a.check_availability(ROAD,'2035-10-01',session_duration_minutes=30)
   self.assertEqual(c.request.call_count,1)
 def test_cal_service_contract(self):
  a,c=self.cal();s=BookingService(a,self.store,CUSTOMER['email']);slots=s.check_availability(SCOPE,ROAD,'2035-10-01')['available_slots']
  out=s.create_booking(SCOPE,ROAD,[slots[0]['slot_ref']],CUSTOMER)
  self.assertTrue(out['booking_confirmed']);self.assertTrue(out['appointment_id'].startswith('CAL-DEMO-'));self.assertNotIn('provider-private-uid',json.dumps(out))
  self.assertTrue(s.find_booking(SCOPE,out['appointment_id'])['booking_confirmed'])

if __name__=='__main__':unittest.main()

