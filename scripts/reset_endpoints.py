#!/usr/bin/env python3
import os
import shutil

def backup_file(filepath, suffix="reset"):
    """Create a backup of the file."""
    backup_path = f"{filepath}.{suffix}.bak"
    if os.path.exists(filepath):
        shutil.copy2(filepath, backup_path)
        print(f"✅ Backup created: {backup_path}")
        return True
    return False

def reset_campaigns_endpoint():
    """Reset the campaigns endpoint to a clean state."""
    filepath = "/root/berinia/backend/app/api/endpoints/campaigns.py"
    
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return False
    
    backup_file(filepath)
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Extract imports and router definition
    imports_end = content.find("router = APIRouter")
    if imports_end == -1:
        print("❌ Could not find router definition")
        return False
    
    # Find the end of the router line
    router_end = content.find("\n", imports_end)
    if router_end == -1:
        router_end = len(content)
    
    # Get the imports and router definition
    imports_and_router = content[:router_end+1]
    
    # Ensure jsonable_encoder is imported
    if "from fastapi.encoders import jsonable_encoder" not in imports_and_router:
        # Add import before router definition
        imports_and_router = imports_and_router[:imports_end] + "from fastapi.encoders import jsonable_encoder\n" + imports_and_router[imports_end:]
    
    # Reset with clean implementations
    new_content = imports_and_router + """

@router.get("/", response_model=List[Campaign])
def get_campaigns(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    niche_id: Optional[int] = Query(None),
    db: Session = Depends(deps.get_db)
):
    \"\"\"
    Récupérer toutes les campagnes avec filtrage optionnel.
    \"\"\"
    query = db.query(CampaignModel)

    if search:
        query = query.filter(CampaignModel.nom.ilike(f"%{search}%"))

    if status:
        query = query.filter(CampaignModel.statut == status)

    if niche_id:
        query = query.filter(CampaignModel.niche_id == niche_id)

    campaigns = query.offset(skip).limit(limit).all()

    # Enrichir les campagnes avec des données calculées
    for campaign in campaigns:
        # Progression
        if campaign.target_leads and campaign.target_leads > 0:
            lead_count = db.query(func.count(LeadModel.id)).filter(LeadModel.campagne_id == campaign.id).scalar() or 0
            campaign.progress = min(int((lead_count / campaign.target_leads) * 100), 100)
        else:
            campaign.progress = 0

        # Taux de conversion
        total_leads = db.query(func.count(LeadModel.id)).filter(LeadModel.campagne_id == campaign.id).scalar() or 0
        converted_leads = db.query(func.count(LeadModel.id)).filter(
            LeadModel.campagne_id == campaign.id,
            LeadModel.statut == "converted"
        ).scalar() or 0

        if total_leads > 0:
            campaign.conversion = round((converted_leads / total_leads) * 100, 1)
        else:
            campaign.conversion = 0.0

    # Utiliser jsonable_encoder pour sérialiser les objets SQLAlchemy
    result = jsonable_encoder(campaigns)
    return result

@router.get("/{campaign_id}", response_model=Campaign)
def get_campaign(campaign_id: int, db: Session = Depends(deps.get_db)):
    \"\"\"
    Récupérer une campagne spécifique par son ID.
    \"\"\"
    campaign = db.query(CampaignModel).filter(CampaignModel.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Enrichir la campagne avec des données calculées
    if campaign.target_leads and campaign.target_leads > 0:
        lead_count = db.query(func.count(LeadModel.id)).filter(LeadModel.campagne_id == campaign.id).scalar() or 0
        campaign.progress = min(int((lead_count / campaign.target_leads) * 100), 100)
    else:
        campaign.progress = 0
    
    # Taux de conversion
    total_leads = db.query(func.count(LeadModel.id)).filter(LeadModel.campagne_id == campaign.id).scalar() or 0
    converted_leads = db.query(func.count(LeadModel.id)).filter(
        LeadModel.campagne_id == campaign.id,
        LeadModel.statut == "converted"
    ).scalar() or 0

    if total_leads > 0:
        campaign.conversion = round((converted_leads / total_leads) * 100, 1)
    else:
        campaign.conversion = 0.0
    
    # Utiliser jsonable_encoder pour sérialiser l'objet SQLAlchemy
    result = jsonable_encoder(campaign)
    return result

"""
    
    # Find the rest of the file content starting from @router.post
    post_start = content.find('@router.post("/"')
    if post_start != -1:
        new_content += content[post_start:]
    
    # Write the new content
    with open(filepath, 'w') as f:
        f.write(new_content)
    
    print(f"✅ Reset campaigns endpoints in {filepath}")
    return True

