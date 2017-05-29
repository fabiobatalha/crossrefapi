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

    In [1]: from crossref.restful import Works

    In [2]: works = Works()

    In [3]: w1 = works.query(title='zika', author='johannes', publisher_name='Wiley-Blackwell')

    In [4]: for item in w1:
       ...:     print(item['title'])
       ...:
       ...:
    ['Inactivation and removal of Zika virus during manufacture of plasma-derived medicinal products']
    ['Harmonization of nucleic acid testing for Zika virus: development of the 1st\n World Health Organization International Standard']
