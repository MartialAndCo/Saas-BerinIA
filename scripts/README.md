# Agent Intelligent de Débogage pour Applications Python

Un agent intelligent qui apprend de ses expériences pour diagnostiquer et corriger automatiquement les problèmes courants dans les applications Python, en particulier pour les applications FastAPI.

## Fonctionnalités

- **Mémoire vectorielle**: Stocke et récupère les expériences passées pour résoudre des problèmes similaires
- **Auto-apprentissage**: S'améliore avec le temps grâce à vos feedbacks sur les corrections
- **Rapports détaillés**: Fournit des rapports complets sur les actions entreprises
- **Corrections automatiques** pour les problèmes courants:
  - Problèmes d'indentation
  - Erreurs de sérialisation SQLAlchemy (`dict object has no attribute '_sa_instance_state'`)
  - Problèmes de définition de router FastAPI
  - Conflits de préfixes dans les routes FastAPI

## Installation

```bash
# Cloner le dépôt ou télécharger le script smart_debugger_agent.py
# Installer les dépendances
pip install numpy scikit-learn sentence-transformers
```

## Utilisation

### Analyser une erreur

```bash
python smart_debugger_agent.py analyze --error "NameError: name 'router' is not defined" --file "/path/to/endpoint.py"
```

Cette commande va:
1. Analyser l'erreur
2. Rechercher des expériences similaires dans la mémoire vectorielle
3. Proposer une solution basée sur les expériences passées

### Appliquer une correction

```bash
python smart_debugger_agent.py fix --type router_not_defined --file "/path/to/endpoint.py"
```

Types de correction disponibles:
- `indentation`: Problèmes d'indentation dans les fichiers Python
- `sa_instance_state`: Erreurs liées à la sérialisation des objets SQLAlchemy
- `router_not_defined`: Router FastAPI manquant ou commenté
- `router_prefix_duplicate`: Préfixes dupliqués dans les configurations de router

### Générer un rapport

```bash
python smart_debugger_agent.py report
```

Génère un rapport détaillé sur les corrections appliquées pendant la session en cours.

### Fournir un feedback

```bash
python smart_debugger_agent.py feedback --id "memory_id" --feedback positive
```

Options de feedback:
- `positive`: La correction a fonctionné
- `negative`: La correction n'a pas fonctionné

Le feedback est essentiel pour que l'agent puisse apprendre et s'améliorer. Lorsqu'une correction fonctionne, l'agent privilégiera cette approche pour des problèmes similaires à l'avenir.

### Réinitialiser la session

```bash
python smart_debugger_agent.py reset
```

## Exemple de flux de travail

1. Vous rencontrez une erreur dans votre application
2. Vous analysez l'erreur avec l'agent:
   ```bash
   python smart_debugger_agent.py analyze --error "NameError: name 'router' is not defined" --file "/path/to/endpoints/users.py"
   ```
3. Vous appliquez la correction recommandée:
   ```bash
   python smart_debugger_agent.py fix --type router_not_defined --file "/path/to/endpoints/users.py"
   ```
4. Vous générez un rapport pour voir les modifications:
   ```bash
   python smart_debugger_agent.py report
   ```
5. Vous testez l'application et fournissez un feedback:
   ```bash
   python smart_debugger_agent.py feedback --id "1a2b3c4d-5e6f-7g8h-9i0j" --feedback positive
   ```

## Intégration avec les Outils de CI/CD

L'agent peut être intégré dans un pipeline CI/CD pour détecter et corriger automatiquement les problèmes courants avant le déploiement:

```yaml
# Exemple pour GitHub Actions
jobs:
  debug:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install numpy scikit-learn sentence-transformers
      - name: Run diagnostic
        run: |
          python scripts/smart_debugger_agent.py analyze --error "$(python -m pytest 2>&1 | grep -A 2 "Error")" --context "$(git diff)"
```

## Architecture

L'agent utilise une architecture modulaire:

1. **VectorMemory**: Stockage vectoriel des expériences de débogage
2. **SmartDebugger**: Analyseur et correcteur intelligent qui apprend de l'expérience
3. **CLI**: Interface en ligne de commande pour interagir avec l'agent

## Contribuer

1. Ajoutez de nouveaux correcteurs pour les erreurs courantes
2. Améliorez les algorithmes de détection et de correction
3. Étendez les fonctionnalités à d'autres frameworks Python

## Licence

MIT
