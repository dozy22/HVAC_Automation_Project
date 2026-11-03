"""Air-handling-unit operations: mixing, coil performance, ADP/BPF and heating."""

from __future__ import annotations

from dataclasses import dataclass
import math

from .psychrometrics import (
    PsychrometricState,
    P_ATM_STD_KPA,
    H_FG_0,
    enthalpy_from_state,
    humidity_ratio_from_rh,
    moist_air_specific_heat,
    psychrometric_state,
    saturation_humidity_ratio,
    saturation_pressure_kpa,
    state_from_enthalpy_humidity_ratio,
)


@dataclass(frozen=True)
class CoilAnalysis:
    apparatus_dew_point: PsychrometricState
    bypass_factor: float
    contact_factor: float
    coil_total_kw: float
    coil_sensible_kw: float
    coil_latent_kw: float
    coil_sensible_heat_ratio: float
    mass_flow_kg_s: float


@dataclass(frozen=True)
class AhuDesignResult:
    room: PsychrometricState
    outdoor: PsychrometricState
    mixed: PsychrometricState
    supply: PsychrometricState
    apparatus_dew_point: PsychrometricState
    outdoor_air_fraction: float
    supply_db_c: float
    supply_mass_flow_kg_s: float
    supply_volume_flow_m3_s: float
    space_sensible_kw: float
    space_latent_kw: float
    space_rshf: float
    coil_total_kw: float
    coil_sensible_kw: float
    coil_latent_kw: float
    coil_shr: float
    bypass_factor: float
    apparatus_dew_point_c: float


@dataclass(frozen=True)
class HeatingHumidificationResult:
    entering: PsychrometricState
    heated: PsychrometricState
    leaving: PsychrometricState
    mass_flow_kg_s: float
    heating_kw: float
    humidification_kg_h: float
    humidification_energy_kw: float
    target_db_c: float
    target_rh_pct: float


def mix_air(
    room_air: PsychrometricState,
    outdoor_air: PsychrometricState,
    outdoor_fraction: float,
    pressure_kpa: float = P_ATM_STD_KPA,
) -> PsychrometricState:
    """Adiabatic mixing of return air and outdoor air on a dry-air mass basis.

    Outdoor-air fraction is the mass fraction of dry outside air in the mixture.
    Humidity ratio and enthalpy mix linearly, which is the exact conservation
    statement for steady adiabatic mixing.
    """
    fraction = float(outdoor_fraction)
    if not 0.0 <= fraction <= 1.0:
        raise ValueError("Outdoor-air fraction must be between 0 and 100 percent.")
    w_mix = fraction * outdoor_air.humidity_ratio + (1.0 - fraction) * room_air.humidity_ratio
    h_mix = fraction * outdoor_air.enthalpy_kj_kg + (1.0 - fraction) * room_air.enthalpy_kj_kg
    mixed = state_from_enthalpy_humidity_ratio(h_mix, w_mix, pressure_kpa)
    # Enthalpy mixing is exact; the returned state makes the resulting dry bulb
    # transparent and keeps every property internally consistent.
    return mixed


def supply_state_from_space_loads(
    room_air: PsychrometricState,
    sensible_kw: float,
    latent_kw: float,
    supply_db_c: float,
    pressure_kpa: float = P_ATM_STD_KPA,
) -> tuple[PsychrometricState, float]:
    """Determine supply state and dry-air mass flow from room RSH and RLH.

    Sensible load sets the airflow: Qs = m_da * cp_moist * (Tr - Ts).
    Latent load then defines the supply humidity ratio:
        Ql = m_da * h_fg * (Wr - Ws).
    This places the supply point on the space RSHF line at the selected supply
    dry-bulb temperature.
    """
    sensible_kw = float(sensible_kw)
    latent_kw = float(latent_kw)
    if sensible_kw <= 0.0:
        raise ValueError("Room sensible load must be greater than zero for air sizing.")
    if latent_kw < -1e-9:
        raise ValueError("Room latent load cannot be negative in cooling design.")
    if supply_db_c >= room_air.dry_bulb_c - 0.2:
        raise ValueError("Supply air temperature must be at least 0.2 degC below room temperature.")

    cp_moist = moist_air_specific_heat(room_air.humidity_ratio)
    delta_t = room_air.dry_bulb_c - float(supply_db_c)
    mass_flow = sensible_kw / (cp_moist * delta_t)

    if mass_flow <= 0.0 or not math.isfinite(mass_flow):
        raise ValueError("Unable to determine a positive supply-air mass flow.")

    supply_w = room_air.humidity_ratio - latent_kw / (mass_flow * H_FG_0)
    w_sat = saturation_humidity_ratio(supply_db_c, pressure_kpa)
    if supply_w < -1e-9:
        raise ValueError(
            "The latent load requires a negative humidity ratio. Increase airflow or supply temperature."
        )
    if supply_w > w_sat + 1e-6:
        raise ValueError(
            "Calculated supply air would be supersaturated. Raise the supply temperature "
            "or verify the room latent load."
        )
    supply = psychrometric_state(
        float(supply_db_c),
        pressure_kpa,
        humidity_ratio=max(0.0, supply_w),
    )
    return supply, mass_flow


