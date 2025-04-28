#!/usr/bin/env python3
import os
import re
import shutil

def fix_file(filepath):
    """Add jsonable_encoder to return statements in the given file."""
    if not os.path.exists(filepath):
        print(f"⚠️ File not found: {filepath}")
        return False
    
    # Create backup
    backup_path = f"{filepath}.json.bak"
    shutil.copy2(filepath, backup_path)
    print(f"✅ Backup created: {backup_path}")
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Add import if needed
    if "from fastapi.encoders import jsonable_encoder" not in content:
        # Add after the first import block
        import_end = content.find("\n\n", content.find("import "))
        if import_end == -1:
            import_end = content.find("router = APIRouter")
        
        if import_end != -1:
            content = content[:import_end] + "\nfrom fastapi.encoders import jsonable_encoder" + content[import_end:]
            print(f"✅ Added import for jsonable_encoder to {filepath}")
    
    # Replace return statements with jsonable_encoder
    content = re.sub(
        r'return ([a-zA-Z_][a-zA-Z0-9_]*)',
        r'return jsonable_encoder(\1)',
        content
    )
    
    with open(filepath, 'w') as f:
        f.write(content)
    
    print(f"✅ Fixed return statements in {filepath}")
    return True

# Fix both files
campaigns_path = "/root/berinia/backend/app/api/endpoints/campaigns.py"
niches_path = "/root/berinia/backend/app/api/endpoints/niches.py"

print("=" * 50)
print("🔧 CORRECTION FINALE AVEC JSONABLE_ENCODER")
print("=" * 50)

campaigns_fixed = fix_file(campaigns_path)
niches_fixed = fix_file(niches_path)

if campaigns_fixed and niches_fixed:
    print("\n✅ Tous les endpoints ont été corrigés avec succès.")
    print("\n🔄 Redémarrez le service Berinia pour appliquer les modifications:")
    print("   sudo systemctl restart berinia-api.service")
else:
    print("\n⚠️ Certains fichiers n'ont pas pu être corrigés. Vérifiez les logs ci-dessus.")
