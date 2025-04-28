#!/usr/bin/env python3
import os
import datetime
import shutil

def timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def backup_file(file_path):
    """Create a backup of the file."""
    backup_path = f"{file_path}.manual.bak"
    if os.path.exists(file_path):
        shutil.copy2(file_path, backup_path)
        print(f"✅ Backup created: {backup_path}")
        return True
    return False

def fix_campaigns_endpoint():
    """Fix the campaigns endpoint."""
    campaigns_path = "/root/berinia/backend/app/api/endpoints/campaigns.py"
    
    if not os.path.exists(campaigns_path):
        print(f"❌ Campaigns file not found at {campaigns_path}")
        return False
    
    backup_file(campaigns_path)
    
    with open(campaigns_path, 'r') as f:
        content = f.read()
    
    # Modify the return statement in get_campaigns to use jsonable_encoder
    content = content.replace(
        "return campaigns", 
        "return jsonable_encoder(campaigns)"
    )
    
    # Modify the return statement in get_campaign to use jsonable_encoder
    content = content.replace(
        "return campaign", 
        "return jsonable_encoder(campaign)"
    )
    
    # Make sure jsonable_encoder is imported
    if "from fastapi.encoders import jsonable_encoder" not in content:
        import_section = content.find("from app.api import deps")
        if import_section != -1:
            content = content[:import_section] + "from fastapi.encoders import jsonable_encoder\n" + content[import_section:]
        else:
            print("❌ Could not find appropriate place to add jsonable_encoder import")
    
    # Write the updated content back
    with open(campaigns_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Updated campaigns endpoint: {campaigns_path}")
    return True

def fix_niches_endpoint():
    """Fix the niches endpoint."""
    niches_path = "/root/berinia/backend/app/api/endpoints/niches.py"
    
    if not os.path.exists(niches_path):
        print(f"❌ Niches file not found at {niches_path}")
        return False
    
    backup_file(niches_path)
    
    with open(niches_path, 'r') as f:
        content = f.read()
    
    # Fix the get_niche function
    get_niche_block_start = content.find("def get_niche(")
    get_niche_block_end = content.find("@router.put", get_niche_block_start)
    
    if get_niche_block_start != -1 and get_niche_block_end != -1:
        # Extract the get_niche block
        get_niche_block = content[get_niche_block_start:get_niche_block_end]
        
        # Fix variable reference to 'niches' that doesn't exist
        fixed_get_niche_block = get_niche_block.replace(
            "for niche in niches:",
            "# Préparer la niche pour la sérialisation"
        )
        
        # Replace any return that doesn't use jsonable_encoder
        fixed_get_niche_block = fixed_get_niche_block.replace(
            "return niche",
            "return jsonable_encoder(niche)"
        )
        
        # Update the block in the full content
        content = content[:get_niche_block_start] + fixed_get_niche_block + content[get_niche_block_end:]
    else:
        print("❌ Could not find get_niche function to fix")
    
    # Fix the get_niches function to use jsonable_encoder
    content = content.replace(
        "return niches", 
        "return jsonable_encoder(niches)"
    )
    
    # Make sure jsonable_encoder is imported
    if "from fastapi.encoders import jsonable_encoder" not in content:
        import_section = content.find("from app.api import deps")
        if import_section != -1:
            content = content[:import_section] + "from fastapi.encoders import jsonable_encoder\n" + content[import_section:]
        else:
            print("❌ Could not find appropriate place to add jsonable_encoder import")
    
    # Write the updated content back
    with open(niches_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Updated niches endpoint: {niches_path}")
    return True

def main():
    print("=" * 50)
    print(f"🔧 CORRECTION MANUELLE DES ENDPOINTS CAMPAIGNS ET NICHES")
    print(f"🕒 {timestamp()}")
    print("=" * 50)
    
    campaigns_fixed = fix_campaigns_endpoint()
    niches_fixed = fix_niches_endpoint()
    
    if campaigns_fixed and niches_fixed:
        print("\n✅ Tous les endpoints ont été corrigés avec succès.")
        print("\n🔄 Redémarrez le service Berinia pour appliquer les modifications:")
        print("   sudo systemctl restart berinia-api.service")
    else:
        print("\n⚠️ Certains endpoints n'ont pas pu être corrigés. Vérifiez les logs ci-dessus.")

if __name__ == "__main__":
    main()
