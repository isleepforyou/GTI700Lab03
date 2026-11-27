# GTI700 — Laboratoire 3 — Équipe 02

Un seul diagramme Node-RED regroupe les cinq tâches. Le JavaScript se trouve dans
les nœuds Function. Les deux scripts Python communiquent avec le matériel.

## 1. Préparer le Raspberry Pi

Installer Node-RED et rendre les modules Python `RPi.GPIO` et `smbus`
(ou `smbus2`)
accessibles au compte qui lance Node-RED. Pour le DHT11, relier VCC au 3,3 V
(broche physique 1), DATA à **BCM 17** (broche 11) et GND à la broche 6.
Un capteur nu peut nécessiter une résistance de tirage de 4,7 à 10 kΩ entre
DATA et 3,3 V; les modules DHT11 l'intègrent souvent déjà.

Pour le LCD1602 I²C avec adaptateur PCF8574T, le schéma du laboratoire utilise
les connexions suivantes :

| LCD | Carte d'extension GPIO | Broche physique du Pi |
| --- | --- | --- |
| VCC | 5V0 | 2 |
| GND | GND | 6 |
| SDA | SDA1 (GPIO2) | 3 |
| SCL | SCL1 (GPIO3) | 5 |

Vérifier que les signaux SDA/SCL côté Raspberry Pi restent à 3,3 V. Si le
module utilise des tirages à 5 V, intercaler un convertisseur de niveau I²C.
Activer le bus **I²C 1** pour le LCD avec `sudo raspi-config` (Interface
Options > I2C), puis redémarrer.

Extraire l’archive dans le dossier personnel de ce compte. Le chemin attendu
pour les scripts est `~/GTI700Lab03/python_examples`. Si le dossier est ailleurs,
définir `GTI700_SCRIPT_DIR` dans l’environnement du processus Node-RED.

Le script LCD utilise un écran **16 × 2** et détecte automatiquement une
adresse répondant dans les plages des PCF8574/PCF8574A (souvent **0x27** ou
**0x3f**). Le code fourni du LCD1602 utilise **0x27**. Vérifier l’adresse
détectée sur le Pi avec `i2cdetect -y 1`. Si
plusieurs périphériques répondent, définir explicitement `GTI700_LCD_ADDRESS`
avec l’adresse du LCD. Selon le montage, définir ensemble
`GTI700_LCD_COLUMNS=20` et `GTI700_LCD_ROWS=4`. Le script suppose que le module
PCF8574T relie P0 à RS, P1 à RW, P2 à E, P3 au rétroéclairage et P4 à P7 aux
quatre bits de données du contrôleur.

Tester l'écran seul, avant de démarrer le flot Node-RED :

```bash
sudo i2cdetect -y 1
python3 ~/GTI700Lab03/python_examples/LCD.py 'GTI700 OK'
```

Pour utiliser exactement l'adresse du code fourni :

```bash
GTI700_LCD_ADDRESS=0x27 python3 ~/GTI700Lab03/python_examples/LCD.py 'GTI700 OK'
```

Si le LCD est détecté mais reste illisible, régler le potentiomètre de contraste
du module. Les erreurs I²C du script sont visibles dans le Debug de Node-RED.

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
