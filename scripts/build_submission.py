"""Build the source archive from an allowlist and reject embedded credentials."""

import hashlib
import json
import re
import shutil
import zipfile
from pathlib import Path

from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parents[1]


def main():
    names = [
        'README.md', 'PROCESS_LOG.md', 'prompts.md', 'AGENTS.md',
        'main.py', 'agent_client.py', 'mcp_client.py', 'activity.py',
        'Dockerfile', '.dockerignore', '.gitignore', '.env.example', 'deploy.sh',
        'requirements.txt', 'requirements.in', 'package.json', 'package-lock.json',
        'mcp_servers.json', 'data/notes.txt',
    ]
    for directory in ('scripts', 'tests', 'static', 'docs'):
        names.extend(str(path.relative_to(ROOT)) for path in (ROOT / directory).rglob('*')
                     if path.is_file() and path.suffix in {'.py', '.cjs', '.js', '.html', '.css', '.md', '.json', '.svg', '.png', '.mmd'})
    files = {}
    values = dotenv_values(ROOT / '.env')
    secrets = [value.encode() for key, value in values.items()
               if value and len(value) >= 8 and any(word in key for word in ('KEY', 'TOKEN', 'SECRET', 'PASSWORD'))]
    credential_pattern = re.compile(rb'(?:nvapi-[A-Za-z0-9_-]{20,}|sk-[A-Za-z0-9_-]{30,})')
    for name in sorted(set(names)):
        path = ROOT / name
        if path.is_symlink():
            raise RuntimeError('Symlinks are not included in the source submission.')
        content = path.read_bytes()
        if any(secret in content for secret in secrets) or credential_pattern.search(content):
            raise RuntimeError(f'Possible credential found in {name}; archive was not written.')
        files[name] = content

    process_log = files['PROCESS_LOG.md'].decode()
    narrative = process_log.split('## Development narrative\n', 1)[1].split('\n## ', 1)[0]
    word_count = len(narrative.split())
    if not 200 <= word_count <= 300:
        raise RuntimeError(f'Development narrative must be 200–300 words; found {word_count}.')
    reflection = process_log.split('## What I learned\n', 1)[1].split('\n## ', 1)[0]
    if not reflection.strip():
        raise RuntimeError('The personal learning reflection is missing.')

    directory = ROOT / 'dist'
    directory.mkdir(exist_ok=True)
    output = directory / 'assignment-1-source.zip'
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name in files:
            archive.write(ROOT / name, name)
    with zipfile.ZipFile(output) as archive:
        if archive.testzip() is not None:
            raise RuntimeError('Archive integrity check failed.')
        assert set(archive.namelist()) == set(files)
        assert all(not any(part in {'.env', '.venv', 'node_modules', 'tmp', '__pycache__', '.git'}
                           for part in Path(name).parts) for name in archive.namelist())
    deployment = json.loads((ROOT / 'docs/deployment/result.json').read_text())
    (directory / 'live-url.txt').write_text(deployment['url'] + '\n')
    shutil.copyfile(ROOT / 'PROCESS_LOG.md', directory / 'PROCESS_LOG.md')
    shutil.copyfile(ROOT / 'README.md', directory / 'README.md')
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    (directory / 'assignment-1-source.zip.sha256').write_text(digest + '  assignment-1-source.zip\n')
    print(f'Created {output.relative_to(ROOT)}: {len(files)} files, {output.stat().st_size} bytes.')
    print('Integrity, allowlist, and credential checks passed.')
    print('SHA-256: ' + digest)
    print(f'Development narrative: {word_count} words; existing personal reflection included.')


if __name__ == '__main__':
    main()
