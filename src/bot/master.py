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
from time import perf_counter
import os


utc = datetime.now(ZoneInfo('UTC'))
kst = datetime.now(ZoneInfo('Asia/Seoul'))

logger = Logger('BOT@v1')
logger.formatter = "%(message)s"
logger(f"RUNS ON: {os.getenv('EVENT_NAME', 'LOCAL').upper()}")

# BASELINE UPDATE
tic = perf_counter()
market = Market()
market.update_baseline(interval='60minutes')
market_time = datetime.strptime(market.baseline.index[-1], "%Y-%m-%dT%H:%M:%S")
if (market_time.hour > kst.hour) and (kst.minute < 45):
    market.baseline = market.baseline.iloc[:-1]
for failed in market.failures:
    logger(f"⚠️  FAILED TICKER: {failed}")
market.reset_failures()
elapsed = perf_counter() - tic
logger(f"UPDATE BASELINE ... {int(elapsed // 60)}m {int(elapsed % 60)}s")
logger(f'KST: {kst.strftime("%Y/%m/%d %H:%M")}')
logger(f'MKT: {market_time.strftime("%Y/%m/%d %H:%M")}')

# INSTALL STRATEGY
strategy = Strategy(market.baseline)
strategy.install()


# REPORT SIGNALS
send = False
book = TradingBook()
for name, signal in [
    ("Squeeze & Expand", strategy.squeeze_expand()),
]:
    detect = signal.iloc[-1].dropna()
    if detect.empty:
        continue

    logger(f'<h1>{name}</h1>')
    logger(f'---')
    for n, ticker in enumerate(detect.index, start=1):
        coin = Ticker(ticker=ticker)
        coin.to_logger(logger)

        book.append(
            ticker=ticker,
            status='WATCH',
            signal=name,
            signaled_time=market.baseline.index[-1],
            signaled_price=coin['trade_price'],
            signaled_amount=coin['acc_trade_price_24h'],
            signaled_volume=coin['acc_trade_volume_24h'],
        )
    send = True

book.save()

# SEND E-MAIL
if send:
    mail = Mail()
    mail.Subject = f'TRADER@v1 ON {kst.strftime("%Y/%m/%d %H:%M")}'
    mail.content = mail.to_html(logger.to_html())
    mail.To = ",".join([
        "jhlee_0319@naver.com",
        # "ghost3009@naver.com"
    ])
    mail.send("html", "utf-8")

else:
    logger('NO SIGNALS DETECTED ... SYSTEM ABORT')

