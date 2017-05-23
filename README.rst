Crossref API Client
----------------------

Library with functions to iterate through the Crossref API.

Como Instalar
-------------

pip install crossrefapi

Como usar
---------


.. code-block:: python

    In [1]: from crossref.restful import Works

    In [2]: works = Works()

    In [3]: for item in works.sample(2):
       ...:     print(item['title'])
       ...:
    ['On the Origin of the Color-Magnitude Relation in the Virgo Cluster']
    ['Biopsychosocial Wellbeing among Women with Gynaecological Cancer']

    In [4]: w1 = works.query(title='zika', author='johannes', publisher_name='Wiley-Blackwell')

    In [5]: for item in w1:
       ...:     print(item['title'])
       ...:
       ...:
    ['Inactivation and removal of Zika virus during manufacture of plasma-derived medicinal products']
    ['Harmonization of nucleic acid testing for Zika virus: development of the 1st\n World Health Organization International Standard']