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

now = datetime.now(TZ)
diff = now - pd.to_datetime(report.index[-2]).tz_localize(TZ)
if TIMEUNIT != 'min' or (TIMEUNIT == 'min' and (int(diff.total_seconds() / 60) <= 2 * INTERVAL)):

    clock = datetime.now(TZ).strftime("%Y/%m/%d %H:%M")
    logger(f'□ 감지 시간: {report.index[-1].replace("-", "/").replace("T", " ")[:-3]}')
    logger(f'□ 현재 시간: {clock}')
    for ticker in str(report.values[-1]).split(","):
        coin = Ticker(ticker=f'KRW-{ticker}')
        snap = coin.snapShot()
        logger(f'□ TICKER: <a href="https://m.bithumb.com/react/trade/chart/{ticker}-KRW">{ticker}</a>')
        logger(f'  - 현재가: {snap["trade_price"]}원')
        logger(f'  - 등락률: {100 * snap["signed_change_rate"]:.2f}%')
        logger(f'  - 거래대금: {snap["acc_trade_price_24h"] / 1e+8:.2f}억원')

    html = "<br>".join([l[20:] for l in str(logger.stream).splitlines()])
    mail = Mail()
    mail.Subject = f'TRADER@v1 ON {clock}'
    mail.To = 'jhlee_0319@naver.com'
    mail.content = f"""<!doctype html><html><body><p>{html}</p>{report.to_html()}</body></html>"""
    mail.send("html", "utf-8")

else:
    logger('NO SIGNALS DETECTED, SYSTEM ABORT')


