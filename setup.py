import setuptools


setuptools.setup(
    name="pdegen",
    version="0.0.1",
    author="Nicola Farenga",
    author_email="nicola.farenga@mail.polimi.it",
    description="Partial Differential Equations Dataset Generation Library",
    url="https://github.com/farenga/pdegen",
    packages=setuptools.find_packages(),
    install_requires=['fenics>=2018.1.0','torch>=1.5.0', 'numpy>=1.21.0'],
    python_requires='~=3.7',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ]
)