import setuptools

with open("README.md", "r") as readme_file:
    long_description = readme_file.read()

setuptools.setup(
    name = "HTSDS_GEE",
    version = "0.0.1",
    author = "Yongjing Mao",
    author_email = "maomao940405@gmail.com",
    description = "A GEE based python package to derive shoreline position at high tide",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://bitbucket.csiro.au/projects/DIG/repos/optical_sar_blending",
    package_dir = {"": "algorithms\HTSDS_GEE"},
    packages = setuptools.find_packages(include=["HTSDS_GEES", "HTSDS_GEE.*"]),
    python_requires = ">=3.7",
    install_requires = [
		"pandas == 1.1.0"
        "earthengine-api == 0.1.270"
        "geojson == 2.5.0"
    ]
)