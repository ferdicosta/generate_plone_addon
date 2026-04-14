from Products.Five import BrowserView
from zope.interface import Interface


class IPDB(Interface):
    """
    IPDB view interface
    """


class PDB(BrowserView):
    """
    PDB browser view
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        breakpoint()
