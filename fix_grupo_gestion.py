"""
Script para hacer gestion_grupo opcional en la tabla Grupo
"""
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

# Configuración de Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")

print("🔧 Iniciando modificación de tabla Grupo...")
print(f"📡 Conectando a: {SUPABASE_URL}")

# Crear cliente de Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# SQL para hacer gestion_grupo nullable
sql_query = """
ALTER TABLE grupo 
ALTER COLUMN gestion_grupo DROP NOT NULL;
"""

try:
    print("\n📝 Ejecutando SQL para hacer gestion_grupo opcional...")
    result = supabase.rpc('exec_sql', {'query': sql_query}).execute()
    print("✅ Tabla Grupo modificada exitosamente")
    print("   - gestion_grupo ahora es opcional (nullable)")
except Exception as e:
    print(f"⚠️  Error al ejecutar SQL directamente: {e}")
    print("\n💡 Alternativa: Crear grupo de prueba con gestion_grupo null")
    
    try:
        # Intentar crear un grupo de prueba
        test_grupo = {
            "nombre_grupo": "TEST_GRUPO_TEMPORAL",
            "gestion_grupo": None
        }
        
        result = supabase.table("grupo").insert(test_grupo).execute()
        
        if result.data:
            print("✅ Grupo de prueba creado exitosamente con gestion_grupo NULL")
            # Eliminar el grupo de prueba
            supabase.table("grupo").delete().eq("nombre_grupo", "TEST_GRUPO_TEMPORAL").execute()
            print("   (Grupo de prueba eliminado)")
        
    except Exception as e2:
        print(f"❌ No se pudo crear grupo con gestion_grupo NULL")
        print(f"   Error: {e2}")
        print("\n🔨 Necesitamos modificar la tabla manualmente en Supabase...")
        print("\n📋 Ejecuta este SQL en el Editor SQL de Supabase:")
        print("=" * 60)
        print(sql_query)
        print("=" * 60)

print("\n✨ Script completado")