def find_apparatus_dew_point(
    mixed_air: PsychrometricState,
    supply_air: PsychrometricState,
    pressure_kpa: float = P_ATM_STD_KPA,
) -> tuple[PsychrometricState, float]:
    """Extend the coil process line to saturation and compute BPF.

    The nearest saturation intersection below the supply point is the ADP.
    Bypass factor follows the psychrometric distance ratio:
        BPF = (W_mixed - W_supply) / (W_mixed - W_ADP)
    """
    tm, wm = mixed_air.dry_bulb_c, mixed_air.humidity_ratio
    ts, ws = supply_air.dry_bulb_c, supply_air.humidity_ratio
    if ts >= tm - 0.05:
        raise ValueError("The cooling-coil leaving air must be cooler than the entering mixture.")
    if wm < ws - 1e-7:
        raise ValueError("The cooling process must not increase humidity ratio.")
    if tm == ts:
        raise ValueError("Coil line has no temperature span.")

    slope = (ws - wm) / (ts - tm)

    def line_ratio(temp_c: float) -> float:
        return wm + slope * (temp_c - tm)

    def difference(temp_c: float) -> float:
        return line_ratio(temp_c) - saturation_humidity_ratio(temp_c, pressure_kpa)

    f_high = difference(ts)
    if f_high >= -1e-8:
        # Saturated at the coil exit: zero bypass factor.
        adp_t = ts
        adp_w = saturation_humidity_ratio(adp_t, pressure_kpa)
    else:
        step = 0.25
        upper_t = ts
        upper_f = f_high
        lower_t = upper_t
        lower_f = upper_f
        found = False
        cursor = ts
        while cursor > -30.0:
            cursor -= step
            value = difference(cursor)
            if value >= 0.0:
                lower_t, lower_f = cursor, value
                found = True
                break
            upper_t, upper_f = cursor, value
        if not found:
            raise ValueError(
                "The coil process line does not intersect the saturation curve. "
                "Check the leaving-air condition."
            )

        # Bisection between the last unsaturated point and the saturated crossing.
        high_t, low_t = upper_t, lower_t
        for _ in range(100):
            mid = 0.5 * (high_t + low_t)
            if difference(mid) < 0.0:
                high_t = mid
            else:
                low_t = mid
            if abs(low_t - high_t) < 1e-7:
                break
        adp_t = 0.5 * (high_t + low_t)
        adp_w = saturation_humidity_ratio(adp_t, pressure_kpa)

    adp = psychrometric_state(
        adp_t,
        pressure_kpa,
        humidity_ratio=min(adp_w, saturation_humidity_ratio(adp_t, pressure_kpa)),
    )
    if wm - adp_w <= 1e-10:
        raise ValueError("Apparatus dew point cannot be resolved for this coil path.")
    bpf = (wm - ws) / (wm - adp_w)
    bpf = float(min(1.0, max(0.0, bpf)))
    return adp, bpf


