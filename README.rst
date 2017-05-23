ArticleMeta API Client
----------------------

Biblioteca para fornecer metodos para interar em endpoints da API ArticleMeta e API RPC do Articlemeta.

Build Status
------------

.. image:: https://travis-ci.org/scieloorg/articlemetaapi.svg?branch=master
    :target: https://travis-ci.org/scieloorg/articlemetaapi

Como Instalar
-------------

pip install articlemetaapi

Como usar
---------


.. code-block:: python

    In [1]: from articlemeta.client import RestfulClient

    In [2]: cl = RestfulClient()

    In [3]: for journal in cl.journals(collection='spa'):
       ...:     print(journal.title, journal.scielo_issn)
       ...:
    Revista Española de Salud Pública 2173-9110
    Annali dell'Istituto Superiore di Sanità 0021-2571
    Bulletin of the World Health Organization 0042-9686
    Cadernos de Saúde Pública 0102-311X
    Ciência & Saúde Coletiva 1413-8123
    Epidemiologia e Serviços de Saúde 2237-9622
    Gaceta Sanitaria 0213-9111
    Interface - Comunicação, Saúde, Educação 1414-3283
    MEDICC Review 1555-7960
    Physis: Revista de Saúde Coletiva 0103-7331
    Revista Brasileira de Epidemiologia 1415-790X
    Revista Cubana de Salud Pública 0864-3466
    Revista Española de Salud Pública 1135-5727
    Revista Panamericana de Salud Pública 1020-4989
    Revista Peruana de Medicina Experimental y Salud Pública 1726-4634
    Revista de Salud Pública 0124-0064
    Revista de Saúde Pública 0034-8910
    Salud Colectiva 1851-8265
    Salud Pública de México 0036-3634

    In [4]: journal = cl.journal(code='0864-3466', collection='spa')

    In [5]: journal.title
    Out[5]: 'Revista Cubana de Salud Pública'

    In [6]: journal.subject_areas
    Out[6]: ['Health Sciences']

    In [7]: journal.scimago_code
    Out[7]: '4900153106'
