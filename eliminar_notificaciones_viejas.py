"""
Script para eliminar notificaciones antiguas de carpooling sin id_referencia
"""
from supabase import create_client
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Crear cliente de Supabase
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

try:
    # Obtener todas las notificaciones de tipo solicitud_ruta
    notificaciones = supabase.table("notificacion")\
        .select("*")\
        .eq("tipo", "solicitud_ruta")\
        .execute()
    
    print(f"📬 Total de notificaciones de carpooling: {len(notificaciones.data)}")
    
    # Filtrar las que tienen id_referencia nulo
    ids_eliminar = []
    for notif in notificaciones.data:
        if notif.get("id_referencia") is None or notif.get("id_referencia") == "null":
            ids_eliminar.append(notif["id_notificacion"])
            print(f"  ❌ Notificación corrupta: {notif['contenido'][:50]}... (ID: {notif['id_notificacion']})")
    
    # Eliminar una por una
    if ids_eliminar:
        print(f"\n🗑️ Eliminando {len(ids_eliminar)} notificaciones antiguas...")
        for id_notif in ids_eliminar:
            supabase.table("notificacion").delete().eq("id_notificacion", id_notif).execute()
            print(f"  ✅ Eliminada: {id_notif}")
        print(f"\n✅ ¡Listo! {len(ids_eliminar)} notificaciones antiguas eliminadas")
    else:
        print("✅ No hay notificaciones antiguas que eliminar")
        
except Exception as e:
    print(f"❌ Error: {e}")
