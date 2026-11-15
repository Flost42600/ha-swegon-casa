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
                    "description": "Default Swegon settings: 38400 baud, no parity, 1 stop bit. Leave the slave address at 0 to detect it.",
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
                "cannot_connect": "The unit does not answer: check the port, the wiring (A/B), the termination jumper and the speed.",
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
                    "description": "Réglages Swegon par défaut : 38 400 bauds, sans parité, 1 bit de stop. Laissez l'adresse esclave à 0 pour la détecter.",
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
                "cannot_connect": "La centrale ne répond pas : vérifiez le port, le câblage (A/B), le cavalier de terminaison et la vitesse.",
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
