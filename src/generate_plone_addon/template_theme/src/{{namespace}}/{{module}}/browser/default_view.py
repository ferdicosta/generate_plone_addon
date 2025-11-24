from Products.Five import BrowserView
from zope.interface import Interface


class IDefaultView(Interface):
    """
    IDefaultView view interface
    """


class DefaultView(BrowserView):
    """
    DefaultView browser view
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def title(self):
        return self.context.Title()

    @property
    def description(self):
        return self.context.Description()
