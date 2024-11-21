from setuptools import setup, find_packages

setup(
    name="PyRth",
    version="0.1.0",
    author="Nils Ziegeler",
    author_email="nils@example.com",
    description="A tool for thermal transient analysis",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.26.0,<2.0.0",
        "scipy>=1.11.0,<2.0.0",
        "matplotlib>=3.8.0,<4.0.0",
        "numba>=0.59.0,<1.0.0",
        "gmpy2>=2.1.2,<3.0.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
