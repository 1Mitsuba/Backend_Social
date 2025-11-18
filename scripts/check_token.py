from app.config import settings
import jwt, datetime

print('settings.SECRET_KEY =', settings.SECRET_KEY)
print('settings.ALGORITHM =', getattr(settings, 'ALGORITHM', None))
print('settings.DEBUG =', getattr(settings, 'DEBUG', None))

# Token a verificar (pega aquí tu access_token)
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJiNjRmMDgzOC01MmU2LTRmYWQtODlmZC0zYmZmNDllZWU0ZDciLCJyb2wiOiJhZG1pbmlzdHJhZG9yIiwiZXhwIjoxNzYzNDI0NzI3LCJ0eXBlIjoiYWNjZXNzIn0.zZ7EM4UgVTNiLqQ_fD7I_bUEzt9EwxWV-buH2eKqaHc"

print('\nDecodificando payload (sin verificar firma):')
try:
    payload = jwt.decode(token, options={'verify_signature': False})
    print(payload)
    if 'exp' in payload:
        print('exp (unix):', payload['exp'])
        print('exp (UTC):', datetime.datetime.utcfromtimestamp(payload['exp']))
except Exception as e:
    print('Error decodificando sin verificar:', e)

print('\nVerificando firma con settings.SECRET_KEY:')
try:
    verified = jwt.decode(token, settings.SECRET_KEY, algorithms=[getattr(settings, 'ALGORITHM', 'HS256')])
    print('Verificado OK. payload:', verified)
except Exception as e:
    print('Verificación falló:', e)
