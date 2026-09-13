"""Read-only public availability and explicitly synthetic mock transactions."""
import copy
import hashlib
import json
import re
from datetime import date, datetime
from threading import RLock
from typing import Protocol
import requests


MESSAGES={'INVALID_PACKAGE':'That package could not be identified.',
 'INVALID_LOCATION':'The scheduling location has not been confirmed.',
 'VALIDATION_ERROR':'Please check the requested booking details.',
 'SLOT_NO_LONGER_AVAILABLE':'That time is no longer available. Please check other times.',
 'AUTHENTICATION_FAILURE':'Please complete customer verification.',
 'BOOKING_NOT_FOUND':'The verified booking could not be found.',
 'IDEMPOTENCY_CONFLICT':'This request differs from the previous request.',
 'BACKEND_UNAVAILABLE':'Scheduling is temporarily unavailable.',
 'TIMEOUT':'Scheduling took too long. Please try again.',
 'UNKNOWN_SERVER_ERROR':'Scheduling could not be completed.',
 'LIVE_DISABLED':'Live scheduling is disabled.',
 'LIVE_WRITES_DISABLED':'Production booking changes are not enabled.',
 'NOT_SCHEDULABLE':'This self-paced course does not use a timed appointment.'}


def failure(code,mode):
    code=code if code in MESSAGES else 'UNKNOWN_SERVER_ERROR'
    return {'success':False,'mode':mode,'booking_confirmed':False,'error_code':code,'user_safe_message':MESSAGES[code]}


def validate_date(value):
    if not isinstance(value,str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}',value):raise ValueError('Invalid date')
    return date.fromisoformat(value)


def normalize_times(payload,requested_date):
    validate_date(requested_date)
    if isinstance(payload,dict):payload=list(payload.values())
    if not isinstance(payload,list):raise ValueError('Invalid response shape')
    result={}
    for label in payload:
        if not isinstance(label,str) or not re.fullmatch(r'\d{1,2}:\d{2}\s*[AP]M\s*-\s*\d{1,2}:\d{2}\s*[AP]M',label,re.I):raise ValueError('Not a time-only response')
        start,end=re.split(r'\s*-\s*',label)
        start=datetime.strptime(start.upper().strip(),'%I:%M %p').strftime('%H:%M')
        end=datetime.strptime(end.upper().strip(),'%I:%M %p').strftime('%H:%M')
        if end<=start:raise ValueError('Invalid time range')
        result[start,end]={'slot_id':None,'date':requested_date,'start_time':start,'end_time':end,
                          'timezone':None,'backend_time_label':label.strip(),
                          'bookable_through_this_adapter':False}
    return [result[k] for k in sorted(result)]


class BookingAdapter(Protocol):
    def check_availability(self,package_id,preferred_date,location_id=None):...
    def create_booking(self,**kwargs):...
    def find_booking(self,**kwargs):...
    def reschedule_booking(self,**kwargs):...
    def cancel_booking(self,**kwargs):...


class BestDrivingSchoolBookingAdapter:
    """Three evidenced GET routes only; never submits enrollment/payment.

    No cookies, tokens, caller details or guessed package/location parameters.
    Raw response bodies and exceptions are not returned/logged. No redirects.
    """
    mode='live_read_only'
    def __init__(self,package_map,enabled=False,client=None):
        self.package_map={p['package_id']:p for p in package_map}
        self.enabled=enabled;self.client=client or requests

    def check_availability(self,package_id,preferred_date,location_id=None):
        if not self.enabled:return failure('LIVE_DISABLED',self.mode)
        p=self.package_map.get(package_id)
        if not p:return failure('INVALID_PACKAGE',self.mode)
        if location_id is not None:return failure('INVALID_LOCATION',self.mode)
        try:validate_date(preferred_date)
        except (ValueError,TypeError):return failure('VALIDATION_ERROR',self.mode)
        path=p.get('observed_availability_path')
        if path not in ('/api/appointment-times','/api/adult-appointment-times','/api/teen-appointment-times'):
            return failure('NOT_SCHEDULABLE',self.mode)
        try:
            r=self.client.get('https://bestdrivingschool.us'+path,params={'date':preferred_date},
                headers={'Accept':'application/json'},timeout=(5,10),allow_redirects=False)
            if r.status_code in (401,403):return failure('AUTHENTICATION_FAILURE',self.mode)
            if r.status_code!=200:return failure('BACKEND_UNAVAILABLE',self.mode)
            slots=normalize_times(r.json(),preferred_date)
            return {'success':True,'mode':self.mode,'package_id':package_id,'available_slots':slots,
                    'booking_confirmed':False,'production_booking_enabled':False,
                    'warning':'Time labels only; stable slot/resource IDs, timezone and backend package acceptance are unverified.'}
        except requests.Timeout:return failure('TIMEOUT',self.mode)
        except (ValueError,requests.RequestException):return failure('BACKEND_UNAVAILABLE',self.mode)

    def create_booking(self,**kwargs):return failure('LIVE_WRITES_DISABLED',self.mode)
    def find_booking(self,**kwargs):return failure('LIVE_WRITES_DISABLED',self.mode)
    def reschedule_booking(self,**kwargs):return failure('LIVE_WRITES_DISABLED',self.mode)
    def cancel_booking(self,**kwargs):return failure('LIVE_WRITES_DISABLED',self.mode)


