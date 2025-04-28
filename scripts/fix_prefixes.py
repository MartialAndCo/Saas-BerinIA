#!/usr/bin/env python3
import os

def remove_router_prefix(filepath):
    """Remove the prefix from router definition to avoid duplication."""
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return False
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Find the router definition line
    if "router = APIRouter(prefix=" in content:
        # Replace with a version without prefix
        updated_content = content.replace(
            "router = APIRouter(prefix=\"/campaigns\", tags=[\"Campaigns\"])",
            "router = APIRouter()"
        ).replace(
            "router = APIRouter(prefix=\"/niches\", tags=[\"Niches\"])",
            "router = APIRouter()"
        )
        
        # Write back the updated content
        with open(filepath, 'w') as f:
            f.write(updated_content)
        
        print(f"✅ Removed prefix from router definition in {filepath}")
        return True
    else:
        print(f"✓ No prefix found in router definition for {filepath}")
        return True

# Fix both files
campaigns_path = "/root/berinia/backend/app/api/endpoints/campaigns.py"
niches_path = "/root/berinia/backend/app/api/endpoints/niches.py"

print("=" * 50)
print("🔧 CORRECTION DES PRÉFIXES DE ROUTER")
print("=" * 50)

campaigns_fixed = remove_router_prefix(campaigns_path)
niches_fixed = remove_router_prefix(niches_path)

if campaigns_fixed and niches_fixed:
    print("\n✅ Les préfixes des routers ont été corrigés.")
    print("\n🔄 Redémarrez le service Berinia pour appliquer les modifications:")
    print("   sudo systemctl restart berinia-api.service")
else:
    print("\n⚠️ Certaines corrections ont échoué. Vérifiez les logs ci-dessus.")
