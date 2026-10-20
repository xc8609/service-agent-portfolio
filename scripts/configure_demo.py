"""Create local-only credentials without overwriting existing settings or printing secrets."""
from pathlib import Path
import os
import secrets

root=Path(__file__).resolve().parents[1]
path=root/'.env'
fd=os.open(path,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
with os.fdopen(fd,'w') as f:
    f.write('BANK_ADMIN_PASSWORD='+secrets.token_urlsafe(32)+'\n')
    f.write('BANK_APP_PASSWORD='+secrets.token_urlsafe(32)+'\n')
print('Created .env for the local disposable demo. Keep it untracked.')
