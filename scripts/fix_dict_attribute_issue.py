#!/usr/bin/env python3
import os
import datetime
import shutil
import re

def timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def backup_file(file_path):
    """Create a backup of the file."""
    backup_path = f"{file_path}.dict_fix.bak"
    if os.path.exists(file_path):
        shutil.copy2(file_path, backup_path)
        print(f"✅ Backup created: {backup_path}")
        return True
    return False

def fix_campaigns_endpoint():
    """Fix the dict attribute issue in campaigns endpoint."""
    campaigns_path = "/root/berinia/backend/app/api/endpoints/campaigns.py"
    
    if not os.path.exists(campaigns_path):
        print(f"❌ Campaigns file not found at {campaigns_path}")
        return False
    
    backup_file(campaigns_path)
    
    with open(campaigns_path, 'r') as f:
        content = f.read()
    
    # Trouvons la fonction get_campaigns complète pour la remplacer
    get_campaigns_start = content.find("@router.get(\"/\"")
    get_campaigns_end = content.find("@router.post", get_campaigns_start)
    
    if get_campaigns_start == -1 or get_campaigns_end == -1:
        print("❌ Could not locate the get_campaigns function")
        return False
    
    # Extrayons la fonction get_campaigns
    get_campaigns = content[get_campaigns_start:get_campaigns_end]
    
    # Créons une version corrigée qui évite de modifier les objets avant leur sérialisation
    fixed_get_campaigns = re.sub(
        r'# Préparation des données pour la sérialisation.*?return campaigns',
        '# Utilisation de jsonable_encoder pour la sérialisation\n    return jsonable_encoder(campaigns)',
        get_campaigns,
        flags=re.DOTALL
    )
    
    # Si la modification précédente n'a pas fonctionné, essayons une approche plus directe
    if fixed_get_campaigns == get_campaigns:
        # Trouver et remplacer le bloc problématique qui modifie les objets leads
        fixed_get_campaigns = re.sub(
            r'for campaign in campaigns:.*?campaign\.leads = \[.*?\]',
            'for campaign in campaigns:\n        # Calculer la progression\n        if campaign.target_leads and campaign.target_leads > 0:\n            lead_count = db.query(func.count(LeadModel.id)).filter(LeadModel.campagne_id == campaign.id).scalar() or 0\n            campaign.progress = min(int((lead_count / campaign.target_leads) * 100), 100)\n        else:\n            campaign.progress = 0\n\n        # Calculer le taux de conversion\n        total_leads = db.query(func.count(LeadModel.id)).filter(LeadModel.campagne_id == campaign.id).scalar() or 0\n        converted_leads = db.query(func.count(LeadModel.id)).filter(\n            LeadModel.campagne_id == campaign.id,\n            LeadModel.statut == "converted"\n        ).scalar() or 0\n\n        if total_leads > 0:\n            campaign.conversion = round((converted_leads / total_leads) * 100, 1)\n        else:\n            campaign.conversion = 0.0',
            fixed_get_campaigns,
            flags=re.DOTALL
        )
    
    # Remplace la section return pour utiliser jsonable_encoder
    fixed_get_campaigns = fixed_get_campaigns.replace(
        "return campaigns",
        "return jsonable_encoder(campaigns)"
    )
    
    # Mettre à jour le contenu complet
    content = content[:get_campaigns_start] + fixed_get_campaigns + content[get_campaigns_end:]
    
    # Corriger le endpoint get_campaign (pour un ID spécifique) aussi
    get_campaign_start = content.find("@router.get(\"/{campaign_id}\"")
    get_campaign_end = content.find("@router.put", get_campaign_start)
    
    if get_campaign_start != -1 and get_campaign_end != -1:
        get_campaign = content[get_campaign_start:get_campaign_end]
        
        # Corriger la fonction get_campaign pour utiliser jsonable_encoder
        fixed_get_campaign = get_campaign.replace(
            "return campaign",
            "return jsonable_encoder(campaign)"
        )
        
        content = content[:get_campaign_start] + fixed_get_campaign + content[get_campaign_end:]
    
    # Écrire la version corrigée
    with open(campaigns_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Fixed campaigns endpoint: {campaigns_path}")
    return True

def fix_niches_endpoint():
    """Fix the dict attribute issue in niches endpoint."""
    niches_path = "/root/berinia/backend/app/api/endpoints/niches.py"
    
    if not os.path.exists(niches_path):
        print(f"❌ Niches file not found at {niches_path}")
        return False
    
    backup_file(niches_path)
    
    with open(niches_path, 'r') as f:
        content = f.read()
    
    # Trouver la fonction get_niches complète pour la remplacer
    get_niches_start = content.find("@router.get(\"/\"")
    get_niches_end = content.find("@router.post", get_niches_start)
    
    if get_niches_start == -1 or get_niches_end == -1:
        print("❌ Could not locate the get_niches function")
        return False
    
    # Extraire la fonction get_niches
    get_niches = content[get_niches_start:get_niches_end]
    
    # Créer une version corrigée qui évite de modifier les objets avant leur sérialisation
    fixed_get_niches = re.sub(
        r'# Préparation des données pour la sérialisation.*?return niches',
        '# Utilisation de jsonable_encoder pour la sérialisation\n    return jsonable_encoder(niches)',
        get_niches,
        flags=re.DOTALL
    )
    
    # Si la modification précédente n'a pas fonctionné, essayons une approche plus directe
    if fixed_get_niches == get_niches:
        # Trouver et remplacer le bloc qui modifie les objets
        fixed_get_niches = re.sub(
            r'# Préparation des données pour la sérialisation.*?for niche in niches:.*?campagne\.leads = lead_dicts',
            '# Utiliser jsonable_encoder pour la sérialisation',
            get_niches,
            flags=re.DOTALL
        )
    
    # Remplacer la section return pour utiliser jsonable_encoder
    fixed_get_niches = fixed_get_niches.replace(
        "return niches",
        "return jsonable_encoder(niches)"
    )
    
    # Mettre à jour le contenu complet
    content = content[:get_niches_start] + fixed_get_niches + content[get_niches_end:]
    
    # Simplifier la fonction entière pour utiliser directement jsonable_encoder
    simplified_get_niches = """@router.get("/", response_model=List[NicheResponse])
def get_niches(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    search: Optional[str] = Query(None),
    statut: Optional[str] = Query(None),
    db: Session = Depends(deps.get_db)
):
    """
    simplified_get_niches += """\"\"\"
    Récupère la liste des niches avec filtres optionnels
    \"\"\"
    query = db.query(NicheModel)

    if search:
        query = query.filter(NicheModel.nom.ilike(f"%{search}%"))

    if statut:
        query = query.filter(NicheModel.statut == statut)

    niches = query.offset(skip).limit(limit).all()

    # Enrichir les niches avec des données calculées
    for niche in niches:
        # Compter les campagnes
        niche.campagnes = db.query(CampaignModel).filter(CampaignModel.niche_id == niche.id).all()

        # Compter les leads
        lead_count = 0
        for campagne in niche.campagnes:
            campagne_leads = db.query(LeadModel).filter(LeadModel.campagne_id == campagne.id).all()
            lead_count += len(campagne_leads)

        niche.leads = []  # Nous ne renvoyons pas les leads individuels, juste le compte

    return jsonable_encoder(niches)
"""
    
    # Remplacer potentiellement la fonction entière
    if "for niche in niches:" in get_niches and "if hasattr(niche, 'campagnes'):" in get_niches:
        content = content[:get_niches_start] + simplified_get_niches + content[get_niches_end:]
    
    # Corriger aussi la fonction get_niche
    get_niche_start = content.find("@router.get(\"/{niche_id}\"")
    get_niche_end = content.find("@router.put", get_niche_start) if get_niche_start != -1 else -1
    
    if get_niche_start != -1 and get_niche_end != -1:
        get_niche = content[get_niche_start:get_niche_end]
        
        # Remplacer la partie problématique dans get_niche
        fixed_get_niche = re.sub(
            r'# Préparation des données pour la sérialisation.*?return niche',
            '    return jsonable_encoder(niche)',
            get_niche,
            flags=re.DOTALL
        )
        
        if fixed_get_niche == get_niche:
            # Si le pattern précédent n'a pas fonctionné, essayons un remplacement direct
            fixed_get_niche = get_niche.replace(
                "return niche",
                "return jsonable_encoder(niche)"
            )
        
        content = content[:get_niche_start] + fixed_get_niche + content[get_niche_end:]
    
    # Simplifier la fonction get_niche également
    simplified_get_niche = """@router.get("/{niche_id}", response_model=NicheResponse)
def get_niche(niche_id: int, db: Session = Depends(deps.get_db)):
    """
    simplified_get_niche += """\"\"\"
    Récupère une niche spécifique par son ID
    \"\"\"
    niche = db.query(NicheModel).filter(NicheModel.id == niche_id).first()
    if not niche:
        raise HTTPException(status_code=404, detail="Niche not found")

    # Enrichir la niche avec des données calculées
    niche.campagnes = db.query(CampaignModel).filter(CampaignModel.niche_id == niche.id).all()

    # Compter les leads
    lead_count = 0
    for campagne in niche.campagnes:
        campagne_leads = db.query(LeadModel).filter(LeadModel.campagne_id == campagne.id).all()
        lead_count += len(campagne_leads)

    niche.leads = []  # Nous ne renvoyons pas les leads individuels, juste le compte

    return jsonable_encoder(niche)
"""
    
    # Remplacer potentiellement la fonction get_niche entière
    if "for niche in niches:" in get_niche:
        content = content[:get_niche_start] + simplified_get_niche + content[get_niche_end:]
    
    # Vérifier que jsonable_encoder est importé
    if "from fastapi.encoders import jsonable_encoder" not in content:
        # Ajouter l'import
        first_import = content.find("from ")
        if first_import != -1:
            content = content[:first_import] + "from fastapi.encoders import jsonable_encoder\n" + content[first_import:]
    
    # Écrire la version corrigée
    with open(niches_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Fixed niches endpoint: {niches_path}")
    return True

def main():
    print("=" * 50)
    print(f"🔧 CORRECTION FINALE DE L'ERREUR DICT ATTRIBUTE")
    print(f"🕒 {timestamp()}")
    print("=" * 50)
    
    campaigns_fixed = fix_campaigns_endpoint()
    niches_fixed = fix_niches_endpoint()
    
    if campaigns_fixed and niches_fixed:
        print("\n✅ Toutes les erreurs dict attribute ont été corrigées.")
        print("\n🔄 Redémarrez le service Berinia pour appliquer les modifications:")
        print("   sudo systemctl restart berinia-api.service")
    else:
        print("\n⚠️ Certaines erreurs n'ont pas pu être corrigées. Vérifiez les logs ci-dessus.")

if __name__ == "__main__":
    main()
