"""Offline demonstration: MOCK — NOT PRODUCTION; all five operations."""
import json
from config.settings import ROOT
from src.booking.adapters import MockBookingAdapter

def main():
 packages=json.loads((ROOT/'data/structured/package_backend_map.json').read_text())
 pid=next(p['package_id'] for p in packages if p.get('observed_availability_path'))
 adapter=MockBookingAdapter([pid]);auth=dict(customer_ref='MOCK-CUSTOMER-1',verification_token='MOCK-VERIFY-1')
 results={'label':'MOCK — NOT PRODUCTION','availability':adapter.check_availability(pid,'2026-10-01')}
 results['create']=adapter.create_booking(pid,['MOCK-SLOT-1'],idempotency_key='MOCK-DEMO-1',**auth)
 bid=results['create']['booking']['appointment_id']
 results['find']=adapter.find_booking(bid,**auth)
 results['reschedule']=adapter.reschedule_booking(bid,['MOCK-SLOT-2'],expected_version=1,**auth)
 results['cancel']=adapter.cancel_booking(bid,expected_version=2,**auth)
 target=ROOT/'reports/phase_c_mock_demo.json';target.write_text(json.dumps(results,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
 print('Offline synthetic five-operation demo saved to '+str(target))
if __name__=='__main__':main()
