"""
Script simple para sincronizar estudiantes via API del backend
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# Token de admin (debes obtenerlo del login)
print("=" * 60)
print("  🔧 SINCRONIZACIÓN VIA API")
print("=" * 60)
print("\n1. Primero, ingresa el token de administrador")
print("   (Puedes obtenerlo desde el navegador en localStorage)")
print()

token = input("Token de administrador: ").strip()

if not token:
    print("❌ Token requerido")
    exit(1)

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

try:
    # Obtener todos los usuarios
    print("\n🔍 Obteniendo usuarios...")
    response = requests.get(f"{BASE_URL}/usuarios", headers=headers)
    response.raise_for_status()
    usuarios = response.json()
    
    print(f"   Encontrados {len(usuarios)} usuarios")
    
    # Obtener estudiantes existentes
    print("\n🔍 Obteniendo estudiantes existentes...")
    response = requests.get(f"{BASE_URL}/estudiantes", headers=headers)
    response.raise_for_status()
    estudiantes = response.json()
    cis_estudiantes = {e['ci_est'] for e in estudiantes}
    
    print(f"   Encontrados {len(estudiantes)} estudiantes")
    
    # Obtener docentes existentes
    print("\n🔍 Obteniendo docentes existentes...")
    response = requests.get(f"{BASE_URL}/docentes", headers=headers)
    response.raise_for_status()
    docentes = response.json()
    cis_docentes = {d['ci_doc'] for d in docentes}
    
    print(f"   Encontrados {len(docentes)} docentes")
    
    # Buscar inconsistencias
    usuarios_estudiantes = [u for u in usuarios if u['rol'] == 'estudiante']
    usuarios_docentes = [u for u in usuarios if u['rol'] == 'docente']
    
    faltantes_estudiantes = [u for u in usuarios_estudiantes if u['ci_user'] not in cis_estudiantes]
    faltantes_docentes = [u for u in usuarios_docentes if u['ci_user'] not in cis_docentes]
    
    if faltantes_estudiantes:
        print(f"\n⚠️  {len(faltantes_estudiantes)} usuarios 'estudiante' sin registro:")
        for u in faltantes_estudiantes:
            print(f"   - {u['nombre']} {u['apellido']} (CI: {u['ci_user']})")
    else:
        print("\n✅ Todos los estudiantes están sincronizados")
    
    if faltantes_docentes:
        print(f"\n⚠️  {len(faltantes_docentes)} usuarios 'docente' sin registro:")
        for u in faltantes_docentes:
            print(f"   - {u['nombre']} {u['apellido']} (CI: {u['ci_user']})")
    else:
        print("\n✅ Todos los docentes están sincronizados")
    
    if not faltantes_estudiantes and not faltantes_docentes:
        print("\n🎉 Todo está sincronizado correctamente")
        exit(0)
    
    # Pedir confirmación
    print("\n" + "=" * 60)
    respuesta = input("\n¿Deseas crear los registros faltantes? (s/n): ").strip().lower()
    
    if respuesta != 's':
        print("\n❌ Sincronización cancelada")
        exit(0)
    
    # Crear estudiantes
    creados_est = 0
    errores_est = 0
    
    for usuario in faltantes_estudiantes:
        try:
            data = {
                "ci_est": usuario['ci_user'],
                "carrera": "Sin especificar",
                "semestre": 1
            }
            response = requests.post(
                f"{BASE_URL}/estudiantes",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            print(f"   ✅ Estudiante creado: {usuario['nombre']} {usuario['apellido']}")
            creados_est += 1
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            errores_est += 1
    
    # Crear docentes
    creados_doc = 0
    errores_doc = 0
    
    for usuario in faltantes_docentes:
        try:
            data = {
                "ci_doc": usuario['ci_user'],
                "especialidad_doc": "Sin especificar"
            }
            response = requests.post(
                f"{BASE_URL}/docentes",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            print(f"   ✅ Docente creado: {usuario['nombre']} {usuario['apellido']}")
            creados_doc += 1
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            errores_doc += 1
    
    print(f"\n📊 Resultado:")
    print(f"   Estudiantes creados: {creados_est}")
    print(f"   Estudiantes con error: {errores_est}")
    print(f"   Docentes creados: {creados_doc}")
    print(f"   Docentes con error: {errores_doc}")
    
    print("\n✅ Sincronización completada")

except requests.exceptions.HTTPError as e:
    if e.response.status_code == 401:
        print("\n❌ Token inválido o expirado")
    else:
        print(f"\n❌ Error HTTP: {e}")
except Exception as e:
    print(f"\n❌ Error: {str(e)}")

print("\n" + "=" * 60)
