"""Quick design: six friendly answers become a load, a system and a design day.

The detailed curriculum modules ask for every envelope layer, every gain and
every psychrometric state.  This module sits in front of them for the visitor
who only knows the space: type, area, city, glazing, orientation and build
quality.  Engineering defaults fill the rest, every default is visible in the
advanced panel, and the result is handed to the same Chapter-4 load engine used
by Module 1 so the quick path and the detailed path never disagree about the
physics.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import Any

from .thermal_loads import (
    TR_KW,
    LoadInputs,
    LoadResult,
    calculate_thermal_load,
)

AUTO_SYSTEM = "Auto (recommended)"


@dataclass(frozen=True)
class SpacePreset:
    """Typical engineering defaults for one kind of space."""

    height_m: float
    area_per_person_m2: float
    lighting_w_m2: float
    equipment_w_m2: float
    activity_key: str
    ventilation_l_s_person: float
    infiltration_ach: float
    capacitance_kj_m2k: float
    schedule: str
    open_plan: bool = False
    note: str = ""


SPACE_TYPES: dict[str, SpacePreset] = {
    "Apartment living room": SpacePreset(
        height_m=2.9,
        area_per_person_m2=18.0,
        lighting_w_m2=5.0,
        equipment_w_m2=7.0,
        activity_key="Seated, quiet",
        ventilation_l_s_person=8.0,
        infiltration_ach=0.60,
        capacitance_kj_m2k=140.0,
        schedule="residential",
        note="Domestic room with evening occupancy and a lighter internal gain.",
    ),
    "Office": SpacePreset(
        height_m=3.0,
        area_per_person_m2=9.0,
        lighting_w_m2=9.0,
        equipment_w_m2=12.0,
        activity_key="Office work",
        ventilation_l_s_person=10.0,
        infiltration_ach=0.50,
        capacitance_kj_m2k=160.0,
        schedule="office",
        note="Working hours dominate; people and plug loads are the steady gains.",
    ),
    "Classroom": SpacePreset(
        height_m=3.2,
        area_per_person_m2=2.5,
        lighting_w_m2=9.0,
        equipment_w_m2=4.0,
        activity_key="Seated, quiet",
        ventilation_l_s_person=8.0,
        infiltration_ach=0.60,
        capacitance_kj_m2k=150.0,
        schedule="classroom",
        note="High occupant density for a short teaching day.",
    ),
    "Retail shop": SpacePreset(
        height_m=3.5,
        area_per_person_m2=12.0,
        lighting_w_m2=12.0,
        equipment_w_m2=6.0,
        activity_key="Standing / light work",
        ventilation_l_s_person=8.0,
        infiltration_ach=0.70,
        capacitance_kj_m2k=120.0,
        schedule="retail",
        open_plan=True,
        note="Tall, open sales floor with strong lighting and door traffic.",
    ),
    "Restaurant / café": SpacePreset(
        height_m=3.2,
        area_per_person_m2=3.0,
        lighting_w_m2=8.0,
        equipment_w_m2=25.0,
        activity_key="Light bench work",
        ventilation_l_s_person=12.0,
        infiltration_ach=0.70,
        capacitance_kj_m2k=160.0,
        schedule="restaurant",
        open_plan=True,
        note="Kitchen equipment and a long evening schedule drive the load.",
    ),
    "Mosque / assembly hall": SpacePreset(
        height_m=4.2,
        area_per_person_m2=2.0,
        lighting_w_m2=5.0,
        equipment_w_m2=2.0,
        activity_key="Seated, quiet",
        ventilation_l_s_person=8.0,
        infiltration_ach=0.80,
        capacitance_kj_m2k=220.0,
        schedule="assembly",
        open_plan=True,
        note="Large volume, dense prayer peaks and a heavy envelope mass.",
    ),
    "Clinic / laboratory": SpacePreset(
        height_m=3.0,
        area_per_person_m2=10.0,
        lighting_w_m2=11.0,
        equipment_w_m2=20.0,
        activity_key="Light bench work",
        ventilation_l_s_person=12.0,
        infiltration_ach=0.60,
        capacitance_kj_m2k=150.0,
        schedule="clinic",
        note="Continuous equipment load and a higher fresh-air rate.",
    ),
}


@dataclass(frozen=True)
class CityPreset:
    name: str
    db_c: float
    wb_c: float
    daily_swing_k: float
    note: str


CITIES: dict[str, CityPreset] = {
    "Baghdad": CityPreset("Baghdad", 46.0, 24.0, 13.0, "Hot dry summer design day."),
    "Basra": CityPreset("Basra", 46.0, 27.5, 11.0, "Hot and humid Gulf design day."),
    "Mosul": CityPreset("Mosul", 42.0, 23.0, 14.0, "Hot summer with a wide day–night swing."),
    "Erbil": CityPreset("Erbil", 40.0, 21.5, 15.0, "Warm summer and cool nights."),
    "Najaf": CityPreset("Najaf", 45.5, 23.5, 13.5, "Hot dry design day."),
    "Other / custom": CityPreset("Other / custom", 43.0, 23.0, 13.0, "Enter your own design condition."),
}


@dataclass(frozen=True)
class EnvelopePreset:
    label: str
    wall_u: float
    roof_u: float
    window_u: float
    shgc: float
    shading: float
    infiltration_factor: float
    note: str


ENVELOPE_QUALITY: dict[str, EnvelopePreset] = {
    "Basic (older building)": EnvelopePreset(
        "Basic (older building)", 1.35, 1.00, 4.80, 0.67, 0.95, 1.30,
        "Single glazing and little insulation; expect a heavier load.",
    ),
    "Standard": EnvelopePreset(
        "Standard", 0.55, 0.35, 2.60, 0.50, 0.85, 1.00,
        "Insulated wall and double glazing: a common modern build.",
    ),
    "High performance": EnvelopePreset(
        "High performance", 0.30, 0.22, 1.45, 0.30, 0.65, 0.75,
        "Low-e glazing, good insulation and controlled infiltration.",
    ),
}


@dataclass(frozen=True)
class OrientationPreset:
    label: str
    wall_solar_w_m2: float
    shape: str
    note: str


ORIENTATIONS: dict[str, OrientationPreset] = {
    "North": OrientationPreset("North", 130.0, "north", "Diffuse light all day; the mildest façade."),
    "East": OrientationPreset("East", 520.0, "east", "Morning sun; the peak arrives before midday."),
    "South": OrientationPreset("South", 430.0, "south", "High midday sun; overhangs work well here."),
    "West": OrientationPreset("West", 600.0, "west", "Afternoon sun; the hottest and latest peak."),
}


SYSTEM_LABELS: dict[str, dict[str, str]] = {
    "split": {
        "name": "High-wall split units",
        "family": "Single-zone DX",
        "note": "Simple, low first cost, and easy to add one unit at a time.",
    },
    "ducted": {
        "name": "Ducted packaged units",
        "family": "Ducted DX",
        "note": "A ducted distribution for open plans, with a fresh-air duct.",
    },
    "vrf": {
        "name": "VRF multi-split",
        "family": "Variable-refrigerant flow",
        "note": "Zoned indoor units with strong part-load efficiency through the day.",
    },
    "chiller": {
        "name": "Air-cooled chiller + AHU",
        "family": "Central chilled water",
        "note": "A central plant feeding an air-handling unit and ducted distribution.",
    },
}

SYSTEM_COP = {"split": 3.15, "ducted": 3.00, "vrf": 3.65, "chiller": 3.25}
SYSTEM_FAN_KW_PER_1000 = {"split": 0.10, "ducted": 0.28, "vrf": 0.16, "chiller": 0.34}
SYSTEM_SUPPLY_DT = {"split": 10.0, "ducted": 10.0, "vrf": 9.0, "chiller": 8.0}

_SPLIT_SIZES = (2.6, 3.5, 5.3, 7.1)
_VRF_SIZES = (8.0, 10.0, 12.5, 14.0, 16.0, 18.0, 20.0)
_DUCTED_SIZES = (10.0, 15.0, 20.0, 25.0, 30.0, 40.0, 50.0, 60.0)
_CHILLER_SIZES = (40.0, 60.0, 80.0, 100.0, 130.0, 160.0, 200.0, 250.0, 300.0)

_OPEN_PLAN = {"Retail shop", "Restaurant / café", "Mosque / assembly hall"}


@dataclass(frozen=True)
class QuickInputs:
    """The six questions, plus an optional fine-tuning layer."""

    space_type: str = "Office"
    floor_area_m2: float = 96.0
    city: str = "Baghdad"
    glazing_ratio: float = 0.25
    orientation: str = "West"
    envelope_quality: str = "Standard"

    occupants: int | None = None
    indoor_db_c: float = 24.0
    indoor_rh_pct: float = 50.0
    outdoor_db_c: float | None = None
    outdoor_wb_c: float | None = None
    system_preference: str = AUTO_SYSTEM
    safety_margin: float = 0.12

    def validate(self) -> None:
        if self.space_type not in SPACE_TYPES:
            raise ValueError("Unknown space type.")
        if self.city not in CITIES:
            raise ValueError("Unknown city.")
        if self.orientation not in ORIENTATIONS:
            raise ValueError("Unknown window orientation.")
        if self.envelope_quality not in ENVELOPE_QUALITY:
            raise ValueError("Unknown envelope quality.")
        if not 10.0 <= self.floor_area_m2 <= 4000.0:
            raise ValueError("Floor area must be between 10 and 4000 square metres.")
        if not 0.0 <= self.glazing_ratio <= 0.70:
            raise ValueError("Glazing ratio must be between 0 and 70 percent of the wall.")
        if self.occupants is not None and self.occupants < 0:
            raise ValueError("Occupant count cannot be negative.")
        if not 20.0 <= self.indoor_db_c <= 30.0:
            raise ValueError("Indoor setpoint must be between 20 and 30 degrees.")
        if not 0.0 <= self.safety_margin <= 0.40:
            raise ValueError("Selection margin must be between 0 and 40 percent.")
        if self.custom_weather:
            if self.outdoor_db_c is None or self.outdoor_wb_c is None:
                raise ValueError("Enter both custom design temperatures.")
            if self.outdoor_wb_c >= self.outdoor_db_c:
                raise ValueError("Outdoor wet-bulb must be below dry-bulb.")

    @property
    def custom_weather(self) -> bool:
        return self.city == "Other / custom"

    @classmethod
    def from_state(cls, state: Any) -> "QuickInputs":
        """Build the six answers from the Streamlit widget state.

        Shared by the page and the sidebar snapshot so both always describe the
        same case, even on the first render after navigation.
        """
        space = state.get("qd_space", "Office")
        area = float(state.get("qd_area", 96.0))
        city = state.get("qd_city", "Baghdad")
        preset = SPACE_TYPES.get(space)
        auto = (
            max(1, int(round(area / preset.area_per_person_m2)))
            if preset is not None
            else 1
        )
        manual = bool(state.get("qd_manual_occ", False))
        return cls(
            space_type=space,
            floor_area_m2=area,
            city=city,
            glazing_ratio=float(state.get("qd_glazing", 25.0)) / 100.0,
            orientation=state.get("qd_orientation", "West"),
            envelope_quality=state.get("qd_envelope", "Standard"),
            occupants=int(state.get("qd_occupants", auto)) if manual else None,
            indoor_db_c=float(state.get("qd_indoor_db", 24.0)),
            indoor_rh_pct=float(state.get("qd_indoor_rh", 50.0)),
            outdoor_db_c=(
                float(state.get("qd_custom_db", 43.0))
                if city == "Other / custom"
                else None
            ),
            outdoor_wb_c=(
                float(state.get("qd_custom_wb", 23.0))
                if city == "Other / custom"
                else None
            ),
            system_preference=state.get("qd_system", AUTO_SYSTEM),
            safety_margin=float(state.get("qd_margin", 12.0)) / 100.0,
        )

    @property
    def design_db_c(self) -> float:
        if self.custom_weather and self.outdoor_db_c is not None:
            return float(self.outdoor_db_c)
        return CITIES[self.city].db_c

    @property
    def design_wb_c(self) -> float:
        if self.custom_weather and self.outdoor_wb_c is not None:
            return float(self.outdoor_wb_c)
        return CITIES[self.city].wb_c


@dataclass(frozen=True)
class RecommendationPoint:
    """One sentence with live values interpolated after translation."""

    template: str
    values: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SystemRecommendation:
    key: str
    name: str
    family: str
    note: str
    capacity_kw: float
    capacity_tr: float
    capacity_target_kw: float
    unit_size_kw: float
    outdoor_units: int
    indoor_units: int
    airflow_m3h: float
    fresh_air_m3h: float
    supply_dt_k: float
    cop_rated: float
    fan_kw_per_1000_m3h: float
    reasons: tuple[RecommendationPoint, ...]
    cautions: tuple[RecommendationPoint, ...]

    @property
    def margin_pct(self) -> float:
        if self.capacity_kw <= 1e-9:
            return 0.0
        return 100.0 * (self.capacity_kw / self.capacity_target_kw - 1.0)


@dataclass(frozen=True)
class QuickDesign:
    inputs: QuickInputs
    space: SpacePreset
    city: CityPreset
    envelope: EnvelopePreset
    orientation: OrientationPreset
    load_inputs: LoadInputs
    load: LoadResult
    recommendation: SystemRecommendation
    occupants: int
    daily_swing_k: float

    @property
    def capacity_kw(self) -> float:
        return self.recommendation.capacity_kw


def auto_occupants(inputs: QuickInputs) -> int:
    space = SPACE_TYPES[inputs.space_type]
    return max(1, int(round(inputs.floor_area_m2 / space.area_per_person_m2)))


def _geometry(inputs: QuickInputs) -> tuple[float, float, float, float]:
    """Room dimensions and gross exposed wall for the entered floor area."""
    space = SPACE_TYPES[inputs.space_type]
    length = math.sqrt(inputs.floor_area_m2 * 1.35)
    width = inputs.floor_area_m2 / length
    perimeter = 2.0 * (length + width)
    gross_wall = perimeter * space.height_m * 0.85
    return length, width, gross_wall, space.height_m


def to_load_inputs(inputs: QuickInputs) -> LoadInputs:
    """Map the six answers onto the detailed Chapter-4 input structure."""
    inputs.validate()
    space = SPACE_TYPES[inputs.space_type]
    envelope = ENVELOPE_QUALITY[inputs.envelope_quality]
    orientation = ORIENTATIONS[inputs.orientation]
    city = CITIES[inputs.city]
    length, width, gross_wall, height = _geometry(inputs)
    window_area = max(0.0, min(0.70 * gross_wall, inputs.glazing_ratio * gross_wall))
    occupants = auto_occupants(inputs) if inputs.occupants is None else int(inputs.occupants)

    return LoadInputs(
        project_name=f"Quick design · {inputs.space_type}",
        length_m=length,
        width_m=width,
        height_m=height,
        exposed_wall_fraction=0.85,
        wall_u_w_m2k=envelope.wall_u,
        wall_absorptivity=0.65,
        roof_u_w_m2k=envelope.roof_u,
        roof_absorptivity=0.75,
        window_u_w_m2k=envelope.window_u,
        window_shgc=envelope.shgc,
        window_area_m2=window_area,
        shading_factor=envelope.shading,
        wall_solar_w_m2=orientation.wall_solar_w_m2,
        roof_solar_w_m2=950.0,
        outdoor_film_w_m2k=20.0,
        outdoor_db_c=inputs.design_db_c,
        outdoor_wb_c=inputs.design_wb_c,
        indoor_db_c=inputs.indoor_db_c,
        indoor_rh_pct=inputs.indoor_rh_pct,
        occupants=occupants,
        activity_key=space.activity_key,
        lighting_w_m2=space.lighting_w_m2,
        equipment_w=space.equipment_w_m2 * inputs.floor_area_m2,
        infiltration_ach=space.infiltration_ach * envelope.infiltration_factor,
        ventilation_l_s_person=space.ventilation_l_s_person,
    )


def _pick_sizes(target: float, sizes: tuple[float, ...]) -> tuple[float, int, float]:
    """Smallest combination from a nominal size list that covers the target."""
    for size in sizes:
        if target <= size + 1e-9:
            return size, 1, size
    largest = sizes[-1]
    count = max(1, int(math.ceil(target / largest)))
    if len(sizes) > 1:
        for size in sizes:
            if size * count >= target - 1e-9:
                return size, count, size * count
    return largest, count, largest * count


def _choose_system_key(inputs: QuickInputs, design_kw: float, target_kw: float) -> str:
    if inputs.system_preference != AUTO_SYSTEM:
        for key in SYSTEM_LABELS:
            if SYSTEM_LABELS[key]["name"] == inputs.system_preference:
                return key
        mapping = {
            "High-wall split": "split",
            "Ducted / packaged": "ducted",
            "VRF multi-split": "vrf",
            "Chiller + AHU": "chiller",
        }
        return mapping.get(inputs.system_preference, "vrf")
    if target_kw <= 7.5:
        return "split"
    if inputs.space_type in _OPEN_PLAN:
        return "ducted" if target_kw <= 60.0 else "chiller"
    if target_kw <= 100.0:
        return "vrf"
    return "chiller"


def recommend_system(
    inputs: QuickInputs,
    load: LoadResult,
    *,
    margin: float | None = None,
) -> SystemRecommendation:
    """Rule-based selection that stays honest about its own limits."""
    if margin is None:
        margin = inputs.safety_margin
    target_kw = load.design_total_kw * (1.0 + margin)
    key = _choose_system_key(inputs, load.design_total_kw, target_kw)
    sizes = {
        "split": _SPLIT_SIZES,
        "ducted": _DUCTED_SIZES,
        "vrf": _VRF_SIZES,
        "chiller": _CHILLER_SIZES,
    }[key]
    unit_size, units, capacity = _pick_sizes(target_kw, sizes)

    supply_dt = SYSTEM_SUPPLY_DT[key]
    airflow = (
        load.design_sensible_kw / (1.02 * supply_dt) * 3600.0 / 1.15
    )
    airflow = max(200.0, round(airflow / 50.0) * 50.0)
    fresh_air = load.ventilation_m3_s * 3600.0

    if key == "split":
        indoor_units = units
    elif key == "vrf":
        indoor_units = max(1, int(math.ceil(inputs.floor_area_m2 / 28.0)))
    elif key == "ducted":
        indoor_units = units
    else:
        indoor_units = max(1, int(math.ceil(inputs.floor_area_m2 / 450.0)))

    latent_pct = 100.0 * load.design_latent_kw / max(1e-9, load.design_total_kw)
    wwr_pct = 100.0 * load.inputs.window_area_m2 / max(1e-9, load.gross_wall_area_m2)
    q = load.design_total_kw
    tr = load.design_tr

    reasons = [
        RecommendationPoint(
            "The peak coil load is {q:.1f} kW ({tr:.1f} TR), and this selection covers it with a {margin:.0f}% margin for duct gain, fan heat and real-world tolerance.",
            {"q": q, "tr": tr, "margin": 100.0 * margin},
        )
    ]
    if key == "split":
        reasons.append(RecommendationPoint(
            "A single-zone split is the simplest and lowest-cost answer at this size; shade the outdoor unit and keep the indoor unit clear of the bed and seating."
        ))
    elif key == "ducted":
        reasons.append(RecommendationPoint(
            "The space is open-plan, so a ducted system distributes air evenly and can carry a fresh-air duct into the occupied zone."
        ))
    elif key == "vrf":
        reasons.append(RecommendationPoint(
            "Several rooms and a long operating day favour VRF: zoned indoor units track occupancy and part-load efficiency stays high outside the peak."
        ))
    else:
        reasons.append(RecommendationPoint(
            "At this capacity a central chilled-water plant and an AHU are more practical and serviceable than a large bank of DX units."
        ))

    if latent_pct >= 20.0:
        reasons.append(RecommendationPoint(
            "Latent heat is {latent:.0f}% of the load, so choose a coil that genuinely dehumidifies; an oversized dry unit would leave the space cold and clammy.",
            {"latent": latent_pct},
        ))
    else:
        reasons.append(RecommendationPoint(
            "The load is mostly sensible at {latent:.0f}% latent, so sensible capacity and airflow set the selection rather than dehumidification.",
            {"latent": latent_pct},
        ))
    if wwr_pct >= 40.0:
        reasons.append(RecommendationPoint(
            "Glazing is {wwr:.0f}% of the exposed wall, so solar gain dominates; low-e glass or external shading buys more comfort than extra capacity.",
            {"wwr": wwr_pct},
        ))
    if inputs.orientation == "West":
        reasons.append(RecommendationPoint(
            "A west-facing main window puts the solar peak in the late afternoon, when the outdoor air is already hottest. That is the hour the system must win."
        ))

    cautions = [
        RecommendationPoint(
            "Fresh air is {oa:.0f} m³/h. Confirm the ventilation and exhaust schedule with the people who will use the space.",
            {"oa": fresh_air},
        ),
        RecommendationPoint(
            "Keep the outdoor unit shaded and clear of walls; a hot condenser can lose 10% of capacity exactly when you need it."
        ),
        RecommendationPoint(
            "This is a design estimate. Final equipment selection must be checked by a qualified engineer against the project brief and local code."
        ),
    ]

    return SystemRecommendation(
        key=key,
        name=SYSTEM_LABELS[key]["name"],
        family=SYSTEM_LABELS[key]["family"],
        note=SYSTEM_LABELS[key]["note"],
        capacity_kw=capacity,
        capacity_tr=capacity / TR_KW,
        capacity_target_kw=target_kw,
        unit_size_kw=unit_size,
        outdoor_units=units,
        indoor_units=indoor_units,
        airflow_m3h=airflow,
        fresh_air_m3h=fresh_air,
        supply_dt_k=supply_dt,
        cop_rated=SYSTEM_COP[key],
        fan_kw_per_1000_m3h=SYSTEM_FAN_KW_PER_1000[key],
        reasons=tuple(reasons),
        cautions=tuple(cautions),
    )


def build_quick_design(inputs: QuickInputs | None = None) -> QuickDesign:
    """Run the full quick path from six answers to a sized recommendation."""
    inputs = inputs or QuickInputs()
    load_inputs = to_load_inputs(inputs)
    load = calculate_thermal_load(load_inputs)
    space = SPACE_TYPES[inputs.space_type]
    city = CITIES[inputs.city]
    envelope = ENVELOPE_QUALITY[inputs.envelope_quality]
    orientation = ORIENTATIONS[inputs.orientation]
    recommendation = recommend_system(inputs, load)
    return QuickDesign(
        inputs=inputs,
        space=space,
        city=city,
        envelope=envelope,
        orientation=orientation,
        load_inputs=load_inputs,
        load=load,
        recommendation=recommendation,
        occupants=load_inputs.occupants,
        daily_swing_k=city.daily_swing_k,
    )


def quick_summary_payload(design: QuickDesign) -> dict[str, Any]:
    """Small dictionary for diagnostics, tests and future exports."""
    return {
        "space_type": design.inputs.space_type,
        "floor_area_m2": design.inputs.floor_area_m2,
        "city": design.inputs.city,
        "design_total_kw": design.load.design_total_kw,
        "system": design.recommendation.key,
        "capacity_kw": design.recommendation.capacity_kw,
        "occupants": design.occupants,
    }
