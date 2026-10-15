"""Deploy the prepared image and record its live URL and revision."""

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', required=True)
    args = parser.parse_args()
    directory = ROOT / 'docs' / 'deployment'
    plan = json.loads((directory / 'plan.json').read_text())
    if plan['project'] != args.project:
        parser.error('The prepared plan belongs to a different project.')
    subprocess.run(plan['deploy_command'], cwd=ROOT, check=True)
    account = next(arg for arg in plan['deploy_command'] if arg.startswith('--account='))
    output = subprocess.check_output([
        'gcloud', 'run', 'services', 'describe', plan['service'],
        '--project=' + args.project, '--region=' + plan['region'], account, '--format=json',
    ], cwd=ROOT, text=True)
    service = json.loads(output)
    status = service['status']
    record = {
        'verified_at': datetime.now(timezone.utc).isoformat(),
        'project': args.project, 'region': plan['region'], 'service': plan['service'],
        'image': plan['image'], 'url': status['url'],
        'revision': status['latestReadyRevisionName'], 'conditions': status['conditions'],
    }
    (directory / 'result.json').write_text(json.dumps(record, indent=2) + '\n')
    print('Live service: ' + record['url'])


if __name__ == '__main__':
    main()
