import pandas as pd
import glob
import json
import datetime
import os

if __name__ == '__main__':
    items = []
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    for file in glob.glob('parts-page*.json'):
        print(file)
        with open(file) as f: rows = json.load(f)['data']['componentPageInfo']['list']

        for row in rows:
            moq = row['minPurchaseNum'] or 99999
            filterPrices = filter(lambda x: x['startNumber'] >= moq, row['componentPrices'])
            sortedPrices = sorted(list(filterPrices), key=lambda x: x['startNumber'])
            price = 99999 if len(sortedPrices)==0 else sortedPrices[0]['productPrice']
            items.append({
                'code':    row['componentCode'],
                'url':     row['urlSuffix'],
                'file':    row['dataManualFileAccessId'],
                'library': row['componentLibraryType'],
                'deleted': 0,
                'lastSeen': now,

                'brand':    row['componentBrandEn'],
                'model':    row['componentModelEn'],
                'package':  row['componentSpecificationEn'],
                'type':     row['componentTypeEn'],
                'describe': row['describe'],
                'erpComponentName': row['erpComponentName'],

                'price': price,
                'stock': row['stockCount'],
                'MOQ':   row['minPurchaseNum'],
            })

    df = pd.DataFrame(items)
    df.sort_values('code', inplace=True)

    filename = 'economic-parts.csv'
    if not os.path.isfile(filename):
        df.to_csv(filename, index=False)
        exit()

    old_df = pd.read_csv(filename)
    deleted_codes = set(old_df['code']) - set(df['code'])
    if deleted_codes:
        deleted_items = old_df[old_df['code'].isin(deleted_codes)].copy()
        deleted_items['deleted'] = 1
        df = pd.concat([df, deleted_items], ignore_index=True)
    df.sort_values(['deleted', 'code'], inplace=True)
    df.to_csv(filename, index=False)
