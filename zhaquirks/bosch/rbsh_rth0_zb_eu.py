        """Device handler for Bosch RBSH-RTH0-ZB-EU thermostat."""

from typing import Any, Final

from zigpy.device import Device
from zigpy.profiles import zha
from zigpy.quirks import CustomCluster
from zigpy.quirks.registry import DeviceRegistry
from zigpy.quirks.v2 import (
    CustomDeviceV2,
    add_to_registry_v2,
)
from zigpy.quirks.v2.homeassistant.number import NumberDeviceClass
import zigpy.types as t
from zigpy.zcl import ClusterType
from zigpy.zcl.clusters.hvac import Thermostat, UserInterface
from zigpy.zcl.foundation import BaseAttributeDefs, ZCLAttributeDef, ZCLCommandDef

"""Bosch specific thermostat attribute ids."""
OPERATING_MODE_ATTR_ID = 0x4007
VALVE_POSITION_ATTR_ID = 0x4020
WINDOW_OPEN_ATTR_ID = 0x4042
BOOST_ATTR_ID = 0x4043

"""Bosch specific user interface attribute ids."""
SCREEN_TIMEOUT_ATTR_ID = 0x403a
SCREEN_BRIGHTNESS_ATTR_ID = 0x403b

"""Bosh operating mode attribute values."""
class BoschOperatingMode(t.enum8):
    Schedule = 0x00
    Manual = 0x01
    Pause = 0x05

"""Bosch thermostat preset."""
class BoschPreset(t.enum8):
    Normal = 0x00
    Boost = 0x01

"""Binary attribute (window open) value."""
class State(t.enum8):
    Off = 0x00
    On = 0x01

class BoschThermostatCluster(CustomCluster, Thermostat):
    """Bosch thermostat cluster."""

    class AttributeDefs(Thermostat.AttributeDefs):
        operating_mode = ZCLAttributeDef(
            id=t.uint16_t(OPERATING_MODE_ATTR_ID),
            type=BoschOperatingMode,
            is_manufacturer_specific=True,
        )

        pi_heating_demand = ZCLAttributeDef(
            id=t.uint16_t(VALVE_POSITION_ATTR_ID),
            # Values range from 0-100
            type=t.enum8,
            is_manufacturer_specific=True,
        )

        window_open = ZCLAttributeDef(
            id=t.uint16_t(WINDOW_OPEN_ATTR_ID),
            type=State,
            is_manufacturer_specific=True,
        )

        boost = ZCLAttributeDef(
            id=t.uint16_t(BOOST_ATTR_ID),
            type=BoschPreset,
            is_manufacturer_specific=True,
        )


class BoschUserInterfaceCluster(CustomCluster, UserInterface):
    """Bosch UserInterface cluster."""

    class AttributeDefs(UserInterface.AttributeDefs):
        display_ontime = ZCLAttributeDef(
            id=t.uint16_t(SCREEN_TIMEOUT_ATTR_ID),
            # Usable values range from 5-30
            type=t.enum8,
            is_manufacturer_specific=True,
        )

        display_brightness = ZCLAttributeDef(
            id=t.uint16_t(SCREEN_BRIGHTNESS_ATTR_ID),
            # Values range from 0-10
            type=t.enum8,
            is_manufacturer_specific=True,
        )


class BoschThermostat(CustomDeviceV2):
    """Bosch thermostat custom device."""

(
    add_to_registry_v2(
        "Bosch", "RBSH-RTH0-ZB-EU"
    )
    .device_class(BoschThermostat)
    .replaces(BoschThermostatCluster)
    .replaces(BoschUserInterfaceCluster)
    # Operating mode: controlled automatically through Thermostat.system_mode (HAVC mode).
    .enum(
        BoschThermostatCluster.AttributeDefs.operating_mode.name,
        BoschOperatingMode,
        BoschThermostatCluster.cluster_id,
        translation_key="switch_mode"
    )
    # Preset - normal/boost.
    .enum(
        BoschThermostatCluster.AttributeDefs.boost.name,
        BoschPreset,
        BoschThermostatCluster.cluster_id,
        translation_key="preset"
    )
    # Window open switch: manually set or through an automation.
    .switch(
        BoschThermostatCluster.AttributeDefs.window_open.name,
        BoschThermostatCluster.cluster_id,
        translation_key="window_detection"
    )
    # Display time-out
    .number(
        BoschUserInterfaceCluster.AttributeDefs.display_ontime.name,
        BoschUserInterfaceCluster.cluster_id,
        min_value=5,
        max_value=30,
        step=1,
        translation_key="on_off_transition_time"
    )
    # Display brightness
    .number(
        BoschUserInterfaceCluster.AttributeDefs.display_brightness.name,
        BoschUserInterfaceCluster.cluster_id,
        min_value=0,
        max_value=10,
        step=1,
        translation_key="backlight_mode"
    )
)
