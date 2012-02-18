import json

def sum_sources(stats):
    sums = {}
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


