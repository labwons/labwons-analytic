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
if not "TradingBook" in globals():
    from src.bot.book.tradingbook import TradingBook
from datetime import datetime
from zoneinfo import ZoneInfo
import os


TZ = ZoneInfo('Asia/Seoul')
EVENT = os.getenv('EVENT_NAME', None)
TIMER = os.getenv('CRON_TIMER', '')
SENDMAIL = False

utc = datetime.now(ZoneInfo('UTC'))
kst = datetime.now(ZoneInfo('Asia/Seoul'))
if 15 <= utc.minute < 45:
    units = [30]
elif 45 <= utc.minute:
    units = [60]
else:
    units = [30, 60]

logger = Logger('BOT@v1')
logger(f'RUN TYPE: {EVENT} @{TIMER}')
book = TradingBook()
market = Market()
for unit in units:
    logger(f'BASELINE /{unit}min.')
    market.update_baseline(period='min', unit=unit, count=200)

    strategy = Strategy(market.baseline)
    timespan = strategy('KRW-BTC').index
    strategy.install()

    for name, signal in [
        ("Squeeze & Expand", strategy.squeeze_expand()),
    ]:
        report = strategy.to_report(signal)
        clock = datetime.now(TZ).strftime("%Y/%m/%d %H:%M")
        if report.index[-1] == timespan[-1]:
            logger.formatter = "%(message)s"
            logger(f'<h1>{name}</h1>')
            logger(f'□ 분석 시간: {clock}')
            logger(f'□ 주가 시간: {timespan[-1].replace("-", "/").replace("T", " ")[:-3]}')
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

                book.append(ticker)
                book.status = 'TBD'
                book.detected_signal = name
                book.detected_time = clock
                book.signal_confirmed_time = 'TBD'
                book.bid_price = 'TBD'
                book.execution_price = 'TBD'
                book.detected_price = snap["trade_price"]
                book.yield_from_detected = 'TBD'
                book.yield_from_executed = 'TBD'

            SENDMAIL = True

book.save()
if SENDMAIL:
    html = str(logger.stream) \
            .replace("\n", "<br>") \
            .replace("  -", f'{"&nbsp;" * 4}-') \
            .replace("---", "<hr>")
    # table = report.to_html(classes="styled-table", border=0)
    mail = Mail()
    mail.Subject = f'TRADER@v1 ON {datetime.now(TZ).strftime("%Y/%m/%d %H:%M")}'
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
        </body>
    </html>
    """


    user = ",".join([
        "jhlee_0319@naver.com",
        'wpgur3@gmail.com'
        # "ghost3009@naver.com"
    ])
    mail.To = user
    mail.send("html", "utf-8")

else:
    logger('NO SIGNALS DETECTED ... SYSTEM ABORT')

