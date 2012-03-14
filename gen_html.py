import json
import process_stats
import markdown
import sys
import boto

def create_summary_table(data, fp):
    fp.write('Total Downloads for All Versions\n')
    fp.write('--------------------------------\n\n')
    fp.write('Release | PyPI | GoogleCode | Github | Total\n')
    fp.write('------- | ---- | ---------- | ------ | -----\n')
    days = data.keys()
    days.sort()
    latest = data[days[-1]]
    pypi = latest['pypi']
    google = latest['googlecode']
    github = latest['github']
    version_keys = pypi.keys()
    version_keys.sort()
    version_keys.reverse()
    for version in version_keys:
        row_list = [version]
        pypi_num = pypi.get(version, 0)
        google_num = google.get(version, 0)
        github_num = github.get(version, 0)
        row_list.append('%d' % pypi_num)
        row_list.append('%d' % google_num)
        row_list.append('%d' % github_num)
        row_list.append('%d' % (pypi_num + google_num + github_num))
        fp.write(' | '.join(row_list))
        fp.write('\n')
    pypi_total = sum(pypi.values())
    google_total = sum(google.values())
    github_total = sum(github.values())
    row_list = ['Total']
    row_list.append('%d' % pypi_total)
    row_list.append('%d' % google_total)
    row_list.append('%d' % github_total)
    row_list.append('%d' % (pypi_total + google_total + github_total))
    fp.write(' | '.join(row_list))
    fp.write('\n\n')

def create_daily_table(data, fp):
    fp.write('Daily Downloads (Last 7 days) for All Versions\n')
    fp.write('----------------------------------------------\n\n')
    fp.write('\n<a name="daily_stats"></a>\n\n')
    data = process_stats.calculate_daily_data(data)
    dates = data.keys()
    dates.sort()
    row_list = ['Release']
    for day in dates:
        row_list.append(day)
    fp.write(' | '.join(row_list))
    fp.write('\n')
    dashes = []
    for label in row_list:
        dashes.append('-'*len(label))
    fp.write(' | '.join(dashes))
    fp.write('\n')
    versions = data[dates[-1]]
    row_list = []
    version_keys = versions.keys()
    version_keys.sort()
    version_keys.reverse()
    for version in version_keys:
        row_list = [version]
        for day in dates:
            row_list.append('%d' % data[day][version])
        fp.write(' | '.join(row_list))
        fp.write('\n')
    row_list = ['Total']
    for day in dates:
        row_list.append('%d' % sum(data[day].values()))
    fp.write(' | '.join(row_list))
    fp.write('\n\n')

def create_weekly_table(data, fp):
    fp.write('Weekly Downloads for All Versions\n')
    fp.write('---------------------------------\n\n')
    fp.write('\n<a name="weekly_stats"></a>\n\n')
    data = process_stats.calculate_weekly_data(data)
    dates = data.keys()
    dates.sort()
    row_list = ['Release']
    for date in dates:
        row_list.append(' %s ' % date)
    fp.write(' | '.join(row_list))
    fp.write('\n')
    dashes = []
    for label in row_list:
        dashes.append('-'*len(label))
    fp.write(' | '.join(dashes))
    fp.write('\n')
    versions = data[dates[-1]]
    row_list = []
    version_keys = versions.keys()
    version_keys.sort()
    version_keys.reverse()
    for version in version_keys:
        row_list = [version]
        for date in dates:
            row_list.append('%d' % data[date][version])
        fp.write(' | '.join(row_list))
        fp.write('\n')
    row_list = ['Total']
    for date in dates:
        row_list.append('%d' % sum(data[date].values()))
    fp.write(' | '.join(row_list))
    fp.write('\n')

def main(data_path):
    fp = open(data_path)
    data = json.load(fp)
    fp.close()
    fp = open('stats.markdown', 'w')
    fp.write('Boto Download Statistics\n')
    fp.write('========================\n\n')
    fp.write('[Daily Stats](#daily_stats)\n')
    fp.write('[Weekly Stats](#weekly_stats)\n\n')
    create_summary_table(data, fp)
    create_daily_table(data, fp)
    create_weekly_table(data, fp)
    fp.close()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Usage: generate_html.py <path_to_stats>'
        sys.exit(1)
    print 'Generating Markdown'
    main(sys.argv[1])
    print 'Generating HTML'
    fp = open('stats.markdown')
    md = fp.read()
    fp.close()
    html = markdown.markdown(md, extensions=['tables'], output_format='xhtml5')
    fp = open('stats.html', 'w')
    fp.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    fp.write('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"\n')
    fp.write('"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n')
    fp.write('<html xmlns="http://www.w3.org/1999/xhtml">\n')
    fp.write('<head>\n')
    fp.write('<title>Boto Download Stats</title>\n')
    fp.write('<link href="markdown.css" rel="stylesheet"></link>\n\n')
    fp.write('</head>\n')
    fp.write('<body>\n\n')
    fp.write(html)
    fp.write('</body>\n')
    fp.write('</html>\n')
    fp.close()
    print 'Uploading to S3'
    s3 = boto.connect_s3()
    bucket = s3.lookup('stats.pythonboto.org')
    k = bucket.new_key('index.html')
    k.set_contents_from_filename('stats.html', policy='public-read')
