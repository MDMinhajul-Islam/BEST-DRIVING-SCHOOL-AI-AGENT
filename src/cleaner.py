import re
from bs4 import BeautifulSoup, NavigableString, Tag
from src.utils import tidy


def clean_html(html):
    soup = BeautifulSoup(html, 'lxml')
    main = soup.select_one('main')
    warnings = []
    if main is None:
        main = soup.body or soup
        warnings.append('main_missing_fallback_used; manual review required')
    # Render attribute-only selector information in cleaned output as well as JSON.
    for chip in main.select('[data-pk-chip]'):
        replacement = soup.new_tag('p')
        replacement.string = 'Package: ' + ' · '.join(filter(None, [chip.get('data-value'),
            chip.get('data-price'), ('original ' + chip['data-was']) if chip.get('data-was') else None,
            chip.get('data-meta'), chip.get('data-note')]))
        chip.replace_with(replacement)
    for panel in main.select('[data-pk-panel]'):
        label = soup.new_tag('h3')
        label.string = 'Package details: ' + panel['data-pk-panel']
        panel.insert(0, label)
    # Harvest attribute-only package information separately in the extractor.
    for node in list(main.select('script,style,noscript,svg,nav,header,footer,form,input,select,textarea,#batches,#enroll,[data-consent],.bd-social,.bd-reviews,.bd-testimonials,.bd-hero__actions,.bd-course__actions')):
        if node.parent:
            node.decompose()
    for node in list(main.select('[aria-hidden="true"]')):
        if node.parent:
            node.decompose()
    for node in list(main.select('.bd-kv')):
        key = node.select_one('.bd-kv__k')
        if key and tidy(key.get_text()).lower() == 'selected':
            node.decompose()
    for node in list(main.select('button')):
        if node.has_attr('data-faq'):
            node.unwrap()
        else:
            node.decompose()
    blocks = []
    heading_path = []

    def emit(kind, text, **extra):
        text = tidy(text)
        if text and not re.fullmatch(r'[\W_]+', text) and text.lower() not in ('choose a package','selected','showing details for','jump to','more less','details','course description'):
            blocks.append({'type': kind, 'text': text, 'heading_path': [x[1] for x in heading_path], **extra})

    def walk(node):
        nonlocal heading_path
        if isinstance(node, NavigableString):
            emit('text', str(node))
            return
        if not isinstance(node, Tag):
            return
        if node.name in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            level = int(node.name[1])
            text = tidy(node.get_text(' ', strip=True))
            heading_path = [x for x in heading_path if x[0] < level] + [(level, text)]
            emit('heading', text, level=level)
        elif node.name in ('p', 'li', 'address', 'summary'):
            emit('list_item' if node.name == 'li' else 'paragraph', node.get_text(' ', strip=True))
        elif node.name == 'table':
            rows = [[tidy(c.get_text(' ', strip=True)) for c in row.select('th,td')]
                    for row in node.select('tr')]
            emit('table', ' | '.join(' / '.join(row) for row in rows), rows=rows)
        elif node.name == 'a':
            text = tidy(node.get_text(' ', strip=True))
            # Preserve meaningful inline link text; CTA-only standalone links go
            # into links.json instead of being repeated as knowledge paragraphs.
            if not text.lower().startswith(('enroll', 'book ', 'call ', 'read ', 'see ', 'view ', 'go ', 'check ', 'compare ', 'contact ', 'learn ', 'explore ', 'start ', 'full ')):
                emit('text', text)
        elif node.name in ('div','span') and not node.find(['div','p','ul','ol','li','h1','h2','h3','h4','h5','h6','table','address','section','article','aside']):
            emit('paragraph', node.get_text(' ',strip=True))
        else:
            for child in node.children:
                walk(child)
    walk(main)
    return blocks, warnings


def markdown_blocks(blocks):
    lines = []
    for block in blocks:
        if block['type'] == 'heading':
            lines.append('#' * block['level'] + ' ' + block['text'])
        elif block['type'] == 'list_item':
            lines.append('- ' + block['text'])
        elif block['type'] == 'table':
            rows = block['rows']
            if rows:
                width = max(map(len, rows))
                rows = [row + [''] * (width - len(row)) for row in rows]
                lines.append('| ' + ' | '.join(rows[0]) + ' |')
                lines.append('| ' + ' | '.join(['---'] * width) + ' |')
                lines.extend('| ' + ' | '.join(row) + ' |' for row in rows[1:])
        else:
            lines.append(block['text'])
    return '\n\n'.join(lines) + '\n'
