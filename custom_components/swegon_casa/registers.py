"""Swegon CASA Smart Modbus register map (SCB controller, software 3.0 and later).

Source: "Swegon CASA Smart ModBus Register SCB 3.0" (valid for SEM / SEC with
device version 3.0->). Numbers are written as in that document (1-based,
"4x" = holding register, "3x" = input register); the Modbus address actually
sent is number + offset, the offset being detected at setup (normally -1).

Each definition drives one Home Assistant entity. `feature` ties it to an
optional equipment chosen in the options; `sw` limits it to a software range.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

Table = Literal["input", "holding"]
Platform = Literal["sensor", "binary_sensor", "number", "select", "switch", "button"]

# Optional equipment (options flow). "core" is always present.
FEATURES = (
    "air_quality",  # CO2 / RH / VOC sensors
    "user_panel",  # Swegon wall panel (UP1 / UP2)
    "heater",  # re-heater or external heating / cooling device
    "preheater",  # preheater (incl. Nordic)
    "cooker_hood",  # Casa cooker hood damper
    "vacuum",  # central vacuum cleaner
    "gio",  # general purpose inputs / outputs configured for Modbus
    "expert",  # installer settings: airflows, sensor tuning, panel visibility
)
# Deduced from the model name, never shown in the options: R-series units have a rotary exchanger.
AUTO_FEATURES = ("rotor",)


@dataclass(frozen=True, kw_only=True)
class Reg:
    key: str
    number: int  # as in the Swegon document, e.g. 5001 for 4x5001
    table: Table
    platform: Platform
    name_en: str
    name_fr: str
    feature: str = "core"
    signed: bool = False
    scale: float = 1.0  # value = raw * scale
    unit: str | None = None
    device_class: str | None = None
    state_class: str | None = None
    precision: int | None = None
    options: dict[int, str] = field(default_factory=dict)  # raw value -> option key
    options_fr: dict[str, str] = field(default_factory=dict)
    options_en: dict[str, str] = field(default_factory=dict)
    minimum: float | None = None
    maximum: float | None = None
    step: float = 1.0
    category: Literal["config", "diagnostic"] | None = None
    enabled: bool = True
    icon: str | None = None
    sw_min: tuple[int, int] = (3, 0)
    sw_max: tuple[int, int] | None = None  # inclusive
    write_only: bool = False  # e.g. confirm buttons
    state_number: int | None = None  # input register giving the state of a write-only switch
    press_value: int = 1  # value written by a button
    invalid: tuple[int, ...] = ()  # raw values meaning "no sensor"


def _opts(pairs: list[tuple[int, str, str, str]]) -> dict:
    """[(raw, key, fr, en)] -> kwargs for options / labels."""
    return {
        "options": {raw: key for raw, key, _, _ in pairs},
        "options_fr": {key: fr for _, key, fr, _ in pairs},
        "options_en": {key: en for _, key, _, en in pairs},
    }


LEVELS = _opts(
    [
        (0, "off", "Arrêt", "Off"),
        (1, "user", "Utilisateur", "User"),
        (2, "low", "Faible", "Low"),
        (3, "normal", "Normal", "Normal"),
        (4, "high", "Élevé", "High"),
        (5, "full", "Maximal", "Full"),
    ]
)
COOLING_LEVELS = _opts(
    [
        (0, "off", "Arrêt", "Off"),
        (1, "low", "Faible", "Low"),
        (2, "normal", "Normal", "Normal"),
        (3, "high", "Élevé", "High"),
        (4, "full", "Maximal", "Full"),
        (5, "user", "Utilisateur", "User"),
    ]
)
OPERATING_MODES = _opts(
    [
        (0, "stopped", "Arrêt", "Stopped"),
        (1, "away", "Absent", "Away"),
        (2, "home", "Maison", "Home"),
        (3, "boost", "Boost", "Boost"),
        (4, "travelling", "Voyage", "Travelling"),
    ]
)
SENSOR_SOURCES = _opts(
    [
        (0, "internal", "Interne", "Internal"),
        (1, "t6", "T6", "T6"),
        (2, "t7", "T7", "T7"),
        (3, "t8", "T8", "T8"),
        (4, "t9", "T9", "T9"),
    ]
)
TEMP_NO_SENSOR = (-550, 600, 32767, -32768)

C = "°C"
PCT = "%"

REGISTERS: tuple[Reg, ...] = (
    # ------------------------------------------------------------ user settings
    Reg(key="operating_mode", number=5001, table="holding", platform="select",
        name_fr="Mode de fonctionnement", name_en="Operating mode", icon="mdi:fan", **OPERATING_MODES),
    Reg(key="smart_control", number=5019, table="holding", platform="number", signed=True,
        name_fr="Réglage Smart", name_en="Smart control", unit=PCT, minimum=-100, maximum=100, icon="mdi:tune-vertical"),
    Reg(key="emergency_stop", number=5018, table="holding", platform="switch",
        name_fr="Arrêt d'urgence", name_en="Emergency stop", icon="mdi:alert-octagon", category="config"),
    Reg(key="travelling_mode", number=5004, table="holding", platform="switch",
        name_fr="Mode voyage", name_en="Travelling mode", icon="mdi:bag-suitcase"),
    Reg(key="travelling_speed_drop", number=5106, table="holding", platform="number",
        name_fr="Mode voyage : baisse de vitesse", name_en="Travelling speed drop", unit=PCT, minimum=0, maximum=20, category="config"),
    Reg(key="fireplace", number=5002, table="holding", platform="switch", write_only=True, state_number=6335,
        name_fr="Fonction cheminée", name_en="Fireplace function", icon="mdi:fireplace"),
    Reg(key="fireplace_run_time", number=5104, table="holding", platform="number",
        name_fr="Cheminée : durée", name_en="Fireplace run time", unit="min", device_class="duration", minimum=0, maximum=60, category="config"),
    Reg(key="fireplace_max_difference", number=5105, table="holding", platform="number",
        name_fr="Cheminée : écart max de ventilation", name_en="Fireplace max fan difference", unit=PCT, minimum=0, maximum=25, category="config"),
    Reg(key="cooker_hood_damper", number=5005, table="holding", platform="switch", feature="cooker_hood",
        name_fr="Volet de hotte", name_en="Cooker hood damper", icon="mdi:stove"),
    Reg(key="cooker_hood_function", number=5020, table="holding", platform="switch", feature="cooker_hood",
        name_fr="Fonction hotte", name_en="Cooker hood function", category="config"),
    Reg(key="cooker_hood_home_compensation", number=5109, table="holding", platform="number", feature="cooker_hood",
        name_fr="Hotte : compensation Maison", name_en="Cooker hood home compensation", unit=PCT, minimum=0, maximum=50, category="config"),
    Reg(key="cooker_hood_boost_compensation", number=5110, table="holding", platform="number", feature="cooker_hood",
        name_fr="Hotte : compensation Boost", name_en="Cooker hood boost compensation", unit=PCT, minimum=0, maximum=50, category="config"),
    Reg(key="cooker_hood_boost", number=5151, table="holding", platform="number", feature="cooker_hood",
        name_fr="Hotte : vitesse minimale", name_en="Cooker hood minimum fan speed", unit=PCT, minimum=0, maximum=100, category="config"),
    Reg(key="central_vacuum", number=5006, table="holding", platform="switch", feature="vacuum",
        name_fr="Aspiration centralisée", name_en="Central vacuum cleaner", icon="mdi:vacuum"),
    Reg(key="central_vacuum_run_time", number=5112, table="holding", platform="number", feature="vacuum",
        name_fr="Aspiration : durée", name_en="Central vacuum run time", unit="min", device_class="duration", minimum=0, maximum=60, category="config"),
    Reg(key="central_vacuum_compensation", number=5113, table="holding", platform="number", feature="vacuum",
        name_fr="Aspiration : compensation", name_en="Central vacuum compensation", unit=PCT, minimum=0, maximum=50, category="config"),
    # Automatic functions (air quality sensors)
    Reg(key="auto_co2", number=5009, table="holding", platform="switch", feature="air_quality",
        name_fr="Pilotage auto par CO2", name_en="Auto CO2 control", icon="mdi:molecule-co2"),
    Reg(key="auto_co2_home_limit", number=5114, table="holding", platform="number", feature="air_quality",
        name_fr="CO2 : seuil Maison", name_en="CO2 home limit", unit="ppm", minimum=0, maximum=2000, step=10, category="config"),
    Reg(key="auto_co2_away_limit", number=5115, table="holding", platform="number", feature="air_quality",
        name_fr="CO2 : seuil Absent", name_en="CO2 away limit", unit="ppm", minimum=0, maximum=2000, step=10, category="config"),
    Reg(key="auto_humidity", number=5010, table="holding", platform="select", feature="air_quality", sw_min=(3, 1),
        name_fr="Pilotage auto par humidité", name_en="Auto humidity control", icon="mdi:water-percent", **LEVELS),
    Reg(key="auto_humidity_switch", number=5010, table="holding", platform="switch", feature="air_quality", sw_max=(3, 0),
        name_fr="Pilotage auto par humidité", name_en="Auto humidity control", icon="mdi:water-percent"),
    Reg(key="auto_humidity_boost_limit", number=5117, table="holding", platform="number", feature="air_quality",
        name_fr="Humidité : seuil Boost", name_en="Humidity boost limit", unit=PCT, minimum=0, maximum=50, category="config"),
    Reg(key="auto_humidity_full_boost_limit", number=5118, table="holding", platform="number", feature="air_quality",
        name_fr="Humidité : seuil Boost max", name_en="Humidity full boost limit", unit=PCT, minimum=0, maximum=50, category="config"),
    Reg(key="auto_humidity_boost_delay", number=5119, table="holding", platform="number", feature="air_quality", sw_min=(3, 1),
        name_fr="Humidité : délai du Boost", name_en="Humidity boost delay", unit="min", device_class="duration", minimum=0, maximum=30, category="config"),
    Reg(key="auto_humidity_boost_during_delay", number=5120, table="holding", platform="number", feature="air_quality", sw_min=(3, 1),
        name_fr="Humidité : Boost pendant le délai", name_en="Humidity boost during delay", unit=PCT, minimum=0, maximum=25, category="config"),
    Reg(key="auto_air_quality", number=5011, table="holding", platform="select", feature="air_quality", sw_min=(3, 1),
        name_fr="Pilotage auto par COV", name_en="Auto air quality control", icon="mdi:air-filter", **LEVELS),
    Reg(key="auto_air_quality_switch", number=5011, table="holding", platform="switch", feature="air_quality", sw_max=(3, 0),
        name_fr="Pilotage auto par COV", name_en="Auto air quality control", icon="mdi:air-filter"),
    Reg(key="auto_air_quality_boost_limit", number=5121, table="holding", platform="number", feature="air_quality",
        name_fr="COV : seuil Boost", name_en="Air quality boost limit", unit="ppm", minimum=0, maximum=2000, step=10, category="config"),
    Reg(key="auto_air_quality_full_boost_limit", number=5122, table="holding", platform="number", feature="air_quality",
        name_fr="COV : seuil Boost max", name_en="Air quality full boost limit", unit="ppm", minimum=0, maximum=2000, step=10, category="config"),
    # Summer night cooling
    Reg(key="summer_cooling", number=5164, table="holding", platform="select",
        name_fr="Rafraîchissement nocturne", name_en="Summer night cooling", icon="mdi:weather-night", **COOLING_LEVELS),
    Reg(key="summer_cooling_fresh_limit", number=5165, table="holding", platform="number",
        name_fr="Rafraîchissement : limite air neuf", name_en="Summer cooling fresh air limit", unit=C, device_class="temperature", minimum=0, maximum=25, category="config"),
    Reg(key="summer_cooling_fresh_start", number=5166, table="holding", platform="number",
        name_fr="Rafraîchissement : démarrage air neuf", name_en="Summer cooling fresh air start", unit=C, device_class="temperature", minimum=0, maximum=25, category="config"),
    Reg(key="summer_cooling_room_limit", number=5167, table="holding", platform="number",
        name_fr="Rafraîchissement : limite pièce", name_en="Summer cooling room limit", unit=C, device_class="temperature", minimum=0, maximum=35, category="config"),
    Reg(key="summer_cooling_min_supply", number=5168, table="holding", platform="number",
        name_fr="Rafraîchissement : soufflage minimum", name_en="Summer cooling minimum supply", unit=C, device_class="temperature", minimum=10, maximum=25, category="config"),
    Reg(key="summer_cooling_open_hood", number=5177, table="holding", platform="switch", feature="cooker_hood",
        name_fr="Rafraîchissement : ouvrir la hotte", name_en="Summer cooling opens hood damper", category="config"),
    Reg(key="summer_cooling_boost", number=5169, table="holding", platform="select",
        name_fr="Rafraîchissement : Boost", name_en="Summer cooling boost", category="config", **COOLING_LEVELS),
    Reg(key="summer_cooling_boost_limit", number=5170, table="holding", platform="number",
        name_fr="Rafraîchissement : seuil Boost", name_en="Summer cooling boost limit", unit=C, device_class="temperature", minimum=18, maximum=28, category="config"),
    Reg(key="summer_cooling_full_boost_limit", number=5125, table="holding", platform="number", sw_min=(3, 1),
        name_fr="Rafraîchissement : seuil Boost max", name_en="Summer cooling full boost limit", unit=C, device_class="temperature", minimum=18, maximum=40, category="config"),
    # Heating
    Reg(key="heating_boost", number=5012, table="holding", platform="switch", feature="heater",
        name_fr="Boost chauffage", name_en="Heating boost", icon="mdi:radiator"),
    Reg(key="heating_boost_gain", number=5124, table="holding", platform="number", feature="heater",
        name_fr="Boost chauffage : gain", name_en="Heating boost gain", unit=PCT, minimum=0, maximum=100, category="config"),
    Reg(key="temperature_setpoint", number=5101, table="holding", platform="number", feature="heater",
        name_fr="Consigne de température", name_en="Temperature setpoint", unit=C, device_class="temperature", minimum=13, maximum=25, icon="mdi:thermometer"),
    Reg(key="heating_mode", number=5174, table="holding", platform="select", feature="heater", sw_min=(3, 1),
        name_fr="Mode de chauffe", name_en="Heating mode", category="config",
        **_opts([(1, "eco", "Éco", "Eco"), (2, "comfort", "Confort", "Comfort")])),
    Reg(key="temperature_control_method", number=5130, table="holding", platform="select", feature="heater",
        name_fr="Régulation de température", name_en="Temperature control method", category="config",
        **_opts([(0, "supply", "Air soufflé", "Supply air"), (1, "room", "Air ambiant", "Room air")])),
    Reg(key="travelling_temperature_drop", number=5107, table="holding", platform="number", feature="heater",
        name_fr="Mode voyage : baisse de consigne", name_en="Travelling temperature drop", unit=C, minimum=0, maximum=10, category="config"),
    Reg(key="away_temperature_drop", number=5171, table="holding", platform="number", feature="heater",
        name_fr="Mode absent : baisse de consigne", name_en="Away temperature drop", unit=C, minimum=0, maximum=10, category="config"),
    Reg(key="internal_post_heater", number=5014, table="holding", platform="switch", feature="heater",
        name_fr="Post-chauffage interne", name_en="Internal post heater", category="config"),
    Reg(key="external_post_heater", number=5016, table="holding", platform="switch", feature="heater",
        name_fr="Post-chauffage externe", name_en="External post heater", category="config"),
    Reg(key="external_cooling", number=5015, table="holding", platform="switch", feature="heater",
        name_fr="Refroidissement externe", name_en="External cooling", category="config"),
    Reg(key="heating_fresh_limit", number=5129, table="holding", platform="number", feature="heater", signed=True,
        name_fr="Chauffage autorisé sous (air neuf)", name_en="Heating fresh air limit", unit=C, device_class="temperature", minimum=-50, maximum=50, category="config"),
    # Service
    Reg(key="service_reminder", number=5141, table="holding", platform="switch",
        name_fr="Rappel d'entretien", name_en="Service reminder", category="config"),
    Reg(key="service_interval", number=5142, table="holding", platform="number",
        name_fr="Intervalle d'entretien", name_en="Service interval", unit="mois", minimum=0, maximum=12, category="config"),
    # Expert: airflows (the document: "don't use for external fan control")
    Reg(key="away_supply_speed", number=5302, table="holding", platform="number", feature="expert", enabled=False,
        name_fr="Absent : vitesse soufflage", name_en="Away supply fan speed", unit=PCT, minimum=20, maximum=100, category="config"),
    Reg(key="away_exhaust_speed", number=5303, table="holding", platform="number", feature="expert", enabled=False,
        name_fr="Absent : vitesse extraction", name_en="Away exhaust fan speed", unit=PCT, minimum=20, maximum=100, category="config"),
    Reg(key="home_supply_speed", number=5304, table="holding", platform="number", feature="expert", enabled=False,
        name_fr="Maison : vitesse soufflage", name_en="Home supply fan speed", unit=PCT, minimum=20, maximum=100, category="config"),
    Reg(key="home_exhaust_speed", number=5305, table="holding", platform="number", feature="expert", enabled=False,
        name_fr="Maison : vitesse extraction", name_en="Home exhaust fan speed", unit=PCT, minimum=20, maximum=100, category="config"),
    Reg(key="boost_supply_speed", number=5306, table="holding", platform="number", feature="expert", enabled=False,
        name_fr="Boost : vitesse soufflage", name_en="Boost supply fan speed", unit=PCT, minimum=20, maximum=100, category="config"),
    Reg(key="boost_exhaust_speed", number=5307, table="holding", platform="number", feature="expert", enabled=False,
        name_fr="Boost : vitesse extraction", name_en="Boost exhaust fan speed", unit=PCT, minimum=20, maximum=100, category="config"),
    Reg(key="max_smart_boost", number=5308, table="holding", platform="number", feature="expert", enabled=False,
        name_fr="Limite du Boost Smart", name_en="Max smart boost limitation", unit=PCT, minimum=0, maximum=100, category="config"),
    Reg(key="room_temperature_fine_tuning", number=5132, table="holding", platform="number", feature="expert", signed=True, scale=0.1,
        name_fr="Correction sonde ambiante", name_en="Room temperature fine tuning", unit=C, minimum=-5, maximum=5, step=0.1, category="config", enabled=False),
    Reg(key="supply_temperature_fine_tuning", number=5155, table="holding", platform="number", feature="expert", signed=True, scale=0.1,
        name_fr="Correction sonde soufflage", name_en="Supply temperature fine tuning", unit=C, minimum=-5, maximum=5, step=0.1, category="config", enabled=False),
    Reg(key="room_temperature_sensor", number=5152, table="holding", platform="sensor", feature="expert", category="diagnostic",
        name_fr="Sonde ambiante utilisée", name_en="Room temperature sensor", device_class="enum",
        **_opts([(0, "internal", "Interne", "Internal"), (1, "t6", "T6", "T6"), (2, "t7", "T7", "T7"), (3, "t8", "T8", "T8"),
                 (4, "t9", "T9", "T9"), (5, "up1", "Panneau 1", "Panel 1"), (6, "up2", "Panneau 2", "Panel 2")])),
    Reg(key="ventilation_control_mode", number=5311, table="holding", platform="sensor", feature="expert", category="diagnostic",
        name_fr="Mode de régulation des débits", name_en="Ventilation control mode", device_class="enum",
        **_opts([(0, "normal", "Normal", "Normal"), (1, "pa_supply", "Pression soufflage", "Supply pressure"),
                 (2, "pa_extract", "Pression extraction", "Extract pressure"), (3, "pa", "Pression", "Pressure"),
                 (4, "airflow", "Débit (l/s)", "Airflow (l/s)"), (5, "other", "Autre", "Other")])),
    # Panel visibility of smart functions
    Reg(key="visibility_shutdown", number=5207, table="holding", platform="switch", feature="user_panel", enabled=False,
        name_fr="Panneau : afficher l'arrêt", name_en="Panel: show shutdown", category="config"),
    Reg(key="visibility_travelling", number=5202, table="holding", platform="switch", feature="user_panel", enabled=False,
        name_fr="Panneau : afficher le mode voyage", name_en="Panel: show travelling", category="config"),
    Reg(key="visibility_fireplace", number=5201, table="holding", platform="switch", feature="user_panel", enabled=False,
        name_fr="Panneau : afficher la cheminée", name_en="Panel: show fireplace", category="config"),
    Reg(key="visibility_summer_cooling", number=5205, table="holding", platform="switch", feature="user_panel", enabled=False,
        name_fr="Panneau : afficher le rafraîchissement", name_en="Panel: show summer cooling", category="config"),
    Reg(key="visibility_humidity", number=5208, table="holding", platform="switch", feature="user_panel", enabled=False,
        name_fr="Panneau : afficher les fonctions auto", name_en="Panel: show auto functions", category="config"),
    # ---------------------------------------------------------------- buttons
    Reg(key="reset_info_alarms", number=5406, table="holding", platform="button", write_only=True,
        name_fr="Acquitter les informations", name_en="Confirm info alarms", icon="mdi:bell-check"),
    Reg(key="confirm_filter", number=5404, table="holding", platform="button", write_only=True,
        name_fr="Acquitter le contrôle filtre", name_en="Confirm filter guard", icon="mdi:air-filter"),
    Reg(key="confirm_service", number=5405, table="holding", platform="button", write_only=True,
        name_fr="Acquitter le rappel d'entretien", name_en="Confirm service reminder", icon="mdi:wrench-check"),
    Reg(key="confirm_fan_failure", number=5407, table="holding", platform="button", write_only=True, category="config",
        name_fr="Acquitter le défaut ventilateur", name_en="Confirm fan failure", enabled=False),
    Reg(key="confirm_sensor_failure", number=5408, table="holding", platform="button", write_only=True, category="config",
        name_fr="Acquitter le défaut sonde", name_en="Confirm sensor failure", enabled=False),
    Reg(key="confirm_freezing", number=5403, table="holding", platform="button", write_only=True, category="config", feature="heater",
        name_fr="Acquitter le risque de gel", name_en="Confirm freezing danger", enabled=False),
    Reg(key="confirm_reheater", number=5401, table="holding", platform="button", write_only=True, category="config", feature="heater",
        name_fr="Acquitter le défaut post-chauffage", name_en="Confirm re-heater failure", enabled=False),
    Reg(key="confirm_preheater", number=5402, table="holding", platform="button", write_only=True, category="config", feature="preheater",
        name_fr="Acquitter le défaut préchauffage", name_en="Confirm preheater failure", enabled=False),
    # ------------------------------------------------------------ measurements
    Reg(key="fresh_air_temperature", number=6201, table="input", platform="sensor", signed=True, scale=0.1, invalid=TEMP_NO_SENSOR,
        name_fr="Température air neuf", name_en="Fresh air temperature", unit=C, device_class="temperature", state_class="measurement", precision=1),
    Reg(key="supply_before_heater_temperature", number=6202, table="input", platform="sensor", signed=True, scale=0.1, invalid=TEMP_NO_SENSOR, feature="heater",
        name_fr="Température avant post-chauffage", name_en="Supply before re-heater temperature", unit=C, device_class="temperature", state_class="measurement", precision=1),
    Reg(key="supply_air_temperature", number=6203, table="input", platform="sensor", signed=True, scale=0.1, invalid=TEMP_NO_SENSOR,
        name_fr="Température air soufflé", name_en="Supply air temperature", unit=C, device_class="temperature", state_class="measurement", precision=1),
    Reg(key="extract_air_temperature", number=6204, table="input", platform="sensor", signed=True, scale=0.1, invalid=TEMP_NO_SENSOR,
        name_fr="Température air extrait", name_en="Extract air temperature", unit=C, device_class="temperature", state_class="measurement", precision=1),
    Reg(key="exhaust_air_temperature", number=6205, table="input", platform="sensor", signed=True, scale=0.1, invalid=TEMP_NO_SENSOR,
        name_fr="Température air rejeté", name_en="Exhaust air temperature", unit=C, device_class="temperature", state_class="measurement", precision=1),
    Reg(key="room_temperature", number=6206, table="input", platform="sensor", signed=True, scale=0.1, invalid=TEMP_NO_SENSOR,
        name_fr="Température ambiante", name_en="Room temperature", unit=C, device_class="temperature", state_class="measurement", precision=1),
    Reg(key="panel1_temperature", number=6207, table="input", platform="sensor", signed=True, scale=0.1, invalid=TEMP_NO_SENSOR, feature="user_panel",
        name_fr="Température panneau 1", name_en="User panel 1 temperature", unit=C, device_class="temperature", state_class="measurement", precision=1),
    Reg(key="panel2_temperature", number=6208, table="input", platform="sensor", signed=True, scale=0.1, invalid=TEMP_NO_SENSOR, feature="user_panel", enabled=False,
        name_fr="Température panneau 2", name_en="User panel 2 temperature", unit=C, device_class="temperature", state_class="measurement", precision=1),
    Reg(key="water_radiator_temperature", number=6209, table="input", platform="sensor", signed=True, scale=0.1, invalid=TEMP_NO_SENSOR, feature="heater",
        name_fr="Température batterie eau", name_en="Water radiator temperature", unit=C, device_class="temperature", state_class="measurement", precision=1),
    Reg(key="preheater_temperature", number=6210, table="input", platform="sensor", signed=True, scale=0.1, invalid=TEMP_NO_SENSOR, feature="preheater",
        name_fr="Température préchauffage", name_en="Pre-heater temperature", unit=C, device_class="temperature", state_class="measurement", precision=1),
    Reg(key="external_fresh_air_temperature", number=6211, table="input", platform="sensor", signed=True, scale=0.1, invalid=TEMP_NO_SENSOR, feature="preheater",
        name_fr="Température air neuf externe", name_en="External fresh air temperature", unit=C, device_class="temperature", state_class="measurement", precision=1),
    Reg(key="co2_unfiltered", number=6212, table="input", platform="sensor", feature="air_quality", enabled=False,
        name_fr="CO2 (brut)", name_en="CO2 (unfiltered)", unit="ppm", device_class="carbon_dioxide", state_class="measurement"),
    Reg(key="co2", number=6213, table="input", platform="sensor", feature="air_quality",
        name_fr="CO2", name_en="CO2", unit="ppm", device_class="carbon_dioxide", state_class="measurement"),
    Reg(key="humidity", number=6214, table="input", platform="sensor", feature="air_quality",
        name_fr="Humidité relative", name_en="Relative humidity", unit=PCT, device_class="humidity", state_class="measurement"),
    Reg(key="absolute_humidity", number=6215, table="input", platform="sensor", feature="air_quality", scale=0.1,
        name_fr="Humidité absolue", name_en="Absolute humidity", unit="g/m³", state_class="measurement", precision=1, icon="mdi:water"),
    Reg(key="absolute_humidity_setpoint", number=6216, table="input", platform="sensor", feature="air_quality", scale=0.1, category="diagnostic",
        name_fr="Consigne d'humidité absolue", name_en="Absolute humidity setpoint", unit="g/m³", state_class="measurement", precision=1, icon="mdi:water"),
    Reg(key="voc", number=6217, table="input", platform="sensor", feature="air_quality",
        name_fr="COV", name_en="VOC", unit="ppm", state_class="measurement", icon="mdi:air-filter"),
    Reg(key="supply_duct_pressure", number=6218, table="input", platform="sensor",
        name_fr="Pression gaine soufflage", name_en="Supply duct pressure", unit="Pa", device_class="pressure", state_class="measurement", category="diagnostic"),
    Reg(key="exhaust_duct_pressure", number=6219, table="input", platform="sensor",
        name_fr="Pression gaine extraction", name_en="Exhaust duct pressure", unit="Pa", device_class="pressure", state_class="measurement", category="diagnostic"),
    Reg(key="supply_airflow", number=6220, table="input", platform="sensor",
        name_fr="Débit soufflage", name_en="Supply airflow", unit="L/s", device_class="volume_flow_rate", state_class="measurement"),
    Reg(key="exhaust_airflow", number=6221, table="input", platform="sensor",
        name_fr="Débit extraction", name_en="Exhaust airflow", unit="L/s", device_class="volume_flow_rate", state_class="measurement"),
    # ------------------------------------------------------------ unit status
    Reg(key="unit_state", number=6301, table="input", platform="sensor", device_class="enum",
        name_fr="État de la centrale", name_en="Unit state",
        **_opts([(0, "external_stop", "Arrêt externe", "External stop"), (1, "user_stopped", "Arrêtée", "Stopped by user"),
                 (2, "starting", "Démarrage", "Starting"), (3, "normal", "Normal", "Normal"), (4, "commissioning", "Mise en service", "Commissioning")])),
    Reg(key="ventilation_state", number=6302, table="input", platform="sensor", device_class="enum",
        name_fr="Niveau de ventilation", name_en="Ventilation level",
        **_opts([(0, "stopped", "Arrêt", "Stopped"), (1, "away", "Absent", "Away"), (2, "home", "Maison", "Home"),
                 (3, "boost", "Boost", "Boost"), (4, "travelling", "Voyage", "Travelling")])),
    Reg(key="supply_fan_control", number=6303, table="input", platform="sensor",
        name_fr="Commande ventilateur soufflage", name_en="Supply fan control", unit=PCT, state_class="measurement", icon="mdi:fan"),
    Reg(key="exhaust_fan_control", number=6304, table="input", platform="sensor",
        name_fr="Commande ventilateur extraction", name_en="Exhaust fan control", unit=PCT, state_class="measurement", icon="mdi:fan"),
    Reg(key="supply_fan_rpm", number=6305, table="input", platform="sensor",
        name_fr="Vitesse ventilateur soufflage", name_en="Supply fan speed", unit="tr/min", state_class="measurement", icon="mdi:fan", category="diagnostic"),
    Reg(key="exhaust_fan_rpm", number=6306, table="input", platform="sensor",
        name_fr="Vitesse ventilateur extraction", name_en="Exhaust fan speed", unit="tr/min", state_class="measurement", icon="mdi:fan", category="diagnostic"),
    Reg(key="rotor_rpm", number=6234, table="input", platform="sensor", feature="rotor",
        name_fr="Vitesse de la roue", name_en="Rotor speed", unit="tr/min", state_class="measurement", icon="mdi:rotate-right", category="diagnostic"),
    Reg(key="boost_time_left", number=6308, table="input", platform="sensor",
        name_fr="Temps restant (fonction minutée)", name_en="Timed function remaining", unit="min", device_class="duration", icon="mdi:timer-sand"),
    Reg(key="a_plus_control", number=6310, table="input", platform="sensor", feature="air_quality", signed=True, category="diagnostic",
        name_fr="Régulation A+ (CO2)", name_en="A+ control", unit=PCT, state_class="measurement"),
    Reg(key="auto_humidity_level", number=6311, table="input", platform="sensor", feature="air_quality", category="diagnostic",
        name_fr="Régulation humidité", name_en="Auto RH control level", unit=PCT, state_class="measurement"),
    Reg(key="auto_air_quality_level", number=6312, table="input", platform="sensor", feature="air_quality", category="diagnostic",
        name_fr="Régulation COV", name_en="Auto air quality level", unit=PCT, state_class="measurement"),
    Reg(key="auto_temperature_boost_level", number=6313, table="input", platform="sensor", feature="heater", category="diagnostic",
        name_fr="Régulation boost température", name_en="Auto temperature boost level", unit=PCT, state_class="measurement"),
    Reg(key="fan_speed_limit", number=6314, table="input", platform="sensor", signed=True, category="diagnostic",
        name_fr="Limitation de vitesse", name_en="Fan speed limit control", unit=PCT, state_class="measurement"),
    Reg(key="smart_control_level", number=6315, table="input", platform="sensor", signed=True, category="diagnostic",
        name_fr="Niveau Smart appliqué", name_en="Smart control level", unit=PCT, state_class="measurement"),
    Reg(key="temperature_setpoint_active", number=6316, table="input", platform="sensor", feature="heater",
        name_fr="Consigne de température appliquée", name_en="Active temperature setpoint", unit=C, device_class="temperature", state_class="measurement"),
    Reg(key="supply_control_power", number=6317, table="input", platform="sensor", feature="heater",
        name_fr="Puissance chauffage / refroidissement", name_en="Heating / cooling output", unit=PCT, state_class="measurement", icon="mdi:radiator"),
    Reg(key="room_supply_setpoint", number=6320, table="input", platform="sensor", feature="heater", scale=0.1, category="diagnostic",
        name_fr="Consigne de soufflage calculée", name_en="Room controller supply setpoint", unit=C, device_class="temperature", state_class="measurement", precision=1),
    Reg(key="defrost", number=6328, table="input", platform="binary_sensor",
        name_fr="Dégivrage", name_en="Defrost", icon="mdi:snowflake-melt"),
    Reg(key="rotor_active", number=6332, table="input", platform="binary_sensor", feature="rotor",
        name_fr="Roue en rotation", name_en="Rotor active", device_class="running", icon="mdi:rotate-right"),
    Reg(key="preheater_active", number=6333, table="input", platform="binary_sensor", feature="preheater",
        name_fr="Préchauffage actif", name_en="Preheater active", device_class="heat"),
    Reg(key="summer_cooling_active", number=6334, table="input", platform="binary_sensor",
        name_fr="Rafraîchissement nocturne actif", name_en="Summer cooling active", icon="mdi:weather-night"),
    Reg(key="cooling_active", number=6323, table="input", platform="binary_sensor", feature="heater",
        name_fr="Refroidissement actif", name_en="Cooling active", device_class="cold"),
    Reg(key="travelling_active", number=6307, table="input", platform="binary_sensor",
        name_fr="Mode voyage actif", name_en="Travelling active", icon="mdi:bag-suitcase"),
    Reg(key="week_timer_active", number=6309, table="input", platform="binary_sensor", category="diagnostic",
        name_fr="Programme hebdomadaire actif", name_en="Week timer active", icon="mdi:calendar-clock"),
    Reg(key="central_vacuum_active", number=6336, table="input", platform="binary_sensor", feature="vacuum",
        name_fr="Aspiration centralisée active", name_en="Central vacuum active"),
    Reg(key="hood_compensation_active", number=6337, table="input", platform="binary_sensor", feature="cooker_hood",
        name_fr="Compensation hotte active", name_en="Hood compensation active"),
    Reg(key="external_boost_active", number=6338, table="input", platform="binary_sensor", category="diagnostic",
        name_fr="Boost externe actif", name_en="External boost active"),
    Reg(key="external_away_active", number=6339, table="input", platform="binary_sensor", category="diagnostic",
        name_fr="Absent externe actif", name_en="External away active"),
    Reg(key="manual_bypass", number=6340, table="input", platform="sensor", device_class="enum", category="diagnostic",
        name_fr="By-pass manuel", name_en="Manual bypass plate",
        **_opts([(0, "closed", "Fermé (hiver)", "Closed (winter)"), (1, "open", "Ouvert (été)", "Open (summer)")])),
    Reg(key="bypass_position", number=6348, table="input", platform="sensor",
        name_fr="Position du by-pass", name_en="Bypass position", unit=PCT, state_class="measurement", icon="mdi:valve"),
    Reg(key="filter_guard_input", number=6342, table="input", platform="binary_sensor", category="diagnostic",
        name_fr="Entrée contrôle filtre", name_en="Filter guard input", device_class="problem"),
    Reg(key="hours_to_service", number=6343, table="input", platform="sensor",
        name_fr="Heures avant entretien", name_en="Hours to next service", unit="h", device_class="duration", icon="mdi:wrench-clock"),
    Reg(key="preheater_power", number=6344, table="input", platform="sensor", feature="preheater",
        name_fr="Puissance préchauffage", name_en="Preheater output", unit=PCT, state_class="measurement"),
    Reg(key="nordic_preheater_power", number=6345, table="input", platform="sensor", feature="preheater",
        name_fr="Puissance préchauffage Nordic", name_en="Nordic preheater output", unit=PCT, state_class="measurement"),
    Reg(key="defrost_supply_limit", number=6346, table="input", platform="sensor", category="diagnostic",
        name_fr="Dégivrage : limitation soufflage", name_en="Defrost supply limit", unit=PCT, state_class="measurement"),
    Reg(key="defrost_exhaust_forcing", number=6347, table="input", platform="sensor", category="diagnostic",
        name_fr="Dégivrage : forçage extraction", name_en="Defrost exhaust forcing", unit=PCT, state_class="measurement"),
    # ------------------------------------------------------------------ alarms
    Reg(key="alarm", number=6132, table="input", platform="binary_sensor", device_class="problem",
        name_fr="Alarme active", name_en="Active alarm"),
    Reg(key="info", number=6133, table="input", platform="binary_sensor", device_class="problem",
        name_fr="Information non acquittée", name_en="Unconfirmed info"),
    Reg(key="filter_info", number=6130, table="input", platform="binary_sensor", device_class="problem",
        name_fr="Filtre à remplacer", name_en="Filter guard info", icon="mdi:air-filter"),
    Reg(key="service_info", number=6129, table="input", platform="binary_sensor", device_class="problem",
        name_fr="Entretien à faire", name_en="Service info", icon="mdi:wrench"),
    Reg(key="emergency_stop_active", number=6131, table="input", platform="binary_sensor", device_class="problem",
        name_fr="Arrêt d'urgence actif", name_en="Emergency stop active"),
    Reg(key="supply_fan_failure", number=6125, table="input", platform="binary_sensor", device_class="problem",
        name_fr="Défaut ventilateur soufflage", name_en="Supply fan failure"),
    Reg(key="exhaust_fan_failure", number=6127, table="input", platform="binary_sensor", device_class="problem",
        name_fr="Défaut ventilateur extraction", name_en="Exhaust fan failure"),
    Reg(key="fan_control_alarm", number=6149, table="input", platform="binary_sensor", device_class="problem",
        name_fr="Défaut régulation ventilateurs", name_en="Fan control alarm"),
    Reg(key="rotor_alarm", number=6147, table="input", platform="binary_sensor", feature="rotor", device_class="problem", sw_min=(3, 1),
        name_fr="Défaut roue", name_en="Rotor alarm"),
    Reg(key="internal_temperature_alarm", number=6123, table="input", platform="binary_sensor", device_class="problem",
        name_fr="Alarme température interne", name_en="Internal temperature alarm"),
    Reg(key="supply_temperature_low_alarm", number=6143, table="input", platform="binary_sensor", device_class="problem",
        name_fr="Soufflage trop froid", name_en="Supply temperature low"),
    Reg(key="supply_temperature_high_alarm", number=6145, table="input", platform="binary_sensor", device_class="problem",
        name_fr="Soufflage trop chaud", name_en="Supply temperature high"),
    Reg(key="freezing_danger", number=6121, table="input", platform="binary_sensor", device_class="problem", feature="heater",
        name_fr="Risque de gel", name_en="Freezing danger"),
    Reg(key="reheater_failure", number=6117, table="input", platform="binary_sensor", device_class="problem", feature="heater",
        name_fr="Défaut post-chauffage", name_en="Re-heater failure"),
    Reg(key="preheater_failure", number=6119, table="input", platform="binary_sensor", device_class="problem", feature="preheater",
        name_fr="Défaut préchauffage", name_en="Preheater failure"),
    Reg(key="preheater_high_alarm", number=6141, table="input", platform="binary_sensor", device_class="problem", feature="preheater",
        name_fr="Préchauffage trop chaud", name_en="Preheater temperature high"),
)

# Sensor failure flags T1..T9 (aggregated into one binary sensor with the list in attributes)
SENSOR_FAILURES: dict[str, int] = {
    "T1": 6101, "T2": 6102, "T3": 6103, "T4": 6104, "T5": 6105,
    "T6": 6106, "T7": 6107, "T8": 6108, "T9": 6134,
}

# Active-alarm bitfield 3x6136 (bit -> key), for the attributes of the "alarm" sensor
ALARM_BITS: dict[int, str] = {
    0: "reheater_failure", 1: "preheater_failure", 2: "external_preheater_failure",
    3: "freezing_danger", 4: "supply_fan_failure", 5: "exhaust_fan_failure",
    6: "temperature_sensor_failure", 7: "emergency_stop", 8: "filter_guard",
    9: "service", 10: "internal_temperature", 11: "supply_temperature_low",
    12: "supply_temperature_high", 13: "preheater_temperature_high",
    14: "rotor", 15: "fan_control",
}
ALARM_BITFIELD = 6136
INFO_BITFIELD = 6137

# Device information
FIRMWARE = (6001, 6002, 6003)  # major, minor, build
PARAMETERS = (6004, 6005)
MODEL_NAME = (6008, 15)  # first register, count (one ASCII character per register)
SERIAL_NUMBER = (6024, 24)

# GIO (general purpose IO) configured for Modbus
GIO_FUNCTIONS = (5157, 5158, 5159, 5160, 5161)
GIO_RELAYS = (5021, 5022, 5023, 5024, 5025)
GIO_DI = (6349, 6350, 6351, 6352, 6353)
GIO_AI = (6354, 6355, 6356, 6357, 6358)
GIO_FUNCTION_MODBUS_DI = 10
GIO_FUNCTION_MODBUS_AI = 66
GIO_FUNCTION_MODBUS_DO = 132


def by_key() -> dict[str, Reg]:
    return {r.key: r for r in REGISTERS}


def applicable(reg: Reg, features: set[str], sw: tuple[int, int]) -> bool:
    """True when the register exists on this unit (equipment and software)."""
    if reg.feature != "core" and reg.feature not in features:
        return False
    if sw < reg.sw_min:
        return False
    if reg.sw_max is not None and sw > reg.sw_max:
        return False
    return True


def to_raw(reg: Reg, value: float) -> int:
    """Value in entity units -> 16-bit register value."""
    raw = int(round(value / reg.scale))
    if reg.signed and raw < 0:
        raw += 0x10000
    if not 0 <= raw <= 0xFFFF:
        raise ValueError(f"{value} out of range for {reg.key}")
    return raw


def from_raw(reg: Reg, raw: int | None) -> float | int | None:
    """16-bit register value -> value in entity units (None when invalid)."""
    if raw is None:
        return None
    value = raw - 0x10000 if reg.signed and raw >= 0x8000 else raw
    if value in reg.invalid:
        return None
    if reg.scale == 1:
        return value
    return round(value * reg.scale, 3)
