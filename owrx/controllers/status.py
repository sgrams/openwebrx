from . import Controller
from owrx.version import openwebrx_version
from owrx.sdr import SdrService
from owrx.config import Config
from owrx.receiverid import ReceiverId, KeyException
import json

import logging

logger = logging.getLogger(__name__)


class StatusController(Controller):
    def getProfileStats(self, profile):
        return {
            "name": profile["name"],
            "center_freq": profile["center_freq"],
            "sample_rate": profile["samp_rate"],
        }

    def getReceiverStats(self, receiver):
        stats = {
            "name": receiver.getName(),
            # TODO would be better to have types from the config here
            "type": type(receiver).__name__,
            "profiles": [self.getProfileStats(p) for p in receiver.getProfiles().values()]
        }
        return stats

    def indexAction(self):
        pm = Config.get()
        headers = None
        if "Authorization" in self.request.headers:
            try:
                headers = ReceiverId.getResponseHeader(self.request.headers["Authorization"])
            except KeyException:
                logger.exception("error processing authorization header")
        status = {
            "receiver": {
                "name": pm["receiver_name"],
                "admin": pm["receiver_admin"],
                "gps": pm["receiver_gps"],
                "asl": pm["receiver_asl"],
                "location": pm["receiver_location"],
            },
            "max_clients": pm["max_clients"],
            "version": openwebrx_version,
            "sdrs": [self.getReceiverStats(r) for r in SdrService.getSources().values()]
        }
        self.send_response(json.dumps(status), content_type="application/json", headers=headers)
