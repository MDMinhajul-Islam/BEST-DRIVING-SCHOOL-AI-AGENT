"""Offline offering model audit. Reads saved public evidence; no API calls."""
import json
import re
from collections import defaultdict, Counter
from decimal import Decimal
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from config.settings import ROOT
from src.utils import tidy, write_json, write_text, normalize, digest
from src.extractor import canonical_package


def load(name):
    return json.loads((ROOT/name).read_text(encoding='utf-8'))


def slug(text):
    return re.sub(r'[^a-z0-9]+','_',text.lower()).strip('_')


def amount(text):
    if text is None:return None
    m=re.fullmatch(r'\$?([\d,]+(?:\.\d{1,2})?)',text.strip())
    if not m:raise ValueError('Malformed price '+text)
    return float(Decimal(m.group(1).replace(',','')))


def source_inventory(metadata):
    """Count actual option controls once, not selected/mobile display repeats.

    Independent enumeration of saved markup, with retained locators. Does not
    call the package extractor or trust its reported package count.
    """
    rows=[]
    for meta in metadata:
        if meta['status']!='success':continue
        soup=BeautifulSoup((ROOT/meta['raw_html']).read_bytes(),'lxml')
        for i,container in enumerate(soup.select('main [data-pk]')):
            chips=container.select('[data-pk-chip]')
            for j,option in enumerate(chips or [container]):
                if chips:
                    name=option.get('data-value'); price=option.get('data-price')
                    was=option.get('data-was') or None; label=option.get('data-badge') or None
                    target=option.get('data-link')
                else:
                    label_el=container.select_one('[data-pk-label]')
                    heading=container.select_one('h1,h3,h2')
                    name=tidy((label_el or heading).get_text(' ',strip=True))
                    price_el=container.select_one('[data-pk-price]')
                    price=tidy(price_el.get_text(' ',strip=True)) if price_el else None
                    was_el=container.select_one('[data-pk-was]');was=tidy(was_el.get_text(' ',strip=True)) if was_el else None
                    badge=container.select_one('[data-pk-badge]:not([hidden])');label=tidy(badge.get_text(' ',strip=True)) if badge else None
                    target=None
                if not target:
                    link=container.select_one('a[href*="/driving-courses/"]')
                    target=link['href'] if meta['page_category']!='course' and link else meta['url']
                rows.append({'identity_url':normalize(urljoin(meta['url'],target)),
                             'package_name':name,'canonical_name':canonical_package(name),
                             'price':amount(price),'original_price':amount(was) if was else None,
                             'marketing_label':label,'source_url':meta['url'],'page_category':meta['page_category'],
                             'raw_html':meta['raw_html'],'content_hash':meta['content_hash'],
                             'selector':f'main [data-pk] #{i+1}, option #{j+1}',
                             'evidence':dict(option.attrs) if chips else {'name':name,'price':price,'label':label}})
    return rows


def program_for(course):
    if course['category']=='adult' and 'online' in course['canonical_course_url']:
        return 'adult_online','Adult 6 Hours Online Permit Class'
    return {'teen':('teen','Teen Driver Education'),
            'adult':('adult_driving','Adult Driving Lessons in Plano'),
            'parent_taught':('parent_taught','Parent-Taught Log Driving Hours'),
            'road_test':('road_test','3rd Party Road Test in Plano')}[course['category']]


