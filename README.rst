-------------------
Crossref API Client
-------------------

Library with functions to iterate through the Crossref API.

.. image:: https://travis-ci.org/fabiobatalha/crossrefapi.svg?branch=master
    :target: https://travis-ci.org/fabiobatalha/crossrefapi

--------------
How to Install
--------------

pip install crossrefapi

----------
How to Use
----------

Works
-----


Sample
``````

.. code-block:: python

  In [1]: from crossref.restful import Works

  In [2]: works = Works()

  In [3]: for item in works.sample(2):
     ...:     print(item['title'])
     ...:
  ['On the Origin of the Color-Magnitude Relation in the Virgo Cluster']
  ['Biopsychosocial Wellbeing among Women with Gynaecological Cancer']


Query
`````
.. code-block:: python

  In [1]: from crossref.restful import Works

  In [2]: works = Works()

  In [3]: w1 = works.query(title='zika', author='johannes', publisher_name='Wiley-Blackwell')

  In [4]: for item in w1:
     ...:     print(item['title'])
     ...:
     ...:
  ['Inactivation and removal of Zika virus during manufacture of plasma-derived medicinal products']
  ['Harmonization of nucleic acid testing for Zika virus: development of the 1st\n World Health Organization International Standard']

Base Methods
------------

The base methods could be used compounded with with query, filter, sort, order and facet methods.

Version
```````

This method returns the Crossref API version.

.. code-bolck:: python

  In [1]: from crossref.restful import Journals

  In [2]: journals = Journals()

  In [3]: journals.version
  Out[3]: '1.0.0'

Count
`````
This method returns the total of itens a query result should retrive. This method will not
iterate and retrieve through the API documents. This method will fetch 0 documents
and retrieve the value of **total-result** attribute.

.. code-bolck:: python

  In [1]: from crossref.restful import Works

  In [2]: works = Works()

  In [3]: works.query('zika').count()
  Out[3]: 3597

  In [4]: works.query('zika').filter(from_online_pub_date='2017').count()
  Out[4]: 444

Url
```

This method returns the url that will be used to query the Crossref API.

.. code-bolck:: python

  In [1]: from crossref.restful import Works

  In [2]: works = Works()

  In [3]: works.query('zika').url
  Out[3]: 'https://api.crossref.org/works?query=zika'

  In [4]: works.query('zika').filter(from_online_pub_date='2017').url
  Out[4]: 'https://api.crossref.org/works?query=zika&filter=from-online-pub-date%3A2017'

  In [5]: works.query('zika').filter(from_online_pub_date='2017').query(author='Mari').url
  Out[5]: 'https://api.crossref.org/works?query.author=Mari&filter=from-online-pub-date%3A2017&query=zika'

  In [6]: works.query('zika').filter(from_online_pub_date='2017').query(author='Mari').sort('published').url
  Out[6]: 'https://api.crossref.org/works?query.author=Mari&query=zika&filter=from-online-pub-date%3A2017&sort=published'

  In [7]: works.query('zika').filter(from_online_pub_date='2017').query(author='Mari').sort('published').order('asc').url
  Out[7]: 'https://api.crossref.org/works?filter=from-online-pub-date%3A2017&query.author=Mari&order=asc&query=zika&sort=published'

  In [8]: from crossref.restful import Prefixes

  In [9]: prefixes = Prefixes()

  In [10]: prefixes.works('10.1590').query('zike').url
  Out[10]: 'https://api.crossref.org/prefixes/10.1590/works?query=zike'

  In [11]: from crossref.restful import Journals

  In [12]: journals = Journals()

  In [13]: journals.url
  Out[13]: 'https://api.crossref.org/journals'

  In [14]: journals.works('0102-311X').url
  Out[14]: 'https://api.crossref.org/journals/0102-311X/works'

  In [15]: journals.works('0102-311X').query('zika').url
  Out[15]: 'https://api.crossref.org/journals/0102-311X/works?query=zika'

  In [16]: journals.works('0102-311X').query('zika').count()
  Out[16]: 12

All
```

This method returns all items of an endpoint. It will use the limit offset
parameters to iterate through the endpoints Journals, Types, Members and Prefixes.

For the **works** endpoint, the library will make use of the **cursor** to paginate through
API until it is totally consumed.

.. code-bolck:: python

  In [1]: from crossref.restful import Journals

  In [2]: journals = Journals()

  In [3]: for item in journals.all():
     ...:     print(item['title'])
     ...:
  JNSM
  New Comprehensive Biochemistry
  New Frontiers in Ophthalmology
  Oral Health Case Reports
  Orbit A Journal of American Literature
  ORDO
