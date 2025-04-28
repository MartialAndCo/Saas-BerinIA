#!/usr/bin/env python3
import os
import re

def uncomment_router(filepath):
    """Uncomment the router definition line."""
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return False
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Check if there's a commented router definition
    if "# router = APIRouter" in content:
        # Extract the commented router line
        lines = content.splitlines()
        for i, line in enumerate(lines):
            if "# router = APIRouter" in line:
                # Extract the router definition, removing the comment
                router_def = line.replace("# ", "", 1)
                # Replace the line
                lines[i] = router_def
                print(f"✅ Uncommented router definition in {filepath}")
                break
        
        # Write the updated content
        with open(filepath, 'w') as f:
            f.write("\n".join(lines))
        
        return True
    elif "router = APIRouter" in content:
        print(f"✓ Router already defined in {filepath}")
        return True
    else:
        # Insert a new router definition after imports
        router_def = ""
        if "campaigns" in filepath:
            router_def = "router = APIRouter(prefix=\"/campaigns\", tags=[\"Campaigns\"])"
        elif "niches" in filepath:
            router_def = "router = APIRouter(prefix=\"/niches\", tags=[\"Niches\"])"
        else:
            # Default in case we can't determine the proper prefix
            base_name = os.path.basename(filepath).replace(".py", "")
            router_def = f"router = APIRouter(prefix=\"/{base_name}\", tags=[\"{base_name.capitalize()}\"])"
        
        # Find a good place to insert after imports but before the first function
        pos = content.find("@router")
        if pos == -1:
            print(f"❌ Could not find appropriate position for router definition in {filepath}")
            return False
        
        # Find the last import line
        last_import = max(
            content.rfind("\nfrom ", 0, pos),
            content.rfind("\nimport ", 0, pos)
        )
        
        if last_import != -1:
            insert_pos = content.find("\n", last_import + 1)
            if insert_pos != -1:
                # Add an empty line after imports and then the router definition
                new_content = content[:insert_pos] + "\n\n" + router_def + "\n" + content[insert_pos:]
                
                with open(filepath, 'w') as f:
                    f.write(new_content)
                
                print(f"✅ Added router definition to {filepath}")
                return True
        
        print(f"❌ Could not find appropriate position for router definition in {filepath}")
        return False

# Fix both files
campaigns_path = "/root/berinia/backend/app/api/endpoints/campaigns.py"
niches_path = "/root/berinia/backend/app/api/endpoints/niches.py"

print("=" * 50)
print("🔧 CORRECTION DES DÉFINITIONS DE ROUTER")
print("=" * 50)

campaigns_fixed = uncomment_router(campaigns_path)
niches_fixed = uncomment_router(niches_path)

if campaigns_fixed and niches_fixed:
    print("\n✅ Les définitions de router ont été corrigées.")
    print("\n🔄 Redémarrez le service Berinia pour appliquer les modifications:")
    print("   sudo systemctl restart berinia-api.service")
else:
    print("\n⚠️ Certaines corrections ont échoué. Vérifiez les logs ci-dessus.")
