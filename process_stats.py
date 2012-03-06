import json
import datetime
import copy

def sum_sources(stats, dates=None):
    """
    Sums all of the downloads from all of the sources for each version
    for all of the dates specified in ``dates`` or for all dates in
    ``stats``.  Returns a dictionary with keys from each of the dates
    in ``dates``.  The value of each of these is another dictionary
    with versions as key and the total downloads across all sources
    as the value.
    """
    sums = {}
    if not dates:
        dates = stats.keys()
    for date in stats:
        sums[date] = {}
        daily_dict = stats[date]
        daily_total = 0
        for source in daily_dict:
            source_dict = daily_dict[source]
            for version in source_dict:
                if version in sums[date]:
                    sums[date][version] += source_dict[version]
                else:
                    sums[date][version] = source_dict[version]
    return sums

def calculate_daily_data(stats, num_days=7):
    days = stats.keys()
    days.sort()
    if num_days is not None:
        days = days[-(num_days+1):]
    days.reverse()
    # When bootstrapping, we won't have seven days of data yet
    num_days = len(days)
    summary_stats = sum_sources(stats, days)
    daily_data = {}
    for i in range(0, num_days-1):
        day1 = summary_stats[days[i]]
        day2 = summary_stats[days[i+1]]
        day_data = {}
        for version in day1:
            day_data[version] = day1[version] - day2[version]
        daily_data[days[i].split('T')[0]] = day_data
    return daily_data
                   
def calculate_weekly_data(stats):
    daily = calculate_daily_data(stats, None)
    weekly_data = {}
    days = daily.keys()
    days.sort()
    for i, day in enumerate(days):
        y, m, d = map(int, day.split('-'))
        date = datetime.date(y, m, d)
        if date.weekday() == 1:
            break
    while i+7 < len(days):
        week_name = '%s thru ' % days[i]
        this_week = copy.copy(daily[days[i]])
        print this_week['2.2.2']
        i += 1
        for i in range(i, i+6):
            for v in this_week:
                this_week[v] += daily[days[i]][v]
            print this_week['2.2.2']
        week_name += days[i]
        weekly_data[week_name] = this_week
    return weekly_data
            
    
