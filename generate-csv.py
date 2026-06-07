import pandas as pd
import glob
import json
import datetime
import os

TYPE_CATEGORY_OVERRIDES = {
    'AC-DC Controllers and Regulators': 'Power Management (PMIC)',
    'Aluminum Electrolytic Capacitors - Leaded': 'Capacitors',
    'Antennas': 'RF & Wireless',
    'Audio Connectors': 'Connectors',
    'Button And Strip Battery Connector': 'Connectors',
    'Crystal Oscillators': 'Crystals, Oscillators, Resonators',
    'Darlington Transistors': 'Transistors/Thyristors',
    'Digital Potentiometers': 'Interface',
    'DIP Switches': 'Switches',
    'Disposable fuses': 'Circuit Protection',
    'ESD Protection Devices': 'Circuit Protection',
    'Gate Drivers': 'Power Management (PMIC)',
    'LED Drivers': 'LED Drivers',
    'Limit Switches': 'Switches',
    'Logic Output Optoisolators': 'Optoisolators',
    'LVDS ICs': 'Interface',
    'Multilayer Ceramic Capacitors MLCC - Leaded': 'Capacitors',
    'Pin Headers': 'Connectors',
    'Pluggable System Terminal Block': 'Connectors',
    'Pogo Pin Spring Probe Connector': 'Connectors',
    'Polymer Aluminum Capacitors': 'Capacitors',
    'Polypropylene Film Capacitors (CBB)': 'Capacitors',
    'Power Distribution Switches': 'Power Management (PMIC)',
    'Power Inductors': 'Inductors, Coils, Chokes',
    'Power Management - Specialized': 'Power Management (PMIC)',
    'Pre-ordered Connectors': 'Connectors',
    'Pre-ordered Products': 'Pre-ordered',
    'Pre-ordered RLCs': 'Pre-ordered',
    'Pre-ordered transistors': 'Transistors/Thyristors',
    'Programmable Oscillators': 'Crystals, Oscillators, Resonators',
    'Pulse Transformers(LAN)': 'Transformers',
    'RF Amplifiers': 'RF & Wireless',
    'RF Filters': 'RF & Wireless',
    'RF Switches': 'RF & Wireless',
    'Rotary Switches': 'Switches',
    'Safety Capacitors': 'Capacitors',
    'Screw Terminal Blocks': 'Connectors',
    'Slide Switches': 'Switches',
    'Spring Clamp System Terminal Block': 'Connectors',
    'Super Barrier Rectifiers (SBR)': 'Diodes',
    'Supervisor and Reset ICs': 'Power Management (PMIC)',
    'Through Hole Resistors': 'Resistors',
    'Triac, SCR Output Optoisolators': 'Optoisolators',
    'USB Connectors': 'Connectors',
    'Varistors': 'Circuit Protection',
    'WiFi Modules': 'RF & Wireless',
    'Wire To Board Connector': 'Connectors',
}

if __name__ == '__main__':
    items = []
    now = datetime.datetime.now(tz=datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
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
                'category': row['secondSortName'] or 'Undefined',
            })

    df = pd.DataFrame(items)
    df.sort_values('code', inplace=True)
    output_columns = list(df.columns)
    type_category_map = df.drop_duplicates('type').set_index('type')['category'].to_dict()

    filename = 'economic-parts.csv'
    if not os.path.isfile(filename):
        df.to_csv(filename, index=False)
        exit()

    old_df = pd.read_csv(filename)
    for column in df.columns:
        if column not in old_df.columns:
            old_df[column] = ''
    old_df = old_df.reindex(columns=df.columns)
    old_df['category'] = old_df['category'].fillna('')
    missing_category = old_df['category'].isin(['', 'Undefined'])
    old_df.loc[missing_category, 'category'] = old_df.loc[missing_category, 'type'].map(type_category_map)
    old_df['category'] = old_df['category'].fillna('')
    missing_category = old_df['category'].isin(['', 'Undefined'])
    old_df.loc[missing_category, 'category'] = old_df.loc[missing_category, 'type'].map(TYPE_CATEGORY_OVERRIDES)
    old_df['category'] = old_df['category'].fillna('')
    deleted_codes = set(old_df['code']) - set(df['code'])
    if deleted_codes:
        deleted_items = old_df[old_df['code'].isin(deleted_codes) & (old_df['category'] != '')].copy()
        deleted_items['deleted'] = 1
        df = pd.concat([df, deleted_items], ignore_index=True)
    df = df.reindex(columns=output_columns)
    df.sort_values(['deleted', 'code'], inplace=True)
    df.to_csv(filename, index=False)
