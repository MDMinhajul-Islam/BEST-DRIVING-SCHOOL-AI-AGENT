"""Strict normalized date, package and attendee boundaries."""
import re,json
from datetime import datetime,timedelta,timezone
from zoneinfo import ZoneInfo
from config.settings import ROOT
from src.booking.adapters import validate_date
class BookingError(Exception):
 def __init__(self,code):self.code=code

def package_plan(package_id):
 catalog=json.loads((ROOT/'data/structured/package_catalog.json').read_text(encoding='utf-8'))
 p=next((p for p in catalog if p['package_id']==package_id),None)
 if not p:raise BookingError('INVALID_PACKAGE')
 if p['program_id']=='adult_online':return []
 rules=json.loads((ROOT/'data/structured/internal_business_scheduling_rules.json').read_text(encoding='utf-8'))
 if package_id in rules['package_plans']:return rules['package_plans'][package_id]['session_plan_minutes']
 if package_id=='road_test_road_test_only':return [30]
 raise BookingError('PACKAGE_REQUIRES_REVIEW')

EVENTS={120:'driving_standard',60:'driving_remainder',30:'road_test'}
def utc_stamp(value):
 if not isinstance(value,str) or len(value)>40:raise BookingError('VALIDATION_ERROR')
 try:dt=datetime.fromisoformat(value.replace('Z','+00:00'))
 except ValueError:raise BookingError('VALIDATION_ERROR')
 if dt.tzinfo is None:raise BookingError('VALIDATION_ERROR')
 return dt.astimezone(timezone.utc)

def date_bounds(value,tz='America/Chicago'):
 try:d=validate_date(value);zone=ZoneInfo(tz)
 except (ValueError,TypeError,KeyError):raise BookingError('VALIDATION_ERROR')
 return datetime.combine(d,datetime.min.time(),zone).astimezone(timezone.utc),datetime.combine(d+timedelta(days=1),datetime.min.time(),zone).astimezone(timezone.utc)

def customer_data(value):
 if not isinstance(value,dict) or set(value)-{'name','email'}:raise BookingError('VALIDATION_ERROR')
 name=value.get('name');email=value.get('email')
 if not isinstance(name,str) or not name.startswith('BDS AI TEST') or len(name)>100:raise BookingError('CUSTOMER_DATA_MISSING')
 if not isinstance(email,str) or len(email)>254 or not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+',email):raise BookingError('CUSTOMER_DATA_MISSING')
 return {'name':name,'email':email}
