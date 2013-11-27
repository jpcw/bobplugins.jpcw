.. contents::

Introduction
============

Flexibles rendering plugins for mrbob

Plugins
========

If_Statement
--------------

Add an **+__if_any.var__+** statement to influence rendering. 

For example foo/+if_render.me++author+/+age+.bob given variables author being Foo and age being 12, foo/Foo/12 will be rendered if **render.me** is True.

Else only foo/ will be rendered. Please notice that only ('y', 'yes', 'true', 'True', 1) are True, anything else will be considred as False.



Tests
=====

bobplugins.jpcw is continuously 

+ tested on Travis |travisstatus|_ 

+ coverage tracked on coveralls.io |coveralls|_.

.. |travisstatus| image:: https://api.travis-ci.org/jpcw/bobplugins.jpcw.png
.. _travisstatus:  http://travis-ci.org/jpcw/bobplugins.jpcw


.. |coveralls| image:: https://coveralls.io/repos/jpcw/bobplugins.jpcw/badge.png
.. _coveralls: https://coveralls.io/r/jpcw/bobplugins.jpcw



