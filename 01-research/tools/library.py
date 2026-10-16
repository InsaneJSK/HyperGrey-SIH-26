"""Maintain the curated research library; Python 3 plus pypdf. No solver imports.

fetch downloads only explicitly catalogued public URLs, never overwrites an
existing PDF, and records failures instead of saving an HTML error as a PDF.
build renders local indexes/notes. verify is offline and checks held files.
"""
import argparse
import concurrent.futures
import hashlib
import html
import io
import json
import re
import unicodedata
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / 'catalog.json'
RETRIEVAL = ROOT / 'retrieval.json'
MAX_BYTES = 80 * 1024 * 1024


def read_json(path, default=None):
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else default


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def slug(source):
    title = unicodedata.normalize('NFKD', source['title']).encode('ascii', 'ignore').decode()
    title = re.sub('[^a-z0-9]+', '-', title.lower()).strip('-')
    return str(source['year']) + '-' + title


def target_path(source, extension):
    path = (ROOT / source['topic'] / (slug(source) + extension)).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError('Catalog path escapes research root')
    return path


def request(url):
    if not url.startswith('https://'):
        raise ValueError('Only explicitly catalogued HTTPS sources are allowed')
    req = urllib.request.Request(url, headers={'User-Agent': 'HyperGreyResearchLibrary/1.0 (academic source archiving)'})
    with urllib.request.urlopen(req, timeout=35) as response:
        data = response.read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES:
            raise ValueError('Source exceeds 80 MiB collection limit')
        return data, response.geturl(), response.headers.get('Content-Type', '')


class PageMetadata(HTMLParser):
    def __init__(self):
        super().__init__()
        self.meta = {}
        self.in_title = False
        self.title = ''

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'meta':
            name = attrs.get('name', attrs.get('property', ''))
            if name.startswith('citation_') and name != 'citation_abstract':
                self.meta.setdefault(name, []).append(attrs.get('content', ''))
        if tag == 'title':
            self.in_title = True

    def handle_endtag(self, tag):
        if tag == 'title':
            self.in_title = False

    def handle_data(self, value):
        if self.in_title:
            self.title += value


def inspect_pdf(data):
    from pypdf import PdfReader
    if not data.lstrip().startswith(b'%PDF-'):
        raise ValueError('Response is not a PDF (possibly an access/bot page)')
    reader = PdfReader(io.BytesIO(data), strict=False)
    if reader.is_encrypted or not reader.pages:
        raise ValueError('Encrypted or empty PDF')
    # No full-text reproduction in the catalog: retain only title metadata.
    first_pages = ' '.join((page.extract_text() or '') for page in reader.pages[:2])
    return {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(),
            'pages': len(reader.pages), 'pdf_title': str((reader.metadata or {}).get('/Title', '')),
            'extractable_text': len(first_pages) > 80}


def fetch_one(source, previous):
    record = dict(previous or {})
    record['checked_at_utc'] = datetime.now(timezone.utc).isoformat(timespec='seconds')
    record['url'] = source['url']
    try:
        body, final_url, content_type = request(source['url'])
        record['landing'] = {'status': 'retrieved', 'resolved_url': final_url, 'content_type': content_type}
        if 'html' in content_type:
            parser = PageMetadata()
            parser.feed(body.decode('utf-8', errors='replace'))
            record['landing']['title'] = html.unescape(parser.title).strip()
            if parser.meta:
                record['landing']['citation_metadata'] = parser.meta
    except Exception as exc:
        record['landing'] = {'status': 'unavailable', 'error': str(exc)}
    if not source.get('pdf_url'):
        record['pdf'] = {'status': 'not-mirrored', 'reason': source.get('notes', 'Reference link only')}
        return source['id'], record
    path = target_path(source, '.pdf')
    try:
        if path.exists():
            details = inspect_pdf(path.read_bytes())
            expected = (previous or {}).get('pdf', {}).get('sha256')
            if expected and expected != details['sha256']:
                raise ValueError('Existing PDF changed; refusing to replace it')
            record['pdf'] = dict(record.get('pdf', {}), status='held', local_file=path.relative_to(ROOT).as_posix(), **details)
        else:
            payload, final_url, content_type = request(source['pdf_url'])
            details = inspect_pdf(payload)
            path.parent.mkdir(parents=True, exist_ok=True)
            # Exclusive creation protects existing work during concurrent migration.
            with path.open('xb') as stream:
                stream.write(payload)
            record['pdf'] = dict(status='held', local_file=path.relative_to(ROOT).as_posix(),
                                 requested_url=source['pdf_url'], resolved_url=final_url,
                                 content_type=content_type, retrieved_at_utc=record['checked_at_utc'], **details)
    except Exception as exc:
        record['pdf'] = {'status': 'unavailable', 'requested_url': source['pdf_url'], 'error': str(exc)}
    return source['id'], record


