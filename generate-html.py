import csv
import html

TRACKING_STARTED = '2026-06-07'

def get_item(item, field, fallback=''):
    return item[field] if field in item else fallback

def get_float(item, field, fallback=0):
    try:
        return float(get_item(item, field, fallback))
    except (TypeError, ValueError):
        return fallback

def get_int(item, field, fallback=0):
    try:
        return int(get_item(item, field, fallback))
    except (TypeError, ValueError):
        return fallback

def generate(input_csvpath, output_htmlpath, mode):
    only_active = mode == 'active'
    show_first_seen = mode != 'active'
    categories = {}
    item_count = 0

    table = f'''<table><thead><tr>
  <th>Code</th>
  <th class="filter-select">Library</th>
  <th class="filter-select">Category</th>
  <th class="filter-select">Brand</th>
  <th>Model</th>
  <th class="filter-select">Package</th>
  <th>Describe</th>
  <th>erpComponentName</th>
  <th>Price</th>
  <th>Stock</th>
  <th>Purchase MOQ</th>
  <th>PCBA Min Qty</th>
  <th>PCBA Min Price</th>
  {'<th>FirstSeen (UTC)</th>' if show_first_seen else ''}
  {'<th>LastSeen (UTC)</th>' if not(only_active) else ''}
  {'<th class="filter-select">Deleted</th>' if not(only_active) else ''}
</tr></thead>\n'''
    with open(input_csvpath) as f:
        reader = csv.DictReader(f)
        rows = list(reader)

        for item in rows:
            td = ''

            code = f'<a href="https://jlcpcb.com/partdetail/{get_item(item, "url")}" target="_blank">{get_item(item, "code")}</a>'
            if get_item(item, 'file'): code += f' (<a href="https://jlcpcb.com/api/file/downloadByFileSystemAccessId/{get_item(item, "file")}" target="_blank">doc</a>)'
            td += f'<td>{code}</td>'

            library = html.escape(get_item(item, 'library'))
            if get_item(item, 'library') != 'base': library += ' &#x1f44d;' # Preferred Extended Parts
            td += f'<td>{library}</td>'

            component_type = get_item(item, 'type')
            parent_category = get_item(item, 'category') or 'Other'
            if parent_category and component_type and parent_category != component_type:
                category = f'{parent_category}: {component_type}'
            else:
                category = component_type
            category = html.escape(category)
            td += f'<td>{category}</td>'

            brand = html.escape(get_item(item, 'brand'))
            td += f'<td>{brand}</td>'

            model = html.escape(get_item(item, 'model'))
            td += f'<td>{model}</td>'

            package = html.escape(get_item(item, 'package'))
            td += f'<td>{package}</td>'

            describe = html.escape(get_item(item, 'describe'))
            td += f'<td>{describe}</td>'

            erpComponentName = html.escape(get_item(item, 'erpComponentName'))
            td += f'<td>{erpComponentName}</td>'

            price = html.escape(get_item(item, 'price'))
            td += f'<td>{price}</td>'

            stock = int(get_item(item, 'stock'))
            if stock > 100:
                td += f'<td>{stock}</td>'
            elif stock >= 10:
                td += f'<td style="background:#ffd700">{stock}</td>'
            else:
                td += f'<td style="background:red;color:#FFF">{stock}</td>'
                if only_active: continue

            moq = int(get_item(item, 'MOQ'))
            if moq == 1:
                td += f'<td>{moq}</td>'
            elif moq <= 5:
                td += f'<td style="background:#ffd700">{moq}</td>'
            else:
                td += f'<td style="background:red;color:#FFF">{moq}</td>'
                if only_active: continue

            pcba_min_qty = get_int(item, 'pcbaMinQty')
            if pcba_min_qty > 20:
                td += f'<td style="background:red;color:#FFF">{pcba_min_qty}</td>'
            elif pcba_min_qty >= 10:
                td += f'<td style="background:#ffd700">{pcba_min_qty}</td>'
            else:
                td += f'<td>{pcba_min_qty}</td>'

            pcba_min_price = get_float(item, 'pcbaMinPrice')
            price = get_float(item, 'price')
            pcba_min_price_ratio = pcba_min_price / price if price else 1
            pcba_min_price_text = html.escape(get_item(item, 'pcbaMinPrice'))
            if (pcba_min_price >= 10 and pcba_min_price_ratio > 5) or (pcba_min_price >= 2 and pcba_min_price_ratio > 10):
                td += f'<td style="background:red;color:#FFF">{pcba_min_price_text}</td>'
            elif (pcba_min_price >= 10 and pcba_min_price_ratio > 2) or (pcba_min_price >= 2 and pcba_min_price_ratio > 5) or pcba_min_price_ratio > 25:
                td += f'<td style="background:#ffd700">{pcba_min_price_text}</td>'
            else:
                td += f'<td>{pcba_min_price_text}</td>'

            firstSeen = html.escape(get_item(item, 'firstSeen'))
            if show_first_seen: td += f'<td>{firstSeen}</td>'

            lastSeen = html.escape(get_item(item, 'lastSeen'))
            if not(only_active): td += f'<td>{lastSeen}</td>'

            deleted = html.escape(get_item(item, 'deleted'))
            if only_active:
                if deleted == "1": continue
            else:
                if deleted != "1":
                    td += f'<td>{deleted}</td>'
                else:
                    td += f'<td style="background:#000;color:#FFF">{deleted}</td>'

            table += f'<tr>{td}</tr>\n'
            item_count += 1
            if category in categories:
                categories[category] += 1
            else:
                categories[category] = 1
    table += '</table>'

    title = 'JLCPCB Basic/Preferred Extended Parts'
    if only_active: title += ' (active)'

    note = ''
    if mode == 'all':
        note = f'<p>FirstSeen is tracked from {TRACKING_STARTED} onward. Parts that were already present when tracking began use that date as their FirstSeen value.</p>'

    fhtml = open(output_htmlpath, 'w')
    fhtml.write('''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.7.1/jquery.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery.tablesorter/2.32.0/js/jquery.tablesorter.combined.min.js"></script>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/jquery.tablesorter/2.32.0/css/theme.default.min.css">
<script>
$(document).ready(function() {
  $('table').tablesorter({
    textExtraction: function(node) {
      return $(node).text().trim().replace(/\s(\-|To)\s/gi, '$1');
    },
    widthFixed: true,
    widgets: ['zebra', 'columns', 'filter', 'resizable', 'stickyHeaders'],
    widgetOptions : {
      filter_functions : {
        9: {
          "> 100":  function(e, n, f, i, $r, c, data) { return n>100; },
          "10-100": function(e, n, f, i, $r, c, data) { return 10<=n && n<=100; },
          "< 10":   function(e, n, f, i, $r, c, data) { return n<10; },
        },
        10: {
          "1":   function(e, n, f, i, $r, c, data) { return n==1; },
          "2-5": function(e, n, f, i, $r, c, data) { return 2<=n && n<5; },
          "> 5": function(e, n, f, i, $r, c, data) { return n>5; },
        },
        11: {
          "1-9":   function(e, n, f, i, $r, c, data) { return 1<=n && n<=9; },
          "10-20": function(e, n, f, i, $r, c, data) { return 10<=n && n<=20; },
          "> 20":  function(e, n, f, i, $r, c, data) { return n>20; },
        }
      }
    }
  });
});
</script>
<meta name="viewport" content="width=device-width" />''')
    fhtml.write(f'''<title>{title}</title>
</head>
<body>
<h1>{title}</h1>
<ul>
<li><a href="index.html">Economic Parts</a></li>
<li><a href="active.html">Active Economic Parts (In-stock, small orders accepted)</a></li>
<li><a href="economic-parts.csv">Economic Parts (CSV)</a></li>
</ul>
{note}
<details>
<summary>Categories</summary>
{', '.join(list(map(lambda x: x[0]+" ("+str(x[1])+")", sorted(categories.items(), key=lambda x:-x[1]))))}
</details>

<p>Total: {item_count} items.</p>
{table}
</body></html>''')

if __name__ == '__main__':
    generate('economic-parts.csv', 'economic-parts.html', 'all')
    generate('economic-parts.csv', 'economic-parts-active.html', 'active')
