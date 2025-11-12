from zope.interface import Interface
from zope.viewlet.interfaces import IViewletManager


class IMainNavigationManager(IViewletManager):
    """Viewlet manager for nav"""


class IFooterManager(IViewletManager):
    """Viewlet manager for footer"""
