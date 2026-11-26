# GTI700 — Laboratoire 3 — Équipe 02

Un seul diagramme Node-RED regroupe les cinq tâches. Le JavaScript se trouve dans
les nœuds Function. Les deux scripts Python communiquent avec le matériel.

## 1. Préparer le Raspberry Pi

Installer Node-RED et rendre les modules Python `RPi.GPIO` et `smbus2`
accessibles au compte qui lance Node-RED. Utiliser le montage du cours, avec
le DHT11 relié à **BCM 17**, et activer le bus **I²C 1** pour le LCD.

Extraire l’archive dans le dossier personnel de ce compte. Le chemin attendu
pour les scripts est `~/gti700-lab3/python_examples`. Si le dossier est ailleurs,
définir `GTI700_SCRIPT_DIR` dans l’environnement du processus Node-RED.

Le script LCD utilise par défaut l’adresse I²C **0x27** et un écran **16 × 2**.
Vérifier l’adresse détectée sur le Pi, par exemple avec `i2cdetect -y 1`. Selon le
montage, définir `GTI700_LCD_ADDRESS`, ou définir ensemble
`GTI700_LCD_COLUMNS=20` et `GTI700_LCD_ROWS=4`. Le script suppose que le module
PCF8574T relie P0 à RS, P1 à RW, P2 à E, P3 au rétroéclairage et P4 à P7 aux
quatre bits de données du contrôleur.

## 2. Importer et déployer

Dans le fichier de configuration Node-RED du Pi, placer l’éditeur sous `/red`
pour libérer la racine `/` pour la page météo. Modifier les propriétés
existantes dans `settings.js`, puis redémarrer Node-RED.

```js
httpAdminRoot: "/red",
httpNodeRoot: "/",
```

Ouvrir `http://<adresse-du-pi>:1880/red/`, importer
`flows-equipe02.json` et déployer. Les nœuds utilisés sont livrés avec Node-RED.

## 3. Vérifier les sorties

- Consulter la fenêtre de débogage pour les statistiques de groupe et les
  conditions actuelles de Montréal.
- Souscrire sur HiveMQ à `gti700e2025/data/emplacements/equipe02/+`.
  Une lecture valide produit deux publications à une décimale toutes les 3 s.
- Observer sur le LCD les quatre modes à 5 s d’intervalle. Sur un 16 × 2, un
  mode trop long est paginé dans son créneau. Si la cadence LCD est ramenée
  à 3 s, la pause de pagination peut être ajustée avec
  `GTI700_LCD_FRAME_SECONDS` et le délai du nœud Exec doit rester inférieur
  à l’intervalle entre deux écritures.
- Depuis un navigateur, ouvrir `/`, `/self`, `/group`, `/group/02` et
  `/outside` sur le port 1880. Une équipe incomplète renvoie `{}` sur sa route.
  `/group` affiche les statistiques déjà disponibles, même si un type de mesure
  n’a encore fourni aucun échantillon.

Les cadences de **3 s, 20 s et 5 s** suivent les sections 1.1 à 1.4 de
l’énoncé. Les nœuds Inject permettent de les ajuster selon la grille de correction
si nécessaire.

L’adresse météo de l’énoncé renvoyait 404 lors de la vérification. Le nœud HTTP
utilise l’adresse du flux Atom publiée par la page officielle de Montréal.
[Page météo](https://meteo.gc.ca/fr/location/index.html?coords=45.51,-73.55) ·
[Flux Atom](https://meteo.gc.ca/rss/weather/45.51_-73.55_f.xml)
