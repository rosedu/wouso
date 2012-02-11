.. Wouso API documentation master file, created by
   sphinx-quickstart on Sat Feb 11 20:35:09 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Wouso API's documentation!
=====================================

Testing API:

.. http:get:: /api/notifications/all

	Return the notification count for the requesting user.

	**Example request**:
	 .. sourcecode:: http

		GET /api/notificaations/all HTTP/1.1
		Host: wouso.cs.pub.ro
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


Contents:

.. toctree::
   :maxdepth: 2

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

