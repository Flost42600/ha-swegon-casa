# Swegon CASA pour Home Assistant

Intégration Home Assistant **locale** pour les centrales de ventilation double flux **Swegon CASA** (contrôleur SCB 3.0 et plus récent : W3, R3, R5, R15…), en **Modbus RTU** (adaptateur USB RS-485) ou **Modbus TCP** (passerelle).

- **Toutes les variables** de la table Modbus Swegon SCB 3.x : environ 150 entités (températures, qualité d'air, débits, ventilateurs, roue, by-pass, dégivrage, alarmes, fonctions Smart, réglages).
- **Ventilateur** avec les modes Absent, Maison, Boost et Voyage, pour les tableaux de bord et les assistants vocaux.
- **Carte de tableau de bord** livrée avec l'intégration : schéma animé de la centrale, avec les deux flux qui se croisent dans l'échangeur à plaques (ou la roue de la série R), colorés selon leur température, le by-pass et son volet en %, les batteries de préchauffe et de post-chauffe, les filtres, les ventilateurs, les modes, la qualité d'air et les alarmes. Une mini-carte existe aussi.
- **Détection automatique** de l'adresse esclave, de la numérotation des registres et de la version du logiciel (3.0 ou 3.1).
- **Seuls les équipements présents** créent des entités : sondes de qualité d'air, panneau, post-chauffage, préchauffage, hotte, aspiration centralisée, entrées/sorties GIO, réglages installateur.
- **Écritures vérifiées** : chaque réglage est contrôlé par rapport aux bornes de la documentation, puis relu après écriture.

![Carte Swegon CASA](docs/carte.png)

## Câblage

| Élément | Réglage |
| --- | --- |
| Liaison | RS-485 (bornes A/B du connecteur Modbus de la carte SEM / SEC) |
| Vitesse | 38 400 bauds (par défaut) |
| Format | 8 bits, sans parité, 1 bit de stop |
| Adresse esclave | 1 (parfois 16), détectée automatiquement |
| Terminaison | Placer le cavalier **JP1** de la carte SEM en position terminaison ; la plupart des adaptateurs USB ont la leur |

Consultez la notice Swegon de votre carte SEM / SEC pour l'emplacement exact des bornes. Si rien ne répond, inversez A et B : c'est l'erreur la plus fréquente.

> Le port série ne peut être utilisé que par un seul programme. Si l'intégration Modbus de Home Assistant (YAML) utilise déjà ce port, retirez-la d'abord.

## Installation

**HACS (recommandé)** : HACS > menu ⋮ > Dépôts personnalisés > `https://github.com/Flost42600/ha-swegon-casa`, type « Intégration ». Installez « Swegon CASA », puis redémarrez Home Assistant.

**Manuelle** : copiez `custom_components/swegon_casa` dans le dossier `config/custom_components/`, puis redémarrez.

## Configuration

1. Paramètres > Appareils et services > Ajouter une intégration > **Swegon CASA**.
2. Choisissez **Adaptateur USB RS-485** ou **Passerelle Modbus TCP**.
3. Choisissez le port (de préférence le chemin `/dev/serial/by-id/…`, qui ne change pas au redémarrage). Laissez l'adresse esclave à **0** pour la détecter.
4. Cochez les **équipements** de votre centrale. Les sondes de qualité d'air et le panneau sont détectés et précochés quand c'est possible.

Les équipements et les intervalles de lecture (15 s pour les mesures, 60 s pour les réglages) se modifient ensuite via **Configurer**.

## Carte de tableau de bord

Elle est chargée automatiquement avec l'intégration : modifier le tableau de bord > Ajouter une carte > **Swegon CASA**, ou en YAML :

```yaml
type: custom:swegon-casa-card        # ou custom:swegon-casa-mini-card
```

Ce que montre le schéma :

- **Échangeur à plaques à flux croisés** : l'air neuf (haut gauche → bas droite) et l'air extrait (haut droite → bas gauche) traversent le bloc de plaques et se croisent au centre. Chaque gaine est colorée de sa température d'entrée à sa température de sortie, et l'air s'anime à la vitesse des ventilateurs. Givre et flocons pendant le dégivrage. Les centrales de la série R affichent une roue qui tourne à sa vitesse réelle.
- **By-pass** : le volet pivote selon l'ouverture en %, le canal de contournement s'allume et les canaux d'air neuf de l'échangeur s'estompent d'autant.
- **Batteries** de préchauffe et de post-chauffe, qui rougeoient selon leur puissance (bleu en rafraîchissement), **filtres** (orange quand ils sont à remplacer), **ventilateurs** avec commande en % et vitesse, températures des quatre flux et de l'ambiance.
- **Modes** Arrêt / Absent / Maison / Boost / Voyage et bouton Cheminée, **alertes** avec bouton « Acquitter » pour le filtre et l'entretien, **tuiles** : rendement, débits en m³/h, ventilateurs, CO₂, humidité, COV, heures avant entretien.

Un clic sur un élément ouvre son entité. En dessous de 640 px de large, la carte passe en version compacte.

| Option | Défaut | Rôle |
| --- | --- | --- |
| `title` | nom de l'appareil | Titre |
| `device_id` | première centrale | Si plusieurs centrales |
| `exchanger` | détecté | `plate` ou `rotor` |
| `show_header`, `show_controls`, `show_stats` | `true` | Masquer l'en-tête, les boutons ou les tuiles |
| `entities` | détectées | Remplacer une entité, ou `null` pour la masquer |
| `navigation_path` | — | Mini-carte : page ouverte au clic sur le schéma |

La carte fonctionne aussi avec une configuration **Modbus YAML** : indiquez vos entités avec `entities:`. Les modes numériques (0 = arrêt … 4 = voyage) sont reconnus.

```yaml
type: custom:swegon-casa-card
title: Ventilation
entities:
  fresh: sensor.casa_air_neuf
  supply: sensor.casa_air_souffle
  extract: sensor.casa_air_extrait
  exhaust: sensor.casa_air_rejete
  ventilation: sensor.casa_mode
  supply_fan: sensor.casa_ventilateur_soufflage
  exhaust_fan: sensor.casa_ventilateur_extraction
  bypass: sensor.casa_bypass
```

Autres clés : `room`, `supply_pre`, `preheater_temp`, `efficiency`, `supply_rpm`, `exhaust_rpm`, `supply_flow`, `exhaust_flow`, `bypass_manual`, `preheater_power`, `preheater_active`, `heater_power`, `cooling`, `defrost`, `night_cooling`, `rotor`, `rotor_rpm`, `co2`, `humidity`, `abs_humidity`, `voc`, `boost_left`, `week_timer`, `alarm`, `filter`, `service`, `hours_service`, `mode` (sélecteur), `fan`, `fireplace`, `confirm_filter`, `confirm_service`.

## Entités principales

| Entité | Type | Registre |
| --- | --- | --- |
| Ventilation (modes Absent / Maison / Boost / Voyage) | ventilateur | 4x5001 |
| Mode de fonctionnement | sélecteur | 4x5001 |
| Réglage Smart (−100 à +100 %) | nombre | 4x5019 |
| Fonction cheminée, mode voyage, arrêt d'urgence | interrupteurs | 4x5002, 4x5004, 4x5018 |
| Pilotage auto par CO2 / humidité / COV | interrupteur / sélecteurs | 4x5009 à 4x5011 |
| Rafraîchissement nocturne | sélecteur + réglages | 4x5164 à 4x5170 |
| Températures air neuf, soufflé, extrait, rejeté, ambiante, panneau | capteurs | 3x6201 à 3x6208 |
| CO2, humidité relative et absolue, COV | capteurs | 3x6212 à 3x6217 |
| Débits et pressions de gaine | capteurs | 3x6218 à 3x6221 |
| État, niveau de ventilation, commande et vitesse des ventilateurs, roue, by-pass | capteurs | 3x6301 à 3x6348 |
| Rendement de récupération (calculé) | capteur | (T soufflé − T neuf) / (T extrait − T neuf) |
| Alarme active (liste en attribut), filtre, entretien, défauts ventilateurs, sondes, roue… | capteurs binaires | 3x6101 à 3x6150 |
| Acquitter : informations, filtre, entretien, défauts | boutons | 4x5401 à 4x5408 |
| Heures avant entretien | capteur | 3x6343 |

Les réglages installateur (vitesses par mode, corrections de sondes, visibilité sur le panneau) existent aussi, désactivés par défaut. La documentation Swegon déconseille de piloter les ventilateurs en continu par ces registres.

## Exemples d'automatisations

**Boost pendant la douche** quand l'humidité dépasse 75 % :

```yaml
alias: CASA – Boost humidité
triggers:
  - trigger: numeric_state
    entity_id: sensor.swegon_casa_w3_humidite_relative
    above: 75
actions:
  - action: fan.set_preset_mode
    target:
      entity_id: fan.swegon_casa_w3
    data:
      preset_mode: boost
```

**Mode Absent** quand tout le monde est parti :

```yaml
alias: CASA – Absent
triggers:
  - trigger: state
    entity_id: zone.home
    to: "0"
    for: "00:15:00"
actions:
  - action: select.select_option
    target:
      entity_id: select.swegon_casa_w3_mode_de_fonctionnement
    data:
      option: away
```

Valeurs du mode : `stopped`, `away`, `home`, `boost`, `travelling`.

## Dépannage

- **La détection tourne sans aboutir** : un bloc `modbus:` en YAML utilise sans doute déjà le port. Commentez-le, redémarrez, puis reprenez la configuration avec le même port, la même vitesse et la même parité que dans le YAML. Avec un adaptateur USB, préférez le chemin `/dev/serial/by-id/usb-…` à `/dev/ttyUSB0` (liste complète : Paramètres > Système > Matériel > Tout le matériel, filtre « tty »).
- **« La centrale ne répond pas »** : vérifiez le port, l'inversion A/B, le cavalier JP1, la vitesse (38 400) et que rien d'autre n'utilise le port.
- **Valeurs décalées** (le CO2 affiche l'humidité, par exemple) : la documentation Swegon numérote les registres à partir de 1. L'intégration détecte ce décalage ; les diagnostics indiquent celui qui a été retenu (`offset`).
- **Diagnostics** : page de l'intégration > ⋮ > Télécharger les diagnostics. Toutes les valeurs brutes y figurent ; le numéro de série est masqué.

## État du projet

Développé à partir de la table « Swegon CASA Smart ModBus Register SCB 3.0/3.1 », et testé avec un simulateur qui reproduit le comportement du bus (décalage d'adresse, registres absents, absence de réponse). Les retours sur d'autres modèles de CASA sont les bienvenus, avec un fichier de diagnostics.

## Développement

```bash
pip install pytest-homeassistant-custom-component pymodbus pyserial
pytest
python scripts/gen_translations.py   # après modification de registers.py
```

## Licence

MIT. Ce projet n'est ni affilié à Swegon ni soutenu par Swegon. Swegon et CASA sont des marques de leurs propriétaires respectifs.
