.. :changelog:

History
-------

0.2.0 (2014-05-06)
++++++++++++++++++

* Added a CLI option. Original idea for this came from `Marek Wywiał
  <https://github.com/onjin/pgextrascli>`_.
* Remove commas from integer output so no additional parsing is needed if
  someone wants to store the results.
* Make API more consistent by not raising an exception when the
  "pg_stat_statement" module is not installed. Instead a list with a single
  namedtuple containing the error message is returned.

0.1.1 (2014-05-01)
++++++++++++++++++

* updated documentation
* increased test coverage

0.1.0 (2014-04-25)
++++++++++++++++++

* First release on PyPI.
