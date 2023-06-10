"""Breeze switch of the Renson ventilation unit."""
from __future__ import annotations

import logging
from typing import Any

from renson_endura_delta.field_enum import CURRENT_LEVEL_FIELD, BREEZE_LEVEL_FIELD, DataType
from renson_endura_delta.renson import Level, RensonVentilation

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.switch import SwitchEntity, SwitchDeviceClass

from . import RensonCoordinator
from .const import DOMAIN
from .entity import RensonEntity

_LOGGER = logging.getLogger(__name__)

class RensonBreezeSwitch(RensonEntity, SwitchEntity):
    """Provide the breeze switch."""

    _attr_icon = "mdi:weather-dust"
    _attr_name = "Breeze"

    def __init__(
        self,
        api: RensonVentilation,
        coordinator: RensonCoordinator,
    ) -> None:
        """Initialize class."""
        super().__init__("breeze", api, coordinator)

        self._state = None

    @property
    def is_on(self):
        """Return true if switch is on."""
        return self._state

    @property
    def device_class(self) -> str:
        return SwitchDeviceClass.SWITCH

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the switch."""
        _LOGGER.debug("Enable Breeze")

        await self.hass.async_add_executor_job(self.api.set_manual_level, Level.BREEZE)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the switch."""
        _LOGGER.debug("Disable Breeze")

        breeze_level = self.api.parse_value(
            self.api.get_field_value(self.coordinator.data, BREEZE_LEVEL_FIELD.name),
            DataType.LEVEL,
        )

        await self.hass.async_add_executor_job(self.api.set_manual_level, Level[breeze_level.upper()])

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        all_data = self.coordinator.data

        level = self.api.parse_value(
            self.api.get_field_value(self.coordinator.data, CURRENT_LEVEL_FIELD.name),
            DataType.LEVEL,
        )

        self._state = (level == Level.BREEZE.value)

        self.async_write_ha_state()

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
    discovery_info=None,
) -> None:
    """Call the Renson integration to setup."""

    api: RensonVentilation = hass.data[DOMAIN][config_entry.entry_id]["api"]
    coordinator: RensonCoordinator = hass.data[DOMAIN][config_entry.entry_id][
        "coordinator"
    ]

    async_add_entities([RensonBreezeSwitch(api, coordinator)])
