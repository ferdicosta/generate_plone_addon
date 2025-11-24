from setuptools import setup, find_packages

setup(
    name = "generate_plone_addon",
    version = "0.3.4",
    description = "Generator per addon Plone",
    long_description = "",
    packages = find_packages(where = "src"),
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
