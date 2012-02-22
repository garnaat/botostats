import json
import process_stats
import sys
import boto

# Massively ugly approach to generating HTML files.  Nuff said.

html_prefix = """
<!--
You are free to copy and use this sample in accordance with the terms of the
Apache license (http://www.apache.org/licenses/LICENSE-2.0.html)
-->

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <meta http-equiv="content-type" content="text/html; charset=utf-8"/>
    <title>
      Boto Download Metrics
    </title>
    <script type="text/javascript" src="http://www.google.com/jsapi"></script>
    <script type="text/javascript">
      google.load('visualization', '1', {packages: ['table']});
    </script>"""
    
html_postfix = """
</head>
  <body style="font-family: Arial;border: 0 none;">
    <h2>Total Downloads For All Releases</h2>
    <div id="summary"></div>
    <h2>Last 7 Days For All Releases</h2>
    <div id="daily"></div>
  </body>
</html>"""

def create_summary_script(data):
    l = []
    l.append('  function drawSummaryTable() {')
    l.append('    var SummaryObject = {')
    l.append("    cols: [{id: 'release', label: 'Release', type: 'string'},")
    l.append("           {id: 'pypi', label: 'PyPI', type: 'number'},")
    l.append("           {id: 'google', label: 'Google Code', type: 'number'},")
    l.append("           {id: 'github', label: 'Github', type: 'number'},")
    l.append("           {id: 'total', label: 'Total Downloads', type: 'number'}],")
    l.append("    rows: [")
    s = '\n'.join(l)
    days = data.keys()
    days.sort()
    latest = data[days[-1]]
    pypi = latest['crate']
    google = latest['googlecode']
    github = latest['github']
    version_keys = pypi.keys()
    version_keys.sort()
    version_keys.reverse()
    row_list = []
    for version in version_keys:
        row = "{c: [{v: '%s'}, " % version
        pypi_num = pypi.get(version, 0)
        google_num = google.get(version, 0)
        github_num = github.get(version, 0)
        row += '{v: %d}, ' % pypi_num
        row += '{v: %d}, ' % google_num
        row += '{v: %d}, ' % github_num
        row += '{v: %d}]}' % (pypi_num + google_num + github_num)
        row_list.append(row)
    row = "{c: [{v: 'Total'}, "
    pypi_total = sum(pypi.values())
    google_total = sum(google.values())
    github_total = sum(github.values())
    row += '{v: %d}, ' % pypi_total
    row += '{v: %d}, ' % google_total
    row += '{v: %d}, ' % github_total
    row += '{v: %d}]}' % (pypi_total + google_total + github_total)
    row_list.append(row)
    s += ','.join(row_list)
    s += ']};'
    l = ['var data = new google.visualization.DataTable(SummaryObject, 0.5);']
    l.append("visualization = new google.visualization.Table(document.getElementById('summary'));")
    l.append("visualization.draw(data, {'allowHtml': true});")
    l.append('}')
    s += '\n'.join(l)
    return s

def create_weekly_script(data):
    data = process_stats.calculate_daily_data(data)
    dates = data.keys()
    dates.sort()
    l = []
    l.append('  function drawDailyTable() {')
    l.append('    var WeekObject = {')
    l.append("    cols: [{id: 'release', label: 'Release', type: 'string'},")
    for day in dates:
        l.append("{id: '%s', label: '%s', type: 'number'}," % (day, day))
    l.append("    ], \nrows: [")
    s = '\n'.join(l)
    versions = data[dates[-1]]
    row_list = []
    version_keys = versions.keys()
    version_keys.sort()
    version_keys.reverse()
    for version in version_keys:
        row = "{c: [{v: '%s'}, " % version
        data_list = []
        for day in dates:
            data_list.append('{v: %d}' % data[day][version])
        row += ','.join(data_list)
        row += ']}'
        row_list.append(row)
    row = "{c: [{v: 'Total'}, "
    data_list = []
    for day in dates:
        data_list.append('{v: %d}' % sum(data[day].values()))
    row += ','.join(data_list)
    row += ']}'
    row_list.append(row)
    s += ','.join(row_list)
    s += ']};'
    l = ['var data = new google.visualization.DataTable(WeekObject, 0.5);']
    l.append("visualization = new google.visualization.Table(document.getElementById('daily'));")
    l.append("visualization.draw(data, {'allowHtml': true});")
    l.append('}')
    s += '\n'.join(l)
    return s

def main(data_path, html_path):
    fp = open(data_path)
    data = json.load(fp)
    fp.close()
    fp = open(html_path, 'w')
    fp.write(html_prefix)
    fp.write('\n<script type="text/javascript">\n')
    fp.write(create_summary_script(data))
    fp.write(create_weekly_script(data))
    fp.write('\ngoogle.setOnLoadCallback(drawSummaryTable);')
    fp.write('\ngoogle.setOnLoadCallback(drawDailyTable);')
    fp.write('\n</script>\n')
    fp.write(html_postfix)
    fp.close()

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print 'Usage: generate_html.py <path_to_stats> <path_to_html>'
        sys.exit(1)
    print 'Generating HTML'
    main(sys.argv[1], sys.argv[2])
    print 'Uploading to S3'
    s3 = boto.connect_s3()
    bucket = s3.lookup('stats.pythonboto.org')
    k = bucket.new_key('index.html')
    k.set_contents_from_filename(sys.argv[2], policy='public-read')