def fetch(catalog, ids):
    records = read_json(RETRIEVAL, {})
    selected = [s for s in catalog['sources'] if not ids or s['id'] in ids]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures = [pool.submit(fetch_one, s, records.get(s['id'])) for s in selected]
        for future in concurrent.futures.as_completed(futures):
            key, record = future.result()
            records[key] = record
            write_json(RETRIEVAL, records)
            print(key, record['pdf']['status'], record['landing']['status'], flush=True)


def table_escape(value):
    return str(value).replace('|', '\\|').replace('\n', ' ')


def build(catalog):
    records = read_json(RETRIEVAL, {})
    held = sum(records.get(s['id'], {}).get('pdf', {}).get('status') == 'held' for s in catalog['sources'])
    contents = ['# Research contents', '', 'Generated from [catalog.json](catalog.json) and [retrieval.json](retrieval.json).', '']
    index = ['# 01-research - SIH26119 research library', '',
             'Sources are organized by the mathematical technique, engineering decision or industrial use case they support, following the numbered topic-folder structure of the Hyper-Grey-SIH-26 reference repository.', '',
             f"**{len(catalog['sources'])} sources across {len(catalog['topics'])} topics: {held} PDFs held locally and {len(catalog['sources']) - held} reference-only entries.** Every entry has an original source note with its citation, relevance, scope and retrieval status. Curated on {catalog['curated_on']}.", '',
             '## Index', '', '| Folder | Sources | PDFs held | Supports |', '|---|---:|---:|---|']
    for topic in catalog['topics']:
        sources = [s for s in catalog['sources'] if s['topic'] == topic['folder']]
        n_held = sum(records.get(s['id'], {}).get('pdf', {}).get('status') == 'held' for s in sources)
        index.append(f"| [{topic['folder']}]({topic['folder']}/README.md) | {len(sources)} | {n_held} | {topic['supports']} |")
        lines = [f"# {topic['folder']}", '', f"{topic['title']}", '', '## What this folder supports', '', topic['supports'], '',
                 f"**Problem-statement mapping:** {topic['requirements']} (IDs follow the preserved PS_REQUIREMENTS matrix).", '', '## Where it is used in our work', '']
        for code in topic['code']:
            # The software migration uses 02-software/solver; only link verified paths.
            local = ROOT.parent / '02-software' / 'solver' / code
            lines.append(f"- [{code}](../../02-software/solver/{code})" if local.exists() else f"- `{code}` in the solver tree (migration location not verified).")
        lines += ['', '## Scope note', '', topic['status'], '', f'## Sources ({len(sources)}; {n_held} PDFs held)', '',
                  '| Year | Title | Venue / source | Local copy and note | Original |', '|---|---|---|---|---|']
        contents += [f"## {topic['folder']}", '']
        for source in sources:
            record = records.get(source['id'], {})
            pdf = record.get('pdf', {})
            note_path = target_path(source, '.source.md')
            note_path.parent.mkdir(parents=True, exist_ok=True)
            parts = [f"[note]({note_path.name})"]
            if pdf.get('status') == 'held':
                parts.insert(0, f"[PDF]({Path(pdf['local_file']).name})")
            else:
                parts.append('reference only')
            lines.append('| ' + ' | '.join(table_escape(v) for v in [source['year'], source['title'], source['venue'], ' / '.join(parts), f"[source]({source['url']})"]) + ' |')
            status = 'PDF held locally' if pdf.get('status') == 'held' else 'Reference only; no local full text'
            note = [f"# {source['title']}", '', f"- **Authors / organization:** {source['authors']}", f"- **Citation year:** {source['year']}",
                    f"- **Venue / source:** {source['venue']}", f"- **Type:** {source.get('kind', 'reference')}", f"- **Original:** [source]({source['url']})", f"- **Source ID:** `{source['id']}`", f"- **Storage:** {status}"]
            if source.get('doi'):
                note.append(f"- **DOI:** [{source['doi']}](https://doi.org/{source['doi']})")
            note += ['', '## What this source supports', '', source['support'], '', '## Version and applicability', '', source.get('notes') or topic['status'], '',
                     '## Access and provenance', '', f"Checked: {record.get('checked_at_utc', 'not yet retrieved')}."]
            landing = record.get('landing', {})
            if landing.get('status') == 'retrieved':
                note.append(f"The source URL was retrieved successfully. Resolved location: [source]({landing['resolved_url']}).")
            elif landing:
                note.append(f"The source page could not be retrieved by the collection script: `{landing.get('error', '')}`. Bibliographic selection was checked during web research; this is not a claim of successful scripted retrieval.")
            if pdf.get('status') == 'held':
                note += ['', f"Local file: [PDF]({Path(pdf['local_file']).name}) ({pdf['pages']} pages; {pdf['bytes']:,} bytes).", '',
                         f"Download: [retrieved PDF]({pdf.get('resolved_url', source['pdf_url'])}).", '', f"SHA-256: `{pdf['sha256']}`."]
            elif pdf.get('status') == 'unavailable':
                note += ['', f"A public PDF download was attempted but not stored: `{pdf.get('error', '')}`."]
            note += ['', '## Rights', '', source['rights'], '', 'This note is an original relevance summary, not a copy of the source abstract or full text.', '']
            note_path.write_text('\n'.join(note), encoding='utf-8')
            contents.append(f"- [{source['year']} - {source['title']}]({note_path.relative_to(ROOT).as_posix()}) ({status})")
        lines += ['', '## Reading notes', '']
        lines += [f"- **{s['id']}:** {s['support']}" for s in sources]
        lines += ['', '[Back to the research index](../README.md)', '']
        (ROOT / topic['folder'] / 'README.md').write_text('\n'.join(lines), encoding='utf-8')
        contents.append('')
    index += ['', '## Start here', '',
              'Read [RESEARCH_MAP.md](RESEARCH_MAP.md) for priority reading and open research questions. [_CONTENTS.md](_CONTENTS.md) lists every entry. [references.bib](references.bib) provides portable citations. [CURATION.md](CURATION.md) records the collection checks and access limitations.', '',
              '## Relation to the software problem statement', '',
              'The controlling requirement is SIH26119, the MRPL from-scratch GPU-accelerated optimization solver problem. Its supplied dataset paragraph is truncated; no missing requirement has been invented. The local solver and its dated experiment reports remain the authority on what is implemented and measured.', '',
              'External libraries appear here as papers, documentation, benchmark sources or independent comparison systems. Collecting their literature does not add a solver dependency or claim their algorithms are already implemented.', '',
              '## Sourcing, versions and rights', '',
              'Downloads come from arXiv, author/institutional repositories, publishers and official documentation/report hosts. Public accessibility does not imply a blanket redistribution license. Source notices remain in the unmodified PDFs, and source notes distinguish preprints, technical reports, final publications and living documentation. Books or publisher items selected as citation-only are not mirrored.', '',
              'Filenames use `YYYY-lower-case-hyphenated-title.pdf`; the year is the catalog citation year. For living documentation, it is the access year and the note says so. A preprint may have an earlier date than its final journal citation. Retrieval timestamps, resolved URLs, byte counts, page counts and SHA-256 hashes are in [retrieval.json](retrieval.json).', '',
              '## How to add or maintain a source', '',
              '1. Add one entry to `catalog.json`, under the single topic it primarily supports. Write a concrete relevance sentence and scope/version note.',
              '2. Set `pdf_url` only to a legitimate public full-text location; otherwise retain a reference note. Do not substitute an unrelated PDF when retrieval fails.',
            '3. From `01-research`, run `python tools/library.py fetch --ids SOURCE_ID` to collect it (requires network and `pypdf`). Existing PDFs are never overwritten.',
              '4. Run `python tools/library.py build`, then `python tools/library.py verify` to update and audit the indexes. `verify` is offline.', '',
              'Counts are generated from actual successful PDF retrievals, not planned downloads. The collection is deliberately selected for relevance rather than a fixed number of papers per folder.', '']
    (ROOT / 'README.md').write_text('\n'.join(index), encoding='utf-8')
    (ROOT / '_CONTENTS.md').write_text('\n'.join(contents), encoding='utf-8')
    bib = ['% Curated source citations. See source notes for stored-version differences.', '']
    for source in catalog['sources']:
        author = source['authors'].replace(' et al.', ' and others')
        if ' and others' not in author:
            author = author.replace(', ', ' and ')
        fields = {'title': '{' + source['title'] + '}', 'author': author, 'year': str(source['year']),
                  'howpublished': source['venue'], 'url': source['url'], 'note': source.get('notes', '')}
        if source.get('doi'):
            fields['doi'] = source['doi']
        for key in ('title', 'author', 'howpublished', 'note'):
            fields[key] = re.sub(r'([&%#_])', r'\\\1', fields[key])
        bib += [f"@misc{{{source['id']},"] + [f"  {k} = {{{v}}}," for k, v in fields.items() if v] + ['}', '']
    (ROOT / 'references.bib').write_text('\n'.join(bib), encoding='utf-8')
    print(f"Built {len(catalog['topics'])} topic indexes, {len(catalog['sources'])} notes; {held} PDFs held.")


