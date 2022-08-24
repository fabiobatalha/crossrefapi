-------------------
Crossref API Client
-------------------

Library with functions to iterate through the Crossref API.

.. image:: https://travis-ci.org/fabiobatalha/crossrefapi.svg?branch=master
    :target: https://travis-ci.org/fabiobatalha/crossrefapi

--------------
How to Install
--------------

.. code-block:: shell

  pip install crossrefapi

----------
How to Use
----------

Works
-----

Agency
``````

.. code-block:: python

  In [1]: from crossref.restful import Works

  In [2]: works = Works()

  In [3]: works.agency('10.1590/0102-311x00133115')
  Out[3]:
  {'DOI': '10.1590/0102-311x00133115',
   'agency': {'id': 'crossref', 'label': 'CrossRef'}}

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

  In [3]: w1 = works.query(bibliographic='zika', author='johannes', publisher_name='Wiley-Blackwell')

  In [4]: for item in w1:
     ...:     print(item['title'])
     ...:
     ...:
  ['Inactivation and removal of Zika virus during manufacture of plasma-derived medicinal products']
  ['Harmonization of nucleic acid testing for Zika virus: development of the 1st\n World Health Organization International Standard']

Doi
```

.. code-block:: python

  In [1]: from crossref.restful import Works

  In [2]: works = Works()

  In [3]: works.doi('10.1590/0102-311x00133115')
  Out[3]:
  {'DOI': '10.1590/0102-311x00133115',
   'ISSN': ['0102-311X'],
   'URL': 'http://dx.doi.org/10.1590/0102-311x00133115',
   'alternative-id': ['S0102-311X2016001107002'],
   'author': [{'affiliation': [{'name': 'Surin Rajabhat University,  Thailand'}],
     'family': 'Wiwanitki',
     'given': 'Viroj'}],
   'container-title': ['Cadernos de Saúde Pública'],
   'content-domain': {'crossmark-restriction': False, 'domain': []},
   'created': {'date-parts': [[2016, 12, 7]],
    'date-time': '2016-12-07T21:52:08Z',
    'timestamp': 1481147528000},
   'deposited': {'date-parts': [[2017, 5, 24]],
    'date-time': '2017-05-24T01:57:26Z',
    'timestamp': 1495591046000},
   'indexed': {'date-parts': [[2017, 5, 24]],
    'date-time': '2017-05-24T22:39:11Z',
    'timestamp': 1495665551858},
   'is-referenced-by-count': 0,
   'issn-type': [{'type': 'electronic', 'value': '0102-311X'}],
   'issue': '11',
   'issued': {'date-parts': [[2016, 11]]},
   'member': '530',
   'original-title': [],
   'prefix': '10.1590',
   'published-print': {'date-parts': [[2016, 11]]},
   'publisher': 'FapUNIFESP (SciELO)',
   'reference-count': 3,
   'references-count': 3,
   'relation': {},
   'score': 1.0,
   'short-container-title': ['Cad. Saúde Pública'],
   'short-title': [],
   'source': 'Crossref',
   'subject': ['Medicine(all)'],
   'subtitle': [],
   'title': ['Congenital Zika virus syndrome'],
   'type': 'journal-article',
   'volume': '32'}

Select
``````

.. code-block:: python

    In [1]: from crossref.restful import Works

    In [2]: works = Works()

    In [3]: for i in works.filter(has_funder='true', has_license='true').sample(5).select('DOI, prefix'):
       ...:     print(i)
       ...:
    {'DOI': '10.1111/str.12144', 'member': 'http://id.crossref.org/member/311', 'prefix': '10.1111'}
    {'DOI': '10.1002/admi.201400154', 'member': 'http://id.crossref.org/member/311', 'prefix': '10.1002'}
    {'DOI': '10.1016/j.surfcoat.2010.10.057', 'member': 'http://id.crossref.org/member/78', 'prefix': '10.1016'}
    {'DOI': '10.1007/s10528-015-9707-8', 'member': 'http://id.crossref.org/member/297', 'prefix': '10.1007'}
    {'DOI': '10.1016/j.powtec.2016.04.009', 'member': 'http://id.crossref.org/member/78', 'prefix': '10.1016'}

    In [4]: for i in works.filter(has_funder='true', has_license='true').sample(5).select(['DOI', 'prefix']):
       ...:     print(i)
       ...:
    {'DOI': '10.1002/jgrd.50059', 'member': 'http://id.crossref.org/member/311', 'prefix': '10.1002'}
    {'DOI': '10.1111/ajt.13880', 'member': 'http://id.crossref.org/member/311', 'prefix': '10.1111'}
    {'DOI': '10.1016/j.apgeochem.2015.05.006', 'member': 'http://id.crossref.org/member/78', 'prefix': '10.1016'}
    {'DOI': '10.1016/j.triboint.2015.01.023', 'member': 'http://id.crossref.org/member/78', 'prefix': '10.1016'}
    {'DOI': '10.1007/s10854-016-4649-4', 'member': 'http://id.crossref.org/member/297', 'prefix': '10.1007'}

    In [5]: for i in works.filter(has_funder='true', has_license='true').sample(5).select('DOI').select('prefix'):
       ...:     print(i)
       ...:
    {'DOI': '10.1002/mrm.25790', 'member': 'http://id.crossref.org/member/311', 'prefix': '10.1002'}
    {'DOI': '10.1016/j.istruc.2016.11.001', 'member': 'http://id.crossref.org/member/78', 'prefix': '10.1016'}
    {'DOI': '10.1002/anie.201505015', 'member': 'http://id.crossref.org/member/311', 'prefix': '10.1002'}
    {'DOI': '10.1016/j.archoralbio.2010.11.011', 'member': 'http://id.crossref.org/member/78', 'prefix': '10.1016'}
    {'DOI': '10.1145/3035918.3064012', 'member': 'http://id.crossref.org/member/320', 'prefix': '10.1145'}

    In [6]: for i in works.filter(has_funder='true', has_license='true').sample(5).select('DOI', 'prefix'):
       ...:     print(i)
       ...:
    {'DOI': '10.1016/j.cplett.2015.11.062', 'member': 'http://id.crossref.org/member/78', 'prefix': '10.1016'}
    {'DOI': '10.1016/j.bjp.2015.06.001', 'member': 'http://id.crossref.org/member/78', 'prefix': '10.1016'}
    {'DOI': '10.1111/php.12613', 'member': 'http://id.crossref.org/member/311', 'prefix': '10.1111'}
    {'DOI': '10.1002/cfg.144', 'member': 'http://id.crossref.org/member/98', 'prefix': '10.1155'}
    {'DOI': '10.1002/alr.21987', 'member': 'http://id.crossref.org/member/311', 'prefix': '10.1002'}

Facet
`````

