from BeautifulSoup import BeautifulSoup
import urllib
import json
import datetime
import os
import re
import sys

version_regex = re.compile('boto-(?P<version>[0-9a-z\.]*?).tar.gz')

all_versions = [u'0.7a', u'0.5a', u'1.4a', u'1.8c', u'1.8b', u'2.0a2',
                u'1.8d', u'2.0a1', u'2.0rc1', u'2.0b4', u'2.2.1',
                u'1.4c', u'2.2.2', u'2.1.0', u'1.4b', u'2.0', u'1.6b',
                u'1.6a', u'0.9d', u'1.2a', u'0.9a', u'0.9c', u'0.9b',
                u'1.0a', u'1.8a', u'2.0b2', u'0.3a', u'0.6a', u'0.6b',
                u'0.6c', u'1.5c', u'2.0b3', u'1.9b', u'2.0b1', u'0.4b',
                u'0.4a', u'1.9a', u'2.1.1', u'1.7a', u'0.8b', u'0.8c',
                u'0.8a', u'1.5d', u'0.8d', u'1.3a', u'1.1b', u'1.1c',
                u'1.1a', u'0.2a', u'2.2.0', u'2.3.0']

def get_pypi_stats():
    """
    Pull download stats for all versions on pypi.
    Return a dictionary where keys are version strings and
    values are download counts.
    """
    stats = {}
    base_url = 'http://pypi.python.org/pypi?:action=display&name=boto&version='

    for version in all_versions:
        print 'processing %s' % version
        html = urllib.urlopen(base_url+version)
        soup = BeautifulSoup(html)
        table = soup.findAll('table', {'class': 'list'})[0]
        rows = table.findAll('tr')
        data_row = rows[1]
        tds = data_row.findAll('td')
        downloads = tds[-1]
        downloads = int(downloads.string.replace(',', ''))
        stats[version] = downloads
    return stats

def get_crate_stats():
    """
    Pull download stats for all versions on crate.io.
    Return a dictionary where keys are version strings and
    values are download counts.
    """
    stats = {}
    base_url = 'http://crate.io'
    html = urllib.urlopen(base_url+'/packages/boto/').read()
    soup = BeautifulSoup(html)

    versions = soup.findAll(id='all-versions')[0]
    links = versions.findAll('a')

    for link in links:
        version = link['href'].split('/')
        version = version[3]
        print 'processing %s' % version
        html = urllib.urlopen(base_url+link['href'])
        soup = BeautifulSoup(html)
        files = soup.findAll(id='files')[0]
        tds = files.findAll('td')
        downloads = tds[-1]
        downloads = int(downloads.string.replace(',', ''))
        stats[version] = downloads
    return stats

def get_google_stats():
    """
    Pull download stats for all versions on Google code.
    Return a dictionary where keys are version strings and
    values are download counts.
    """
    stats = {}
    url = 'http://code.google.com/p/boto/downloads/list'
    html = urllib.urlopen(url).read()
    soup = BeautifulSoup(html)

    table = soup.findAll(id='resultstable')[0]
    rows = table.findAll('tr')
    for row in rows[1:]:
        file_name = row.find('td', {'class': 'vt id col_0'}).text
        version = version_regex.match(file_name).group('version')
        downloads = int(row.find('td', {'class': 'vt col_5'}).text)
        print 'Version=%s, Downloads=%s' % (version, downloads)
        stats[version] = downloads
    return stats

def get_github_stats():
    """
    Pull download stats for all versions in github downloads.
    Return a dictionary where keys are version strings and
    values are download counts.
    """
    stats = {}
    url = 'https://api.github.com/repos/boto/boto/downloads'
    json_data = urllib.urlopen(url).read()
    d = json.loads(json_data)
    for download in d:
        file_name = download['name']
        version = version_regex.match(file_name).group('version')
        downloads = download['download_count']
        print 'Version: %s, Downloads: %d' % (version, downloads)
        stats[version] = downloads
    return stats

def main(stats_file):
    timestamp = datetime.datetime.utcnow().isoformat()

    if os.path.isfile(stats_file):
        fp = open(stats_file)
        all_stats = json.load(fp)
        fp.close()
    else:
        all_stats = {}

    daily_stats = {}
    #stats = get_crate_stats()
    stats = get_pypi_stats()
    daily_stats['pypi'] = stats
    stats = get_google_stats()
    daily_stats['googlecode'] = stats
    stats = get_github_stats()
    daily_stats['github'] = stats
    all_stats[timestamp] = daily_stats
    fp = open(stats_file, 'w')
    json.dump(all_stats, fp, indent=4, sort_keys=True)
    fp.close()
                      
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print 'Usage: get_stats.py <path_to_json_stats_file>'
        sys.exit(1)
    main(sys.argv[1])
