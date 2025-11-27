"""
Script para sincronizar usuarios con rol estudiante/docente
con las tablas estudiante y docente respectivamente.

Esto asegura que cada usuario con rol 'estudiante' tenga su registro
en la tabla 'estudiante', y cada usuario con rol 'docente' tenga su
registro en la tabla 'docente'.
"""

import os
import sys

# Agregar el directorio raíz al path para importar app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import get_supabase_client

# Usar el cliente de supabase de la app (ya configurado)
supabase = get_supabase_client()

def sincronizar_estudiantes():
    """
    Crea registros en la tabla 'estudiante' para todos los usuarios
    con rol 'estudiante' que no tengan ya un registro.
    """
    print("\n🔄 Sincronizando estudiantes...")
    
    # Obtener todos los usuarios con rol 'estudiante'
    response = supabase.table('usuario').select('*').eq('rol', 'estudiante').execute()
    usuarios_estudiantes = response.data
    
    print(f"   Encontrados {len(usuarios_estudiantes)} usuarios con rol 'estudiante'")
    
    # Obtener todos los estudiantes existentes
    response = supabase.table('estudiante').select('ci_est').execute()
    cis_existentes = {est['ci_est'] for est in response.data}
    
    creados = 0
    errores = 0
    
    for usuario in usuarios_estudiantes:
        ci_est = usuario['ci_user']
        
        # Si ya existe en la tabla estudiante, saltar
        if ci_est in cis_existentes:
            continue
        
        try:
            # Crear registro en tabla estudiante
            nuevo_estudiante = {
                'ci_est': ci_est,
                'id_user': usuario['id_user'],
                'carrera': 'Sin especificar',  # Valor por defecto
                'semestre': 1  # Valor por defecto
            }
            
            supabase.table('estudiante').insert(nuevo_estudiante).execute()
            print(f"   ✅ Creado estudiante: {usuario['nombre']} {usuario['apellido']} (CI: {ci_est})")
            creados += 1
            
        except Exception as e:
            print(f"   ❌ Error al crear estudiante {ci_est}: {str(e)}")
            errores += 1
    
    print(f"\n📊 Resultado estudiantes:")
    print(f"   - Creados: {creados}")
    print(f"   - Errores: {errores}")
    print(f"   - Ya existían: {len(cis_existentes)}")

def sincronizar_docentes():
    """
    Crea registros en la tabla 'docente' para todos los usuarios
    con rol 'docente' que no tengan ya un registro.
    """
    print("\n🔄 Sincronizando docentes...")
    
    # Obtener todos los usuarios con rol 'docente'
    response = supabase.table('usuario').select('*').eq('rol', 'docente').execute()
    usuarios_docentes = response.data
    
    print(f"   Encontrados {len(usuarios_docentes)} usuarios con rol 'docente'")
    
    # Obtener todos los docentes existentes
    response = supabase.table('docente').select('ci_doc').execute()
    cis_existentes = {doc['ci_doc'] for doc in response.data}
    
    creados = 0
    errores = 0
    
    for usuario in usuarios_docentes:
        ci_doc = usuario['ci_user']
        
        # Si ya existe en la tabla docente, saltar
        if ci_doc in cis_existentes:
            continue
        
        try:
            # Crear registro en tabla docente
            nuevo_docente = {
                'ci_doc': ci_doc,
                'id_user': usuario['id_user'],
                'especialidad_doc': 'Sin especificar'  # Valor por defecto
            }
            
            supabase.table('docente').insert(nuevo_docente).execute()
            print(f"   ✅ Creado docente: {usuario['nombre']} {usuario['apellido']} (CI: {ci_doc})")
            creados += 1
            
        except Exception as e:
            print(f"   ❌ Error al crear docente {ci_doc}: {str(e)}")
            errores += 1
    
    print(f"\n📊 Resultado docentes:")
    print(f"   - Creados: {creados}")
    print(f"   - Errores: {errores}")
    print(f"   - Ya existían: {len(cis_existentes)}")

def listar_inconsistencias():
    """
    Lista usuarios que tienen rol estudiante/docente pero no tienen
    registro en la tabla correspondiente.
    """
    print("\n🔍 Buscando inconsistencias...")
    
    # Estudiantes sin registro
    response = supabase.table('usuario').select('ci_user, nombre, apellido').eq('rol', 'estudiante').execute()
    usuarios_est = {u['ci_user']: u for u in response.data}
    
    response = supabase.table('estudiante').select('ci_est').execute()
    cis_est = {e['ci_est'] for e in response.data}
    
    faltantes_est = [usuarios_est[ci] for ci in usuarios_est if ci not in cis_est]
    
    if faltantes_est:
        print(f"\n⚠️  {len(faltantes_est)} usuarios con rol 'estudiante' sin registro en tabla estudiante:")
        for u in faltantes_est:
            print(f"   - {u['nombre']} {u['apellido']} (CI: {u['ci_user']})")
    else:
        print("   ✅ Todos los estudiantes están sincronizados")
    
    # Docentes sin registro
    response = supabase.table('usuario').select('ci_user, nombre, apellido').eq('rol', 'docente').execute()
    usuarios_doc = {u['ci_user']: u for u in response.data}
    
    response = supabase.table('docente').select('ci_doc').execute()
    cis_doc = {d['ci_doc'] for d in response.data}
    
    faltantes_doc = [usuarios_doc[ci] for ci in usuarios_doc if ci not in cis_doc]
    
    if faltantes_doc:
        print(f"\n⚠️  {len(faltantes_doc)} usuarios con rol 'docente' sin registro en tabla docente:")
        for u in faltantes_doc:
            print(f"   - {u['nombre']} {u['apellido']} (CI: {u['ci_user']})")
    else:
        print("   ✅ Todos los docentes están sincronizados")

if __name__ == '__main__':
    print("=" * 60)
    print("  🔧 SINCRONIZACIÓN DE USUARIOS CON ESTUDIANTES/DOCENTES")
    print("=" * 60)
    
    try:
        # Primero listar inconsistencias
        listar_inconsistencias()
        
        # Pedir confirmación
        print("\n" + "=" * 60)
        respuesta = input("\n¿Deseas sincronizar ahora? (s/n): ").strip().lower()
        
        if respuesta == 's':
            sincronizar_estudiantes()
            sincronizar_docentes()
            print("\n✅ Sincronización completada")
        else:
            print("\n❌ Sincronización cancelada")
    
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
    
    print("\n" + "=" * 60)
