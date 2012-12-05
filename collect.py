"""
Update a SoMA panel from a source file of panelists
"""

from __future__ import unicode_literals, print_function

import sys
import multiprocessing
import logging
from collections import defaultdict
from urlparse import urlparse
from os.path import splitext
import time

import source
import client

logger = logging.getLogger('wood_panelling')
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)


class UnexpectedError(Exception):
    pass


class RedisStorage(object):

    def __init__(self):
        self.id_map = {}
        self.follower_map = defaultdict(list)
        self.friends_map = defaultdict(list)

    def store_profile(self, profile):
        pass

    def store_followers(self, follower_list):
        pass

    def store_friends(self, friends_list):
        pass


def wait_time(client, resource_uri):
    ratelimit_uri = "https://api.twitter.com/1.1/application/rate_limit_status.json"
    group, method = splitext(urlparse(resource_uri).path)[0].split('/')[-2:]
    info = client.get(ratelimit_uri, params={'resources': group})
    timestamp = info.json['resources'][group]["/%s/%s" % (group, method)]['reset']
    # add 1 second to account for fractions of a second which are not returned in timestamp
    return timestamp - int(time.time()) + 1


def fetch(client, twitter_handles, storage):
    print(",".join(twitter_handles))
    pass


def fetch_profiles(client, twitter_handles, storage):
    """
    Fetch twitter profile information for twitter_handles and add them to storage

    Can request 100 profiles per request and 180 requests per 15mins
    """

    lookup_uri = "https://api.twitter.com/1.1/users/lookup.json"
    size_limit = 100

    while twitter_handles:
        clump = twitter_handles[:size_limit]
        response = client.get(lookup_uri, params={'screen_name': ",".join(clump)})
        if response.status_code == 200:
            del twitter_handles[:size_limit]
            for profile in response.json:
                storage.store_profile(profile)
            logger.debug("fetched 100 profiles, %d left" % len(screen_names))
        elif response.status_code == 429:
            # rate limiting, need to sleep
            delay = wait_time(client, lookup_uri)
            logger.info("rate limit for users/lookup (delay: %s)" % delay)
            time.sleep(wait_time)
        else:
            raise UnexpectedError(response.error)


def fetch_followers(twitter_id):
    pass


def fetch_friends(twitter_id):
    pass


if __name__ == "__main__":
    try:
        filename = sys.argv[1]
    except IndexError:
        print("Usage: {} filename".format(sys.argv[0]))
        sys.exit(1)

    twitter_handles = source.load_source(filename)
    storage = RedisStorage()
    fetch(client, twitter_handles, storage)