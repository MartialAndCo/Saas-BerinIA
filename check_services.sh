#!/bin/bash

echo "=== Vérification des services BerinIA ==="
echo ""

echo "1. Service API:"
systemctl status berinia-api.service | grep Active
echo ""

echo "2. Service Git Watcher:"
systemctl status git-watcher.service | grep Active
echo ""

echo "3. Base de données PostgreSQL:"
systemctl status postgresql | grep Active
echo ""

echo "4. Utilisation disque:"
df -h /
echo ""

echo "5. Mémoire disponible:"
free -h
echo ""

echo "=== Vérification terminée ==="