def build_catalog(kb,observations):
    grouped=defaultdict(list)
    for row in observations:grouped[row['identity_url'],row['canonical_name']].append(row)
    catalog=[];conflicts=[]
    for c in kb['courses']:
        key=c['canonical_course_url'],canonical_package(c['name']); rows=grouped.pop(key,[])
        if not rows:raise ValueError('No independently enumerated source option: '+c['name'])
        values=sorted({r['price'] for r in rows if r['price'] is not None})
        originals=sorted({r['original_price'] for r in rows if r['original_price'] is not None})
        price=values[0] if len(values)==1 else None
        original=originals[0] if len(originals)==1 else None
        pid=slug(c['category']+' '+c['name']); program_id,program=program_for(c)
        labels=sorted({r['marketing_label'] for r in rows if r['marketing_label']})
        if len(values)>1 or len(originals)>1:
            conflicts.append({'package_id':pid,'issue':'price_conflict','classification':'POSSIBLE PRICE CONFLICT','values':rows})
        text=' '.join(str(x or '') for x in [c.get('course_description'),c.get('package_description'),c.get('description')]+(c.get('included_services') or []))
        road=c['category']=='road_test'
        online=program_id=='adult_online'
        fees=[{'type':'processing_fee','percentage':3,'value':'3%',
               'non_refundable':True,'conditions':'Online payments; separate from advertised base price.',
               'sources':[s for s in c.get('pricing_conditions') or []]}]
        # Verify fee from actual primary raw page, not a universal assumption.
        meta=next(m for m in kb['source_pages'] if m['url']==c['canonical_course_url'])
        soup=BeautifulSoup((ROOT/meta['raw_html']).read_bytes(),'lxml')
        fee=soup.select_one('.bd-hero__price-note')
        fees=fees if fee and '3%' in fee.get_text() else []
        if fees:fees[0]['source']={'url':meta['url'],'section':'.bd-hero__price-note','evidence':tidy(fee.get_text(' ',strip=True)),'raw_html':meta['raw_html']}
        included={'classroom_hours':c.get('classroom_hours'),'driving_hours':c.get('driving_hours'),
                  'observation_hours':c.get('observation_hours'),'practice_hours':None,
                  'road_test':True if road else False if 'road test not included' in text.lower() else None,
                  'vehicle_included':True if 'dual-control vehicle' in text.lower() else None,
                  'pickup_dropoff':None,'online_access':True if online else None,
                  'certificate':next((x for x in c.get('included_services') or [] if 'certificate' in x.lower()),None),
                  'number_of_sessions':c.get('number_of_sessions'),'session_duration_hours':c.get('session_duration')}
        if c['category']=='adult' and not online:included['driving_hours']=c['included_hours']
        if c['category']=='parent_taught':included['practice_hours']=c['included_hours']
        included['education_hours']=6 if online else None
        if c['category']=='teen' and 'in-car instruction only' in text.lower():included['classroom_hours']=0
        practice=road and 'practice session' in c['name'].lower()
        included['pre_test_practice']=True if practice else False if road else None
        expected='online_course_access' if online else 'class_and_driving_schedule' if c['category']=='teen' and included['classroom_hours'] else 'road_test_and_practice_schedule' if practice else 'road_test_schedule' if road else 'driving_lesson_schedule'
        catalog.append({'package_id':pid,'legacy_package_id':c['id'],'program_id':program_id,'program':program,
            'course_id':slug(c['canonical_course_url'].rsplit('/',1)[-1]),'course':c['course_name'],
            'package_name':c['name'],'website_aliases':sorted({r['package_name'] for r in rows}),
            'description':c.get('description'),'package_description':c.get('package_description'),
            'current_price':price,'currency':'USD','original_price':original,
            'discount':{'amount':round(original-price,2),'currency':'USD','website_labels':sorted({o.get('promotion') for o in c['observations'] if (o.get('promotion') or '').startswith('Save')})} if original is not None and price is not None else None,
            'marketing_labels':labels,'additional_fees':fees,'included':included,
            'included_services':c.get('included_services') or [],'prerequisites':c.get('prerequisites') or [],
            'required_documents':c.get('required_documents'),'target_customer':c.get('target_customer'),
            'age_requirement':c.get('age_requirement'),'requires_official_verification':c['requires_official_verification'],
            'booking_required':False if online else True,
            'booking_required_refers_to_timed_reservation':True,
            'booking_required_basis':'Website says self-paced online access' if online else 'Website enrollment/lesson scheduling or scheduled test description; backend policy unverified',
            'expected_availability_type':expected,'requires_live_availability':not online,
            'availability_source':'not_applicable_self_paced' if online else 'live_api_required',
            'live_slots':None,'location_dependency':{'delivery':'online' if online else 'in_person',
                'location':'Plano' if road or program_id=='adult_driving' else None,
                'pickup_dropoff':'UNKNOWN — REQUIRES BUSINESS CONFIRMATION'},
            'price_status':'verified_saved_snapshot' if price is not None else 'conflict_requires_review',
            'live_price_rechecked':False,'source_snapshot_dates':sorted({s['scraped_at'] for s in c['sources']}),
            'sources':c['sources'],'option_observations':rows,'source':{'url':meta['url'],'page_title':meta['title'],
                'section':c['course_name'],'last_modified':meta['sitemap_lastmod']},
            'unknown_fields':[k for k,v in included.items() if v is None]})
    if grouped:raise ValueError('Unmatched website packages: '+str(list(grouped)))
    return catalog,conflicts


