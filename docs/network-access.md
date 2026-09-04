# Configuration et Accès Réseau

L'accès SSH aux serveurs de staging se fait uniquement via le bastion **Bastion-01** (IP `10.0.4.12`).
Toutes les connexions nécessitent une clé SSH RSA 4096 bits valide enregistrée auprès de l'équipe InfraOps.
Les ports ouverts par défaut sur l'environnement de staging sont le 80, 443 et 22.
