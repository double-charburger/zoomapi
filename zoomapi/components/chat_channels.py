"""Zoom.us REST API Python Client -- Chat Messages component"""

from zoomapi import util
from zoomapi.components import base

class ChatChannelsComponentV2(base.BaseComponent):
    """Component dealing with all chat channels related matters"""

    def list(self, **kwargs):
        return self.get_request("/chat/users/me/channels")

    def create(self, **kwargs):
        return self.post_request("/chat/users/me/channels", data=kwargs)

    def update(self, **kwargs):
        util.require_keys(kwargs, "channel_id")
        return self.patch_request("/chat/channels/{}".format(kwargs.get("channel_id")), params=kwargs, data=kwargs)

    def delete(self, **kwargs):
        util.require_keys(kwargs, "channel_id")
        return self.delete_request("/chat/channels/{}".format(kwargs.get("channel_id")), params=kwargs)

    def get(self, **kwargs):
        util.require_keys(kwargs, "channel_id")
        return self.get_request("/chat/channels/{}".format(kwargs.get("channel_id")), params=kwargs)

    def list_members(self, **kwargs):
        util.require_keys(kwargs, "channel_id")
        return self.get_request("/chat/channels/{}/members".format(kwargs.get("channel_id")), params=kwargs)