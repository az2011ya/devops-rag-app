# Runbook Base de Données

Les sauvegardes PostgreSQL sont exécutées tous les jours à **05:00 UTC**.
Les backups sont chiffrés avec AES-256 et conservés pendant 30 jours dans le bucket S3 `company-db-backups`.
En cas de restauration d'urgence, utiliser le script `/opt/scripts/restore_db.sh --latest`.
