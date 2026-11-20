from __future__ import annotations

import logging

from homeassistant.components.button import (
    DOMAIN as ENTITY_DOMAIN,
    ButtonEntity as BaseEntity,
)
from . import XEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    attrs = []
    coordinator = hass.data[entry.entry_id]['coordinator']
    for conv in coordinator.converters:
        if conv.parent or conv.domain != ENTITY_DOMAIN:
            continue
        attrs.append(conv.attr)
        async_add_entities([ButtonEntity(coordinator, conv)])
    _LOGGER.info('async_setup_entry: %s', [ENTITY_DOMAIN, attrs])


class ButtonEntity(XEntity, BaseEntity):
    async def async_press(self):
        """Press the button."""
        fun = self.conv.encode(self.coordinator, {}, None)
        if fun and callable(fun):
            res = await fun() or {}
            self._attr_extra_state_attributes.update(res)
            # 主动写一次：否则按钮返回值要等下一次轮询（最多 60s）才出现在前端，
            # 而轮询推送现在只写"有变化"的实体，按钮自身属性永远不变。
            self.async_write_ha_state()
