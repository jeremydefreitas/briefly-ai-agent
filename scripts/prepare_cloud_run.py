"""Build/push the image and prepare runtime secrets; never print secret values."""

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parents[1]


def run(args, *, data=None):
    # Capture output so secret payloads never enter logs or command arguments.
    result = subprocess.run(args, cwd=ROOT, input=data, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(f"Command failed: {' '.join(args)}\n{result.stderr}")
    return result.stdout.strip()


def ensure(describe, create):
    result = subprocess.run(describe, cwd=ROOT, capture_output=True, text=True)
    if result.returncode == 0:
        return
    if 'NOT_FOUND' not in result.stderr and 'does not exist' not in result.stderr:
        raise RuntimeError(result.stderr)
    run(create)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', required=True)
    parser.add_argument('--account', required=True)
    parser.add_argument('--region', default='us-west1')
    args = parser.parse_args()
    values = dotenv_values(ROOT / '.env')
    if not (values.get('OPENAI_API_KEY') or '').strip():
        parser.error('Set OPENAI_API_KEY in the ignored .env first.')
    common = ['--project=' + args.project, '--account=' + args.account, '--quiet']

    def cloud(*command, data=None):
        return run(['gcloud', *command, *common], data=data)

    cloud('projects', 'describe', args.project, '--format=value(projectId)')
    billing = json.loads(cloud('billing', 'projects', 'describe', args.project, '--format=json'))
    if not billing.get('billingEnabled'):
        raise RuntimeError('Enable project billing before preparing deployment.')
    print('Enabling the required APIs.', flush=True)
    cloud('services', 'enable', 'run.googleapis.com', 'artifactregistry.googleapis.com',
          'secretmanager.googleapis.com', 'iam.googleapis.com')

    repo = 'assignment-1'
    account_id = 'assignment-1-runtime'
    identity = f'{account_id}@{args.project}.iam.gserviceaccount.com'
    ensure(['gcloud', 'artifacts', 'repositories', 'describe', repo, '--location=' + args.region, *common],
           ['gcloud', 'artifacts', 'repositories', 'create', repo, '--repository-format=docker',
            '--location=' + args.region, *common])
    ensure(['gcloud', 'iam', 'service-accounts', 'describe', identity, *common],
           ['gcloud', 'iam', 'service-accounts', 'create', account_id,
            '--display-name=Assignment 1 runtime', *common])

    secrets = []
    for variable, name in [('OPENAI_API_KEY', 'assignment-1-nim-key'), ('TAVILY_API_KEY', 'assignment-1-tavily-key')]:
        value = (values.get(variable) or '').strip()
        if not value:
            continue
        ensure(['gcloud', 'secrets', 'describe', name, *common],
               ['gcloud', 'secrets', 'create', name, '--replication-policy=automatic', *common])
        version = cloud('secrets', 'versions', 'add', name, '--data-file=-', '--format=value(name)', data=value)
        cloud('secrets', 'add-iam-policy-binding', name, '--member=serviceAccount:' + identity,
              '--role=roles/secretmanager.secretAccessor', '--format=none')
        secrets.append(f'{variable}={name}:{version.rsplit("/", 1)[-1]}')

    registry = f'{args.region}-docker.pkg.dev'
    tag = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
    image = f'{registry}/{args.project}/{repo}/briefly:{tag}'
    print('Building and pushing the Linux AMD64 image.', flush=True)
    cloud('auth', 'configure-docker', registry)
    run(['docker', 'build', '--platform', 'linux/amd64', '-t', image, '.'])
    run(['docker', 'push', image])
    digest = cloud('artifacts', 'docker', 'images', 'describe', image, '--format=value(image_summary.digest)')
    if not digest.startswith('sha256:'):
        raise RuntimeError('Could not resolve the pushed image digest.')
    immutable_image = image.rsplit(':', 1)[0] + '@' + digest
    env = {
        'OPENAI_BASE_URL': values.get('OPENAI_BASE_URL') or 'https://integrate.api.nvidia.com/v1',
        'OPENAI_MODEL': values.get('OPENAI_MODEL') or 'nvidia/nemotron-3-ultra-550b-a55b',
    }
    # JSON is valid YAML for gcloud --env-vars-file; only non-secret settings here.
    directory = ROOT / 'docs' / 'deployment'
    directory.mkdir(parents=True, exist_ok=True)
    env_path = directory / 'environment.json'
    env_path.write_text(json.dumps(env, indent=2) + '\n')
    deploy = ['gcloud', 'run', 'deploy', 'csci599-a1', '--image=' + immutable_image,
              '--region=' + args.region, '--service-account=' + identity,
              '--port=8080', '--cpu=1', '--memory=512Mi', '--min-instances=0',
              '--max-instances=1', '--concurrency=8', '--timeout=600',
              '--execution-environment=gen2', '--cpu-throttling', '--session-affinity',
              '--allow-unauthenticated', '--env-vars-file=docs/deployment/environment.json',
              '--set-secrets=' + ','.join(secrets), *common]
    plan = {'project': args.project, 'region': args.region, 'service': 'csci599-a1',
            'service_account': identity, 'image_tag': image, 'image': immutable_image,
            'secret_references': secrets, 'deploy_command': deploy}
    (directory / 'plan.json').write_text(json.dumps(plan, indent=2) + '\n')
    print('Prepared deployment. Non-secret settings saved to docs/deployment/plan.json.', flush=True)


if __name__ == '__main__':
    main()
