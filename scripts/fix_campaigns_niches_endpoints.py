#!/usr/bin/env python3
import os
import re
import datetime
import shutil
import sys

def timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log(message):
    print(f"\n{message}")

def backup_file(file_path):
    """Create a backup of the file."""
    backup_path = f"{file_path}.endpoints.bak"
    if os.path.exists(file_path):
        shutil.copy2(file_path, backup_path)
        return True
    return False

def fix_campaigns_endpoint():
    """Fix the campaigns endpoint."""
    campaigns_path = "/root/berinia/backend/app/api/endpoints/campaigns.py"
    
    if not os.path.exists(campaigns_path):
        log(f"❌ Campaigns file not found at {campaigns_path}")
        return False
    
    if backup_file(campaigns_path):
        log(f"✅ Backup created: {campaigns_path}.endpoints.bak")
    
    with open(campaigns_path, 'r') as f:
        content = f.read()
    
    # The main issue is related to converting SQLAlchemy objects to dictionaries
    # Let's modify the implementation to use jsonable_encoder correctly
    
    # Pattern for get_campaigns route
    get_campaigns_pattern = re.compile(
        r'@router\.get\(".*?"\).*?async def get_campaigns\(.*?\):(.*?)return', 
        re.DOTALL
    )
    
    # Update the implementation to use jsonable_encoder properly
    if get_campaigns_pattern.search(content):
        content = get_campaigns_pattern.sub(
            r'@router.get("")\nasync def get_campaigns():\n    """Get all campaigns."""\n    db = SessionLocal()\n    try:\n        campaigns = db.query(Campaign).all()\n        return jsonable_encoder(campaigns)\n    finally:\n        db.close()\n\nreturn', 
            content
        )
        log("✅ Updated get_campaigns endpoint to use jsonable_encoder properly")
    else:
        log("❌ Could not find get_campaigns endpoint pattern")
    
    # Pattern for get_campaign route
    get_campaign_pattern = re.compile(
        r'@router\.get\("/{campaign_id}"\).*?async def get_campaign\(.*?\):(.*?)return', 
        re.DOTALL
    )
    
    # Update the implementation to use jsonable_encoder properly
    if get_campaign_pattern.search(content):
        content = get_campaign_pattern.sub(
            r'@router.get("/{campaign_id}")\nasync def get_campaign(campaign_id: int):\n    """Get a specific campaign by ID."""\n    db = SessionLocal()\n    try:\n        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()\n        if not campaign:\n            raise HTTPException(status_code=404, detail="Campaign not found")\n        return jsonable_encoder(campaign)\n    finally:\n        db.close()\n\nreturn', 
            content
        )
        log("✅ Updated get_campaign endpoint to use jsonable_encoder properly")
    else:
        log("❌ Could not find get_campaign endpoint pattern")
    
    # Make sure jsonable_encoder is imported
    if "from fastapi.encoders import jsonable_encoder" not in content:
        import_section_end = content.find("router = APIRouter(")
        if import_section_end == -1:
            import_section_end = 0
        content = content[:import_section_end] + "from fastapi.encoders import jsonable_encoder\n" + content[import_section_end:]
        log("✅ Added import for jsonable_encoder")
    
    # Write the updated content back
    with open(campaigns_path, 'w') as f:
        f.write(content)
    
    log(f"✅ Updated campaigns endpoint: {campaigns_path}")
    return True

def fix_niches_endpoint():
    """Fix the niches endpoint."""
    niches_path = "/root/berinia/backend/app/api/endpoints/niches.py"
    
    if not os.path.exists(niches_path):
        log(f"❌ Niches file not found at {niches_path}")
        return False
    
    if backup_file(niches_path):
        log(f"✅ Backup created: {niches_path}.endpoints.bak")
    
    with open(niches_path, 'r') as f:
        content = f.read()
    
    # Pattern for get_niches route
    get_niches_pattern = re.compile(
        r'@router\.get\(".*?"\).*?async def get_niches\(.*?\):(.*?)return', 
        re.DOTALL
    )
    
    # Update the implementation to use jsonable_encoder properly
    if get_niches_pattern.search(content):
        content = get_niches_pattern.sub(
            r'@router.get("")\nasync def get_niches():\n    """Get all niches."""\n    db = SessionLocal()\n    try:\n        niches = db.query(Niche).all()\n        return jsonable_encoder(niches)\n    finally:\n        db.close()\n\nreturn', 
            content
        )
        log("✅ Updated get_niches endpoint to use jsonable_encoder properly")
    else:
        log("❌ Could not find get_niches endpoint pattern")
    
    # Pattern for get_niche route
    get_niche_pattern = re.compile(
        r'@router\.get\("/{niche_id}"\).*?async def get_niche\(.*?\):(.*?)return', 
        re.DOTALL
    )
    
    # Update the implementation to use jsonable_encoder properly
    if get_niche_pattern.search(content):
        content = get_niche_pattern.sub(
            r'@router.get("/{niche_id}")\nasync def get_niche(niche_id: int):\n    """Get a specific niche by ID."""\n    db = SessionLocal()\n    try:\n        niche = db.query(Niche).filter(Niche.id == niche_id).first()\n        if not niche:\n            raise HTTPException(status_code=404, detail="Niche not found")\n        return jsonable_encoder(niche)\n    finally:\n        db.close()\n\nreturn', 
            content
        )
        log("✅ Updated get_niche endpoint to use jsonable_encoder properly")
    else:
        log("❌ Could not find get_niche endpoint pattern")
    
    # Make sure jsonable_encoder is imported
    if "from fastapi.encoders import jsonable_encoder" not in content:
        import_section_end = content.find("router = APIRouter(")
        if import_section_end == -1:
            import_section_end = 0
        content = content[:import_section_end] + "from fastapi.encoders import jsonable_encoder\n" + content[import_section_end:]
        log("✅ Added import for jsonable_encoder")
    
    # Write the updated content back
    with open(niches_path, 'w') as f:
        f.write(content)
    
    log(f"✅ Updated niches endpoint: {niches_path}")
    return True

def main():
    print("=" * 50)
    print(f"🔧 CORRECTION DES ENDPOINTS CAMPAIGNS ET NICHES")
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
