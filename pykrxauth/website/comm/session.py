import os

import requests
from dotenv import load_dotenv

load_dotenv()

_session = requests.Session()
_logged_in = False

_LOGIN_PAGE = "https://data.krx.co.kr/contents/MDC/COMS/client/MDCCOMS001.cmd"
_LOGIN_JSP = "https://data.krx.co.kr/contents/MDC/COMS/client/view/login.jsp?site=mdc"
_LOGIN_URL = "https://data.krx.co.kr/contents/MDC/COMS/client/MDCCOMS001D1.cmd"
_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)


def get_session() -> requests.Session:
    return _session


def is_logged_in() -> bool:
    return _logged_in


def ensure_login() -> bool:
    """환경변수에 인증정보가 있으면 자동 로그인 시도"""
    if _logged_in:
        return True
    if os.getenv("KRX_ID") and os.getenv("KRX_PW"):
        return login()
    return False


def login(login_id: str = None, login_pw: str = None) -> bool:
    """KRX 로그인

    로그인 흐름:
    1. GET MDCCOMS001.cmd → 초기 JSESSIONID 발급
    2. GET login.jsp → iframe 세션 초기화
    3. POST MDCCOMS001D1.cmd → 실제 로그인
    4. CD011(중복 로그인) → skipDup=Y 추가 후 재전송

    Args:
        login_id: KRX 로그인 ID (없으면 환경변수 KRX_ID 사용)
        login_pw: KRX 로그인 비밀번호 (없으면 환경변수 KRX_PW 사용)

    Returns:
        bool: 로그인 성공 여부
    """
    global _logged_in
    login_id = login_id or os.getenv("KRX_ID")
    login_pw = login_pw or os.getenv("KRX_PW")

    if not login_id or not login_pw:
        return False

    try:
        # 1. 초기 세션 발급
        _session.get(_LOGIN_PAGE, headers={"User-Agent": _UA}, timeout=15)
        _session.get(
            _LOGIN_JSP, headers={"User-Agent": _UA, "Referer": _LOGIN_PAGE}, timeout=15
        )

        # 2. 로그인 요청
        payload = {
            "mbrNm": "",
            "telNo": "",
            "di": "",
            "certType": "",
            "mbrId": login_id,
            "pw": login_pw,
        }
        headers = {"User-Agent": _UA, "Referer": _LOGIN_PAGE}

        resp = _session.post(_LOGIN_URL, data=payload, headers=headers, timeout=15)
        data = resp.json()
        error_code = data.get("_error_code", "")

        # 3. CD011 중복 로그인 처리
        if error_code == "CD011":
            payload["skipDup"] = "Y"
            resp = _session.post(_LOGIN_URL, data=payload, headers=headers, timeout=15)
            data = resp.json()
            error_code = data.get("_error_code", "")

        # 4. 로그인 성공 여부 확인 (CD001 = 정상)
        if error_code == "CD001":
            _logged_in = True
            return True

        return False
    except Exception:
        return False
