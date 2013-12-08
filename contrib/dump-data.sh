#!/bin/bash

# Pass in filename where to store the data

APPS="config user game scoring qpool magic security qotd challenge grandchallenge \
      specialchallenge quest specialquest workshop cpanel top activity pages \
      statistics messaging"

echo "Dumping all data for: $APPS.."
wouso/manage.py dumpdata $APPS > $1

