"""
Lista los primeros usuarios y detecta el esquema (prefijo) del campo `contrasena`.
No imprime contraseñas completas, sólo fragmentos y una etiqueta del esquema.
"""
import sys
import os
from pathlib import Path

# Asegurar que el directorio padre (donde está el paquete `app`) esté en sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import settings
from supabase import create_client
from textwrap import shorten

def detect_scheme(h: str) -> str:
    if not h:
        return 'empty'
    if h.startswith('$2'):
        return 'bcrypt'
    if h.startswith('pbkdf2_') or h.startswith('pbkdf2$'):
        return 'pbkdf2'
    if 'argon2' in h:
        return 'argon2'
    if h.startswith('$argon2'):
        return 'argon2'
    # common unix crypt markers
    if h.startswith('$1$'):
        return 'md5crypt'
    if h.startswith('$5$'):
        return 'sha256-crypt'
    if h.startswith('$6$'):
        return 'sha512-crypt'
    # Django style: 'pbkdf2_sha256$...' or 'bcrypt_sha256$...'
    if h.startswith('pbkdf2_sha256$'):
        return 'django_pbkdf2_sha256'
    # fallback: try to detect presence of $ separators
    if h.startswith('$'):
        parts = h.split('$')
        if len(parts) > 2:
            return f'unknown($...):{parts[1]}'
    return 'unknown'


def main():
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE)
    try:
        res = supabase.table('usuario').select('id_user, correo, contrasena').limit(100).execute()
    except Exception as e:
        print('ERROR al consultar Supabase:', e)
        return

    data = res.data or []
    if not data:
        print('No se encontraron usuarios (tabla vacía o no hay permisos).')
        return

    print(f'Mostrando {len(data)} usuarios (id, correo, scheme, hash-fragment)')
    for u in data:
        hid = u.get('id_user')
        correo = u.get('correo')
        h = u.get('contrasena') or ''
        scheme = detect_scheme(h)
        print(hid, correo, scheme, shorten(h, width=80, placeholder='...'))


if __name__ == '__main__':
    main()
