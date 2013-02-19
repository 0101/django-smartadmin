__version__ = VERSION = 0, 0, 2
__versionstr__ = '.'.join(map(str, VERSION))

try:
    from smartadmin.admin import SmartAdmin, filter_existing
    # this only works inside a django project...
except ImportError:
    pass
