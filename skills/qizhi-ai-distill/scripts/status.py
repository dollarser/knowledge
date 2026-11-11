#!/usr/bin/env python3
"""Read-only progress report for a manifest/chunks/raw distillation output."""
import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    root = args.output
    chunks = json.loads((root / 'chunks.json').read_text())
    done, candidates, invalid, truncated = [], [], [], []
    for chunk in chunks:
        cid = chunk['chunk_id']
        raw = root / 'raw' / f'{cid}.json'
        if raw.exists():
            try:
                result = json.loads(raw.read_text())
                if not isinstance(result.get('segments'), list) or not result['segments']:
                    raise ValueError('missing segments list')
                if result.get('truncated'):
                    truncated.append(cid)
                else:
                    done.append(chunk)
            except (ValueError, OSError) as exc:
                invalid.append({'chunk': cid, 'error': str(exc)})
        candidate = root / 'candidates' / f'{cid}.json'
        if candidate.exists():
            try:
                json.loads(candidate.read_text())
                candidates.append(cid)
            except (ValueError, OSError) as exc:
                invalid.append({'chunk': cid, 'candidate_error': str(exc)})
    review_path = root / 'review.json'
    review = json.loads(review_path.read_text()) if review_path.exists() else {}
    duration = lambda items: sum(c['core_end'] - c['core_start'] for c in items)
    total, completed = duration(chunks), duration(done)
    print(json.dumps({
        'chunks_completed': len(done), 'chunks_total': len(chunks),
        'audio_completed_seconds': round(completed, 2),
        'audio_total_seconds': round(total, 2),
        'audio_remaining_seconds': round(total - completed, 2),
        'candidates_present': len(candidates),
        'reviewed_chunks': len(set(review.get('reviewed_chunks', {})) & {c['chunk_id'] for c in chunks}),
        'pending_review': [c['chunk_id'] for c in chunks if c['chunk_id'] not in review.get('reviewed_chunks', {})],
        'truncated': truncated, 'invalid': invalid,
        'note': 'Presence/schema checks only; coverage and evidence require review.'
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