def design_ahu(
    room_air: PsychrometricState,
    outdoor_air: PsychrometricState,
    sensible_kw: float,
    latent_kw: float,
    supply_db_c: float,
    outdoor_fraction: float,
    pressure_kpa: float = P_ATM_STD_KPA,
) -> AhuDesignResult:
    """Full mixing + cooling/dehumidification design calculation."""
    mixed = mix_air(room_air, outdoor_air, outdoor_fraction, pressure_kpa)
    supply, mass_flow = supply_state_from_space_loads(
        room_air, sensible_kw, latent_kw, supply_db_c, pressure_kpa
    )
    if supply.dry_bulb_c >= mixed.dry_bulb_c:
        raise ValueError("Supply air must be cooler than the mixed air entering the coil.")
    if supply.humidity_ratio > mixed.humidity_ratio + 1e-7:
        raise ValueError("This cooling process would humidify the air instead of dehumidifying it.")

    adp, bpf = find_apparatus_dew_point(mixed, supply, pressure_kpa)
    coil_total = mass_flow * (mixed.enthalpy_kj_kg - supply.enthalpy_kj_kg)
    coil_latent = mass_flow * H_FG_0 * (mixed.humidity_ratio - supply.humidity_ratio)
    coil_sensible = coil_total - coil_latent
    coil_shr = coil_sensible / coil_total if coil_total > 1e-9 else 0.0
    space_total = sensible_kw + latent_kw
    rshf = sensible_kw / space_total if space_total > 1e-9 else 0.0
    supply_volume = mass_flow * supply.specific_volume_m3_kg

    return AhuDesignResult(
        room=room_air,
        outdoor=outdoor_air,
        mixed=mixed,
        supply=supply,
        apparatus_dew_point=adp,
        outdoor_air_fraction=outdoor_fraction,
        supply_db_c=supply_db_c,
        supply_mass_flow_kg_s=mass_flow,
        supply_volume_flow_m3_s=supply_volume,
        space_sensible_kw=sensible_kw,
        space_latent_kw=latent_kw,
        space_rshf=rshf,
        coil_total_kw=coil_total,
        coil_sensible_kw=coil_sensible,
        coil_latent_kw=coil_latent,
        coil_shr=coil_shr,
        bypass_factor=bpf,
        apparatus_dew_point_c=adp.dry_bulb_c,
    )


def heating_and_steam_humidification(
    entering: PsychrometricState,
    target_db_c: float,
    target_rh_pct: float,
    mass_flow_kg_s: float,
    pressure_kpa: float = P_ATM_STD_KPA,
) -> HeatingHumidificationResult:
    """Sensible preheat followed by idealized steam humidification.

    Heating is constant humidity ratio.  Steam humidification is represented at
    constant dry-bulb temperature, a standard teaching idealization.  The
    humidifier steam mass flow is the actual moisture added per hour.
    """
    m_da = float(mass_flow_kg_s)
    if m_da <= 0.0:
        raise ValueError("Mass flow must be positive.")
    target_db_c = float(target_db_c)
    target_rh_pct = float(target_rh_pct)
    if not 0.0 < target_rh_pct <= 100.0:
        raise ValueError("Target relative humidity must be between 0 and 100 percent.")
    if target_db_c < entering.dry_bulb_c - 0.01:
        raise ValueError("This heating module expects a target temperature above the entering air.")

    at_temperature = psychrometric_state(
        target_db_c,
        pressure_kpa,
        humidity_ratio=entering.humidity_ratio,
    )
    target_w = humidity_ratio_from_rh(target_db_c, target_rh_pct, pressure_kpa)
    if target_w < entering.humidity_ratio - 1e-9:
        raise ValueError("Target humidity ratio is lower than the entering condition.")
    leaving = psychrometric_state(
        target_db_c,
        pressure_kpa,
        humidity_ratio=target_w,
    )
    heating_kw = m_da * (at_temperature.enthalpy_kj_kg - entering.enthalpy_kj_kg)
    humidification_kg_h = m_da * (leaving.humidity_ratio - entering.humidity_ratio) * 3600.0
    humidification_energy = m_da * (
        leaving.enthalpy_kj_kg - at_temperature.enthalpy_kj_kg
    )
    return HeatingHumidificationResult(
        entering=entering,
        heated=at_temperature,
        leaving=leaving,
        mass_flow_kg_s=m_da,
        heating_kw=heating_kw,
        humidification_kg_h=humidification_kg_h,
        humidification_energy_kw=humidification_energy,
        target_db_c=target_db_c,
        target_rh_pct=target_rh_pct,
    )
