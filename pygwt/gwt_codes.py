import re
import time
from abc import ABC, abstractmethod
from enum import Enum

import requests


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
        if time_delta > 60 * 60:  # cada una hora
            self.update()
        return self._gwt_permutation

    @property
    def strong_name(self):
        now = time.time()
        time_delta = now - self.updated_at
        if time_delta > 24 * 60 * 60:  # un dia en segundos
            self.update()
        return self._strong_name

    def update(self) -> None:
        self._gwt_permutation = self.get_gwt_permutation()
        self._strong_name = self.get_strong_name()
        self.updated_at = time.time()

    def get_gwt_permutation(self):
        """ """
        url = f'https://www4.sii.cl/{self.endpoint}Internet/{self.endpoint}.nocache.js'
        r = requests.get(url)
        text = r.text
        browser_var = re.findall(rf"(\w+)='{self.browser}'", text)[0]
        gwt_permutation_var = re.findall(rf"\[{browser_var}\],(\w+)", text)[0]
        gwt_permutation = re.findall(rf"{gwt_permutation_var}='(\w+)'", text)[0]
        return gwt_permutation

    @abstractmethod
    def get_strong_name(self):
        ...


class SifmConsulta(GwtCodes):

    def __init__(self):
        super(SifmConsulta, self).__init__(endpoint=Endpoint.sifm_consulta.value)

    def get_strong_name(self):
        """ """
        url = f"https://www4.sii.cl/{self.endpoint}Internet/{self.gwt_permutation}.cache.html"
        r = requests.get(url)
        text = r.text
        browser_var = re.findall(r"(\w+)='svcConsulta'", text)[0]
        strong_name = re.findall(rf"{browser_var},'(\w+)'", text)[0]
        return strong_name


class Rfi(GwtCodes):

    def __init__(self):
        super(Rfi, self).__init__(endpoint=Endpoint.rfi.value)

    def get_strong_name(self):
        """ """
        url = f"https://www4.sii.cl/{self.endpoint}Internet/{self.gwt_permutation}.cache.html"
        r = requests.get(url)
        text = r.text
        pattern = r"'formularioFacade','([A-Z0-9]{32})'"
        strong_names = re.findall(pattern, text)
        strong_name = strong_names[0]
        return strong_name
