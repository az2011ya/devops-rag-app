# 1. Utiliser une image Python officielle légère
FROM python:3.12-slim

# 2. Définir le répertoire de travail dans le conteneur
WORKDIR /app

# 3. Copier le fichier des dépendances
COPY requirements.txt .

# 4. Installer les dépendances Python sans conserver le cache pip (pour alléger l'image)
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copier le code source de l'application (main.py)
COPY main.py .

# 6. Exposer le port HTTP de l'API
EXPOSE 8000

# 7. Commande par défaut exécutée au démarrage du conteneur
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
