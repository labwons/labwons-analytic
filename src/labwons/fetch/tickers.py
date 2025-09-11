from labwons.logs import logger
from labwons.util import DATETIME, PATH

from pandas import DataFrame, concat
from re import compile
from requests import get, Session
from time import sleep, perf_counter
from typing import Dict


SECTOR_CODE:Dict[str, str] = {
    'WI100': '에너지', 
    'WI110': '화학',
    'WI200': '비철금속', 
    'WI210': '철강', 
    'WI220': '건설', 
    'WI230': '기계', 
    'WI240': '조선', 
    'WI250': '상사,자본재', 
    'WI260': '운송',
    'WI300': '자동차', 
    'WI310': '화장품,의류', 
    'WI320': '호텔,레저', 
    'WI330': '미디어,교육', 
    'WI340': '소매(유통)',
    'WI400': '필수소비재', 
    'WI410': '건강관리',
    'WI500': '은행', 
    'WI510': '증권', 
    'WI520': '보험',
    'WI600': '소프트웨어', 
    'WI610': 'IT하드웨어', 
    'WI620': '반도체', 
    'WI630': 'IT가전', 
    'WI640': '디스플레이',
    'WI700': '통신서비스',
    'WI800': '유틸리티'
}

CODE_LABEL:Dict[str, str] = {
    'CMP_CD': 'ticker', 
    'CMP_KOR': 'name',
    'SEC_CD': 'sectorCode', 
    'SEC_NM_KOR': 'sectorName',
    'IDX_CD': 'industryCode', 
    'IDX_NM_KOR': 'industryName',
}

REITS_CODE:Dict[str, str] = {
    "088980": "맥쿼리인프라",
    "395400": "SK리츠",
    "365550": "ESR켄달스퀘어리츠",
    "330590": "롯데리츠",
    "348950": "제이알글로벌리츠",
    "293940": "신한알파리츠",
    "432320": "KB스타리츠",
    "094800": "맵스리얼티1",
    "357120": "코람코라이프인프라리츠",
    "448730": "삼성FN리츠",
    "451800": "한화리츠",
    "088260": "이리츠코크렙",
    "334890": "이지스밸류리츠",
    "377190": "디앤디플랫폼리츠",
    "404990": "신한서부티엔디리츠",
    "417310": "코람코더원리츠",
    "400760": "NH올원리츠",
    "350520": "이지스레지던스리츠",
    "415640": "KB발해인프라",
}

EXCEPTIONALS = {
    '950160': {
        "name": "코오롱티슈진",
        "industryCode": "WI410",
        "industryName": "건강관리",
        "sectorCode": "G35",
        "sectorName": "건강관리"
    },
    '950210': {
        'name': '프레스티지바이오파마',
        "industryCode": "WI410",
        "industryName": "건강관리",
        "sectorCode": "G35",
        "sectorName": "건강관리"
    },
    '009410': {
        'name': '태영건설',
        "industryCode": "WI220",
        "industryName": "건설",
        "sectorCode": "G20",
        "sectorName": "산업재"
    },
    '052020': {
        'name': '에스티큐브',
        "industryCode": "WI410",
        "industryName": "건강관리",
        "sectorCode": "G35",
        "sectorName": "건강관리"
    }
}

class MarketSectors:

    @classmethod
    def fetch(cls, date:str=None) -> DataFrame:
        stime = perf_counter()
        logger.info('RUN [FETCH SECTOR COMPOSITION]')

        date = date if date else DATETIME.WISE
        if date is None:
            logger.error(f'- FAILED TO FETCH SECTOR COMPOSITION DATE')
            return

        logger.info(f'- MARKED RESOURCE DATE: {date}')

        objs, size = [], len(SECTOR_CODE) + 1
        for n, (code, name) in enumerate(SECTOR_CODE.items()):
            logger.info(f"- SUCCEED IN FETCHING ({str(n + 1).zfill(2)}/{size}): {code} {name}")
            sector = cls.fetchWiseGroup(code, date)
            if sector.empty:
                logger.error(f'- FAILED TO FETCH ({str(n + 1).zfill(2)}/{size}): {code} {name}')
                return
            objs.append(sector)

        reits = DataFrame(data={'CMP_KOR': REITS_CODE.values(), 'CMP_CD': REITS_CODE.keys()})
        reits[['SEC_CD', 'IDX_CD', 'SEC_NM_KOR', 'IDX_NM_KOR']] = ['G99', 'WI999', '리츠', '리츠']
        objs.append(reits)
        logger.info(f"- SUCCEED IN FETCHING ({size}/{size}): WI999 리츠")

        data = concat(objs, axis=0, ignore_index=True)

        data.drop(inplace=True, columns=[key for key in data if not key in CODE_LABEL])
        data.drop(inplace=True, index=data[data['SEC_CD'].isna()].index)
        data.rename(inplace=True, columns=CODE_LABEL)
        data.set_index(inplace=True, keys="ticker")
        data['industryName'] = data['industryName'].str.replace("WI26 ", "")

        sc_mdi = data[(data['industryCode'] == 'WI330') & (data['sectorCode'] == 'G50')].index
        sc_edu = data[(data['industryCode'] == 'WI330') & (data['sectorCode'] == 'G25')].index
        sc_sw = data[(data['industryCode'] == 'WI600') & (data['sectorCode'] == 'G50')].index
        sc_it = data[(data['industryCode'] == 'WI600') & (data['sectorCode'] == 'G45')].index
        data.loc[sc_mdi, 'industryCode'], data.loc[sc_mdi, 'industryName'] = 'WI331', '미디어'
        data.loc[sc_edu, 'industryCode'], data.loc[sc_edu, 'industryName'] = 'WI332', '교육'
        data.loc[sc_sw, 'industryCode'], data.loc[sc_sw, 'industryName'] = 'WI601', '소프트웨어'
        data.loc[sc_it, 'industryCode'], data.loc[sc_it, 'industryName'] = 'WI602', 'IT서비스'

        adder = {}
        for key in EXCEPTIONALS:
            if not key in data.index:
                adder[key] = EXCEPTIONALS[key]
        exceptionals = DataFrame(adder).T

        data = concat(objs=[data, exceptionals], axis=0)
        data['date'] = date
        
        logger.info(f'END [FETCH SECTOR COMPOSITION] {len(data):,d} ITEMS: {perf_counter() - stime:.2f}')
        return data

    @classmethod
    def fetchWiseGroup(cls, code:str, date:str="", countdown:int=5) -> DataFrame:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0",
            "Accept-Language": "ko,en;q=0.9,en-US;q=0.8",
            "Referer": "http://www.wiseindex.com/"
        }

        session = Session()
        session.headers.update(headers)
        try:
            resp = get(
                url=f'http://www.wiseindex.com/Index/GetIndexComponets?ceil_yn=0&dt={date}&sec_cd={code}',
                # proxies=proxies
            )
        except (Exception, TypeError):
            return DataFrame()

        if not resp.status_code == 200:
            if countdown == 0:
                return DataFrame()
            else:
                sleep(5)
                return cls.fetchWiseGroup(code, date, countdown - 1)
        if "hmg-corp" in resp.text:
            return DataFrame()
        return DataFrame(resp.json()['list'])
    