def reset_niches_endpoint():
    """Reset the niches endpoint to a clean state."""
    filepath = "/root/berinia/backend/app/api/endpoints/niches.py"
    
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return False
    
    backup_file(filepath)
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Extract imports and router definition
    imports_end = content.find("router = APIRouter")
    if imports_end == -1:
        print("❌ Could not find router definition")
        return False
    
    # Find the end of the router line
    router_end = content.find("\n", imports_end)
    if router_end == -1:
        router_end = len(content)
    
    # Get the imports and router definition
    imports_and_router = content[:router_end+1]
    
    # Ensure jsonable_encoder is imported
    if "from fastapi.encoders import jsonable_encoder" not in imports_and_router:
        # Add import before router definition
        imports_and_router = imports_and_router[:imports_end] + "from fastapi.encoders import jsonable_encoder\n" + imports_and_router[imports_end:]
    
    # Reset with clean implementations
    new_content = imports_and_router + """

@router.get("/", response_model=List[NicheResponse])
def get_niches(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    search: Optional[str] = Query(None),
    statut: Optional[str] = Query(None),
    db: Session = Depends(deps.get_db)
):
    \"\"\"
    Récupère la liste des niches avec filtres optionnels
    \"\"\"
    query = db.query(NicheModel)

    if search:
        query = query.filter(NicheModel.nom.ilike(f"%{search}%"))

    if statut:
        query = query.filter(NicheModel.statut == statut)

    niches = query.offset(skip).limit(limit).all()

    # Enrichir les niches avec des données calculées si nécessaire
    for niche in niches:
        # Si vous avez besoin de charger les campagnes associées
        campaigns = db.query(CampaignModel).filter(CampaignModel.niche_id == niche.id).all()
        niche.campagnes = campaigns
        
    # Utiliser jsonable_encoder pour sérialiser les objets SQLAlchemy
    result = jsonable_encoder(niches)
    return result

@router.get("/{niche_id}", response_model=NicheResponse)
def get_niche(niche_id: int, db: Session = Depends(deps.get_db)):
    \"\"\"
    Récupère une niche spécifique par son ID
    \"\"\"
    niche = db.query(NicheModel).filter(NicheModel.id == niche_id).first()
    if not niche:
        raise HTTPException(status_code=404, detail="Niche not found")

    # Charger les campagnes associées
    campaigns = db.query(CampaignModel).filter(CampaignModel.niche_id == niche.id).all()
    niche.campagnes = campaigns
    
    # Utiliser jsonable_encoder pour sérialiser l'objet SQLAlchemy
    result = jsonable_encoder(niche)
    return result

"""
    
    # Find the rest of the file content starting from @router.post
    post_start = content.find('@router.post("/"')
    if post_start != -1:
        new_content += content[post_start:]
    
    # Write the new content
    with open(filepath, 'w') as f:
        f.write(new_content)
    
    print(f"✅ Reset niches endpoints in {filepath}")
    return True

print("=" * 50)
print("🔄 RÉINITIALISATION COMPLÈTE DES ENDPOINTS")
print("=" * 50)

campaigns_reset = reset_campaigns_endpoint()
niches_reset = reset_niches_endpoint()

if campaigns_reset and niches_reset:
    print("\n✅ Tous les endpoints ont été réinitialisés avec succès.")
    print("\n🔄 Redémarrez le service Berinia pour appliquer les modifications:")
    print("   sudo systemctl restart berinia-api.service")
else:
    print("\n⚠️ Certaines réinitialisations ont échoué. Vérifiez les logs ci-dessus.")
