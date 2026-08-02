import pandas as pd
import glob
import json
import datetime
import os

FIELDNAMES = [
    'code',
    'url',
    'file',
    'library',
    'deleted',
    'lastSeen',
    'brand',
    'model',
    'package',
    'type',
    'describe',
    'erpComponentName',
    'price',
    'stock',
    'MOQ',
    'category',
    'firstSeen',
    'pcbaMinQty',
    'pcbaMinPrice',
]

def get_unit_price(prices, qty):
    for price in prices:
        start = price['startNumber']
        end = price['endNumber']
        if start <= qty and (end == -1 or qty <= end):
            return price['productPrice']
    return 99999

def get_data_manual_file(row):
    return (
        row.get('dataManualUrl')
        or row.get('dataManualOfficialLink')
        or row.get('dataManualFileAccessIdUrl')
        or row.get('dataManualFileAccessId')
        or ''
    )

if __name__ == '__main__':
    items = []
    now = datetime.datetime.now(tz=datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    for file in glob.glob('parts-page*.json'):
        print(file)
        with open(file) as f: rows = json.load(f)['data']['componentPageInfo']['list']

        for row in rows:
            moq = row['minPurchaseNum'] or 99999
            price = get_unit_price(row['componentPrices'], moq)
            pcba_min_qty = max(moq + (row['lossNumber'] or 0), row['leastPatchNumber'] or 0)
            pcba_min_price = round(get_unit_price(row['componentPrices'], pcba_min_qty) * pcba_min_qty, 10)
            items.append({
                'code':    row['componentCode'],
                'url':     row['urlSuffix'],
                'file':    get_data_manual_file(row),
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
                'category': row['secondSortName'] or 'Undefined',
                'firstSeen': now,
                'pcbaMinQty': pcba_min_qty,
                'pcbaMinPrice': pcba_min_price,
            })

    df = pd.DataFrame(items)
    df.sort_values('code', inplace=True)

    filename = 'economic-parts.csv'
    if not os.path.isfile(filename):
        df.to_csv(filename, index=False)
        exit()

    old_df = pd.read_csv(filename, keep_default_na=False)
    if 'firstSeen' not in old_df.columns:
        old_df['firstSeen'] = ''
    if 'pcbaMinQty' not in old_df.columns:
        old_df['pcbaMinQty'] = ''
    if 'pcbaMinPrice' not in old_df.columns:
        old_df['pcbaMinPrice'] = ''

    old_items = old_df.set_index('code').to_dict('index')
    def get_first_seen(row):
        old_item = old_items.get(row['code'])
        if old_item is None or str(old_item.get('deleted')) == '1':
            return row['firstSeen']
        return old_item.get('firstSeen') or row['firstSeen']
    df['firstSeen'] = df.apply(get_first_seen, axis=1)

    deleted_codes = set(old_df['code']) - set(df['code'])
    if deleted_codes:
        deleted_items = old_df[old_df['code'].isin(deleted_codes)].copy()
        deleted_items['deleted'] = 1
        df = pd.concat([df, deleted_items], ignore_index=True)
    df.sort_values(['deleted', 'code'], inplace=True)
    df.to_csv(filename, index=False, columns=FIELDNAMES)
