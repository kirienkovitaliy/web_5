import aiohttp
import asyncio
import sys
from datetime import date, timedelta


class CurrencyConverter:
    def __init__(self):
        self.url = 'https://api.privatbank.ua/p24api/exchange_rates?json&date='
        self.currencies = ['USD', 'EUR']

    async def get_rates(self, days):
        today = date.today()
        start_date = today - timedelta(days=days)

        async with aiohttp.ClientSession() as session:
            tasks = []
            for currency in self.currencies:
                for single_date in (start_date + timedelta(n+1) for n in range(days)):
                    formatted_date = single_date.strftime('%d.%m.%Y')
                    tasks.append(asyncio.ensure_future(self.get_rate(session, formatted_date, currency)))

            rates = await asyncio.gather(*tasks)
            return rates

    async def get_rate(self, session, date, currency):
        while True:
            try:
                async with session.get(f'{self.url}{date}') as response:
                    if response.status == 429:
                        await asyncio.sleep(1)
                        continue
                    else:
                        response_json = await response.json()
                        for rate in response_json['exchangeRate']:
                            if rate['currency'] == currency:
                                return {date: {currency: {'sale': rate['saleRate'], 'purchase': rate['purchaseRate']}}}
            except Exception as e:
                print(f'Error getting rate for {currency} on {date}: {e}')
                return {'date': date, 'currency': currency, 'rate': None}


async def main():
    try:
        days = int(sys.argv[1])
        if days > 10:
            raise ValueError('Cannot get rates for more than 10 days.')
    except (ValueError, IndexError):
        print('Please provide a valid number of days (up to 10) as an argument.')
        return

    converter = CurrencyConverter()
    rates = await converter.get_rates(days)
    for rate in rates:
        print(rate)


if __name__ == '__main__':
    asyncio.run(main())
