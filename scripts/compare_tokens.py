import sys
import json
from pathlib import Path

# Añadir la ruta al paquete 'app' (backend)
repo_root = Path(__file__).resolve().parents[1]
backend_path = repo_root / 'backend'
import sys
sys.path.insert(0, str(backend_path))

import jwt
from app.config import settings


def decode_no_verify(token):
    return jwt.decode(token, options={"verify_signature": False})


def verify(token, secret, alg):
    try:
        p = jwt.decode(token, secret, algorithms=[alg])
        return True, p
    except Exception as e:
        return False, str(e)


def pretty(obj):
    return json.dumps(obj, indent=2, ensure_ascii=False)


def main():
    if len(sys.argv) < 3:
        print("Uso: python compare_tokens.py <token_registro> <token_login>")
        sys.exit(1)

    token_reg = sys.argv[1].strip()
    token_log = sys.argv[2].strip()

    print("Usando settings.SECRET_KEY (longitud):", len(getattr(settings, 'SECRET_KEY', '') or ''))
    alg = getattr(settings, 'ALGORITHM', 'HS256')
    print("settings.ALGORITHM:", alg)
    print()

    print("=== Decodificar sin verificar ===")
    try:
        print("Registro payload:")
        print(pretty(decode_no_verify(token_reg)))
    except Exception as e:
        print("Error decodificando token_reg sin verificar:", e)
    print()
    try:
        print("Login payload:")
        print(pretty(decode_no_verify(token_log)))
    except Exception as e:
        print("Error decodificando token_log sin verificar:", e)
    print()

    print("=== Verificar firma ===")
    ok_reg, reg_info = verify(token_reg, settings.SECRET_KEY, alg)
    ok_log, log_info = verify(token_log, settings.SECRET_KEY, alg)

    print("Registro verificado?:", ok_reg)
    print("Login verificado?:", ok_log)
    print()
    if ok_reg:
        print("Registro payload verificado:")
        print(pretty(reg_info))
    else:
        print("Registro error verificación:", reg_info)
    print()
    if ok_log:
        print("Login payload verificado:")
        print(pretty(log_info))
    else:
        print("Login error verificación:", log_info)


if __name__ == "__main__":
    main()
