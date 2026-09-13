"""Preserve reviewed public government documents; never submit forms."""
import argparse
import json
import logging
import re
import time
from urllib.parse import urlsplit, urljoin, unquote
from bs4 import BeautifulSoup
import requests
from config.settings import ROOT
from src.utils import digest, now, write_json, write_text, tidy

DIRECT_HOSTS = {'www.dps.texas.gov', 'dps.texas.gov', 'www.tdlr.texas.gov',
                'tdlr.texas.gov', 'impacttexasdrivers.dps.texas.gov', 'statutes.capitol.texas.gov'}


def official_url(url):
    try:
        p = urlsplit(url)
        return p.scheme == 'https' and p.hostname in DIRECT_HOSTS and not p.username and not p.password and p.port in (None,443)
    except ValueError:
        return False


def public_source_url(url):
    if not official_url(url):
        return False
    decoded=unquote(urlsplit(url).path).lower()
    segments=[]
    for part in decoded.split('/'):
        if part=='..':
            if segments:segments.pop()
        elif part and part!='.':segments.append(part)
    path='/'+'/'.join(segments)
    if urlsplit(url).hostname == 'impacttexasdrivers.dps.texas.gov':
        return path in ('/itad/faq.aspx','/ittd/faq.aspx')
    return not re.search(r'/(?:login|account|descerts|apps|api|payment|checkout|apply-online|enrollment|student|order)(?:/|$)',path) and path!='/parenttaught/ptselect.aspx'


def normalized_sections(html, base_url):
    soup = BeautifulSoup(html, 'lxml')
    title = tidy(soup.title.get_text(' ',strip=True)) if soup.title else None
    body = soup.select_one('.field--name-body') or soup.select_one('main') or soup.select_one('#content') or soup.body
    if body is None:
        raise ValueError('No informational content container')
    # Public eligibility questionnaires contain informational labels and result
    # paragraphs. Preserve those; discard controls and never submit the form.
    for element in list(body.select('script,style,noscript,svg,nav,header,footer,input,select,textarea,iframe')):
        if element.parent:
            element.decompose()
    text = '\n'.join(tidy(line) for line in body.get_text('\n',strip=True).splitlines() if tidy(line))
    headings = [tidy(h.get_text(' ',strip=True)) for h in body.select('h1,h2,h3,h4')]
    dates = [tidy(x.get_text(' ',strip=True)) for x in soup.select('time,.field--name-field-date,.field--name-field-updated-date')]
    links = [{'url':urljoin(base_url,a['href']), 'text':tidy(a.get_text(' ',strip=True))}
             for a in body.select('a[href]')]
    return title, text, headings, dates, links


def fetch(session, url, audit):
    redirects = []
    for hop in range(6):
        if not public_source_url(url):
            raise ValueError('Non-government or non-public destination blocked: '+url)
        for attempt in range(2):
            time.sleep(.5)
            try:
                response = session.get(url,timeout=(4,15),allow_redirects=False)
                audit.append({'url':url,'status_code':response.status_code,'attempt':attempt+1})
                if response.status_code in (429,500,502,503,504) and attempt<1:
                    time.sleep(2**attempt)
                    continue
                break
            except requests.RequestException:
                if attempt==1:
                    raise
                time.sleep(2**attempt)
        if response.status_code in (301,302,303,307,308):
            target=urljoin(url,response.headers.get('Location',''))
            if not public_source_url(target):
                raise ValueError('Unapproved redirect blocked: '+target)
            redirects.append({'from':url,'to':target,'status_code':response.status_code})
            url=target
        else:
            return response,redirects
    raise ValueError('Too many redirects')


