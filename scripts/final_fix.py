#!/usr/bin/env python3
import os
import shutil

def fix_file(filepath):
    """Fix multiple jsonable_encoder wrappers"""
    if not os.path.exists(filepath):
        print(f"⚠️ File not found: {filepath}")
        return False
    
    # Create backup
    backup_path = f"{filepath}.final.bak"
    shutil.copy2(filepath, backup_path)
    print(f"✅ Backup created: {backup_path}")
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Fix potential nested jsonable_encoder calls
    content = content.replace('return jsonable_encoder(jsonable_encoder(', 'return jsonable_encoder(')
    
    # Replace any jsonable_encoder() calls to direct return for None
    content = content.replace('return jsonable_encoder(None)', 'return None')
    
    # Replace all direct return statements to use jsonable_encoder only once
    if 'return campaigns' in content:
        content = content.replace('return campaigns', 'return jsonable_encoder(campaigns)')
    
    if 'return campaign' in content:
        content = content.replace('return campaign', 'return jsonable_encoder(campaign)')
    
    if 'return niches' in content:
        content = content.replace('return niches', 'return jsonable_encoder(niches)')
    
    if 'return niche' in content:
        content = content.replace('return niche', 'return jsonable_encoder(niche)')
    
    with open(filepath, 'w') as f:
        f.write(content)
    
    print(f"✅ Fixed jsonable_encoder issues in {filepath}")
    return True

# Create a completely new simple version of the campaigns endpoint function
def simplify_campaigns_get(filepath):
    """Replace the get_campaigns function with a simpler version"""
    if not os.path.exists(filepath):
        return False
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Find the function
    get_start = content.find('@router.get("/", response_model=List[Campaign])')
    if get_start == -1:
        print("❌ Could not find the get_campaigns function")
        return False
    
    get_end = content.find('@router.post("/")', get_start)
    if get_end == -1:
        print("❌ Could not find the end of the get_campaigns function")
        return False
    
    # Create a simple replacement
    simple_func = '''@router.get("/", response_model=List[Campaign])
def get_campaigns(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    niche_id: Optional[int] = Query(None),
    db: Session = Depends(deps.get_db)
):
    """
    Récupérer toutes les campagnes avec filtrage optionnel.
    """
    query = db.query(CampaignModel)

    if search:
        query = query.filter(CampaignModel.nom.ilike(f"%{search}%"))

    if status:
        query = query.filter(CampaignModel.statut == status)

    if niche_id:
        query = query.filter(CampaignModel.niche_id == niche_id)

    campaigns = query.offset(skip).limit(limit).all()

    # Calculer les statistiques pour chaque campagne
    for campaign in campaigns:
        # Calculer la progression
        if campaign.target_leads and campaign.target_leads > 0:
            lead_count = db.query(func.count(LeadModel.id)).filter(LeadModel.campagne_id == campaign.id).scalar() or 0
            campaign.progress = min(int((lead_count / campaign.target_leads) * 100), 100)
        else:
            campaign.progress = 0

        # Calculer le taux de conversion
        total_leads = db.query(func.count(LeadModel.id)).filter(LeadModel.campagne_id == campaign.id).scalar() or 0
        converted_leads = db.query(func.count(LeadModel.id)).filter(
            LeadModel.campagne_id == campaign.id,
            LeadModel.statut == "converted"
        ).scalar() or 0

        if total_leads > 0:
            campaign.conversion = round((converted_leads / total_leads) * 100, 1)
        else:
            campaign.conversion = 0.0

    return jsonable_encoder(campaigns)
'''
    
    # Replace the function
    content = content[:get_start] + simple_func + content[get_end:]
    
    with open(filepath, 'w') as f:
        f.write(content)
    
    print(f"✅ Simplified get_campaigns function in {filepath}")
    return True

# Fix both files
campaigns_path = "/root/berinia/backend/app/api/endpoints/campaigns.py"
niches_path = "/root/berinia/backend/app/api/endpoints/niches.py"

print("=" * 50)
print("🔧 CORRECTION FINALE DES ENDPOINTS")
print("=" * 50)

# First simplify the campaigns get function
campaigns_simplified = simplify_campaigns_get(campaigns_path)

# Then fix both files for jsonable_encoder issues
campaigns_fixed = fix_file(campaigns_path)
niches_fixed = fix_file(niches_path)

if campaigns_fixed and niches_fixed:
    print("\n✅ Tous les endpoints ont été corrigés avec succès.")
    print("\n🔄 Redémarrez le service Berinia pour appliquer les modifications:")
    print("   sudo systemctl restart berinia-api.service")
else:
    print("\n⚠️ Certains fichiers n'ont pas pu être corrigés. Vérifiez les logs ci-dessus.")
