from pathlib import Path
import sys
# asegurar que el paquete 'app' (dentro de backend) esté en sys.path
repo_root = Path(__file__).resolve().parents[1]
backend_path = repo_root / 'backend'
sys.path.insert(0, str(backend_path))

from jose import jwt
from app.config import settings
import datetime

# Tokens a comparar (modifica si quieres otros)
token_reg = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJiNjRmMDgzOC01MmU2LTRmYWQtODlmZC0zYmZmNDllZWU0ZDciLCJyb2wiOiJhZG1pbmlzdHJhZG9yIiwiZXhwIjoxNzYzNDIzNTU0LCJ0eXBlIjoiYWNjZXNzIn0.Yu-zuIjY00AwEQDEFdn0JNRsV_GJ4af0_0p7BhqQqlg'
token_log = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJiNjRmMDgzOC01MmU2LTRmYWQtODlmZC0zYmZmNDllZWU0ZDciLCJyb2wiOiJhZG1pbmlzdHJhZG9yIiwiZXhwIjoxNzYzNDI0NzI3LCJ0eXBlIjoiYWNjZXNzIn0.zZ7EM4UgVTNiLqQ_fD7I_bUEzt9EwxWV-buH2eKqaHc'

print('Using settings.SECRET_KEY length:', len(getattr(settings,'SECRET_KEY','') or ''))
print('ALGORITHM:', getattr(settings,'ALGORITHM','HS256'))
print('')

def decode_no_verify(t):
    try:
        p = jwt.decode(t, options={"verify_signature": False})
        return p
    except Exception as e:
        return f'error: {e}'

def verify(t):
    try:
        p = jwt.decode(t, settings.SECRET_KEY, algorithms=[getattr(settings,'ALGORITHM','HS256')])
        return True, p
    except Exception as e:
        return False, str(e)

for name, t in [('registro', token_reg), ('login', token_log)]:
    print('-----', name, '-----')
    nover = decode_no_verify(t)
    print('payload (no verify):', nover)
    ok, info = verify(t)
    print('verified?:', ok)
    print('verify result:', info)
    if isinstance(nover, dict) and 'exp' in nover:
        exp = nover['exp']
        try:
            print('exp ->', datetime.datetime.utcfromtimestamp(exp))
        except Exception:
            print('exp value:', exp)
    print('')
