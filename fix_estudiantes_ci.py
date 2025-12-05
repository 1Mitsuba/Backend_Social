"""
Script para corregir CIs de estudiantes que tienen valores incorrectos
(como UUIDs parciales o valores no válidos).

Este script:
1. Identifica estudiantes con CIs sospechosos
2. Les asigna CIs únicos y válidos
3. Mantiene la integridad referencial con la tabla usuario
"""

import os
import sys
import re

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import get_supabase_client

supabase = get_supabase_client()

def es_ci_valido(ci):
    """
    Verifica si un CI parece válido.
    Un CI inválido sería:
    - Que contenga guiones (parece UUID)
    - Que sea demasiado largo (>15 caracteres)
    - Que comience con letras seguidas de números hexadecimales (parece UUID parcial)
    """
    if not ci:
        return False
    
    # Si contiene guiones, probablemente es un UUID
    if '-' in ci:
        return False
    
    # Si es muy largo, probablemente es un UUID parcial
    if len(ci) > 15:
        return False
    
    # Si parece un UUID parcial (letras + números hexadecimales)
    if re.match(r'^[A-Z]+[0-9a-f]{8,}$', ci):
        return False
    
    return True

def generar_ci_unico(base_numero, cis_existentes):
    """
    Genera un CI único en formato numérico.
    """
    ci = f"{base_numero:08d}"
    contador = 1
    
    while ci in cis_existentes:
        ci = f"{base_numero + contador:08d}"
        contador += 1
    
    return ci

def corregir_estudiantes():
    """
    Corrige los CIs de estudiantes que tienen valores inválidos.
    """
    print("\n🔍 Analizando estudiantes...")
    
    # Obtener todos los estudiantes
    response = supabase.table('estudiante').select('*').execute()
    estudiantes = response.data
    
    print(f"   Total de estudiantes: {len(estudiantes)}")
    
    # Obtener información de usuarios para mostrar nombres
    response_usuarios = supabase.table('usuario').select('*').execute()
    usuarios_map = {u['id_user']: u for u in response_usuarios.data}
    
    # Identificar estudiantes con CIs problemáticos
    estudiantes_problematicos = []
    cis_validos = set()
    
    for est in estudiantes:
        if es_ci_valido(est['ci_est']):
            cis_validos.add(est['ci_est'])
        else:
            estudiantes_problematicos.append(est)
    
    print(f"\n📊 Resultado del análisis:")
    print(f"   - Estudiantes con CI válido: {len(estudiantes) - len(estudiantes_problematicos)}")
    print(f"   - Estudiantes con CI inválido: {len(estudiantes_problematicos)}")
    
    if not estudiantes_problematicos:
        print("\n✅ ¡Todos los estudiantes tienen CIs válidos!")
        return
    
    print("\n⚠️  Estudiantes con CIs problemáticos:")
    for est in estudiantes_problematicos:
        usuario = usuarios_map.get(est['id_user'], {})
        nombre_completo = f"{usuario.get('nombre', 'N/A')} {usuario.get('apellido', 'N/A')}"
        print(f"   - {nombre_completo}")
        print(f"     CI actual: {est['ci_est']}")
        print(f"     Email: {usuario.get('correo', 'N/A')}")
    
    # Proceder con la corrección automáticamente
    print("\n⚠️  Se procederá a corregir estos CIs automáticamente...")
    
    print("\n🔧 Corrigiendo CIs...")
    
    # Iniciar numeración desde 10000000
    base_numero = 10000000
    corregidos = 0
    errores = 0
    
    for est in estudiantes_problematicos:
        usuario = usuarios_map.get(est['id_user'], {})
        nombre_completo = f"{usuario.get('nombre', 'N/A')} {usuario.get('apellido', 'N/A')}"
        ci_viejo = est['ci_est']
        
        try:
            # Generar nuevo CI único
            ci_nuevo = generar_ci_unico(base_numero, cis_validos)
            cis_validos.add(ci_nuevo)
            base_numero += 1
            
            # La tabla estudiante usa ci_est como PRIMARY KEY
            # Para actualizar la PK, necesitamos:
            # 1. Guardar el id_user
            # 2. Eliminar el registro viejo
            # 3. Insertar un nuevo registro con el nuevo CI
            
            id_user = est['id_user']
            carrera = est['carrera']
            semestre = est['semestre']
            id_grupo = est.get('id_grupo')
            
            # Eliminar registro viejo
            supabase.table('estudiante').delete().eq('ci_est', ci_viejo).execute()
            
            # Insertar nuevo registro
            nuevo_estudiante = {
                'ci_est': ci_nuevo,
                'id_user': id_user,
                'carrera': carrera,
                'semestre': semestre
            }
            
            if id_grupo:
                nuevo_estudiante['id_grupo'] = id_grupo
            
            supabase.table('estudiante').insert(nuevo_estudiante).execute()
            
            print(f"   ✅ {nombre_completo}")
            print(f"      CI: {ci_viejo} → {ci_nuevo}")
            corregidos += 1
            
        except Exception as e:
            print(f"   ❌ Error al corregir {nombre_completo}: {str(e)}")
            errores += 1
    
    print(f"\n📊 Resultado final:")
    print(f"   - Corregidos: {corregidos}")
    print(f"   - Errores: {errores}")
    
    if corregidos > 0:
        print("\n✅ ¡CIs corregidos exitosamente!")
        print("   Los estudiantes ahora tienen CIs numéricos únicos.")

def listar_estudiantes():
    """
    Lista todos los estudiantes con su información.
    """
    print("\n📋 Listando todos los estudiantes...")
    
    # Obtener estudiantes
    response = supabase.table('estudiante').select('*').execute()
    estudiantes = response.data
    
    # Obtener usuarios
    response_usuarios = supabase.table('usuario').select('*').execute()
    usuarios_map = {u['id_user']: u for u in response_usuarios.data}
    
    print(f"\n{'CI':<15} {'Nombre':<30} {'Email':<35} {'Carrera':<20} {'Sem'}")
    print("-" * 110)
    
    for est in estudiantes:
        usuario = usuarios_map.get(est['id_user'], {})
        nombre = f"{usuario.get('nombre', '')} {usuario.get('apellido', '')}"
        email = usuario.get('correo', '')
        carrera = est.get('carrera', 'N/A')
        semestre = est.get('semestre', 'N/A')
        
        print(f"{est['ci_est']:<15} {nombre:<30} {email:<35} {carrera:<20} {semestre}")

if __name__ == "__main__":
    print("=" * 70)
    print("  CORRECCIÓN DE CIs DE ESTUDIANTES")
    print("=" * 70)
    
    # Primero listar
    listar_estudiantes()
    
    # Luego corregir si es necesario
    corregir_estudiantes()
    
    # Listar nuevamente para confirmar
    print("\n" + "=" * 70)
    listar_estudiantes()
