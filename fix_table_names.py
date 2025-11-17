"""
Script para cambiar todos los nombres de tablas a minúsculas
para que coincidan con las tablas de Supabase
"""
import os
import re

# Mapeo de nombres de tablas de mayúsculas a minúsculas
TABLE_MAPPING = {
    '"Usuario"': '"usuario"',
    '"Estudiante"': '"estudiante"',
    '"Docente"': '"docente"',
    '"GestionAcademica"': '"gestionacademica"',
    '"Grupo"': '"grupo"',
    '"Materia"': '"materia"',
    '"GrupoMateria"': '"grupomateria"',
    '"Nota"': '"nota"',
    '"Horario"': '"horario"',
    '"Ruta"': '"ruta"',
    '"Parada"': '"parada"',
    '"PasajeroRuta"': '"pasajeroruta"',
    '"Publicacion"': '"publicacion"',
    '"Media"': '"media"',
    '"Comentario"': '"comentario"',
    '"Reaccion"': '"reaccion"',
    '"Conversacion"': '"conversacion"',
    '"UsuarioConversacion"': '"usuarioconversacion"',
    '"Mensaje"': '"mensaje"',
    '"Notificacion"': '"notificacion"',
    '"RelacionUsuario"': '"relacionusuario"',
}

def fix_table_names(directory):
    """Reemplaza nombres de tablas en todos los archivos .py"""
    files_changed = 0
    total_replacements = 0
    
    for root, dirs, files in os.walk(directory):
        # Ignorar carpetas __pycache__
        dirs[:] = [d for d in dirs if d != '__pycache__']
        
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                
                # Leer el archivo
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                replacements_in_file = 0
                
                # Reemplazar cada tabla
                for old_name, new_name in TABLE_MAPPING.items():
                    pattern = r'\.table\(' + re.escape(old_name) + r'\)'
                    replacement = f'.table({new_name})'
                    new_content, count = re.subn(pattern, replacement, content)
                    
                    if count > 0:
                        replacements_in_file += count
                        content = new_content
                
                # Si hubo cambios, guardar el archivo
                if content != original_content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    files_changed += 1
                    total_replacements += replacements_in_file
                    print(f"✅ {filepath}: {replacements_in_file} reemplazos")
    
    return files_changed, total_replacements

if __name__ == "__main__":
    print("🔧 Corrigiendo nombres de tablas a minúsculas...\n")
    
    # Directorio de la aplicación
    app_dir = os.path.join(os.path.dirname(__file__), 'app')
    
    files_changed, total_replacements = fix_table_names(app_dir)
    
    print(f"\n✅ Proceso completado:")
    print(f"   - Archivos modificados: {files_changed}")
    print(f"   - Total de reemplazos: {total_replacements}")
    print(f"\n🚀 Reinicia el servidor para aplicar los cambios")
