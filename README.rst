collective.multilingualtools
============================

This package is WORK IN PROGRESS. It is based on the concepts of
collective/slc.linguatools,
but this package works with plone.app.multilingual and both dexterity and archetypes.

It aims to offer a handfull of utilities for performing the same action on all
translations of an item at the sime time, such as

* change workflow status
* rename (change id)
* reindex
* delete
* cut and paste (move)
* set title / description from msgid
* propagate or block portlets
* set or remove properties (such as layout)
* set or remove marker interface

Also, there's an option to make a copy of any item to all available languages (or
a subset), optionally copying individual attributes (title, description, tags, etc).

As I said, WORK IN PROGRESS. Basic functionality is becoming stable, but documentation
and tests are not there yet.
