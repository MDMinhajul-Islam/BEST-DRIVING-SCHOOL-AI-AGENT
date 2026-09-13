"""Retell-facing five-operation API. No provider secrets in responses or logs."""
import os,secrets,re,json
from fastapi import FastAPI,Request
from fastapi.responses import JSONResponse
from src.booking.configuration import configured_service
from src.booking.validators import BookingError
from src.booking.normalizers import error
SCHEMAS={
 'check-availability':({'package_id','preferred_date'},{'session_duration_minutes','preferred_time_window','timezone'}),
 'create':({'package_id','slot_ids','customer'},set()),
 'find':({'appointment_id'},set()),
 'reschedule':({'appointment_id','slot_ref'},set()),
 'cancel':({'appointment_id'},set())}
METHODS={'check-availability':'check_availability','create':'create_booking','find':'find_booking','reschedule':'reschedule_booking','cancel':'cancel_booking'}
def create_app(service=None,secret=None):
 secret=os.getenv('RETELL_TOOL_SECRET','') if secret is None else secret
 if not isinstance(secret,str) or len(secret)<32:raise ValueError('Set a private RETELL_TOOL_SECRET of at least 32 characters')
 service=service or configured_service();app=FastAPI(docs_url=None,redoc_url=None,openapi_url=None)
 @app.get('/api/health')
 def health():return {'status':'ok'}
 @app.post('/api/booking/{operation}')
 async def booking(operation:str,request:Request):
  supplied=request.headers.get('X-Retell-Tool-Secret','')
  if not secrets.compare_digest(supplied.encode(),secret.encode()):return JSONResponse(error('AUTHENTICATION_FAILURE',service.mode),status_code=401)
  scope=request.headers.get('X-Booking-Scope','')
  if not re.fullmatch(r'[A-Za-z0-9_-]{16,128}',scope):return JSONResponse(error('AUTHENTICATION_FAILURE',service.mode),status_code=401)
  if operation not in SCHEMAS:return JSONResponse(error('VALIDATION_ERROR',service.mode),status_code=404)
  data=bytearray()
  async for chunk in request.stream():
   data.extend(chunk)
   if len(data)>65536:return JSONResponse(error('VALIDATION_ERROR',service.mode),status_code=413)
  try:
   body=json.loads(data)
   if not isinstance(body,dict):raise BookingError('VALIDATION_ERROR')
   if 'args' in body:
    if set(body)-{'args','call','name'}:raise BookingError('VALIDATION_ERROR')
    body=body['args']
   if not isinstance(body,dict):raise BookingError('VALIDATION_ERROR')
   required,optional=SCHEMAS[operation]
   if not required<=body.keys() or set(body)-(required|optional):raise BookingError('VALIDATION_ERROR')
   if any(not isinstance(body[k],str) or len(body[k])>200 for k in required-{'slot_ids','customer'}):raise BookingError('VALIDATION_ERROR')
   from starlette.concurrency import run_in_threadpool
   out=await run_in_threadpool(getattr(service,METHODS[operation]),scope,**body)
   return JSONResponse(out)
  except BookingError as e:return JSONResponse(error(e.code,service.mode),status_code=200)
  except (ValueError,TypeError,KeyError):return JSONResponse(error('VALIDATION_ERROR',service.mode),status_code=400)
  except Exception:return JSONResponse(error('OUTCOME_UNKNOWN' if operation in ('create','reschedule','cancel') else 'PROVIDER_UNAVAILABLE',service.mode),status_code=503)
 return app
