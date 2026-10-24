"""Offline publication hygiene and relative Markdown link checks; not a security certification."""
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
BLOCKED_PARTS = {'.venv', '__pycache__', 'node_modules', '.pytest_cache', 'raw', 'processed'}
REVIEWED_SCREENSHOTS = {
    'projects/investment-research/docs/images/workbench-comparison.png',
}
SECRET_PATTERNS = [
    re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    re.compile(r'gh[pousr]_[A-Za-z0-9]{24,}'),
    re.compile(r'github_pat_[A-Za-z0-9_]{30,}'),
    re.compile(r'AKIA[0-9A-Z]{16}'),
    re.compile(r'(?<![A-Za-z0-9_])sk-(?:proj-|ant-)?[A-Za-z0-9_-]{24,}'),
]

def main():
    names = subprocess.check_output(['git', 'ls-files', '--cached', '--others', '--exclude-standard'], cwd=ROOT, text=True).splitlines()
    failures = []
    link_count = 0
    for name in sorted(set(names)):
        p = ROOT / name
        if p.is_symlink():
            failures.append((name, 'symlink not allowed in initial public export')); continue
        if not p.is_file(): continue
        if BLOCKED_PARTS.intersection(p.relative_to(ROOT).parts) or (p.name.startswith('.env') and p.name != '.env.example'):
            failures.append((name, 'excluded file or directory'))
        if p.suffix in {'.db', '.duckdb', '.sqlite', '.pem', '.key', '.twbx'}:
            failures.append((name, 'database, key or packaged data file'))
        if p.stat().st_size > 2_000_000:
            failures.append((name, 'large file requires explicit publication review'))
        # Reviewed product screenshots: synthetic bank data or attributed public facts.
        if p.suffix == '.png' and (p.parent == ROOT / 'docs/images' or name in REVIEWED_SCREENSHOTS):
            if p.stat().st_size > 400_000:
                failures.append((name, 'screenshot larger than 400 KB'))
            continue
        try: content = p.read_text()
        except UnicodeDecodeError:
            failures.append((name, 'unexpected binary file')); continue
        if any(pattern.search(content) for pattern in SECRET_PATTERNS):
            failures.append((name, 'possible credential/key; inspect locally'))
        if '/' + 'Users/' in content or '/' + 'private/tmp/' in content:
            failures.append((name, 'machine-specific path'))
        if p.suffix != '.md': continue
        for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)', content):
            if target.startswith(('https:', 'http:', 'mailto:', '#')): continue
            target = unquote(target.split('#')[0]).strip('<>')
            if not target: continue
            resolved = (p.parent / target).resolve()
            if not resolved.is_relative_to(ROOT) or not resolved.exists():
                failures.append((name, 'broken/outside local link: ' + target))
            link_count += 1
    if failures:
        for file, reason in failures: print(file + ': ' + reason)
        raise SystemExit(1)
    print(f'PASS: {len(set(names))} public files; {link_count} relative Markdown links; no detected publication exclusions. Pattern checks are not a security audit.')

if __name__ == '__main__': main()