def verify(catalog):
    records = read_json(RETRIEVAL, {})
    report_path = ROOT / 'VALIDATION.json'
    errors, hashes, ids = [], {}, set()
    held = 0
    expected = set()
    for source in catalog['sources']:
        if source['id'] in ids:
            errors.append('Duplicate source ID: ' + source['id'])
        ids.add(source['id'])
        record = records.get(source['id'], {})
        pdf = record.get('pdf', {})
        if pdf.get('status') == 'held':
            path = ROOT / pdf['local_file']
            expected.add(path.resolve())
            try:
                details = inspect_pdf(path.read_bytes())
                if details['sha256'] != pdf['sha256']:
                    errors.append('Hash mismatch: ' + str(path))
                if details['sha256'] in hashes:
                    errors.append('Duplicate PDF: ' + source['id'] + ' / ' + hashes[details['sha256']])
                hashes[details['sha256']] = source['id']
                held += 1
            except Exception as exc:
                errors.append(str(path) + ': ' + str(exc))
        if not target_path(source, '.source.md').exists():
            errors.append('Missing note: ' + source['id'])
    for path in ROOT.rglob('*.pdf'):
        if path.resolve() not in expected:
            errors.append('Uncatalogued PDF: ' + str(path))
    for path in ROOT.rglob('*.md'):
        for match in re.finditer(r'\]\(([^)]+)\)', path.read_text(encoding='utf-8')):
            target = match.group(1).split('#', 1)[0]
            if not target or '://' in target or target.startswith('mailto:'):
                continue
            linked_path = path.parent / target
            # This report is created below, including on the first verification run.
            if linked_path.resolve() != report_path.resolve() and not linked_path.exists():
                errors.append(f'Broken local link in {path.relative_to(ROOT)}: {target}')
    report = {'checked_at_utc': datetime.now(timezone.utc).isoformat(timespec='seconds'),
              'source_count': len(ids), 'topic_count': len(catalog['topics']), 'pdf_count': held,
              'reference_only_count': len(ids) - held, 'errors': errors,
              'checks': ['PDF parsing and page counts', 'SHA-256 integrity', 'duplicate PDF content', 'catalog coverage', 'local Markdown links']}
    write_json(report_path, report)
    print(json.dumps(report, indent=2))
    return 1 if errors else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['fetch', 'build', 'verify'])
    parser.add_argument('--ids', nargs='*')
    args = parser.parse_args()
    catalog = read_json(CATALOG)
    if args.action == 'fetch':
        fetch(catalog, args.ids)
    elif args.action == 'build':
        build(catalog)
    else:
        return verify(catalog)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
