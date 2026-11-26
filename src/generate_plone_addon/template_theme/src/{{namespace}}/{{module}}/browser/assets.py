"""Cache busting degli asset statici: URL con ?v=<data di modifica del file>.

Uso nei template:

    tal:define="assets context/@@assets"
    <link rel="stylesheet" tal:attributes="href python:assets.url('++resource++mio.pacchetto.css/style.css')"/>
    <script defer="defer" tal:attributes="src python:assets.url('++plone++mio.pacchetto/vendors/lib.min.js')"></script>

Restituisce l'URL assoluto dal portale (la cache del browser vale in tutte le sezioni)
con ?v= che cambia ogni volta che il file cambia: ricompilare un CSS, modificare un JS
o fare un deploy basta, senza toccare i template.

Portabile: non conosce nessun pacchetto. Funziona con qualunque risorsa registrata con
browser:resourceDirectory (++resource++) o plone:static (++plone++): la attraversa come
farebbe il browser e legge la data del file da cui viene servita. Per usarla in un altro
progetto basta copiare questo file e registrare la vista (vedi configure.zcml).

In debug mode la data si rilegge a ogni richiesta; in produzione si legge una volta per
processo (i file cambiano solo con un deploy, che riavvia l'istanza).
"""

from App.config import getConfiguration
from plone import api
from Products.Five import BrowserView

import logging
import os


logger = logging.getLogger(__name__)

# percorso della risorsa -> versione (solo fuori dal debug mode)
_VERSIONS = {}


def _filesystem_path(resource):
    """Percorso su disco del file servito dalla risorsa, se c'e'."""
    # plone:static (plone.resource FilesystemFile) ha .path; browser:resource (Five) ha .context.path
    for obj in (resource, getattr(resource, "context", None)):
        path = getattr(obj, "path", None)
        if isinstance(path, str) and os.path.isfile(path):
            return path
    return None


class AssetsView(BrowserView):
    """@@assets: URL degli asset statici con la versione per il cache busting."""

    def version(self, path):
        """Data di modifica (intera) del file servito da `path`, None se non si trova."""
        debug = getConfiguration().debug_mode

        if not debug and path in _VERSIONS:
            return _VERSIONS[path]

        portal = api.portal.get()
        try:
            resource = portal.unrestrictedTraverse(path)
        except (AttributeError, KeyError, LookupError):
            resource = None

        filename = _filesystem_path(resource) if resource is not None else None
        version = int(os.path.getmtime(filename)) if filename else None

        if version is None:
            logger.warning("Asset non trovato, URL senza versione: %s", path)

        if not debug:
            _VERSIONS[path] = version

        return version

    def url(self, path):
        """URL assoluto di `path` (es. '++resource++pacchetto.css/style.css') con ?v=."""
        path = path.lstrip("/")
        url = f"{api.portal.get().absolute_url()}/{path}"
        version = self.version(path)
        return f"{url}?v={version}" if version else url