class MockBookingAdapter:
    """MOCK — NOT PRODUCTION. In-memory fixtures; no real customer fields.

    Customer refs and verification tokens are synthetic pre-provisioned fixtures.
    Appointment count/hours are not representations of actual school behavior.
    """
    mode='mock'
    def __init__(self,package_ids,fixture_date='2026-10-01'):
        self.package_ids=set(package_ids);self.lock=RLock();self.bookings={};self.idempotency={}
        self.customers={'MOCK-CUSTOMER-1':'MOCK-VERIFY-1','MOCK-CUSTOMER-2':'MOCK-VERIFY-2'}
        self.slots={f'MOCK-SLOT-{i}':{'slot_id':f'MOCK-SLOT-{i}','date':fixture_date,
            'start_time':f'{9+i:02}:00','end_time':f'{10+i:02}:00','location_id':'MOCK-LOCATION-1'} for i in range(1,5)}
        self.reserved={}

    def verified(self,customer_ref,verification_token):
        return customer_ref in self.customers and self.customers[customer_ref]==verification_token

    def check_availability(self,package_id,preferred_date,location_id=None):
        with self.lock:
            if package_id not in self.package_ids:return failure('INVALID_PACKAGE',self.mode)
            if location_id not in (None,'MOCK-LOCATION-1'):return failure('INVALID_LOCATION',self.mode)
            try:validate_date(preferred_date)
            except (ValueError,TypeError):return failure('VALIDATION_ERROR',self.mode)
            return {'success':True,'mode':'mock','synthetic':True,'production':False,'booking_confirmed':False,
                    'available_slots':[copy.deepcopy(s) for sid,s in self.slots.items() if sid not in self.reserved and s['date']==preferred_date]}

    def create_booking(self,package_id,slot_ids,customer_ref,verification_token,idempotency_key):
        with self.lock:
            if not self.verified(customer_ref,verification_token):return failure('AUTHENTICATION_FAILURE',self.mode)
            if package_id not in self.package_ids:return failure('INVALID_PACKAGE',self.mode)
            if not isinstance(idempotency_key,str) or not idempotency_key:return failure('VALIDATION_ERROR',self.mode)
            if not isinstance(slot_ids,list) or not slot_ids or not all(isinstance(s,str) for s in slot_ids) or len(slot_ids)!=len(set(slot_ids)) or any(s not in self.slots for s in slot_ids):return failure('VALIDATION_ERROR',self.mode)
            fingerprint=hashlib.sha256(json.dumps([package_id,slot_ids,customer_ref]).encode()).hexdigest()
            if idempotency_key in self.idempotency:
                old_hash,bid=self.idempotency[idempotency_key]
                return self.success(self.bookings[bid]) if old_hash==fingerprint else failure('IDEMPOTENCY_CONFLICT',self.mode)
            if any(s in self.reserved for s in slot_ids):return failure('SLOT_NO_LONGER_AVAILABLE',self.mode)
            bid=f'MOCK-BOOKING-{len(self.bookings)+1}'
            booking={'appointment_id':bid,'package_id':package_id,'slot_ids':list(slot_ids),
                     'customer_ref':customer_ref,'booking_status':'booking_confirmed','version':1}
            self.bookings[bid]=booking
            for s in slot_ids:self.reserved[s]=bid
            result=self.success(booking);self.idempotency[idempotency_key]=fingerprint,bid
            return result

    def success(self,booking):
        return {'success':True,'mode':'mock','synthetic':True,'production':False,
                'booking_confirmed':booking['booking_status']=='booking_confirmed','booking':copy.deepcopy(booking)}

    def find_booking(self,appointment_id,customer_ref,verification_token):
        with self.lock:
            if not self.verified(customer_ref,verification_token):return failure('AUTHENTICATION_FAILURE',self.mode)
            b=self.bookings.get(appointment_id)
            if not b or b['customer_ref']!=customer_ref:return failure('BOOKING_NOT_FOUND',self.mode)
            return self.success(b)

    def reschedule_booking(self,appointment_id,slot_ids,customer_ref,verification_token,expected_version):
        with self.lock:
            found=self.find_booking(appointment_id,customer_ref,verification_token)
            if not found['success']:return found
            b=self.bookings[appointment_id]
            if b['booking_status']!='booking_confirmed' or b['version']!=expected_version:return failure('VALIDATION_ERROR',self.mode)
            if not isinstance(slot_ids,list) or not slot_ids or not all(isinstance(s,str) for s in slot_ids) or len(slot_ids)!=len(set(slot_ids)) or any(s not in self.slots for s in slot_ids):return failure('VALIDATION_ERROR',self.mode)
            if any(s in self.reserved and self.reserved[s]!=appointment_id for s in slot_ids):return failure('SLOT_NO_LONGER_AVAILABLE',self.mode)
            for s in b['slot_ids']:self.reserved.pop(s,None)
            for s in slot_ids:self.reserved[s]=appointment_id
            b.update(slot_ids=list(slot_ids),version=b['version']+1)
            return self.success(b)

    def cancel_booking(self,appointment_id,customer_ref,verification_token,expected_version):
        with self.lock:
            found=self.find_booking(appointment_id,customer_ref,verification_token)
            if not found['success']:return found
            b=self.bookings[appointment_id]
            if b['booking_status']=='booking_cancelled':return self.success(b)
            if b['version']!=expected_version:return failure('VALIDATION_ERROR',self.mode)
            for s in b['slot_ids']:self.reserved.pop(s,None)
            b.update(booking_status='booking_cancelled',version=b['version']+1)
            return self.success(b)
