import logging

from Products.Five import BrowserView
from Products.Five.utilities.interfaces import IMarkerInterfaces
from {{package_name}} import CustomViewInterface
from zope.interface import Interface

logger = logging.getLogger(__name__)


class IInterfacesView(Interface):
    """
    IInterfacesView view interface
    """


class InterfacesView(BrowserView):
    """
    InterfacesView browser view
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.adapted = IMarkerInterfaces(context)

    def __call__(self, SAVE=None, add=(), remove=()):
        if SAVE:
            self.update(add, remove)
            url = '%s?manage_tabs_message=Changes+applied.'
            self.request.response.redirect(url % self.request.ACTUAL_URL)
            return ''
        return self.index()

    def _getNameLinkDicts(self, interfaceNames):
        return [dict(name = name) for name in interfaceNames]

    def getAvailableInterfaceNames(self):
        available = self.adapted.getAvailableInterfaces()
        filtered = [{'dotted': f'{x.__module__}.{x.__name__}', 'name': x.__name__, 'doc': x.__doc__} for x in available if x.isOrExtends(CustomViewInterface) and x is not CustomViewInterface]

        groups = {}

        for iface in filtered:
            parts = iface['name'].split('.')
            group_key = parts[1] if len(parts) > 1 else 'other'

            if group_key not in groups:
                groups[group_key] = []

            groups[group_key].append(iface)

        return [{'group': key, 'interfaces': ifaces} for key, ifaces in sorted(groups.items())]

    def getDirectlyProvidedNames(self):
        return [{'dotted': f'{x.__module__}.{x.__name__}', 'name': x.__name__, 'doc': x.__doc__} for x in self.adapted.getDirectlyProvided() if x.isOrExtends(CustomViewInterface) and x is not CustomViewInterface]

    def update(self, add, remove):
        add = self.adapted.dottedToInterfaces(add)
        remove = self.adapted.dottedToInterfaces(remove)
        self.adapted.update(add = add, remove = remove)
