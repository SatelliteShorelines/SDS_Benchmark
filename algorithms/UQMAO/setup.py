import setuptools

with open("README.md", "r") as readme_file:
    long_description = readme_file.read()

setuptools.setup(
    name = "HT-SDS",
    version = "0.0.1",
    author = "Yongjing Mao",
    author_email = "maomao940405@gmail.com",
    description = "A GEE based python package to derive shoreline position at high tide",
    package_dir = {"": "submissions\team_UQMAO"},
    packages = setuptools.find_packages(),
    python_requires = ">=3.7",
    install_requires = [
	"pandas == 1.1.0"
        "earthengine-api == 0.1.270"
        "geojson == 2.5.0"
    ]
)