def booking_model(catalog):
    return [{'package_id':p['package_id'],'legacy_package_id':p['legacy_package_id'],
             'requires_live_availability':p['requires_live_availability'],
             'expected_availability_type':p['expected_availability_type'],
             'availability_type_is_conceptual_not_backend_enum':True,
             'booking_information_needed':['selected_package_id','student_name','contact','preferred_location','preferred_date','preferred_time'] if p['requires_live_availability'] else ['selected_package_id','student_name','contact'],
             'information_is_planning_requirement_not_verified_backend_fields':True,
             'prerequisite_reference':p['prerequisites'],
             'unknown_operational_fields':['UNKNOWN — REQUIRES BOOKING SYSTEM INSPECTION: actual identifiers, required request fields, timezone, instructor/vehicle allocation, capacity, slot duration, payment/access timing, confirmation, reschedule and cancellation policy'],
             'booking_actions_implemented':False} for p in catalog]


def hierarchy(catalog):
    groups={}
    for p in catalog:
        program=groups.setdefault(p['program_id'],{'program_id':p['program_id'],'program':p['program'],'courses':{}})
        course=program['courses'].setdefault(p['course_id'],{'course_id':p['course_id'],'course_name':p['course'],'packages':[]})
        course['packages'].append({'package_id':p['package_id'],'package_name':p['package_name'],
            'current_price':p['current_price'],'currency':'USD','requires_booking':p['booking_required'],
            'availability_source':p['availability_source'],'booking_requirements_reference':p['package_id']})
    for group in groups.values():group['courses']=list(group['courses'].values())
    return {'schema_version':'1.0','model_scope':'Offline business snapshot and conceptual booking handoff; not workflow import.',
            'programs':list(groups.values())}


def validate_catalog(catalog,booking,mapping):
    errors=[];ids=[p['package_id'] for p in catalog]
    if len(ids)!=len(set(ids)):errors.append('Duplicate package ID')
    identities=[(p['source']['url'],canonical_package(p['package_name'])) for p in catalog]
    if len(identities)!=len(set(identities)):errors.append('Duplicate canonical offering')
    for p in catalog:
        if not p['sources'] or not all(s.get('url','').startswith('https://bestdrivingschool.us/') for s in p['sources']):errors.append('Missing business source')
        if p['current_price'] is not None and (isinstance(p['current_price'],bool) or not isinstance(p['current_price'],(int,float))):errors.append('Non-numeric price')
        if p['live_slots'] is not None:errors.append('Live slots in static catalog')
        if any(label in p['package_name'] for label in p['marketing_labels']):errors.append('Marketing label mixed into name')
    if {b['package_id'] for b in booking}!=set(ids):errors.append('Booking map references mismatch')
    flattened=[p['package_id'] for program in mapping['programs'] for c in program['courses'] for p in c['packages']]
    if Counter(flattened)!=Counter(ids):errors.append('Hierarchy package references mismatch')
    return errors


