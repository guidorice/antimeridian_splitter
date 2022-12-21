import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="antimeridian_splitter",
    version="0.2.0",
    author="Pawarit Laosunthara, Alex G Rice",
    author_email="alex@radiant.earth",
    description="Handling problematic real-world geometries (polygons) that cross the antimeridian (aka 180th meridian or International Date Line)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/guidorice/antimeridian_splitter",
    packages=setuptools.find_packages(),
    platforms='Platform Independent',
    install_requires=[
        'shapely~=1.7'
    ],
    classifiers=[
    ],
    project_urls={
    },
    python_requires='>=3.8',
)
