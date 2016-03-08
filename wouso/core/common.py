from django.core.cache import cache
import sys


class App:
    """ Interface extended by Game and by Top and Qproposal Activity"""

    @classmethod
    def name(kls):
        return kls.__name__

    @classmethod
    def disabled(kls):
        """ Search for a disabled config setting.
        """
        from wouso.core.config.models import BoolSetting

        return BoolSetting.get('disable-%s' % kls.name()).get_value()

    @classmethod
    def get_modifiers(kls):
        """ Return a list of modifiers - as names (this translates to artifact names)
        Player has_modifier checks if the user has an artifact with the modifier id.
        """
        return []

    @classmethod
    def get_sidebar_widget(kls, request):
        """ Return the sidebar widget, for current HttpRequest request.
        This is called in interface.context_processors.sidebar """
        # DEPRECATED
        return None

    @classmethod
    def get_unread_count(kls, request):
        """ Return the app-specific unread counter.
        """
        return 0

    @classmethod
    def get_header_link(kls, request):
        """ Return dictionary containing (link, text, count) for the content
        to be displayed in the page header.
        Called in interface.context_processors.header """
        # DEPRECATED
        return None

    @classmethod
    def get_footer_link(kls, request):
        """ Return html content to be displayed in the footer
        Called in interface.context_processors.footer """
        # DEPRECATED
        return None

    @classmethod
    def get_profile_actions(kls, request, player):
        """ Return html content for player's profile view """
        return ''

    @classmethod
    def get_profile_superuser_actions(kls, request, player):
        """ Return html content for player's profile view
        in the superuser row """
        return ''

    @classmethod
    def get_api(kls):
        """ Return a dictionary with url-regex keys, and PistonHandler values.
        """
        return {}

    @classmethod
    def management_task(cls, datetime=lambda: datetime.now(), stdout=sys.stdout):
        """ Execute maintance task, such as:
        - calculate top ranks
        - inactivate expired spells
        - expire challenges not played
        This method is called from wousocron management task, and the datetime might be faked.
        """
        pass

    management_task = None  # Disable it by default


class Item(object):
    """
     Interface for items that can and should be cached. Usually, they have a string id as the SQL key.
    """
    CREATE_IF_NOT_EXISTS = False

    @classmethod
    def add(cls, name, **data):
        if isinstance(name, cls):
            name.save()
            obj = name
        elif isinstance(name, dict):
            obj = cls.objects.get_or_create(**name)[0]
        else:
            obj = cls.objects.get_or_create(name=name, **data)[0]
        return obj

    @classmethod
    def get(cls, id):
        # TODO: deprecate, poor design
        if isinstance(id, cls):
            return id
        if isinstance(id, dict):
            id = id.get('id', '')
        try:
            return cls.objects.get(name=id)
        except cls.DoesNotExist:
            try:
                return cls.objects.get(id=id)
            except:
                return None

    def __str__(self):
        return u'%s' % self.id

    def __unicode__(self):
        return self.name if hasattr(self, 'name') else str(self)


class CachedItem(Item):
    """
    Interface for standard cached objects
    """
    CACHE_PART = 'id'

    @classmethod
    def _cache_key(cls, part):
        return cls.__name__ + str(part)

    def _get_cache_key(self, part):
        return self.__class__._cache_key(part)

    def _cache_key_part(self):
        return getattr(self, self.CACHE_PART)

    @classmethod
    def _get_fresh(cls, part):
        try:
            return cls.objects.get(**{cls.CACHE_PART: part})
        except cls.DoesNotExist:
            return None

    def save(self, **kwargs):
        r = super(CachedItem, self).save(**kwargs)
        if hasattr(self, self.CACHE_PART) and getattr(self, self.CACHE_PART):
            key = self._get_cache_key(self._cache_key_part())
            cache.delete(key)
        return r

    def delete(self):
        key = self._get_cache_key(self._cache_key_part())
        cache.delete(key)
        return super(CachedItem, self).delete()

    @classmethod
    def get(cls, part):
        if isinstance(part, cls):
            return part
        key = cls._cache_key(part)
        if key in cache:
            return cache.get(key)
        obj = cls._get_fresh(part)
        cache.set(key, obj)
        return obj

    def __str__(self):
        return str(getattr(self, self.CACHE_PART))
