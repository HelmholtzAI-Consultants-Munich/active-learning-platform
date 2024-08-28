from setuptools import setup, find_packages

setup(
    name="data-centric-platform-client",
    version="0.1",
    description="The client of the data centric platform for microscopy image segmentation",
    author=["Christina Bukas", 
            "Helena Pelin",
            "Mariia Koren",
            "Marie Piraud"],
    author_email= ["christina.bukas@helmholtz-munich.de",
                   "helena.pelin@helmholtz-munich.de",
                   "mariia.koren@helmholtz-munich.de",
                   "marie.piraud@helmholtz-munich.de"],
    url="https://github.com/HelmholtzAI-Consultants-Munich/data-centric-platform",
    packages=find_packages(),
    install_requires=[
        "matplotlib >=3.3",
        "napari[pyqt5]>=0.4.17",
        "segment-anything @ git+https://github.com/facebookresearch/segment-anything.git@main",
        "torch",
        "torchvision",
        "napari-sam @ git+https://github.com/christinab12/napari-sam.git@main",
        "bentoml[grpc]>=1.2.5",
        "opencv",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-qt>=4.2.0",
            "sphinx",
            "sphinx-rtd-theme",
        ]
    },
    entry_points={
        "console_scripts": [
            "dcp-client=dcp_client.main:main",
        ]
    },
    python_requires=">=3.9",
    keywords=[],  
    classifiers=[  
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    long_description=open("README.md").read(),  
    maintainer=["Christina Bukas", "Helena Pelin"], 
    maintainer_email=["christina.bukas@helmholtz-munich.de", "helena.pelin@helmholtz-munich.de"],
    project_urls={ 
        "Repository": "https://github.com/HelmholtzAI-Consultants-Munich/data-centric-platform",
        "Documentation": "https://readthedocs.org/projects/data-centric-platform",
    }
)
