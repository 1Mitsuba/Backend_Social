"""
Actualiza la contraseña de un usuario a "Estudiante1234" (hash con bcrypt) y prueba el login llamando al endpoint.
Imprime los resultados en stdout.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import settings
from supabase import create_client
from app.utils.security import get_password_hash

import json
try:
    import requests
except Exception:
    requests = None

email = "andrea.mamani@univalle.edu.bo"
new_plain = "Estudiante1234"

sb = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE)
print('Conectando a Supabase...')

new_hash = get_password_hash(new_plain)
print('Generando hash y actualizando usuario...')
res = sb.table('usuario').update({'contrasena': new_hash}).eq('correo', email).execute()
print('Update result:', res.data)

# Ahora probar el login
login_url = f'http://127.0.0.1:8000/api/v1/auth/login'
print('Probando login POST', login_url)

if requests:
    try:
        resp = requests.post(login_url, data={'username': email, 'password': new_plain})
        print('HTTP', resp.status_code)
        try:
            print('Response JSON:', json.dumps(resp.json(), indent=2, ensure_ascii=False))
        except Exception:
            print('Response text:', resp.text)
    except Exception as e:
        print('Error al hacer POST:', e)
else:
    # fallback usando urllib
    import urllib.parse, urllib.request
    data = urllib.parse.urlencode({'username': email, 'password': new_plain}).encode()
    req = urllib.request.Request(login_url, data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    try:
        with urllib.request.urlopen(req) as r:
            print('HTTP', r.status)
            body = r.read().decode()
            print('Response:', body)
    except Exception as e:
        print('Error urllib:', e)

print('Hecho.')