.. code-block:: python

  In [1]: from crossref.restful import Works, Prefixes

  In [2]: works = Works()

  In [3]: works.facet('issn', 10)
  Out[3]:
  {'issn': {'value-count': 10,
    'values': {'http://id.crossref.org/issn/0009-2975': 306546,
     'http://id.crossref.org/issn/0028-0836': 395353,
     'http://id.crossref.org/issn/0140-6736': 458909,
     'http://id.crossref.org/issn/0302-9743': 369955,
     'http://id.crossref.org/issn/0931-7597': 487523,
     'http://id.crossref.org/issn/0959-8138': 392754,
     'http://id.crossref.org/issn/1095-9203': 253978,
     'http://id.crossref.org/issn/1468-5833': 388355,
     'http://id.crossref.org/issn/1556-5068': 273653,
     'http://id.crossref.org/issn/1611-3349': 329573}}}

  In [4]: prefixes = Prefixes()

  In [5]: prefixes.works('10.1590').facet('issn', 10)
  Out[5]:
  {'issn': {'value-count': 10,
    'values': {'http://id.crossref.org/issn/0004-282X': 7712,
     'http://id.crossref.org/issn/0034-8910': 4752,
     'http://id.crossref.org/issn/0037-8682': 4179,
     'http://id.crossref.org/issn/0074-0276': 7941,
     'http://id.crossref.org/issn/0100-204X': 3946,
     'http://id.crossref.org/issn/0100-4042': 4198,
     'http://id.crossref.org/issn/0102-311X': 6548,
     'http://id.crossref.org/issn/0103-8478': 6607,
     'http://id.crossref.org/issn/1413-8123': 4658,
     'http://id.crossref.org/issn/1516-3598': 4678}}}

  In [6]: prefixes.works('10.1590').query('zika').facet('issn', 10)
  Out[6]:
  {'issn': {'value-count': 10,
    'values': {'http://id.crossref.org/issn/0004-282X': 4,
     'http://id.crossref.org/issn/0036-4665': 4,
     'http://id.crossref.org/issn/0037-8682': 7,
     'http://id.crossref.org/issn/0074-0276': 7,
     'http://id.crossref.org/issn/0102-311X': 12,
     'http://id.crossref.org/issn/0103-7331': 2,
     'http://id.crossref.org/issn/0104-4230': 3,
     'http://id.crossref.org/issn/1519-3829': 7,
     'http://id.crossref.org/issn/1679-4508': 2,
     'http://id.crossref.org/issn/1806-8324': 2}}}