def collect_sources():
    root=ROOT/'data/regulatory_sources'
    for folder in ['html','pdfs','extracted','metadata']:
        (root/folder).mkdir(parents=True,exist_ok=True)
    index=ROOT/'data/structured/regulatory_sources.json'
    old={s['source_id']:s for s in json.loads(index.read_text(encoding='utf-8'))} if index.exists() else {}
    inventory=json.loads((ROOT/'config/regulatory_source_map.json').read_text(encoding='utf-8'))
    session=requests.Session()
    session.headers['User-Agent']='BestDrivingSchoolRegulatoryResearch/1.0 (public informational sources only)'
    records,audit=[],[]
    for entry in inventory:
        sid=entry['source_id']
        record={**entry,'title':None,'source_type':'pdf' if urlsplit(entry['url']).path.lower().endswith('.pdf') else 'webpage',
            'retrieved_at':now(),'published_or_updated':None,'displayed_dates':[], 'date_type':None,
            'active':False,'reviewed':False,'notes':None,'redirects':[], 'content_hash':None,
            'reviewed_content_hash':old.get(sid,{}).get('reviewed_content_hash'),
            'last_verified':old.get(sid,{}).get('last_verified'),
            'normalized_content_hash':None,'previous_normalized_hash':old.get(sid,{}).get('normalized_content_hash'),
            'change_status':'NEW','currency_status':'not_reviewed','raw_path':None,'extracted_path':None}
        try:
            response,redirects=fetch(session,entry['url'],audit)
            record.update(status_code=response.status_code,final_url=response.url,redirects=redirects)
            if response.status_code in (404,410):
                record.update(change_status='SOURCE_REMOVED',notes='Official URL no longer available')
            else:
                response.raise_for_status()
                if record['source_type']=='pdf':
                    if not response.content.startswith(b'%PDF'):
                        raise ValueError('Expected PDF; got non-PDF response')
                    path=root/'pdfs'/(sid+'.pdf');path.write_bytes(response.content)
                    from pypdf import PdfReader
                    reader=PdfReader(path)
                    pages=[{'page_number':i+1,'text':p.extract_text() or ''} for i,p in enumerate(reader.pages)]
                    text='\n'.join(tidy(p['text']) for p in pages)
                    record['title']=str((reader.metadata or {}).get('/Title') or entry['url'].rsplit('/',1)[-1])
                    record['page_count']=len(pages)
                    write_json(root/'extracted'/(sid+'.pages.json'),{'source_id':sid,'url':entry['url'],'pages':pages})
                    dates=re.findall(r'(?:Rev\.?|Revised|Effective|Updated|September|December|Dec\.)[^\n]{0,50}', '\n'.join(p['text'] for p in pages),re.I)
                    record['displayed_dates']=dates[:15]
                else:
                    if 'html' not in response.headers.get('Content-Type','').lower():
                        raise ValueError('Expected public HTML')
                    path=root/'html'/(sid+'.html');path.write_bytes(response.content)
                    title,text,headings,dates,links=normalized_sections(response.content,response.url)
                    record.update(title=title,headings=headings,displayed_dates=dates)
                    write_json(root/'metadata'/(sid+'.links.json'),links)
                if len(text)<100:
                    raise ValueError('Empty/short public source; review required')
                record['raw_path']=path.relative_to(ROOT).as_posix()
                extracted=root/'extracted'/(sid+'.txt');write_text(extracted,text)
                record.update(extracted_path=extracted.relative_to(ROOT).as_posix(),active=True,
                    content_hash=digest(response.content),normalized_content_hash=digest(tidy(text)))
                previous=record['previous_normalized_hash']
                record['change_status']='SOURCE_REDIRECTED' if redirects else ('UNCHANGED' if previous==record['normalized_content_hash'] else 'CHANGED' if previous else 'NEW')
        except Exception as exc:
            record.update(notes=str(exc),currency_status='requires_human_review',change_status='FETCH_FAILED')
        records.append(record)
        write_json(root/'metadata'/(sid+'.json'),record)
        print(sid,record['change_status'],record['status_code'] if 'status_code' in record else record['notes'],flush=True)
    write_json(index,records)
    write_json(root/'metadata/request_audit.json',audit)
    return records


if __name__=='__main__':
    collect_sources()
