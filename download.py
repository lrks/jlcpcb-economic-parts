import requests
import time

if __name__ == '__main__':
    page = 1

    while True:
        print(f'page: {page}')

        url = 'https://jlcpcb.com/api/overseas-pcb-order/v1/shoppingCart/smtGood/selectSmtComponentList/v2'
        r = requests.post(url, headers={'content-type':'application/json'}, json={
                'preferredComponentFlagCheck': False,
                'componentLibraryTypeCheck': False,
                'currentPage': page,
                'pageSize': 100,
                'searchSource': 'search',
                'componentAttributes': [],
                'componentLibraryType': 'base',
                'preferredComponentFlag': True,
                'stockFlag': None,
                'stockSort': None,
                'componentBrand': None,
                'componentSpecification': None,
            })
        r.raise_for_status()

        with open(f'parts-page{page}.json', 'wb') as f: f.write(r.content)
        if page == r.json()['data']['componentPageInfo']['pages']: break

        page += 1
        time.sleep(1)
