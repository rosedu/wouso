.. Wouso API documentation master file, created by
   sphinx-quickstart on Sat Feb 11 20:35:09 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Wouso API's documentation!
=====================================

Base api:
--------

Notifications
~~~~~~~~~~~~~

.. http:post:: /api/notifications/register/

    Register a new Android device for push notifications. POST data must contain `registration_id`.

.. http:post:: /api/notifications/devices/

    List registered Android devices which will receive push notifications.

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

Player information
~~~~~~~~~~~~~~~~~~

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
            avatar:  "http://www.gravatar.com/avatar/d43fad239b039cebdb4206cdc692f314.jpg",
            level: {
                name: "level-1",
                title: "Level 1",
                image: "",
                percents: 100,
                id: 2
            },
            level_no: 1,
            level_progress: {
                percent: 50,
                next_level: 2,
                points_gained: 55,
                points_left: 45,
            }
            race: "CA",
            group: "CA311",
            email: "alex@rosedu.org",
            points: 0,
            gold: 0,
        }

    :statuscode 200: no error
    :statuscode 401: not authorized
    :statuscode 404: current user doesn't have a profile

.. http:get:: /api/search/<query string>/

    Search for players matching query string.

    **Example request**:
     .. sourcecode:: http

        GET /api/search/alex/ HTTP/1.1
        Host: wouso-next.rosedu.org
        Accept: application/json, text/javascript
        Authorization: OAuth oauth_version="1.0",oauth_nonce="a1df9b758e16eaebe8a2208d1e210bfb",oauth_timestamp="1312861474",oauth_consumer_key="xxxxxx",oauth_token="xxxxx",oauth_signature_method="PLAINTEXT",oauth_signature="xxxxxx"

    **Example response**:
     .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept
        Content-Type: text/javascript

        [
            {
                "id":	1,
                "first_name": "Alex",
                "last_name": "Eftimie",
            }
        ]

    :statuscode 200: no error
    :statuscode 401: not authorized

Magic and Bazaar
~~~~~~~~~~~~~~~~

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

.. http:post:: /api/bazaar/buy/

    Attempts to buy a spell sent as POST parameter. Returns success or error.

    Posible errors:
     * Spell not provided
     * No such spell
     * Insufficient gold

    **Example request**:
     .. sourcecode:: http

        POST /api/bazaar/buy/ HTTP/1.1
        Host: wouso-next.rosedu.org
        Accept: application/json, text/javascript
        Authorization: OAuth oauth_version="1.0",oauth_nonce="a1df9b758e16eaebe8a2208d1e210bfb",oauth_timestamp="1312861474",oauth_consumer_key="xxxxxx",oauth_token="xxxxx",oauth_signature_method="PLAINTEXT",oauth_signature="xxxxxx"
        Content-Type: application/x-www-form-urlencoded
        Content-Length: 7

        spell=1

    **Example response**:
     .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept
        Content-Type: text/javascript

        {
            success: true
        }

    :statuscode 200: no error
    :statuscode 401: not authorized

.. http:post:: /api/bazaar/exchange/gold/points/

    Attempts to exchange an amount sent as POST parameter. Returns success or error.

    Posible errors:
     * Invalid Amount
     * Insufficient Amount

.. http:post:: /api/bazaar/exchange/points/gold/

    The same as gold to points.

.. http:post:: /api/player/<player_id>/cast/

    Cast a spell given as POST parameter to player_id.

Top API
-------
.. http:get:: /api/top/race/

    Returns top races in the game.

.. http:get:: /api/top/race/(race_id)/group/

    Returns top groups in selected race.

.. http:get:: /api/top/race/(race_id)/player/

    Returns top groups in selected race.

.. http:get:: /api/top/group/

    Returns top groups in the game.

.. http:get:: /api/top/group/(group_id)/player/

    Returns top players in selected group.

.. http:get:: /api/top/player/

    Returns top players in the game.

Group API
---------
.. http:get:: /api/group/(group_id)/

    Returns information about the group: name, member count, rank.

.. http:get:: /api/group/(group_id)/activity/

    Returns latest activity for group members.

.. http:get:: /api/group/(group_id)/evolution/

    Returns group points evolution.

