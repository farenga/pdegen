import setuptools


setuptools.setup(
    name="pdegen",
    version="0.0.5",
    author="Nicola Farenga",
    author_email="nicola.farenga@mail.polimi.it",
    description="Partial Differential Equations Dataset Generation Library",
    url="https://github.com/farenga/pdegen",
    packages=setuptools.find_packages(),
    install_requires=[
    'numpy>=1.21.5',
    'PyYAML>=6.0',
    'torch>=1.13.1',
    'vtk>=9.2.6'
    ],
    python_requires='~=3.7',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ]
)