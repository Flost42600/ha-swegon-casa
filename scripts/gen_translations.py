"""Generate strings.json and translations/{en,fr}.json from the register table.

Run from the repository root:  python scripts/gen_translations.py
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "custom_components" / "swegon_casa"

spec = importlib.util.spec_from_file_location("registers", COMPONENT / "registers.py")
registers = importlib.util.module_from_spec(spec)
import sys  # noqa: E402

sys.modules["registers"] = registers
spec.loader.exec_module(registers)  # type: ignore[union-attr]

FEATURES = {
    "air_quality": ("Air quality sensors (CO2 / RH / VOC)", "Sondes de qualité d'air (CO2 / HR / COV)"),
    "user_panel": ("Swegon user panel", "Panneau utilisateur Swegon"),
    "heater": ("Re-heater or external heating / cooling", "Post-chauffage ou chauffage / refroidissement externe"),
    "preheater": ("Preheater", "Préchauffage"),
    "cooker_hood": ("Casa cooker hood", "Hotte de cuisine Casa"),
    "vacuum": ("Central vacuum cleaner", "Aspiration centralisée"),
    "gio": ("GIO inputs / outputs set to Modbus", "Entrées / sorties GIO en mode Modbus"),
    "expert": ("Installer settings (airflows, sensor tuning, panel)", "Réglages installateur (débits, sondes, panneau)"),
}

STATIC = {
    "en": {
        "config": {
            "step": {
                "user": {
                    "title": "Connection to the Swegon CASA",
                    "description": "How is the unit connected to Home Assistant?",
                    "menu_options": {"serial": "USB RS-485 adapter (Modbus RTU)", "tcp": "Modbus TCP gateway"},
                },
                "serial": {
                    "title": "USB RS-485 adapter",
                    "description": "Choose the USB RS-485 adapter (not ttyS0, the built-in port). Speed and slave address are detected: if the unit does not answer at the chosen speed, the other usual speeds are tried. The search takes up to about 15 seconds.",
                    "data": {"serial_port": "Serial port", "baudrate": "Baud rate", "parity": "Parity", "stopbits": "Stop bits", "slave": "Slave address (0 = automatic)"},
                },
                "tcp": {
                    "title": "Modbus TCP gateway",
                    "description": "Address of the RS-485 to Ethernet / Wi-Fi gateway. Leave the slave address at 0 to detect it.",
                    "data": {"host": "Host", "tcp_port": "Port", "slave": "Slave address (0 = automatic)"},
                },
                "features": {
                    "title": "Equipment of {model}",
                    "description": "Tick the equipment installed on the unit; only the matching entities are created. Can be changed later.",
                    "data": {"features": "Equipment"},
                },
            },
            "error": {
                "cannot_connect": "The unit does not answer (all usual speeds and addresses were tried): check the wiring (swap A and B), the termination jumper, and that no other integration uses this port.",
                "no_answer_builtin_port": "Nothing answers on this port. It is the computer's built-in serial port, not a USB RS-485 adapter: choose the adapter instead (usually /dev/serial/by-id/usb-… or /dev/ttyUSB0). If it is not in the list, check Settings > System > Hardware.",
                "port_unavailable": "This port cannot be opened: it does not exist, the adapter is unplugged, or another integration (Modbus YAML for example) already uses it.",
                "unknown": "Unexpected error, see the logs.",
            },
            "abort": {"already_configured": "This unit is already configured."},
        },
        "options": {
            "step": {
                "init": {
                    "title": "Options",
                    "data": {"features": "Equipment", "scan_interval": "Measurement interval (s)", "settings_interval": "Settings interval (s)"},
                }
            }
        },
        "exceptions": {"write_failed": {"message": "Could not change {name}: {reason}"}},
    },
    "fr": {
        "config": {
            "step": {
                "user": {
                    "title": "Connexion à la Swegon CASA",
                    "description": "Comment la centrale est-elle reliée à Home Assistant ?",
                    "menu_options": {"serial": "Adaptateur USB RS-485 (Modbus RTU)", "tcp": "Passerelle Modbus TCP"},
                },
                "serial": {
                    "title": "Adaptateur USB RS-485",
                    "description": "Choisissez l'adaptateur USB RS-485 (pas ttyS0, le port intégré). La vitesse et l'adresse esclave sont détectées : si la centrale ne répond pas à la vitesse choisie, les autres vitesses usuelles sont essayées. La recherche dure jusqu'à 15 secondes environ.",
                    "data": {"serial_port": "Port série", "baudrate": "Vitesse (bauds)", "parity": "Parité", "stopbits": "Bits de stop", "slave": "Adresse esclave (0 = automatique)"},
                },
                "tcp": {
                    "title": "Passerelle Modbus TCP",
                    "description": "Adresse de la passerelle RS-485 vers Ethernet / Wi-Fi. Laissez l'adresse esclave à 0 pour la détecter.",
                    "data": {"host": "Hôte", "tcp_port": "Port", "slave": "Adresse esclave (0 = automatique)"},
                },
                "features": {
                    "title": "Équipements de {model}",
                    "description": "Cochez les équipements installés sur la centrale ; seules les entités correspondantes sont créées. Modifiable ensuite.",
                    "data": {"features": "Équipements"},
                },
            },
            "error": {
                "cannot_connect": "La centrale ne répond pas (toutes les vitesses et adresses usuelles ont été essayées) : vérifiez le câblage (inversez A et B), le cavalier de terminaison, et qu'aucune autre intégration n'utilise ce port.",
                "no_answer_builtin_port": "Rien ne répond sur ce port. C'est le port série intégré à l'ordinateur, pas l'adaptateur USB RS-485 : choisissez plutôt l'adaptateur (en général /dev/serial/by-id/usb-… ou /dev/ttyUSB0). S'il n'est pas dans la liste, vérifiez Paramètres > Système > Matériel.",
                "port_unavailable": "Impossible d'ouvrir ce port : il n'existe pas, l'adaptateur est débranché, ou une autre intégration (Modbus en YAML par exemple) l'utilise déjà.",
                "unknown": "Erreur inattendue, voir les journaux.",
            },
            "abort": {"already_configured": "Cette centrale est déjà configurée."},
        },
        "options": {
            "step": {
                "init": {
                    "title": "Options",
                    "data": {"features": "Équipements", "scan_interval": "Intervalle des mesures (s)", "settings_interval": "Intervalle des réglages (s)"},
                }
            }
        },
        "exceptions": {"write_failed": {"message": "Impossible de modifier {name} : {reason}"}},
    },
}

EXTRA_ENTITIES = {
    "sensor": {
        "heat_recovery_efficiency": ("Heat recovery efficiency", "Rendement de récupération"),
        "gio_voltage": ("GIO {index} voltage", "GIO {index} tension"),
    },
    "binary_sensor": {
        "temperature_sensor_failure": ("Temperature sensor failure", "Défaut sonde de température"),
        "gio_input": ("GIO {index} input", "GIO {index} entrée"),
    },
    "switch": {"gio_relay": ("GIO {index} relay", "GIO {index} relais")},
}
PRESETS = {
    "away": ("Away", "Absent"),
    "home": ("Home", "Maison"),
    "boost": ("Boost", "Boost"),
    "travelling": ("Travelling", "Voyage"),
}


def build(lang: str) -> dict:
    out = json.loads(json.dumps(STATIC[lang]))
    i = 0 if lang == "en" else 1
    out["selector"] = {"features": {"options": {k: v[i] for k, v in FEATURES.items()}}}
    entity: dict[str, dict] = {}
    for reg in registers.REGISTERS:
        item: dict = {"name": reg.name_en if lang == "en" else reg.name_fr}
        if reg.options:
            labels = reg.options_en if lang == "en" else reg.options_fr
            item["state"] = {key: labels[key] for key in reg.options.values()}
        entity.setdefault(reg.platform, {})[reg.key] = item
    for platform, items in EXTRA_ENTITIES.items():
        for key, names in items.items():
            entity.setdefault(platform, {})[key] = {"name": names[i]}
    entity["fan"] = {
        "ventilation": {
            "state_attributes": {"preset_mode": {"state": {k: v[i] for k, v in PRESETS.items()}}}
        }
    }
    out["entity"] = {k: entity[k] for k in sorted(entity)}
    return out


def write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    write(COMPONENT / "strings.json", build("en"))
    write(COMPONENT / "translations" / "en.json", build("en"))
    write(COMPONENT / "translations" / "fr.json", build("fr"))
    print("translations written")
