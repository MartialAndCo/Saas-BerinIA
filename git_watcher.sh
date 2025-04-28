#!/bin/bash

WATCH_DIR="/root/berinia"
LOG_FILE="/root/berinia/watcher.log"
MAX_SIZE_KB=500  # Taille maximale du fichier log en KB
IGNORE_FILE="watcher.log"  # Fichier à ignorer complètement

cd $WATCH_DIR

# Vider le fichier log au démarrage
echo "🟢 Git watcher démarré dans $WATCH_DIR le $(date)" > "$LOG_FILE"

# Ajouter le fichier watcher.log à .gitignore s'il n'y est pas déjà
if ! grep -q "^$IGNORE_FILE$" .gitignore 2>/dev/null; then
    echo -e "\n# Git watcher log\n$IGNORE_FILE" >> .gitignore
    git add .gitignore
    git commit -m "🔧 Ajout de $IGNORE_FILE à .gitignore"
    git push origin main
fi

# Supprimer le fichier du suivi Git s'il est déjà suivi
if git ls-files --error-unmatch "$IGNORE_FILE" &>/dev/null; then
    git rm --cached "$IGNORE_FILE"
    git commit -m "🔧 Suppression de $IGNORE_FILE du suivi Git"
    git push origin main
fi

# Surveiller les changements de fichiers en excluant explicitement watcher.log
inotifywait -m -r -e modify,create,delete --exclude '\.git|node_modules|.next|dist|\.log|watcher.log' "$WATCH_DIR" | while read path action file; do
    # Double vérification pour ignorer les fichiers à exclure
    if [[ "$file" == "$IGNORE_FILE" ]] || [[ "$file" == *"~"* ]] || [[ "$file" == *.log ]]; then
        continue
    fi
    
    echo "📁 Changement détecté : $action $file" >> "$LOG_FILE"
    
    # Vérifier s'il y a un fichier de verrouillage Git
    if [ -f "$WATCH_DIR/.git/index.lock" ]; then
        echo "⚠️ Fichier de verrouillage Git détecté, suppression..." >> "$LOG_FILE"
        rm -f "$WATCH_DIR/.git/index.lock"
    fi
    
    # Nettoyer le dépôt Git si nécessaire
    if [ -f "$WATCH_DIR/.git/gc.log" ]; then
        echo "🧹 Nettoyage du dépôt Git..." >> "$LOG_FILE"
        rm -f "$WATCH_DIR/.git/gc.log"
        git gc --prune=now >> "$LOG_FILE" 2>&1
    fi
    
    # Ajouter les changements à Git
    git add .
    
    # Vérifier s'il y a des changements à committer
    if ! git diff --cached --quiet; then
        git commit -m "🛠️ MAJ auto $file - $(date +'%F %T')"
        git push origin main
    fi
    
    # Limiter la taille du fichier log
    if [ -f "$LOG_FILE" ]; then
        size_kb=$(du -k "$LOG_FILE" | cut -f1)
        if [ $size_kb -gt $MAX_SIZE_KB ]; then
            echo "🧹 $(date): Nettoyage du fichier log (taille: ${size_kb}KB)" > "$LOG_FILE"
            echo "🟢 Git watcher redémarré dans $WATCH_DIR" >> "$LOG_FILE"
        fi
    fi
done