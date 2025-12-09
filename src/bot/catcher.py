from src.analysis.strategy import Strategy
from src.crypto.bithumb.market import Market
from src.crypto.bithumb.ticker import Ticker
from src.util.logger import Logger
from src.util.mailing import Mail
from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd


TZ = ZoneInfo('Asia/Seoul')
TIMEUNIT = 'min'
INTERVAL = 30

logger = Logger('BOT@v1')
market = Market(logger=logger)
market.update_baseline(period=TIMEUNIT, unit=INTERVAL, count=200)

strategy = Strategy(market.baseline)
strategy.install()
signal = strategy.squeeze_expand()
report = strategy.to_report(signal)

diff = datetime.now(TZ) - pd.to_datetime(report.index[-1]).tz_localize(TZ)
if TIMEUNIT != 'min' or (TIMEUNIT == 'min' and int(diff.total_seconds() / 60) <= INTERVAL):

    clock = datetime.now(TZ).strftime("%Y/%m/%d %H:%M")
    logger(f'□ 감지 시간: {report.index[-1].replace("-", "/").replace("T", " ")[:-3]}')
    logger(f'□ 현재 시간: {clock}')
    for ticker in str(report.values[-1]).split(","):
        coin = Ticker(ticker=f'KRW-{ticker}')
        snap = coin.snapShot()
        logger(f'□ TICKER: {ticker}')
        logger(f'  - LINK: https://m.bithumb.com/react/trade/chart/{ticker}-KRW')
        logger(f'  - 현재가: {snap["trade_price"]}원')
        logger(f'  - 등락률: {100 * snap["signed_change_rate"]:.2f}%')
        logger(f'  - 거래대금: {snap["acc_trade_price_24h"] / 1e+8:.2f}억원')

    text = []
    for line in str(logger.stream).splitlines():
        line = line[20:]
        if "TICKER" in line:
            ticker = line[line.find(":") + 2:]
            url = f'https://m.bithumb.com/react/trade/chart/{ticker}-KRW'
            line = line.replace(": ", f': <a href="{url}">') + "</a>"
        if "LINK" in line:
            continue
        text.append(line)

    stream = f"""<!doctype html><html><body><p>{"<br>".join(text)}</p>{report.to_html()}</body></html>"""
    mail = Mail()
    mail.Subject = f'TRADER@v1 ON {clock}'
    mail.To = 'jhlee_0319@naver.com'
    mail.content = stream
    mail.send("html", "utf-8")

else:
    logger('NO SIGNALS DETECTED, SYSTEM ABORT')


