from setuptools import setup, find_packages

setup(
    name="GLFS",
    version="1.0.0",
    description="Minecraft Bedrock Shader Loader using BetterRenderDragon and MaterialBin",
    author="GLFS Team",
    packages=find_packages(),
    install_requires=[
        "pillow>=9.0.0",
    ],
    entry_points={
        'console_scripts': [
            'glfs=src.main:main',
        ],
    },
    python_requires='>=3.7',
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
    ],
)
