from setuptools import setup, find_namespace_packages

setup(
    name = "generate_plone_addon",
    version = "0.9.2",
    description = "Generator per addon Plone",
    long_description = "",
    packages = find_namespace_packages(where = "src"),
    package_dir = {"": "src"},
    include_package_data = True,
    install_requires = [
        "setuptools",
    ],
    entry_points = {
        "console_scripts": [
            "generate_plone_addon=generate_plone_addon.generator:main",
        ],
    },
)
