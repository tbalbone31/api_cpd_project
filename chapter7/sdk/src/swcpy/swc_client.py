import httpx
import swcpy.swc_config as config
from .schemas import League, Team, Player, Performance
from typing import List
import backoff
import logging
logger = logging.getLogger(__name__)

class SWCClient:
    """Interacts with the SportsWorldCentral APOI.

    This SDK Class simplifies the process of using the SWC Fantasy Football API.
    It supports all the functions of the SWC API and returns validated data types.

    Typical usage example:

        client = SWCClient()
        response = client.get_health_check()
    
    """

    HEALTH_CHECK_ENDPOINT = "/"
    LIST_LEAGUES_ENDPOINT = "/v0/leagues/"
    LIST_PLAYERS_ENDPOINT = "/v0/players/"
    LIST_PERFORMANCES_ENDPOINT = "/v0/performances/"
    LIST_TEAMS_ENDPOINT = "/v0/teams/"
    GET_COUNTS_ENDPOINT = "/v0/counts/"

    def __init__(self, swc_base_url: str):
        self.swc_base_url = swc_base_url

    def get_health_check(self):
        # make the API call
        with httpx.Client(base_url=self.swc_base_url) as client:
            return client.get("/")

