# GTI700 — Laboratoire 3 — Équipe 02

Un seul diagramme Node-RED regroupe les cinq tâches. Le JavaScript se trouve dans
les nœuds Function. Les deux scripts Python communiquent avec le matériel.

## 1. Préparer le Raspberry Pi

Installer Node-RED et rendre les modules Python `RPi.GPIO` et `smbus2`
accessibles au compte qui lance Node-RED. Pour le DHT11, relier VCC au 3,3 V
(broche physique 1), DATA à **BCM 17** (broche 11) et GND à la broche 6.
Un capteur nu peut nécessiter une résistance de tirage de 4,7 à 10 kΩ entre
DATA et 3,3 V; les modules DHT11 l'intègrent souvent déjà.

Pour le LCD I²C avec adaptateur PCF8574T, relier SDA à GPIO2 (broche 3), SCL à
GPIO3 (broche 5), et partager la masse. Alimenter le module selon ses
spécifications. Si son bus I²C est tiré au 5 V, intercaler un convertisseur de
niveau compatible I²C: les broches du Raspberry Pi ne tolèrent pas le 5 V.
Le flot utilise le DHT11 et le LCD; `thermistor.py` est un exemple séparé.
Activer le bus **I²C 1** pour le LCD.

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

Les sections 1.1 à 1.4 demandent des cadences de **3 s, 20 s et 5 s**. La grille
de correction indique plutôt **2 s, 10 s et 3 s**. Les nœuds Inject permettent
d'ajuster les intervalles; confirmer la cadence attendue avant la démonstration.
Si le LCD passe à 3 s, réduire son délai Exec pour qu'il reste inférieur à cet
intervalle; la pagination doit aussi tenir dans ce délai.

L’adresse météo de l’énoncé renvoyait 404 lors de la vérification. Le nœud HTTP
utilise l’adresse du flux Atom publiée par la page officielle de Montréal.
[Page météo](https://meteo.gc.ca/fr/location/index.html?coords=45.51,-73.55) ·
[Flux Atom](https://meteo.gc.ca/rss/weather/45.51_-73.55_f.xml)
