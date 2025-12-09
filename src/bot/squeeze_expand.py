if not "Strategy" in globals():
    from src.analysis.strategy import Strategy
if not "Market" in globals():
    from src.crypto.bithumb.market import Market
if not "Ticker" in globals():
    from src.crypto.bithumb.ticker import Ticker
if not "Logger" in globals():
    from src.util.logger import Logger
if not "Mail" in globals():
    from src.util.mailing import Mail
from datetime import datetime
from zoneinfo import ZoneInfo


TZ = ZoneInfo('Asia/Seoul')
TIMEUNIT = 'min'
INTERVAL = 30
SENDMAIL = False
DEBUG = False

logger = Logger('BOT@v1')
market = Market(logger=logger)
market.update_baseline(period=TIMEUNIT, unit=INTERVAL, count=200)
logger.clear()

strategy = Strategy(market.baseline)
strategy.install()

signal = strategy.squeeze_expand()
report = strategy.to_report(signal)
timespan = strategy('KRW-BTC').index
if DEBUG or report.index[-1] in [timespan[-1], timespan[-2], timespan[-3]]:
    logger.formatter = "%(message)s"
    logger(f'<h1>Squeeze & Expand</h1>')
    logger(f'□ 분석 시간: {datetime.now(TZ).strftime("%Y/%m/%d %H:%M")}')
    logger(f'□ 주가 시간: {strategy("KRW-BTC").index[-1].replace("-", "/").replace("T", " ")[:-3]}')
    logger(f'□ 신호 발생: {report.index[-1].replace("-", "/").replace("T", " ")[:-3]}')
    logger(f'---')
    for n, ticker in enumerate(report.iloc[-1, -1].split(","), start=1):
        coin = Ticker(ticker=f'KRW-{ticker}')
        snap = coin.snapShot()
        logger(f'{n}. TICKER: <a href="https://m.bithumb.com/react/trade/chart/{ticker}-KRW">{ticker}</a>')
        logger(f'  - 현재가: {snap["trade_price"]}원')
        logger(f'  - 등락률: {100 * snap["signed_change_rate"]:.2f}%')
        logger(f'  - 거래대금: {snap["acc_trade_price_24h"] / 1e+8:.2f}억원')
        logger(f'---')

    SENDMAIL = True
else:
    logger('NO SIGNALS DETECTED ... SYSTEM ABORT')

if SENDMAIL:
    html = str(logger.stream) \
            .replace("\n", "<br>") \
            .replace("  -", f'{"&nbsp;" * 4}-') \
            .replace("---", "<hr>")
    table = report.to_html(classes="styled-table", border=0)
    mail = Mail()
    mail.Subject = f'TRADER@v1 ON {datetime.now(TZ).strftime("%Y/%m/%d %H:%M")}'
    mail.To = 'jhlee_0319@naver.com'
    mail.content = f"""
    <!doctype html>
    <html>    
        <style>
            .styled-table {{
                border-collapse: collapse;
                width: 100%;
                text-align: right;
            }}
            .styled-table th, .styled-table td {{
                border: 1px solid #ccc;
                padding: 8px;
                font-weight: 500;
            }}
        </style>
        <body>
            <p>{html}</p>
            {table}
        </body>
    </html>
    """
    mail.send("html", "utf-8")