Messages API
------------
.. http:get:: /api/messages/(type)

    Returns all messages by type:
     * all
     * sent
     * recv

.. http:post:: /api/messages/send/

    Sends a message, using POST parameters:
     * receiver (*mandatory, id or username)
     * text (*mandatory)
     * subject
     * reply_to (id of the message to reply_to)

Game API
--------

Question of the Day
~~~~~~~~~~~~~~~~~~

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

.. http:post:: /api/qotd/today/

    Attempt to response QotD, by sending the answer id as POST data. In case of error, success is set to false, and an error message is provided.

    Error messages:
     * No question for today
     * User already answered
     * Answer not provided
     * Invalid answer

    **Example request**:
     .. sourcecode:: http

        POST /api/qotd/today/ HTTP/1.1
        Host: wouso-next.rosedu.org
        Accept: application/json, text/javascript
        Authorization: OAuth oauth_version="1.0",oauth_nonce="a1df9b758e16eaebe8a2208d1e210bfb",oauth_timestamp="1312861474",oauth_consumer_key="xxxxxx",oauth_token="xxxxx",oauth_signature_method="PLAINTEXT",oauth_signature="xxxxxx"
        Content-Type: application/x-www-form-urlencoded
        Content-Length: 9

        answer=11

    **Example response**:
     .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept
        Content-Type: text/javascript

        {
            success:	true
            correct:    true
        }

    **Second example response**:
     .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept
        Content-Type: text/javascript

        {
            success:	false
            error: "User already answered"
        }

    :statuscode 200: no error
    :statuscode 401: not authorized
    :statuscode 404: user doesn't have a profile

Challenge
~~~~~~~~~
.. http:get:: /api/challenge/list/

    Return a list of all active challenges.

.. http:get:: /api/challenge/launch/(player_id)/

    Launch a new challenge against given player.

.. http:get:: /api/challenge/(challenge_id)/accept/

    Accept specific challenge.

.. http:get:: /api/challenge/(challenge_id)/refuse/

    Refuse specific challenge.

.. http:get:: /api/challenge/(challenge_id)/cancel/

    Cancel specific challenge.

.. http:get:: /api/challenge/(challenge_id)/

    Return information and questions (content) for given challenge. Also set it as started for user requesting.

    **Example response**:

     .. sourcecode:: json

        {
            success: true,
            status: "A",
            date: "2012-06-19 19:59:32"
            from: "test",
            to: "admin",
            seconds: 61,
            questions: {
                21: {
                    text: "S Which is the codename of current WoUSO devel version?",
                    answers: {
                        81: "Piranha",
                        82: "4",
                        83: "no codename",
                        84: "nom nom nom"
                    }
                },
                26: {
                    text: "S In lumea UNIX un proces poate avea un singur proces parinte. In momentul in care parintele este omorat printr-ul semnal SIGKILL, procesul copil",
                    answers: {
                        101: "este automat omorat si el",
                        102: "devine orfan, isi termina executia, fara a fi adoptat de nimeni",
                        103: "devine orfan si este automat adoptat de parintele parintelui (bunicul procesului)",
                        104: "devine orfan si este automat adoptat de procesul "init""
                    }
                }
            }
        }

.. http:post:: /api/challenge/(challenge_id)/

    Post answers to a challenge. These must be mapped as a list of POST parameters, using the question id as key, and answers ids comma separated.

    **Example request**:
     .. sourcecode:: http

        POST /api/challenge/1/ HTTP/1.1
        Host: wouso-next.rosedu.org
        Accept: application/json, text/javascript
        Authorization: OAuth oauth_version="1.0",oauth_nonce="a1df9b758e16eaebe8a2208d1e210bfb",oauth_timestamp="1312861474",oauth_consumer_key="xxxxxx",oauth_token="xxxxx",oauth_signature_method="PLAINTEXT",oauth_signature="xxxxxx"
        Content-Type: application/x-www-form-urlencoded
        Content-Length: 25

        12=1&13=4&14=5,6&16=9&17=

    This request sends the following answers:

    .. sourcecode:: json

        {
            12: [ 1 ],
            13: [ 4 ],
            14: [ 5, 6 ],
            16: [ 9 ],
            17: [ ]
        }

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

