import requests
from time import time, sleep
import os
import json

# https://docs.kraken.com/rest/#section/Rate-Limits, but...
# Using the listed limit still triggers "Too many requests". Delay++?
request_delay = 10

# https://docs.kraken.com/rest/#tag/Spot-Market-Data/operation/getOHLCData
points_per_ohlc_batch = 720

history_iterations = 10
now = time()

# Output per pair: [int <time>, string <open>,
#                   string <high>, string <low>, string <close>,
#                   string <vwap>, string <volume>, int <count>]

prio_pairs = ['XBTEUR', 'ETHEUR', 'SOLEUR']
alt_pairs = ['BONKEUR', 'WIFEUR', 'UNIEUR', 'SUSHIEUR',
             'MATICEUR', 'OPEUR', 'ARBEUR', 'AVAXEUR']
all_pairs = prio_pairs + alt_pairs

# / 100 and * 100 to round to hundreds, int to truncate unused decimals
history_steps_15min = [int((now-i*(points_per_ohlc_batch*15*60)) / 100) * 100 for i in range(history_iterations)]
history_steps_60min = [int((now-i*(points_per_ohlc_batch*60*60)) / 100) * 100 for i in range(history_iterations)]
step_sets = {15: history_steps_15min, 60: history_steps_60min}

def get_price_info(pair, interval, since):
    url = 'https://api.kraken.com/0/public/OHLC?' \
          + 'pair=' + pair \
          + '&interval=' + str(interval) \
          + '&since=' + str(since)
    price_data = requests.get(url).json()
    if len(price_data['error']) > 0:
        print('Error occurred on request: ' + str(price_data['error']))
        sleep(2)
        price_data = get_price_info(pair, interval, since)
    return price_data

for pair in all_pairs:
    for step_size in step_sets:
        history_steps = step_sets[step_size]
        if not os.path.exists(os.path.join(pair, str(step_size)+'min')):
            os.makedirs(os.path.join(pair, str(step_size)+'min'))
        
        for iteration in range(history_iterations):
            since_when = history_steps[iteration]
            filename = os.path.join(pair, str(step_size)+'min' \
                                    , 'from_unix_' + str(since_when) + '.json')
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(get_price_info(pair, step_size, since_when), f)

            # Don't spam the API, it doesn't like that
            print(f'Retrieved data for ({pair}, {step_size}, {since_when}).')
            sleep(request_delay)
