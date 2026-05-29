from setuptools import setup, find_packages

setup(
    name="slide-generator",
    version="0.1.0",
    description="Generate Google Slides-compatible .pptx from template + plan + content",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=[
        "python-pptx>=1.0.0",
        "PyYAML>=6.0",
        "Pillow>=10.0.0",
        "click>=8.1.0",
    ],
    entry_points={
        "console_scripts": [
            "slide-generator=cli:cli",
        ],
    },
)
