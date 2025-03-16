import csv
import html

def generate(input_csvpath, output_htmlpath, only_active):
    categories = {}
    item_count = 0

    table = f'''<table><thead><tr>
  <th>Code</th>
  <th class="filter-select">Library</th>
  <th class="filter-select">Category</th>
  <th class="filter-select">Brand</th>
  <th>Model</th>
  <th class="filter-select">Package</th>
  <th>describe</th>
  <th>erpComponentName</th>
  <th>Price</th>
  <th>Stock</th>
  <th>MOQ</th>
  {'<th>LastSeen (JST)</th>' if not(only_active) else ''}
  {'<th class="filter-select">Deleted</th>' if not(only_active) else ''}
</tr></thead>\n'''
    with open(input_csvpath) as f:
        reader = csv.reader(f)
        header = next(reader)
        for item in reader:
            td = ''

            code = f'<a href="https://jlcpcb.com/partdetail/{item[1]}" target="_blank">{item[0]}</a>'
            if item[2]: code += f' (<a href="https://jlcpcb.com/api/file/downloadByFileSystemAccessId/{item[2]}" target="_blank">doc</a>)'
            td += f'<td>{code}</td>'

            library = html.escape(item[3])
            if item[3] != 'base': library += ' &#x1f44d;' # Preferred Extended Parts
            td += f'<td>{library}</td>'

            category = html.escape(item[9])
            td += f'<td>{category}</td>'

            brand = html.escape(item[6])
            td += f'<td>{brand}</td>'

            model = html.escape(item[7])
            td += f'<td>{model}</td>'

            package = html.escape(item[8])
            td += f'<td>{package}</td>'

            describe = html.escape(item[10])
            td += f'<td>{describe}</td>'

            erpComponentName = html.escape(item[11])
            td += f'<td>{erpComponentName}</td>'

            price = html.escape(item[12])
            td += f'<td>{price}</td>'

            stock = int(item[13])
            if stock > 100:
                td += f'<td>{stock}</td>'
            elif stock >= 10:
                td += f'<td style="background:#ffd700">{stock}</td>'
            else:
                td += f'<td style="background:red;color:#000">{stock}</td>'
                if only_active: continue

            moq = int(item[14])
            if moq == 1:
                td += f'<td>{moq}</td>'
            elif moq <= 5:
                td += f'<td style="background:#ffd700">{moq}</td>'
            else:
                td += f'<td style="background:red;color:#000">{moq}</td>'
                if only_active: continue

            lastSeen = html.escape(item[5])
            if not(only_active): td += f'<td>{lastSeen}</td>'

            deleted = html.escape(item[4])
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
<details>
<summary>Categories</summary>
{', '.join(list(map(lambda x: x[0]+" ("+str(x[1])+")", sorted(categories.items(), key=lambda x:-x[1]))))}
</details>

<p>Total: {item_count} items.</p>
{table}
</body></html>''')

if __name__ == '__main__':
    generate('economic-parts.csv', 'economic-parts.html', False)
    generate('economic-parts.csv', 'economic-parts-active.html', True)
