Django Smart Admin
==================

Django's default ``ModelAdmin`` is kinda dull. It only displays the
``__unicode__`` column and that's it. ``SmartAdmin`` attempts to create some
more useful defaults for ``list_display``, ``list_filter``, etc., based on the
model. (You can still manually specify whatever you want of course.)

This may be useful to you if you create new models often and want to have a
usable admin for them without much work.


Installation
------------

::

    pip install django-smartadmin


Usage
-----

Just use ``smartadmin.SmartAdmin`` instead of
``django.contrib.admin.ModelAdmin``:

.. code-block:: python

    from smartadmin import SmartAdmin

    class MyModelAdmin(SmartAdmin):
        pass  # or override something

    admin.site.register(MyModel, MyModelAdmin)

    # or just:

    admin.site.register(MyModel, SmartAdmin)
