from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api

from plone.app.layout.viewlets.common import ViewletBase


class MainNav(ViewletBase):
    index = ViewPageTemplateFile('viewlets/main_nav.pt')

    def get_nav(self):
        catalog = api.portal.get_tool("portal_catalog")

        root = api.portal.get_navigation_root(self.context)

        folder_path = '/'.join(root.getPhysicalPath())

        results = []

        parents_brains = catalog(
            path = {'query': folder_path, 'depth': 1},
            portal_type = ["Document", "Folder"],
            exclude_from_nav = False,
            sort_on = 'getObjPositionInParent'
        )

        for parent in parents_brains:
            parent_tmp = {
                'title': parent.Title,
                'URL': parent.getURL(),
                'childs': []
            }

            parent_path = parent.getPath()

            childs_brains = catalog(
                path = {"query": parent_path, "depth": 1},
                sort_on = 'getObjPositionInParent',
                exclude_from_nav = False,
            )

            for child in childs_brains:
                child_tmp = {
                    'title': child.Title,
                    'URL': child.getURL()
                }

                parent_tmp['childs'].append(child_tmp)

            results.append(parent_tmp)

        return results


class Footer(ViewletBase):
    index = ViewPageTemplateFile("viewlets/footer.pt")