Journals
--------

Exemplifying the use of API Library to retrieve data from Journals endpoint.

.. code-block:: python

  In [1]: from crossref.restful import Journals

  In [2]: journals = Journals()

  In [3]: journals.journal('0102-311X')
  Out[3]:
  {'ISSN': ['0102-311X', '0102-311X'],
   'breakdowns': {'dois-by-issued-year': [[2013, 462],
     [2007, 433],
     [2008, 416],
     [2009, 347],
     [2006, 344],
     [2014, 292],
     [2004, 275],
     [2012, 273],
     [2011, 270],
     [2010, 270],
     [2005, 264],
     [2003, 257],
     [2001, 220],
     [2002, 219],
     [1998, 187],
     [2000, 169],
     [1997, 142],
     [1999, 136],
     [1994, 110],
     [1995, 104],
     [1996, 103],
     [1993, 99],
     [2015, 93],
     [1992, 65],
     [1986, 63],
     [1985, 53],
     [1990, 49],
     [1988, 49],
     [1991, 48],
     [1987, 46],
     [1989, 45]]},
   'counts': {'backfile-dois': 5565, 'current-dois': 335, 'total-dois': 5900},
   'coverage': {'award-numbers-backfile': 0.0,
    'award-numbers-current': 0.0,
    'funders-backfile': 0.0,
    'funders-current': 0.0,
    'licenses-backfile': 0.0,
    'licenses-current': 0.0,
    'orcids-backfile': 0.0,
    'orcids-current': 0.0,
    'references-backfile': 0.0,
    'references-current': 0.0,
    'resource-links-backfile': 0.0,
    'resource-links-current': 0.0,
    'update-policies-backfile': 0.0,
    'update-policies-current': 0.0},
   'flags': {'deposits': True,
    'deposits-articles': True,
    'deposits-award-numbers-backfile': False,
    'deposits-award-numbers-current': False,
    'deposits-funders-backfile': False,
    'deposits-funders-current': False,
    'deposits-licenses-backfile': False,
    'deposits-licenses-current': False,
    'deposits-orcids-backfile': False,
    'deposits-orcids-current': False,
    'deposits-references-backfile': False,
    'deposits-references-current': False,
    'deposits-resource-links-backfile': False,
    'deposits-resource-links-current': False,
    'deposits-update-policies-backfile': False,
    'deposits-update-policies-current': False},
   'last-status-check-time': 1459491023622,
   'publisher': 'SciELO',
   'title': 'Cadernos de Saúde Pública'}

  In [4]: journals.journal_exists('0102-311X')
  Out[4]: True

  In [5]: journals.query('Cadernos').url
  Out[5]: 'https://api.crossref.org/journals?query=Cadernos'

  In [6]: journals.query('Cadernos').count()
  Out[6]: 60

  In [7]: journals.works('0102-311X').query('zika').url
  Out[7]: 'https://api.crossref.org/journals/0102-311X/works?query=zika'

  In [8]: journals.works('0102-311X').query('zika').count()
  Out[8]: 12

  In [9]: journals.works('0102-311X').query('zika').query(author='Diniz').url
  Out[9]: 'https://api.crossref.org/journals/0102-311X/works?query.author=Diniz&query=zika'

  In [10]: journals.works('0102-311X').query('zika').query(author='Diniz').count()
  Out[10]: 1


Base Methods
------------

The base methods could be used along with the query, filter, sort, order and facet methods.

Version
```````

This method returns the Crossref API version.

.. code-block:: python

  In [1]: from crossref.restful import Journals

  In [2]: journals = Journals()

  In [3]: journals.version
  Out[3]: '1.0.0'

Count
`````
This method returns the total number of items a query result should retrieve. This method will not
iterate through and retrieve the API documents. This method will fetch 0 documents
and retrieve the value of **total-result** attribute.

