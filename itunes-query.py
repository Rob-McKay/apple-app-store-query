# Generate a MD formatted list of ios apps on the Apple App store containing the specified term

import json
import urllib.request

result_limit = 200
term = 'spelling'
country = 'gb'


# field = 'keywordsTerm'
# field = 'descriptionTerm'

def get_store_data(field):
    address = 'https://itunes.apple.com/search?term={term}&entity=iPadSoftware&' \
              'limit={limit}&country={country}&attribute={field}'.format(term=term, limit=result_limit, country=country,
                                                                         field=field)

    with urllib.request.urlopen(address) as url:
        data = json.loads(url.read().decode())

    return data['results']


results1 = get_store_data('keywordsTerm')
results2 = get_store_data('descriptionTerm')

data_records = {}

for row in results1:
    if row["trackId"] in data_records:
        pass
    else:
        data_records[row['trackId']] = row

for row in results2:
    if row["trackId"] in data_records:
        pass
    else:
        data_records[row['trackId']] = row

print(f'Found {len(data_records)} distinct records\n')
print('Name | Version | Current Version Release Date| Seller Name | Price |'
      'Release Date| Genres |'
      'Description')
print('--- | --- | --- | --- | --- | --- | --- | --- ')

for json_object in sorted(data_records.values(), key=lambda item: item['trackName'].lower()):
    print('{trackName} | {version} | {currentVersionReleaseDate} | {sellerName} | {formattedPrice} |'
          '{releaseDate} | {genres} |'
          '{description!a}'.format(**json_object))
