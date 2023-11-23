import sys
from datetime import datetime, timedelta
import logging

import aiohttp
import asyncio


async def request(url: str):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    r = await resp.json()
                    return r
                logging.error(f"Error status: {resp.status} for {url}")
                return None
        except aiohttp.ClientConnectorError as err:
            logging.error(f"Connection error: {str(err)}")
            return None



async def get_exchange(nums_of_days: int, spec_exch: str=None):
    nums_of_days = int(nums_of_days)
    exchange_rates = []
    
    
    for num in range(nums_of_days):   
                  
        dl = datetime.now() - timedelta(num)
        shift = dl.strftime("%d.%m.%Y")
        
        result = await request(f'https://api.privatbank.ua/p24api/exchange_rates?date={shift}')
        
        if result:
            rates = result.get("exchangeRate")
            currency_data = {}
            
            for exch in ['EUR', 'USD']:
                if spec_exch is not None:
                    currency = spec_exch
                else:
                    currency = exch

                exc = next((element for element in rates if element["currency"] == currency), None)
                if exc:
                    currency_data[currency] = {
                        "sale": round(exc["saleRateNB"], 1),
                        "purchase": round(exc["purchaseRateNB"], 1)
                    }
                    
            exchange_rates.append({shift: currency_data})
            
            
    return exchange_rates if exchange_rates else "No data for such a period"
        

async def main():
    if int(sys.argv[1]) > 10:
        print("Require max 10 days")
        return
    
    else:
        results = []
        
        if len(sys.argv) == 2:
            print("Exchange by default is:")
            rates = await get_exchange(sys.argv[1])
            results.extend(rates)
            
        elif len(sys.argv) == 3:
            print("Specific exchange is:")
            rates = await get_exchange(sys.argv[1], sys.argv[2])
            results.extend(rates)
            
        print(results)
    
if __name__ == "__main__":
    asyncio.run(main())
