.. Wouso API documentation master file, created by
   sphinx-quickstart on Sat Feb 11 20:35:09 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Wouso API's documentation!
=====================================

Base api:
--------

.. http:get:: /api/notifications/all/

    Return the notification count for the requesting user.

    **Example request**:
     .. sourcecode:: http

        GET /api/notifications/all/ HTTP/1.1
        Host: wouso-next.rosedu.org
        Accept: application/json, text/javascript
        Authorization: OAuth oauth_version="1.0",oauth_nonce="a1df9b758e16eaebe8a2208d1e210bfb",oauth_timestamp="1312861474",oauth_consumer_key="xxxxxx",oauth_token="xxxxx",oauth_signature_method="PLAINTEXT",oauth_signature="xxxxxx"

    **Example response**:
     .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept
        Content-Type: text/javascript

        {
            "count":	0
        }

    :statuscode 200: no error
    :statuscode 401: not authorized

.. http:get:: /api/info/

    Returns information about current (authenticated) user.

    **Example request**:
     .. sourcecode:: http

        GET /api/info/ HTTP/1.1
        Host: wouso-next.rosedu.org
        Accept: application/json, text/javascript
        Authorization: OAuth oauth_version="1.0",oauth_nonce="a1df9b758e16eaebe8a2208d1e210bfb",oauth_timestamp="1312861474",oauth_consumer_key="xxxxxx",oauth_token="xxxxx",oauth_signature_method="PLAINTEXT",oauth_signature="xxxxxx"

    **Example response**:
     .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept
        Content-Type: text/javascript

        {
            first_name: "Alex",
            last_name: "Eftimie",
            level: {
                name: "level-1",
                title: "Level 1",
                image: "",
                percents: 100,
                group_id: 2,
                id: 2
            },
            level_no: 1,
            race: "CA",
            email: "alex@rosedu.org",
            points: 0
        }

    :statuscode 200: no error
    :statuscode 401: not authorized
    :statuscode 404: current user doesn't have a profile

.. http:get:: /api/bazaar/

    Returns a list of all available spells for buying.

    **Example request**:
     .. sourcecode:: http

        GET /api/bazaar/ HTTP/1.1
        Host: wouso-next.rosedu.org
        Accept: application/json, text/javascript
        Authorization: OAuth oauth_version="1.0",oauth_nonce="a1df9b758e16eaebe8a2208d1e210bfb",oauth_timestamp="1312861474",oauth_consumer_key="xxxxxx",oauth_token="xxxxx",oauth_signature_method="PLAINTEXT",oauth_signature="xxxxxx"

    **Example response**:
     .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept
        Content-Type: text/javascript

        {
             [
                 {
                     name: "challenge-cannot-be-challenged",
                     title: "Nu poate fi provocat",
                     type: "n",
                     due_days: 3,
                     image: "<custom image>",
                     price: 10,
                     percents: 100,
                     group_id: 1,
                     id: 30,
                     description: "Nu permite provocarea jucătorului pe care este aplicată."
                 },
             ]
         }

    :statuscode 200: no error
    :statuscode 401: not authorized

.. http:get:: /api/bazaar/inventory/

    Returns a list of spells in current authenticated user's inventory.

    **Example request**:
     .. sourcecode:: http

        GET /api/bazaar/ HTTP/1.1
        Host: wouso-next.rosedu.org
        Accept: application/json, text/javascript
        Authorization: OAuth oauth_version="1.0",oauth_nonce="a1df9b758e16eaebe8a2208d1e210bfb",oauth_timestamp="1312861474",oauth_consumer_key="xxxxxx",oauth_token="xxxxx",oauth_signature_method="PLAINTEXT",oauth_signature="xxxxxx"

    **Example response**:
     .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept
        Content-Type: text/javascript

        {
            spells:
            [
                {
                    player_id: 1,
                    spell_id: 30
                    amount: 1,
                    id: 1,
                }
            ]
        }

    :statuscode 200: no error
    :statuscode 401: not authorized
    :statuscode 404: current user does not have a profile

Game API
--------

.. http:get:: /api/qotd/today/

    Get Question of The Day for current date.

    **Example request**:
     .. sourcecode:: http

        GET /api/qotd/today/ HTTP/1.1
        Host: wouso-next.rosedu.org
        Accept: application/json, text/javascript
        Authorization: OAuth oauth_version="1.0",oauth_nonce="a1df9b758e16eaebe8a2208d1e210bfb",oauth_timestamp="1312861474",oauth_consumer_key="xxxxxx",oauth_token="xxxxx",oauth_signature_method="PLAINTEXT",oauth_signature="xxxxxx"

    **Example response**:
     .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept
        Content-Type: text/javascript

        {
            text:	"What is this?"
            answers: {
                10: "yes",
                11: "no",
                12: "other"
            }
            had_answered: false
        }

    :statuscode 200: no error
    :statuscode 401: not authorized
    :statuscode 404: user doesn't have a profile


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

