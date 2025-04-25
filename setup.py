from setuptools import setup, find_packages

setup(
    name="nikke-automation",
    version="0.1.0",
    description="Automation framework for NIKKE: Goddess of Victory",
    author="AI Assistant",
    packages=find_packages(),
    install_requires=[
        "opencv-python>=4.5.5.64",
        "numpy>=1.22.3",
        "PyAutoGUI>=0.9.53",
        "Pillow>=9.1.0",
        "pytest>=7.0.1",
        "pytest-cov>=3.0.0",
        "pyyaml>=6.0",
        "pytesseract>=0.3.9",
    ],
    python_requires=">=3.10",
)
