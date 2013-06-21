__version__ = VERSION = 0, 0, 4
__versionstr__ = '.'.join(map(str, VERSION))

try:
    from smartadmin.admin import SmartAdmin, filter_existing
    # this only works inside a django project...
except:
    print "WARNING: Couldn't import smartadmin, try importing from smartadmin.admin to see why. Note that this only works from inside of a properly configured django project."
    pass
