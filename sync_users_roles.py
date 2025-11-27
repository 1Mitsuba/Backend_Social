"""
Script para sincronizar usuarios con sus tablas correspondientes (estudiante/docente)
Crea registros faltantes basándose en el rol del usuario
"""
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE")

# Crear cliente de Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

def sync_estudiantes():
    """Sincroniza usuarios con rol estudiante"""
    print("\n🔍 Buscando usuarios con rol 'estudiante'...")
    
    # Obtener todos los usuarios con rol estudiante
    usuarios = supabase.table("usuario").select("*").eq("rol", "estudiante").execute()
    
    if not usuarios.data:
        print("   ℹ️  No hay usuarios con rol estudiante")
        return
    
    print(f"   ✅ Encontrados {len(usuarios.data)} usuarios con rol estudiante")
    
    # Obtener todos los estudiantes existentes
    estudiantes = supabase.table("estudiante").select("id_user").execute()
    estudiantes_ids = [e["id_user"] for e in estudiantes.data]
    
    # Encontrar usuarios sin registro de estudiante
    usuarios_sin_estudiante = [u for u in usuarios.data if u["id_user"] not in estudiantes_ids]
    
    if not usuarios_sin_estudiante:
        print("   ✅ Todos los usuarios estudiantes ya tienen su registro")
        return
    
    print(f"\n📝 Creando {len(usuarios_sin_estudiante)} registros de estudiante faltantes...")
    
    created_count = 0
    for idx, usuario in enumerate(usuarios_sin_estudiante, start=1):
        try:
            # Generar CI temporal corto (máximo 20 caracteres)
            # Usar las últimas 8 caracteres del UUID
            user_suffix = usuario['id_user'][-8:]
            ci_temp = f"EST{user_suffix}"
            
            nuevo_estudiante = {
                "ci_est": ci_temp,
                "id_user": usuario["id_user"],
                "carrera": "Sin especificar",
                "semestre": 1,
                "id_grupo": None
            }
            
            result = supabase.table("estudiante").insert(nuevo_estudiante).execute()
            
            if result.data:
                created_count += 1
                print(f"   ✅ Estudiante creado: {usuario['nombre']} {usuario['apellido']} (CI: {ci_temp})")
            
        except Exception as e:
            print(f"   ❌ Error creando estudiante para {usuario['nombre']}: {str(e)}")
    
    print(f"\n✨ Se crearon {created_count} registros de estudiante")

def sync_docentes():
    """Sincroniza usuarios con rol docente"""
    print("\n🔍 Buscando usuarios con rol 'docente'...")
    
    # Obtener todos los usuarios con rol docente
    usuarios = supabase.table("usuario").select("*").eq("rol", "docente").execute()
    
    if not usuarios.data:
        print("   ℹ️  No hay usuarios con rol docente")
        return
    
    print(f"   ✅ Encontrados {len(usuarios.data)} usuarios con rol docente")
    
    # Obtener todos los docentes existentes
    docentes = supabase.table("docente").select("id_user").execute()
    docentes_ids = [d["id_user"] for d in docentes.data]
    
    # Encontrar usuarios sin registro de docente
    usuarios_sin_docente = [u for u in usuarios.data if u["id_user"] not in docentes_ids]
    
    if not usuarios_sin_docente:
        print("   ✅ Todos los usuarios docentes ya tienen su registro")
        return
    
    print(f"\n📝 Creando {len(usuarios_sin_docente)} registros de docente faltantes...")
    
    created_count = 0
    for idx, usuario in enumerate(usuarios_sin_docente, start=1):
        try:
            # Generar CI temporal corto (máximo 20 caracteres)
            # Usar las últimas 8 caracteres del UUID
            user_suffix = usuario['id_user'][-8:]
            ci_temp = f"DOC{user_suffix}"
            
            nuevo_docente = {
                "ci_doc": ci_temp,
                "id_user": usuario["id_user"],
                "especialidad_doc": "Sin especificar"
            }
            
            result = supabase.table("docente").insert(nuevo_docente).execute()
            
            if result.data:
                created_count += 1
                print(f"   ✅ Docente creado: {usuario['nombre']} {usuario['apellido']} (CI: {ci_temp})")
            
        except Exception as e:
            print(f"   ❌ Error creando docente para {usuario['nombre']}: {str(e)}")
    
    print(f"\n✨ Se crearon {created_count} registros de docente")

def main():
    print("=" * 60)
    print("🔄 SINCRONIZACIÓN DE USUARIOS CON ROLES")
    print("=" * 60)
    
    try:
        # Sincronizar estudiantes
        sync_estudiantes()
        
        # Sincronizar docentes
        sync_docentes()
        
        print("\n" + "=" * 60)
        print("✅ Sincronización completada exitosamente")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error durante la sincronización: {str(e)}")

if __name__ == "__main__":
    main()
