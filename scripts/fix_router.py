#!/usr/bin/env python3
import os

def fix_router_definition(filepath, backup_suffix="reset.bak"):
    """Restore router definition from backup file."""
    backup_path = f"{filepath}.{backup_suffix}"
    
    if not os.path.exists(backup_path):
        print(f"⚠️ Backup file not found: {backup_path}")
        return False
    
    # Read the backup file to extract router definition
    with open(backup_path, 'r') as f:
        backup_content = f.read()
    
    # Find the router definition line
    router_line = None
    for line in backup_content.splitlines():
        if "router = APIRouter" in line:
            router_line = line
            break
    
    if not router_line:
        print(f"❌ Could not find router definition in backup file: {backup_path}")
        return False
    
    # Read the current file
    with open(filepath, 'r') as f:
        current_content = f.read()
    
    # Add router definition if missing
    if "router = APIRouter" not in current_content:
        # Extract imports section
        imports_end = current_content.find('\n\n@router')
        if imports_end == -1:
            imports_end = current_content.find('@router')
        
        if imports_end != -1:
            # Insert router definition before first router usage
            new_content = current_content[:imports_end] + f"\n{router_line}\n\n" + current_content[imports_end:]
            
            # Write the fixed content
            with open(filepath, 'w') as f:
                f.write(new_content)
            
            print(f"✅ Added router definition to {filepath}")
            return True
        else:
            print(f"❌ Could not find appropriate position to insert router definition in {filepath}")
            return False
    else:
        print(f"✓ Router definition already exists in {filepath}")
        return True

# Fix both endpoints files
campaigns_path = "/root/berinia/backend/app/api/endpoints/campaigns.py"
niches_path = "/root/berinia/backend/app/api/endpoints/niches.py"

print("=" * 50)
print("🔧 CORRECTION DE LA DÉFINITION DU ROUTER")
print("=" * 50)

campaigns_fixed = fix_router_definition(campaigns_path)
niches_fixed = fix_router_definition(niches_path)

if campaigns_fixed and niches_fixed:
    print("\n✅ La définition du router a été restaurée dans tous les fichiers.")
    print("\n🔄 Redémarrez le service Berinia pour appliquer les modifications:")
    print("   sudo systemctl restart berinia-api.service")
else:
    print("\n⚠️ La correction a échoué pour certains fichiers. Vérifiez les logs ci-dessus.")
