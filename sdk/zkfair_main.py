import asyncio
from loguru import logger
import aiohttp
from sdk.excel import Excel


async def excel_write(address: str, quantity: float, number: int):
    Excel.sheet[f'A{number+1}'] = address
    Excel.sheet[f'B{number+1}'] = quantity


async def get_response(response):
    return await response.json(content_type=None)


async def request_(address: str, number: int, params):

    async with aiohttp.ClientSession() as session:
       try:

            response = await session.get('https://api.zkfair.io/data/api/community-airdrop', params=params)
            token_1 = await get_response(response)
            await excel_write(address=address, quantity=sum(list(float(token_1["community_airdrop"][_]["value_decimal"])
                                                                 for _ in ("Polygon zkEVM", "Lumoz", "zkRollups"))), number=number)

       except Exception as e:
           logger.error(f'Ошибка: {e}')


async def get_eligible(wallets: list):

    tasks = []
    logger.info(f'Найдено {len(wallets)} кошельков')
    for address in wallets:
        params = {
            'address': address.lower(),
        }

        tasks.append(asyncio.create_task(request_(address, wallets.index(address)+1, params)))

    await asyncio.gather(*tasks)


def main_check(wallets: list):
    Excel()

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(get_eligible(wallets))
        loop.close()

    except:
        logger.error('Проблема с указанием кошелька(ов)')


    Excel.workbook.save('results/result.xlsx')
