"""Record live deployed behavior and operational events without exposing keys."""

import argparse
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

import httpx2 as httpx

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', help='Defaults to the recorded deployment URL.')
    parser.add_argument('--output', type=Path, default=ROOT / 'tmp/cloud-checks.json',
                        help='Evidence path; defaults to ignored tmp/ to preserve prior records.')
    args = parser.parse_args()
    url = args.url or json.loads((ROOT / 'docs/deployment/result.json').read_text())['url']
    marker = uuid.uuid4().hex[:10]
    output = args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    report = {'timestamp': datetime.now(timezone.utc).isoformat(), 'url': url,
              'method': 'Public HTTP; live NVIDIA inference and actual MCP servers; no mocked responses.',
              'checks': []}

    def save():
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')

    with httpx.Client(base_url=url, timeout=600) as client:
        report['server_status'] = client.get('/mcp/status').json()
        save()

        def query(name, text, session):
            start = datetime.now(timezone.utc)
            events = []
            with client.stream('POST', '/chat/stream', json={'query': text, 'session_id': session}) as response:
                for line in response.iter_lines():
                    if line.strip():
                        event = json.loads(line)
                        if event.get('type') != 'heartbeat':
                            events.append(event)
                            if event.get('type') in {'tool_start', 'tool_end', 'tool_error', 'model_retry'}:
                                print(name, event.get('message'), flush=True)
            answer = next((event.get('response') for event in events if event.get('type') == 'response'), None)
            record = {'name': name, 'query': text, 'session_id': session,
                      'started_at': start.isoformat(), 'http_status': response.status_code,
                      'elapsed_seconds': (datetime.now(timezone.utc) - start).total_seconds(),
                      'events': events, 'response': answer, 'assessment': 'pending review'}
            report['checks'].append(record)
            save()
            print(name, 'response received' if answer else 'FAILED; see evidence', flush=True)

        memory = f'final-memory-{marker}'
        query('memory-store', f'Remember that my project codename is Cedar-{marker}. Acknowledge briefly. No tools needed.', memory)
        query('memory-recall', 'What is my project codename? Answer briefly.', memory)
        query('memory-isolation', 'What is my project codename? If I have not told you, say that you do not know.', f'final-isolated-{marker}')
        query('no-tool', 'What is 17 times 19? Answer directly with only the number.', f'final-math-{marker}')
        query('weather', 'What is the weather in Los Angeles, California today? Resolve the location, then retrieve the weather. Include Fahrenheit units and the local date/time. Keep it under 100 words.', f'final-weather-{marker}')
        path = f'cloud-mcp-summary-{marker}.txt'
        workflow = f'final-research-{marker}'
        query('search-and-save', f'Search for official Model Context Protocol documentation, then save a summary of at most 120 words with source URLs to {path}. Use at most two searches. Prefer modelcontextprotocol.io and github.com/modelcontextprotocol. Label any third-party mirrors as unofficial; do not group them under official sources. Do not invent links or say a page was read unless a tool read it. Confirm the filename only after the save succeeds.', workflow)
        query('read-saved-summary', f'Read {path} and return its exact contents so I can inspect the summary and source labels.', workflow)
        recovery = f'final-recovery-{marker}'
        query('missing-file', f'Read missing-{marker}.txt with the filesystem tool. Do not create it. If it does not exist, explain the failure.', recovery)
        query('recovery', 'Now read notes.txt and quote its first line.', recovery)
    print('Evidence: ' + str(output), flush=True)


if __name__ == '__main__':
    main()
