#!/usr/bin/env python3
"""Read-only local publication audit. Does not certify semantic completeness."""
import argparse
import hashlib
import json
import re
from pathlib import Path


def load(path):
    return json.loads(path.read_text())


def first_existing(paths):
    return next((p for p in paths if p.exists()), None)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project', type=Path)
    args = parser.parse_args()
    root = args.project.resolve()
    records = list((root / 'outputs').glob('**/published.json'))
    result = []
    for article in load(root / 'knowledge/articles.json'):
        slug = article['slug']
        content = (root / 'knowledge/content' / (slug + '.md')).read_text()
        digest = hashlib.sha256(content.encode()).hexdigest()
        sessions = set()
        for record in records:
            metadata = load(record)
            # Legacy v2 uses document_url; shared public_checks may list other
            # sessions and must not be treated as an ownership mapping.
            if '/notes/' + slug + '/' not in metadata.get('url', metadata.get('document_url', '')):
                continue
            parent = record.parent
            while parent != root and not (parent / 'chunks.json').exists():
                parent = parent.parent
            if (parent / 'chunks.json').exists():
                sessions.add(parent)
        row = {'slug': slug, 'title': article['title'],
               'characters': len(content),
               'chapters': len(re.findall(r'^## ', content, re.M)),
               'article_sha256': digest, 'warnings': [],
               'stale_source_appendix_promise': '来源放在文末' in content}
        if len(sessions) != 1:
            row['warnings'].append('session_mapping_missing_or_ambiguous')
            row['session_candidates'] = [str(p) for p in sorted(sessions)]
        else:
            p = sessions.pop()
            planned = {c['chunk_id'] for c in load(p / 'chunks.json')}
            reviewed = set(load(p / 'review.json')['reviewed_chunks'])
            row.update({'output': str(p), 'planned': len(planned),
                        'reviewed': len(reviewed), 'review_set_exact': planned == reviewed})
            if planned != reviewed:
                row['warnings'].append('review_plan_difference')
            for key, candidates in {
                'omission_audit': [p / 'omission-audit.json', p / 'knowledge-v3/omission-audit.json'],
                'tool_ledger': [p / 'tool-project-ledger.json', p / 'tool-ledger.json',
                                p / 'knowledge-v3/tool-project-ledger.json'],
            }.items():
                found = first_existing(candidates)
                row[key] = str(found) if found else None
                if found is None:
                    row['warnings'].append('missing_' + key)
            if row['omission_audit']:
                audit = load(Path(row['omission_audit']))
                hashes = {k: audit[k] for k in ['article_sha256', 'body_sha256', 'document_sha256'] if k in audit}
                row['audit_recorded_hashes'] = hashes
                row['audit_matches_current_article'] = digest in hashes.values()
                row['audit_state'] = audit.get('state', audit.get('status'))
                if not row['audit_matches_current_article']:
                    row['warnings'].append('audit_not_bound_to_current_article')
        if row['stale_source_appendix_promise']:
            row['warnings'].append('stale_source_appendix_promise')
        result.append(row)
    print(json.dumps({'scope': 'local published bodies, review sets and artifact metadata; '
                      'not full raw rereading, audio listening, external tool verification or zero-omission certification',
                      'articles': result}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
