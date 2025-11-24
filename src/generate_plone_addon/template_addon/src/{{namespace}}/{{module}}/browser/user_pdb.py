from Products.Five import BrowserView
from zope.interface import Interface


class IUserPDB(Interface):
    """
    IUserPDB view interface
    """


class UserPDB(BrowserView):
    """
    UserPDB browser view
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        import pdb; pdb.set_trace()