.. code-block:: python

  In [1]: from crossref.restful import Works

  In [2]: works = Works()

  In [3]: works.query('zika').count()
  Out[3]: 3597

  In [4]: works.query('zika').filter(from_online_pub_date='2017').count()
  Out[4]: 444

Url
```

This method returns the url that will be used to query the Crossref API.

.. code-block:: python

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

.. code-block:: python

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

Support for Polite Requests (Etiquette)
---------------------------------------

Respecting the Crossref API polices for polite requests. This library allows users
to setup an Etiquette object to be used in the http requests.

.. code-block:: python

    In [1]: from crossref.restful import Works, Etiquette

    In [2]: my_etiquette = Etiquette('My Project Name', 'My Project version', 'My Project URL', 'My contact email')

    In [3]: str(my_etiquette)
    Out[3]: 'My Project Name/My Project version (My Project URL; mailto:My contact email) BasedOn: CrossrefAPI/1.1.0'

    In [4]: my_etiquette = Etiquette('My Project Name', '0.2alpha', 'https://myalphaproject.com', 'anonymous@myalphaproject.com')

    In [5]: str(my_etiquette)
    Out[5]: 'My Project Name/0.2alpha (https://myalphaproject.com; mailto:anonymous@myalphaproject.com) BasedOn: CrossrefAPI/1.1.0'

    In [6]: works = Works(etiquette=my_etiquette)

    In [7]: for i in works.sample(5).select('DOI'):
       ...:     print(i)
       ...:

    {'DOI': '10.1016/j.ceramint.2014.10.086'}
    {'DOI': '10.1016/j.biomaterials.2012.02.034'}
    {'DOI': '10.1001/jamaoto.2013.6450'}
    {'DOI': '10.1016/s0021-9290(17)30138-0'}
    {'DOI': '10.1109/ancs.2011.11'}


Voilá!!! The requests made for the Crossref API, were made setting the user-agent as: 'My Project Name/0.2alpha (https://myalphaproject.com; mailto:anonymous@myalphaproject.com) BasedOn: CrossrefAPI/1.1.0'


Depositing Metadata to Crossref
-------------------------------

This library implements the deposit operation "doMDUpload", it means you are able to submit Digital Objects Metadata to Crossref. Se more are: https://support.crossref.org/hc/en-us/articles/214960123

To do that, you must have an active publisher account with crossref.org.

First of all, you need a valid XML following the crossref DTD.

.. code-block:: xml

  <?xml version='1.0' encoding='utf-8'?>
  <doi_batch xmlns:jats="http://www.ncbi.nlm.nih.gov/JATS1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.crossref.org/schema/4.4.0" version="4.4.0" xsi:schemaLocation="http://www.crossref.org/schema/4.4.0 http://www.crossref.org/schemas/crossref4.4.0.xsd">
    <head>
      <doi_batch_id>c5473e12dc8e4f36a40f76f8eae15280</doi_batch_id>
      <timestamp>20171009132847</timestamp>
      <depositor>
        <depositor_name>SciELO</depositor_name>
        <email_address>crossref@scielo.org</email_address>
      </depositor>
      <registrant>SciELO</registrant>
    </head>
    <body>
      <journal>
        <journal_metadata>
          <full_title>Revista Brasileira de Ciência Avícola</full_title>
          <abbrev_title>Rev. Bras. Cienc. Avic.</abbrev_title>
          <issn media_type="electronic">1516-635X</issn>
        </journal_metadata>
        <journal_issue>
          <publication_date media_type="print">
            <month>09</month>
            <year>2017</year>
          </publication_date>
          <journal_volume>
            <volume>19</volume>
          </journal_volume>
          <issue>3</issue>
        </journal_issue>
        <journal_article publication_type="full_text" reference_distribution_opts="any">
          <titles>
            <title>Climatic Variation: Effects on Stress Levels, Feed Intake, and Bodyweight of Broilers</title>
          </titles>
          <contributors>
            <person_name contributor_role="author" sequence="first">
              <given_name>R</given_name>
              <surname>Osti</surname>
              <affiliation>Huazhong Agricultural University,  China</affiliation>
            </person_name>
            <person_name contributor_role="author" sequence="additional">
              <given_name>D</given_name>
              <surname>Bhattarai</surname>
              <affiliation>Huazhong Agricultural University,  China</affiliation>
            </person_name>
            <person_name contributor_role="author" sequence="additional">
              <given_name>D</given_name>
              <surname>Zhou</surname>
              <affiliation>Huazhong Agricultural University,  China</affiliation>
            </person_name>
          </contributors>
          <publication_date media_type="print">
            <month>09</month>
            <year>2017</year>
          </publication_date>
          <pages>
            <first_page>489</first_page>
            <last_page>496</last_page>
          </pages>
          <publisher_item>
            <identifier id_type="pii">S1516-635X2017000300489</identifier>
          </publisher_item>
          <doi_data>
            <doi>10.1590/1806-9061-2017-0494</doi>
            <resource>http://www.scielo.br/scielo.php?script=sci_arttext&amp;pid=S1516-635X2017000300489&amp;lng=en&amp;tlng=en</resource>
          </doi_data>
          <citation_list>
            <citation key="ref1">
              <journal_title>Journal of Agriculture Science</journal_title>
              <author>Alade O</author>
              <volume>5</volume>
              <first_page>176</first_page>
              <cYear>2013</cYear>
              <article_title>Perceived effect of climate variation on poultry production in Oke Ogun area of Oyo State</article_title>
            </citation>

            ...

            <citation key="ref40">
              <journal_title>Poultry Science</journal_title>
              <author>Zulkifli I</author>
              <volume>88</volume>
              <first_page>471</first_page>
              <cYear>2009</cYear>
              <article_title>Crating and heat stress influence blood parameters and heat shock protein 70 expression in broiler chickens showing short or long tonic immobility reactions</article_title>
            </citation>
          </citation_list>
        </journal_article>
      </journal>
    </body>
  </doi_batch>

Second! Using the library

.. code-block:: python

  In [1]: from crossref.restful import Depositor

  In [2]: request_xml = open('tests/fixtures/deposit_xml_sample.xml', 'r').read()

  In [3]: depositor = Depositor('your prefix', 'your crossref user', 'your crossref password')

  In [4]: response = depositor.register_doi('testing_20171011', request_xml)

  In [5]: response.status_code
  Out[5]: 200

  In [6]: response.text
  Out[6]: '\n\n\n\n<html>\n<head><title>SUCCESS</title>\n</head>\n<body>\n<h2>SUCCESS</h2>\n<p>Your batch submission was successfully received.</p>\n</body>\n</html>\n'

  In [7]: response = depositor.request_doi_status_by_filename('testing_20171011.xml')

  In [8]: response.text
  Out[8]: '<?xml version="1.0" encoding="UTF-8"?>\n<doi_batch_diagnostic status="queued">\r\n  <submission_id>1415653976</submission_id>\r\n  <batch_id />\r\n</doi_batch_diagnostic>'

  In [9]: response = depositor.request_doi_status_by_filename('testing_20171011.xml')

  In [10]: response.text
  Out[10]: '<?xml version="1.0" encoding="UTF-8"?>\n<doi_batch_diagnostic status="queued">\r\n  <submission_id>1415653976</submission_id>\r\n  <batch_id />\r\n</doi_batch_diagnostic>'

  In [11]: response = depositor.request_doi_status_by_filename('testing_20171011.xml', data_type='result')

  In [12]: response.text
  Out[12]: '<?xml version="1.0" encoding="UTF-8"?>\n<doi_batch_diagnostic status="queued">\r\n  <submission_id>1415653976</submission_id>\r\n  <batch_id />\r\n</doi_batch_diagnostic>'

  In [13]: response = depositor.request_doi_status_by_filename('testing_20171011.xml', data_type='contents')

  In [14]: response.text
  Out[14]: '<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<doi_batch xmlns:jats="http://www.ncbi.nlm.nih.gov/JATS1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.crossref.org/schema/4.4.0" version="4.4.0" xsi:schemaLocation="http://www.crossref.org/schema/4.4.0 http://www.crossref.org/schemas/crossref4.4.0.xsd">\n  <head>\n    <doi_batch_id>c5473e12dc8e4f36a40f76f8eae15280</doi_batch_id>\n    <timestamp>20171009132847</timestamp>\n    <depositor>\n      <depositor_name>SciELO</depositor_name>\n      <email_address>crossref@scielo.org</email_address>\n    </depositor>\n    <registrant>SciELO</registrant>\n  </head>\n  <body>\n    <journal>\n      <journal_metadata>\n        <full_title>Revista Brasileira de Ciência Avícola</full_title>\n        <abbrev_title>Rev. Bras. Cienc. Avic.</abbrev_title>\n        <issn media_type="electronic">1516-635X</issn>\n      </journal_metadata>\n      <journal_issue>\n        <publication_date media_type="print">\n          <month>09</month>\n          <year>2017</year>\n        </publication_date>\n        <journal_volume>\n          <volume>19</volume>\n        </journal_volume>\n        <issue>3</issue>\n      </journal_issue>\n      <journal_article publication_type="full_text" reference_distribution_opts="any">\n        <titles>\n          <title>Climatic Variation: Effects on Stress Levels, Feed Intake, and Bodyweight of Broilers</title>\n        </titles>\n        <contributors>\n          <person_name contributor_role="author" sequence="first">\n            <given_name>R</given_name>\n            <surname>Osti</surname>\n            <affiliation>Huazhong Agricultural University,  China</affiliation>\n          </person_name>\n          <person_name contributor_role="author" sequence="additional">\n            <given_name>D</given_name>\n            <surname>Bhattarai</surname>\n            <affiliation>Huazhong Agricultural University,  China</affiliation>\n          </person_name>\n          <person_name contributor_role="author" sequence="additional">\n            <given_name>D</given_name>\n            <surname>Zhou</surname>\n            <affiliation>Huazhong Agricultural University,  China</affiliation>\n          </person_name>\n        </contributors>\n        <publication_date media_type="print">\n          <month>09</month>\n          <year>2017</year>\n        </publication_date>\n        <pages>\n          <first_page>489</first_page>\n          <last_page>496</last_page>\n        </pages>\n        <publisher_item>\n          <identifier id_type="pii">S1516-635X2017000300489</identifier>\n        </publisher_item>\n</doi_batch>'

  In [15]: response = depositor.request_doi_status_by_filename('testing_20171011.xml', data_type='result')

  In [16]: response.text
  Out[16]:
    <doi_batch_diagnostic status="completed" sp="ds4.crossref.org">
       <submission_id>1415649102</submission_id>
       <batch_id>9112073c7f474394adc01b82e27ea2a8</batch_id>
       <record_diagnostic status="Success">
          <doi>10.1590/0037-8682-0216-2016</doi>
          <msg>Successfully updated</msg>
          <citations_diagnostic>
             <citation key="ref1" status="resolved_reference">10.1590/0037-8682-0284-2014</citation>
             <citation key="ref2" status="resolved_reference">10.1371/journal.pone.0090237</citation>
             <citation key="ref3" status="resolved_reference">10.1093/infdis/172.6.1561</citation>
             <citation key="ref4" status="resolved_reference">10.1016/j.ijpara.2011.01.005</citation>
             <citation key="ref5" status="resolved_reference">10.1016/j.rvsc.2013.01.006</citation>
             <citation key="ref6" status="resolved_reference">10.1093/trstmh/tru113</citation>
             <citation key="ref7" status="resolved_reference">10.1590/0074-02760150459</citation>
          </citations_diagnostic>
       </record_diagnostic>
       <batch_data>
          <record_count>1</record_count>
          <success_count>1</success_count>
          <warning_count>0</warning_count>
          <failure_count>0</failure_count>
       </batch_data>
    </doi_batch_diagnostic>

Explaining the code
```````````````````

**Line 1:** Importing the Depositor Class

**Line 2:** Loading a valid XML for deposit

**Line 3:** Creating an instance of Depositor. You should use you crossref credentials at this point. If you wana be polite, you should also give an etiquette object at this momment.

.. block-code:: python

  etiquette = Etiquette('My Project Name', 'My Project version', 'My Project URL', 'My contact email')
  Depositor('your prefix', 'your crossref user', 'your crossref password', etiquette)

**Line 4:** Requesting the DOI (Id do not means you DOI was registered, it is just a DOI Request)

**Line 5:** Checking the DOI request response.

**Line 6:** Printing the DOI request response body.

**Line 7:** Requesting the DOI registering status.

**Line 8:** Checking the DOI registering status, reading the body of the response. You should parse this XML to have the current status of the DOI registering request. You should do this util have an success or error status retrieved.

**Line 9-12:** Rechecking the request status. It is still in queue. You can also set the response type between ['result', 'contents'], where result will retrieve the status of the DOI registering process, and contents will retrieve the submitted XML content while requesting the DOI.

**Line 13-14:** Checking the content submitted passing the attribute data_type='contents'.

**Line 15-16:** After a while, the success status was received.