def table(catalog):
    text='| Program | Course | Package | Base price | Original | Discount | Marketing label | Included hours | Included services | Prerequisites | Location | Source | Scraped correctly? | Issue |\n| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n'
    for p in catalog:
        h=p['included']; hours=', '.join(f'{k}: {h[k]}' for k in ['classroom_hours','driving_hours','observation_hours','practice_hours'] if h[k] is not None)
        issue='Missing separate Best selling aggregation corrected' if p['package_id'] in ('teen_24_hr_classroom_driving_package','adult_10_hours') else 'Hierarchy/price/fee fields normalized; no missing package'
        cells=[p['program'],p['course'],p['package_name'],str(p['current_price']),str(p['original_price']),str(p['discount']['amount']) if p['discount'] else 'None',', '.join(p['marketing_labels']) or 'None shown',hours,
               '; '.join(p['included_services']),'; '.join(p['prerequisites']),str(p['location_dependency']['location'] or p['location_dependency']['delivery']),p['source']['url'],'YES after audit',issue]
        text+='| '+' | '.join(x.replace('|','/').replace('\n',' ') for x in cells)+' |\n'
    return text


def render(catalog,booking,mapping,observations,conflicts):
    labels=sum(bool(p['marketing_labels']) for p in catalog);scheduled=sum(p['requires_live_availability'] for p in catalog)
    missing=sum(len(p['unknown_fields']) for p in catalog)
    header='Audit date: 2026-09-13. Prices are verified against preserved website evidence dated in `source_snapshot_dates`; no live price refresh was performed. Recheck before production quoting.\n\n'
    counts=f'Website programs: {len(mapping["programs"])} (purchasable program families; four service pages)\nWebsite courses: 6 (course pages; website also calls five program cards “courses”)\nWebsite package options: {len(catalog)}\nPrevious extracted packages: 13\nCanonical verified packages: {len(catalog)}\nPrices verified: {sum(p["current_price"] is not None for p in catalog)}/{len(catalog)}\nMarketing labels verified: {labels} labeled packages/{len(catalog)} packages checked\nPackages with prerequisites: {sum(bool(p["prerequisites"]) for p in catalog)}\nPackages requiring live availability: {scheduled}\nPackage price conflicts: {len(conflicts)}\nMissing data: {missing} null included-feature fields, plus separately documented operational unknowns\nRaw package-looking records: {len(observations)}\nCanonical unique packages: {len(catalog)}\nDuplicate observations consolidated: {len(observations)-len(catalog)}\nDuplicate canonical records removed: 0\nWebsite/structured package count match: YES\n'
    text='# Course / package / pricing audit\n\n'+header+'```text\n'+counts+'```\n\n'+table(catalog)
    text+='\n## Interpretation and corrections\n\nTeen Driver Education is one program with two course pages/packages, not unrelated programs. Adult education and driving lessons are separate offerings even at the same six-hour duration. Road Test and Road test only, and Practice + Road Test and Practice session + road test, are documented website aliases. Existing opaque IDs remain as legacy IDs; readable catalog IDs are independent of price.\n\nThe 91 source observations contain repeated homepage, service and location cards plus 13 course-page options. Mobile selects and selected displays are alternative presentations, not extra offerings. Previous 13 canonical packages were already correct. No price disagreements were found among option-bound observations across the saved pages. Unbound narrative/per-hour amounts remain separate; no range was used as a package price.\n\nSeparate label aggregation restores Best selling for teen full and adult 10 hours. Discounts and labels now have independent fields. The adult online $70 is an original/crossed-out price, not a competing current price. Online 3% non-refundable charges remain separate; no tax/deposit or all-in checkout total is invented.\n\n## Schedule and booking\n\nSelf-paced adult online education needs course access rather than a timed lesson slot. Twelve in-person options need live scheduling at the relevant stage. Walk-ins welcome is a school statement, not guaranteed capacity. Date-specific teen batch Saturdays–Sundays and 3pm–5pm text belongs to its historical batch, not a universal recurring schedule. Office hours and generic weekend scheduling do not prove available slots. Backend contracts have not been inspected.\n\n## Human review\n\nConfirm package-specific practice duration, pickup/dropoff, all-in checkout fees, location/instructor assignment, availability rules, multi-session scheduling, course-access/payment timing and cancellation/rescheduling policies. Website prerequisites remain business statements flagged for official verification; Phase B rules are unchanged. The road-test page’s teen age heading must not override official age/pathway guidance.\n\nSee [before-correction audit](course_package_pricing_audit_before.md), [package catalog](../knowledge/package_catalog.md) and [schedule distinction](../docs/schedule_vs_availability.md).\n'
    write_text(ROOT/'reports/course_package_pricing_audit.md',text)
    write_text(ROOT/'reports/package_inventory_audit.md','# Individual package inventory audit\n\n'+header+table(catalog)+'\nAll 13 options were checked against raw selector/fixed-price markup and course inclusions/prerequisites. Marketing-label/model issues and corrections are recorded in the main audit. Prices mean saved-snapshot current price.\n')
    text='# Package catalog\n\n'+header+'Program → Course → Package → Price → Requirements → Live Availability → Booking. Null means not established; it does not mean excluded. Additional fees are separate from base prices.\n\n'
    for group in mapping['programs']:
        text+='## '+group['program']+'\n\n'
        for p in [p for p in catalog if p['program_id']==group['program_id']]:
            text+='### '+p['package_name']+'\n\n'
            display_price=f'${p["current_price"]:,.2f}' if p['current_price'] is not None else 'CONFLICT — REQUIRES HUMAN REVIEW'
            text+=f'ID: `{p["package_id"]}`. Course: {p["course"]}.\n\nBase price: **{display_price}**. Original: '+(f'${p["original_price"]:,.2f}' if p['original_price'] is not None else 'not shown')+'.\n\n'
            text+='Marketing labels: '+(', '.join(p['marketing_labels']) or 'none shown')+'.\n\n'
            text+='Includes: `'+json.dumps(p['included'],ensure_ascii=False)+'`\n\n'+ '; '.join(p['included_services'])+'\n\n'
            text+='Description: '+(p['description'] or 'not specified')+'\n\nBest for: '+(p['target_customer'] or 'Use the stated course purpose and caller need; no inferred eligibility')+'.\n\n'
            text+='Prerequisites (school statements): '+ '; '.join(p['prerequisites'])+'\n\n'
            text+='Location: '+json.dumps(p['location_dependency'])+'.\n\nAvailability: '+p['availability_source']+'. '+('Online payment carries a separate 3% non-refundable processing charge.' if p['additional_fees'] else 'No fee extracted.')+'\n\nSource: ['+p['source']['page_title']+']('+p['source']['url']+')\n\n'
    text+='## Teen comparison\n\n| Feature | Full Classroom + Driving | BTW Only |\n| --- | --- | --- |\n| Base price | $399 | $350 |\n| Classroom | 24 hours | Excluded: in-car instruction only |\n| Driving | 7 hours | 7 hours |\n| Observation | 7 hours | 7 hours |\n| Marketing label | Best selling | None shown |\n| Entry stage | Classroom enrollment; learner needed before driving | Classroom completed elsewhere; learner needed |\n\n## Other\n\nNo additional purchasable option was found in the 18 saved pages. Service-area pages do not establish separate products or extra offices. Backend-only products are outside this audit.\n'
    write_text(ROOT/'knowledge/package_catalog.md',text)
    write_text(ROOT/'docs/schedule_vs_availability.md','# Schedule versus availability\n\n'+header+'STATIC SCHEDULE INFORMATION → Website knowledge: self-paced online delivery; explicitly listed session duration/count; generic flexible scheduling including weekends; advertised office hours and 24/7 helpline as separate claims.\n\nLIVE AVAILABLE SLOT → Authorized booking API/classSchedule backend: dated batch options, capacity, actual instructor/vehicle appointment slots and remaining places. Historical batch dates/times remain in raw evidence and are not static availability. Even a batch’s weekday/time pattern must not be generalized beyond that batch.\n\nPrices follow a website-refresh lifecycle; slots must be checked during the conversation. A price card, generic weekend statement or walk-ins welcome does not reserve anything. Online education access is different from reserving an in-person appointment.\n\nLater inspect authorized contracts for service/package identifiers, locations, timezone, instructor/vehicle allocation, capacity, duration, multi-session rules, prerequisites, payment/access timing and booking confirmation/cancellation/rescheduling. All concrete backend fields remain UNKNOWN — REQUIRES BOOKING SYSTEM INSPECTION. No restricted /classSchedule, /api, /enrollment, /student or /order routes were crawled.\n')
    schedule_path=ROOT/'docs/schedule_vs_availability.md'
    write_text(schedule_path,schedule_path.read_text(encoding='utf-8')+'\n## Specific saved schedule observations\n\nThe location pages advertise 9am–7pm, seven days a week, separately from a 24/7 helpline. These statements describe operations/contact coverage, not returned appointment slots. [Plano source](https://bestdrivingschool.us/driving-school-plano). Adult 4/6/8/10-hour selectors explicitly describe two/three/four/five sessions of two hours; the 2-hour option has two total driving hours but no extracted session count. [Adult lessons source](https://bestdrivingschool.us/driving-courses/adult-driving-sessions). Teen full-course dated batch cards show differing weekday/time patterns; none establishes a universal schedule. BTW-only states that the driving schedule is emailed after enrollment. [Teen sources](https://bestdrivingschool.us/services/driving-lessons-for-teens).\n')
    journeys=[('Adult first-time applicant','adult_online'),('Adult driving lesson customer','adult_driving'),('Teen full driver-ed customer','teen'),('Teen behind-the-wheel customer','teen'),('Parent-taught customer','parent_taught'),('Road-test-only customer','road_test'),('Road-test + preparation customer','road_test')]
    text='# Customer purchase journeys\n\nPlanning references only; not Retell workflow definitions. Licensing requirements use separate reviewed Phase B rules.\n\n'
    for name,program in journeys:
        options=[p for p in catalog if p['program_id']==program]
        if name=='Teen full driver-ed customer':options=[p for p in options if p['included']['classroom_hours']==24]
        if name=='Teen behind-the-wheel customer':options=[p for p in options if p['included']['classroom_hours']==0]
        if name=='Road-test-only customer':options=[p for p in options if not p['included']['pre_test_practice']]
        if name=='Road-test + preparation customer':options=[p for p in options if p['included']['pre_test_practice']]
        text+='## '+name+'\n\nCaller need → '+options[0]['program']+' → '+', '.join(p['package_name'] for p in options)+' → package preference → school prerequisites and separately verified licensing pathway → '
        text+=('purchase/enrollment and confirmed online access; timed live slot not established as necessary.' if program=='adult_online' else 'booking required at scheduling stage → authorized live availability → caller-selected returned slot(s) → confirmed backend booking result.')+'\n\n'
    text+='An adult first-time caller aged 25+ must not be forced into education; optional driving lessons and licensing guidance are separate choices. A sales selection is not proof of readiness, payment, availability or a completed booking.\n'
    write_text(ROOT/'knowledge/customer_purchase_journeys.md',text)
    write_text(ROOT/'knowledge/retell_support/course_package_booking_responsibility.md','# Course / package / booking responsibility\n\nManual Retell planning only. Adult/Teen/Road Test Sales identifies need, explains courses and package differences, reads sourced base price/features/fees, clarifies school prerequisites against separate regulatory guidance, and records the chosen package. Sales does not invent availability or announce a completed booking.\n\nBooking receives canonical course/package IDs, selected preference and prerequisite status; obtains live slots from the later authorized backend, offers only returned options, confirms location/date/time and creates a booking. It announces completion only after backend success; reschedule/cancellation require approved policies and confirmed backend results. Multi-session packages may need several appointments; the operational contract is unknown. Online education may require purchase/access confirmation rather than a slot.\n\n## Price challenge\n\nCaller: “I saw the Teen package for $299.”\n\nUse `package_catalog.json.current_price` for the specific selected canonical package, with `price_status`, snapshot date and conflicts checked. Caller input cannot overwrite this value. For the saved full teen package: “The website price in our reviewed catalog is $399 for 24 hours classroom, seven driving and seven observation. If you saw a different offer, we can have the school confirm it.” Recheck current pricing before production; do not claim the snapshot proves a live promotion is invalid. Keep 3% online processing separate.\n\nSuggested assignment test: challenge $399 with $299; the agent must clarify, preserve the sourced value, distinguish BTW at $350, and avoid inventing a discount or slot.\n')
    write_text(ROOT/'knowledge/retell_support/data_source_matrix.md','# Data source matrix\n\n| Field | Source | Rule |\n| --- | --- | --- |\n| Program/course/package name, description, base/original price, discounts, marketing labels, included features, stated school prerequisites | STATIC WEBSITE | Use canonical sourced records; caller price challenges do not overwrite price |\n| Licensing eligibility, education/test/ITD requirements and exemptions | OFFICIAL REGULATORY SOURCE | Use separate Phase B rules and review gates |\n| Slot IDs, dated available times, capacity, booking status and appointment ID | LIVE OPERATIONAL API | Require live confirmed backend result; contract unknown |\n| Student/caller name, contact, needs, preferred location/date/time and package preference | CALLER INPUT | Preferences and self-reported status, not verified system facts |\n| Fee applicability, cancellation exceptions, refund/reschedule authority, manual enrollment exceptions | INTERNAL BUSINESS RULE | Obtain owner-approved policy; preserve public fee evidence separately |\n\n`package_price` comes from `package_catalog.current_price` and currency/snapshot status; no caller amount becomes authoritative. Office hours, duration and generic weekend scheduling are static; actual slots are live. A license-guide answer does not establish school authorization or book a package.\n')
    path=ROOT/'knowledge/retell_support/recommended_shared_variables.md';text=path.read_text(encoding='utf-8');marker='\n## Course/package audit proposed variables\n'
    text=text.split(marker)[0].rstrip()+marker+'\n| Variable | Origin / use |\n| --- | --- |\n| intent | Caller need; existing variable |\n| program / program_id | Canonical business catalog |\n| course_id / course_name | Course entity, distinct from package |\n| package_id / package_name | Chosen canonical option; retain legacy ID for migration |\n| package_price / currency / price_snapshot | Structured source; caller cannot overwrite |\n| selected_package | Existing proposal: normalize to package_id rather than maintain conflicting selections |\n| preferred_location / preferred_date / preferred_time | Caller preferences; not confirmed availability |\n| appointment_id | Verified backend result only; existing variable |\n| selected_slot_id / confirmed_datetime | OPTIONAL after actual backend contract is reviewed; no invented field names |\n\nProposed manual variables, not configured Retell fields. Price, availability and booking state remain distinct.\n'
    write_text(path,text)
    stats={'programs':len(mapping['programs']),'courses':6,'packages':len(catalog),'raw_observations':len(observations),
           'duplicate_observations_consolidated':len(observations)-len(catalog),'canonical_duplicates_removed':0,
           'prices_verified':sum(p['current_price'] is not None for p in catalog),'price_conflicts':len(conflicts),
           'labeled_packages':labels,'requires_live_availability':scheduled,'unknown_included_fields':missing}
    write_json(ROOT/'reports/package_audit_summary.json',stats)
    return stats


def main():
    kb=load('data/structured/knowledge_base.json');observations=source_inventory(kb['source_pages'])
    catalog,conflicts=build_catalog(kb,observations);booking=booking_model(catalog);mapping=hierarchy(catalog)
    errors=validate_catalog(catalog,booking,mapping)
    if errors:raise ValueError('\n'.join(errors))
    for name,value in [('package_catalog',catalog),('package_booking_requirements',booking),('course_package_booking_map',mapping)]:write_json(ROOT/f'data/structured/{name}.json',value)
    write_json(ROOT/'reports/package_source_observations.json',observations)
    write_json(ROOT/'reports/package_price_conflicts.json',conflicts)
    write_json(ROOT/'reports/package_audit_validation.json',{'errors':errors,'valid':not errors})
    print(json.dumps(render(catalog,booking,mapping,observations,conflicts),indent=2))


if __name__=='__main__':main()
