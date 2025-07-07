import re
import time
from abc import ABC, abstractmethod
from enum import Enum

import requests

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:137.0) Gecko/20100101 Firefox/137.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,es-CL;q=0.5',
    # 'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Connection': 'keep-alive',
    # 'Cookie': 'AMCV_673031365C06A5620A495CFC^%^40AdobeOrg=281789898^%^7CMCIDTS^%^7C20155^%^7CMCMID^%^7C17346785853598944552742459662462401285^%^7CMCAAMLH-1726237583^%^7C4^%^7CMCAAMB-1741355770^%^7C6G1ynYcLPuiQxYZrsz_pkqfLG9yMXBpb2zX5dvJdYQJzPXImdj0y^%^7CMCOPTOUT-1741362971s^%^7CNONE^%^7CMCSYNCSOP^%^7C411-19980^%^7CvVersion^%^7C4.1.0; dtCookie=v_4_srv_10_sn_5433FD19C8C0C219C6F799E138183595_perc_100000_ol_0_mul_1_app-3A0eda9ac06dd55ae7_1_rcs-3Acss_0',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Priority': 'u=0, i',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
}


class Endpoint(str, Enum):
    sifm_consulta = "sifmConsulta"
    rfi = "rfi"


class GwtCodes(ABC):

    def __init__(self, endpoint: Endpoint):
        self.browser = "safari"
        self.endpoint = endpoint
        self.updated_at = time.time()
        self._gwt_permutation = self.get_gwt_permutation()
        self._strong_name = self.get_strong_name()

    @property
    def gwt_permutation(self):
        now = time.time()
        time_delta = now - self.updated_at
        if time_delta > 60 * 60:  # refresh every hour
            self.update()
        return self._gwt_permutation

    @property
    def strong_name(self):
        now = time.time()
        time_delta = now - self.updated_at
        if time_delta > 24 * 60 * 60:  # refresh daily
            self.update()
        return self._strong_name

    def update(self) -> None:
        self._gwt_permutation = self.get_gwt_permutation()
        self._strong_name = self.get_strong_name()
        self.updated_at = time.time()

    def get_gwt_permutation(self):
        """Fetch the current permutation token used by the GWT frontend."""
        url = f'https://www4.sii.cl/{self.endpoint}Internet/{self.endpoint}.nocache.js'
        r = requests.get(url, headers=HEADERS)
        text = r.text
        browser_var = re.findall(rf"(\w+)='{self.browser}'", text)[0]
        gwt_permutation_var = re.findall(rf"\[{browser_var}\],(\w+)", text)[0]
        gwt_permutation = re.findall(rf"{gwt_permutation_var}='(\w+)'", text)[0]
        return gwt_permutation

    @abstractmethod
    def get_strong_name(self):
        """Return the strong name used to construct RPC requests."""


class SifmConsulta(GwtCodes):

    def __init__(self):
        super(SifmConsulta, self).__init__(endpoint=Endpoint.sifm_consulta.value)

    def get_strong_name(self):
        """Retrieve the strong name for the ``sifmConsulta`` service."""
        url = f"https://www4.sii.cl/{self.endpoint}Internet/{self.gwt_permutation}.cache.html"
        r = requests.get(url, headers=HEADERS)
        text = r.text
        browser_var = re.findall(r"(\w+)='svcConsulta'", text)[0]
        strong_name = re.findall(rf"{browser_var},'(\w+)'", text)[0]
        return strong_name


class Rfi(GwtCodes):

    def __init__(self):
        super(Rfi, self).__init__(endpoint=Endpoint.rfi.value)

    def get_strong_name(self):
        """Retrieve the strong name for the ``rfi`` service."""
        url = f"https://www4.sii.cl/{self.endpoint}Internet/{self.gwt_permutation}.cache.html"
        r = requests.get(url, headers=HEADERS)
        text = r.text
        pattern = r"'formularioFacade','([A-Z0-9]{32})'"
        strong_names = re.findall(pattern, text)
        strong_name = strong_names[0]
        return strong_name
