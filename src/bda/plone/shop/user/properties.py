# -*- coding: utf-8 -*-
from AccessControl.class_init import InitializeClass
from Products.CMFPlone.utils import safe_unicode
from Products.PluggableAuthService.interfaces.plugins import IPropertiesPlugin
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.utils import classImplements
from bda.plone.checkout.vocabularies import get_pycountry_name
from zope.interface import implementer


PAS_ID = 'bda.plone.shop'


@implementer(IPropertiesPlugin)
class UserPropertiesPASPlugin(BasePlugin):
    """ An implementer of IPropertiesPlugin which
    provides the method getPropertiesForUser, this method
    adds computed properties to PlonePAS which we remove
    at another place.
    """

    meta_type = 'bda.plone.shop user properties'

    def __init__(self, id, title=None):
        self._setId(id)
        self.title = title

    def _getPropertSheetsFromUser(self, user):
        """ Get PropertySheets from a IPropertiedUser without
        the current sheet, so we dont have recursions.
        """
        sheet_ids = user.listPropertysheets()

        result = []
        for sheet_id in sheet_ids:
            if sheet_id != PAS_ID:
                result.append(user.getPropertysheet(sheet_id))

        return result

    def getPropertiesForUser(self, user, request=None):
        """ This can't use plone.api.user.get(user.getId()) as it would
        lead to a recursion.
        """

        sheets = self._getPropertSheetsFromUser(user)

        def getProperty(id, default):
            for sheet in sheets:
                if sheet.hasProperty(id):
                    # Return the first one that has the property.
                    return safe_unicode(sheet.getProperty(id))

            return safe_unicode(default)

        first = getProperty('firstname', u'')
        last = getProperty('lastname', u'')
        street = getProperty('street', u'')
        zip_code = getProperty('zip', u'')
        city = getProperty('city', u'')
        country = getProperty('country', u'')

        try:
            country = country and get_pycountry_name(country) or ''
        except KeyError:
            country = ''

        join_list = [street, '{0} {1}'.format(zip_code, city), country]

        # return {
        #     'fullname': u"bda.plone.shop",
        #     'location': u"bda.plone.shop",
        # }

        return {
            'fullname': u'%s%s%s' % (
                first,
                first and last and u' ' or u'',
                last,
            ),

            'location': u', '.join([it for it in join_list if it]),
        }

classImplements(UserPropertiesPASPlugin, IPropertiesPlugin)
InitializeClass(UserPropertiesPASPlugin)
