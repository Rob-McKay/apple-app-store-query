#!/usr/bin/env python3

# Generate a tsv formatted list of ios apps on the Apple App store containing the specified terms

# BSD 2-Clause License
#
# Copyright (c) 2020, Rob McKay
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import json
import logging
import os
import urllib.request

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
log = logging.getLogger(__name__)


class IgnoreMissingDictionaryEntries(dict):
    def __missing__(self, key):
        return key.join("{}")


result_limit = 200
country = 'gb'


# Valid fields
# actorTerm, languageTerm, allArtistTerm, tvEpisodeTerm, shortFilmTerm, directorTerm, releaseYearTerm, titleTerm,
# featureFilmTerm, ratingIndex, keywordsTerm, descriptionTerm, authorTerm, genreIndex, mixTerm, allTrackTerm,
# artistTerm, composerTerm, tvSeasonTerm, producerTerm, ratingTerm, songTerm, movieArtistTerm, showTerm, movieTerm,
# albumTerm, softwareDeveloper

def get_store_data(field, term):
    address = 'https://itunes.apple.com/search?entity=iPadSoftware&' \
              'limit={limit}&country={country}&attribute={field}&term={term}'.format(term=term, limit=result_limit,
                                                                                     country=country, field=field)

    with urllib.request.urlopen(address) as url:
        data = json.loads(url.read().decode())

    log.info('Found {0} records for {1} in {2}'.format(data['resultCount'], term, field))

    return data['results']


def merge_results(records, r):
    for row in r:
        if row["trackId"] in records:
            pass  # keep existing entry
        else:
            records[row['trackId']] = IgnoreMissingDictionaryEntries(row)


data_records = {}

merge_results(data_records, get_store_data('titleTerm', 'spell'))
merge_results(data_records, get_store_data('titleTerm', 'spelling'))

merge_results(data_records, get_store_data('keywordsTerm', 'spell'))
# merge_results(data_records, get_store_data('descriptionTerm', 'spelling'))

total = 0

print('Name\tVersion\tCurrent Version Release Date\tSeller Name\tPrice\tRelease Date\tGenres\tContent Advisory '
      'Rating\tLanguage\tURL\tDescription')

for json_object in sorted(data_records.values(), key=lambda item: item['trackName'].lower()):
    if json_object['wrapperType'] == 'software' and 'EN' in json_object['languageCodesISO2A']:
        print('{trackName}\t{version}\t{currentVersionReleaseDate}\t{sellerName}\t{formattedPrice}\t'
              '{releaseDate}\t{genres}\t{contentAdvisoryRating}\t{languageCodesISO2A}\t{trackViewUrl}\t'
              '{description!a}'.format_map(json_object))
        total = total + 1

log.info('Found {0} distinct records'.format(total))
