import unittest,json,hashlib
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import Mock
import requests
from src.booking.adapters import *
ROOT=Path(__file__).resolve().parents[1]
class BookingTests(unittest.TestCase):
 def setUp(self):
  self.mapping=json.loads((ROOT/'data/structured/package_backend_map.json').read_text())
  self.pid=next(p['package_id'] for p in self.mapping if p.get('observed_availability_path'))
  self.mock=MockBookingAdapter([self.pid]);self.auth=dict(customer_ref='MOCK-CUSTOMER-1',verification_token='MOCK-VERIFY-1')
 def create(self,slot='MOCK-SLOT-1',key='request-1'):
  return self.mock.create_booking(self.pid,[slot],idempotency_key=key,**self.auth)
 def test_coverage(self):
  catalog=json.loads((ROOT/'data/structured/package_catalog.json').read_text())
  self.assertEqual({p['package_id'] for p in catalog},{p['package_id'] for p in self.mapping});self.assertEqual(len(self.mapping),13)
  for name in ['package_location_map','scheduling_models','session_rules']:
   records=json.loads((ROOT/f'data/structured/{name}.json').read_text());self.assertEqual({p['package_id'] for p in records},{p['package_id'] for p in catalog})
 def test_preservation(self):
  for path,h in json.loads((ROOT/'reports/phase_c_preservation_hashes.json').read_text()).items():self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),h,path)
 def test_normalization(self):
  a=normalize_times(['11:00 AM - 11:15 AM','10:00 AM - 10:15 AM'],'2026-10-01');b=normalize_times({'z':'11:00 AM - 11:15 AM','a':'10:00 AM - 10:15 AM'},'2026-10-01');self.assertEqual(a,b);self.assertIsNone(a[0]['slot_id']);self.assertFalse(a[0]['bookable_through_this_adapter'])
 def test_reject_sensitive_or_invalid_payload(self):
  for payload in [{'customer':{'name':'PRIVATE'}},['PRIVATE'],['11:00 AM - 10:00 AM'],None]:
   with self.assertRaises(ValueError):normalize_times(payload,'2026-10-01')
  with self.assertRaises(ValueError):normalize_times([],'20261001')
 def test_live_disabled_and_writes(self):
  c=Mock();a=BestDrivingSchoolBookingAdapter(self.mapping,client=c)
  self.assertEqual(a.check_availability(self.pid,'2026-10-01')['error_code'],'LIVE_DISABLED')
  for method in ['create_booking','find_booking','reschedule_booking','cancel_booking']:self.assertFalse(getattr(a,method)()['success'])
  c.get.assert_not_called()
 def test_live_parameters_and_no_confirmation(self):
  c=Mock();c.get.return_value.status_code=200;c.get.return_value.json.return_value=['10:00 AM - 10:15 AM'];a=BestDrivingSchoolBookingAdapter(self.mapping,True,c)
  r=a.check_availability(self.pid,'2026-10-01');self.assertTrue(r['success']);self.assertFalse(r['booking_confirmed']);kw=c.get.call_args.kwargs;self.assertEqual(kw['params'],{'date':'2026-10-01'});self.assertFalse(kw['allow_redirects']);self.assertEqual(kw['headers'],{'Accept':'application/json'})
 def test_live_safe_errors(self):
  c=Mock();a=BestDrivingSchoolBookingAdapter(self.mapping,True,c)
  c.get.side_effect=requests.Timeout('PRIVATE TOKEN');r=a.check_availability(self.pid,'2026-10-01');self.assertEqual(r['error_code'],'TIMEOUT');self.assertNotIn('PRIVATE',json.dumps(r))
  c.get.side_effect=None;c.get.return_value.status_code=403;self.assertEqual(a.check_availability(self.pid,'2026-10-01')['error_code'],'AUTHENTICATION_FAILURE')
 def test_live_invalid_inputs(self):
  c=Mock();a=BestDrivingSchoolBookingAdapter(self.mapping,True,c)
  for pid,d,loc,code in [('missing','2026-10-01',None,'INVALID_PACKAGE'),(self.pid,'20261001',None,'VALIDATION_ERROR'),(self.pid,'2026-10-01','guessed','INVALID_LOCATION')]:self.assertEqual(a.check_availability(pid,d,loc)['error_code'],code)
  c.get.assert_not_called()
 def test_mock_five_operations(self):
  self.assertFalse(self.mock.check_availability(self.pid,'2026-10-01')['booking_confirmed']);r=self.create();b=r['booking'];self.assertTrue(r['synthetic']);self.assertFalse(r['production']);bid=b['appointment_id']
  self.assertTrue(self.mock.find_booking(bid,**self.auth)['success']);r=self.mock.reschedule_booking(bid,['MOCK-SLOT-2'],expected_version=1,**self.auth);self.assertTrue(r['success']);r=self.mock.cancel_booking(bid,expected_version=2,**self.auth);self.assertFalse(r['booking_confirmed']);self.assertEqual(len(self.mock.check_availability(self.pid,'2026-10-01')['available_slots']),4)
 def test_customer_isolation(self):
  bid=self.create()['booking']['appointment_id'];r=self.mock.find_booking(bid,'MOCK-CUSTOMER-2','MOCK-VERIFY-2');self.assertEqual(r['error_code'],'BOOKING_NOT_FOUND');self.assertEqual(self.mock.find_booking(bid,'MOCK-CUSTOMER-1','bad')['error_code'],'AUTHENTICATION_FAILURE')
 def test_idempotency_current_state(self):
  r=self.create();self.assertEqual(self.create(),r);self.assertEqual(self.create('MOCK-SLOT-2')['error_code'],'IDEMPOTENCY_CONFLICT');self.mock.cancel_booking(r['booking']['appointment_id'],expected_version=1,**self.auth);self.assertFalse(self.create()['booking_confirmed']);self.assertEqual(len(self.mock.bookings),1)
 def test_slot_race(self):
  with ThreadPoolExecutor(2) as pool:results=list(pool.map(lambda k:self.create(key=k),['a','b']))
  self.assertEqual(sum(r['success'] for r in results),1);self.assertEqual(next(r for r in results if not r['success'])['error_code'],'SLOT_NO_LONGER_AVAILABLE')
 def test_atomic_reschedule_and_version(self):
  b=self.create()['booking'];self.create('MOCK-SLOT-2','other');r=self.mock.reschedule_booking(b['appointment_id'],['MOCK-SLOT-2'],expected_version=1,**self.auth);self.assertFalse(r['success']);self.assertEqual(self.mock.bookings[b['appointment_id']]['slot_ids'],['MOCK-SLOT-1']);self.assertFalse(self.mock.cancel_booking(b['appointment_id'],expected_version=99,**self.auth)['success'])
 def test_malformed_mock_slots(self):
  for slots in [[{}],['MOCK-SLOT-1','MOCK-SLOT-1'],[],['unknown']]:self.assertEqual(self.mock.create_booking(self.pid,slots,idempotency_key='x',**self.auth)['error_code'],'VALIDATION_ERROR')
if __name__=='__main__':unittest.main()
