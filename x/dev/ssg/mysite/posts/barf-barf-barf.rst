.. title: Barf barf barf
.. slug: barf-barf-bar
.. date: 2024-08-10 14:32:59 UTC-07:00
.. tags: 
.. category: 
.. link: 
.. description: Barf barf
.. type: text

Write your post here.

{{% chart Bar title='Browser usage evolution (in %)'
x_labels='["2002","2003","2004","2005","2006","2007"]' %}}
        'Firefox', [None, None, 0, 16.6, 25, 31]
        'Chrome',  [None, None, None, None, None, None]
        'IE',      [85.8, 84.6, 84.7, 74.5, 66, 58.6]
        'Others',  [14.2, 15.4, 15.3, 8.9, 9, 10.4]
        {{% /chart %}}

.. list-table::
   :widths: 15 15 60
   :header-rows: 1

   * - Field
     - Type
     - Details
   * - ``correct_map``
     - dict
     - For each problem ID value listed by ``answers``, provides:

       * ``correctness``: string; 'correct', 'incorrect'
       * ``hint``: string; Gives optional hint. Nulls allowed.
       * ``hintmode``: string; None, 'on_request', 'always'. Nulls allowed.
       * ``msg``: string; Gives extra message response.
       * ``npoints``: integer; Points awarded for this ``answer_id``. Nulls allowed.
       * ``queuestate``: dict; None when not queued, else ``{key:'', time:''}``
         where ``key`` is a secret string dump of a DateTime object in the form
         '%Y%m%d%H%M%S'. Nulls allowed.

   * - ``grade``
     - integer
     - Current grade value.
   * - ``max_grade``
     - integer
     - Maximum possible grade value.
