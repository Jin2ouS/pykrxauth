from abc import abstractmethod

from .session import get_session


class Get:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://data.krx.co.kr/contents/MDC/MDI/outerLoader/index.cmd",
        }

    def read(self, **params):
        resp = get_session().get(self.url, headers=self.headers, params=params)
        return resp

    @property
    @abstractmethod
    def url(self):
        return NotImplementedError


class Post:
    def __init__(self, headers=None):
        self.headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://data.krx.co.kr/contents/MDC/MDI/outerLoader/index.cmd",
        }
        if headers is not None:
            self.headers.update(headers)

    def read(self, **params):
        resp = get_session().post(self.url, headers=self.headers, data=params)
        return resp

    @property
    @abstractmethod
    def url(self):
        return NotImplementedError
