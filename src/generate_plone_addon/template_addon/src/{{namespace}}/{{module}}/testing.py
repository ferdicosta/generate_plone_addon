# -*- coding: utf-8 -*-
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import {{package_name}}


class {{package_layer}}Layer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import plone.app.dexterity

        self.loadZCML(package=plone.app.dexterity)
        import plone.restapi

        self.loadZCML(package=plone.restapi)
        self.loadZCML(package={{package_name}})

    def setUp{{package_layer}}(self, portal):
        applyProfile(portal, "{{package_name}}:default")


{{package_layer_uppercase}}_FIXTURE = {{package_layer}}Layer()


{{package_layer_uppercase}}_INTEGRATION_TESTING = IntegrationTesting(
    bases=({{package_layer_uppercase}}_FIXTURE,),
    name="{{package_layer}}Layer:IntegrationTesting",
)


{{package_layer_uppercase}}_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=({{package_layer_uppercase}}_FIXTURE,),
    name="{{package_layer}}Layer:FunctionalTesting",
)


{{package_layer_uppercase}}_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        {{package_layer_uppercase}}_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name="{{package_layer}}Layer:AcceptanceTesting",
)
