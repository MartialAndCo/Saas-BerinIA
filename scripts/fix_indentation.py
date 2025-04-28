#!/usr/bin/env python3
import os
import datetime
import shutil

def timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def backup_file(file_path):
    """Create a backup of the file."""
    backup_path = f"{file_path}.indent.bak"
    if os.path.exists(file_path):
        shutil.copy2(file_path, backup_path)
        print(f"✅ Backup created: {backup_path}")
        return True
    return False

def fix_niches_indentation():
    """Fix the niches.py indentation error."""
    niches_path = "/root/berinia/backend/app/api/endpoints/niches.py"
    
    if not os.path.exists(niches_path):
        print(f"❌ Niches file not found at {niches_path}")
        return False
    
    backup_file(niches_path)
    
    with open(niches_path, 'r') as f:
        lines = f.readlines()
    
    # Find the get_niches_stats function
    in_stats_function = False
    fixed_lines = []
    
    for line in lines:
        # Check if we're in the "get_niches_stats" function
        if "def get_niches_stats" in line:
            in_stats_function = True
            
        # Fix the indentation for the problematic code block within the stats function
        if in_stats_function and "for niche in niches:" in line:
            # Remove this line completely, as niches is not defined in this function
            continue
        elif in_stats_function and line.strip().startswith("if hasattr(niche, 'campagnes'):"):
            # Skip this line too, as it's part of the problematic block
            continue
        elif in_stats_function and line.strip().startswith("for campagne in niche.campagnes:"):
            # Skip this line too, as it's part of the problematic block
            continue
        elif in_stats_function and line.strip().startswith("if hasattr(campagne, 'leads')"):
            # Skip this line too, as it's part of the problematic block
            continue
        elif in_stats_function and line.strip().startswith("lead_dicts ="):
            # Skip this line too, as it's part of the problematic block
            continue
        elif in_stats_function and line.strip().startswith("for lead in campagne.leads:"):
            # Skip this line too, as it's part of the problematic block
            continue
        elif in_stats_function and line.strip().startswith("lead_dict ="):
            # Skip this line too, as it's part of the problematic block
            continue
        elif in_stats_function and line.strip().startswith("for attr in"):
            # Skip this line too, as it's part of the problematic block
            continue
        elif in_stats_function and line.strip().startswith("if hasattr(lead, attr):"):
            # Skip this line too, as it's part of the problematic block
            continue
        elif in_stats_function and line.strip().startswith("lead_dict[attr] = getattr(lead, attr)"):
            # Skip this line too, as it's part of the problematic block
            continue
        elif in_stats_function and line.strip().startswith("lead_dicts.append(lead_dict)"):
            # Skip this line too, as it's part of the problematic block
            continue
        elif in_stats_function and line.strip().startswith("campagne.leads = lead_dicts"):
            # Skip this line too, as it's part of the problematic block
            continue
            
        fixed_lines.append(line)
        
        # Check if we're leaving the function
        if in_stats_function and line.strip() == "}" and line.strip() in ["}", "return"]:
            in_stats_function = False
    
    # Write the fixed content back
    with open(niches_path, 'w') as f:
        f.writelines(fixed_lines)
    
    print(f"✅ Fixed indentation in niches.py")
    return True

def fix_get_niche_function():
    """Fix the get_niche function that also has an issue with the niches variable."""
    niches_path = "/root/berinia/backend/app/api/endpoints/niches.py"
    
    if not os.path.exists(niches_path):
        print(f"❌ Niches file not found at {niches_path}")
        return False
    
    with open(niches_path, 'r') as f:
        content = f.read()
    
    # Find and fix the get_niche function
    start = content.find("def get_niche(")
    if start == -1:
        print("❌ Could not find get_niche function")
        return False
    
    end = content.find("@router.put", start)
    if end == -1:
        print("❌ Could not find the end of get_niche function")
        return False
    
    # Extract the function
    function = content[start:end]
    
    # Fix the reference to "niches" which is probably meant to be just "niche"
    fixed_function = function.replace("for niche in niches:", "# Add additional niche data processing here")
    
    # Also fix any section using the loop variable that doesn't exist
    fixed_function = fixed_function.replace(
        "    if hasattr(niche, 'campagnes'):  # Vérifier si la niche a des campagnes\n" + 
        "            for campagne in niche.campagnes:  # Pour chaque campagne\n" + 
        "                if hasattr(campagne, 'leads') and campagne.leads:  # Si la campagne a des leads\n" + 
        "                    # Créer des copies des leads avec uniquement les attributs nécessaires\n" + 
        "                    lead_dicts = []\n" + 
        "                    for lead in campagne.leads:\n" + 
        "                        lead_dict = {\"id\": lead.id}\n" + 
        "                        # Ajouter d'autres attributs selon le schéma\n" + 
        "                        for attr in ['nom', 'email', 'phone', 'status']:\n" + 
        "                            if hasattr(lead, attr):\n" + 
        "                                lead_dict[attr] = getattr(lead, attr)\n" + 
        "                        lead_dicts.append(lead_dict)\n" + 
        "                    campagne.leads = lead_dicts",
        "    # Préparer les données pour la sérialisation pour jsonable_encoder"
    )
    
    # Update the original content
    content = content[:start] + fixed_function + content[end:]
    
    # Write the fixed content back
    with open(niches_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Fixed get_niche function in niches.py")
    return True

def main():
    print("=" * 50)
    print(f"🔧 CORRECTION DES ERREURS D'INDENTATION")
    print(f"🕒 {timestamp()}")
    print("=" * 50)
    
    niches_fixed = fix_niches_indentation()
    get_niche_fixed = fix_get_niche_function()
    
    if niches_fixed and get_niche_fixed:
        print("\n✅ Toutes les erreurs d'indentation ont été corrigées.")
        print("\n🔄 Redémarrez le service Berinia pour appliquer les modifications:")
        print("   sudo systemctl restart berinia-api.service")
    else:
        print("\n⚠️ Certaines erreurs n'ont pas pu être corrigées. Vérifiez les logs ci-dessus.")

if __name__ == "__main__":
    main()
