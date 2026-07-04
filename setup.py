from setuptools import setup, find_packages
setup(
    name="feom-mcp",
    version="0.1.0",
    description="OS-native Windows GUI automation MCP server. Zero GPU, zero API tokens.",
    long_description=open("README.md").read() if __import__("os").path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    packages=find_packages(),
    py_modules=["server"],
    install_requires=["pywinauto>=0.6.8","pywin32>=310","mcp>=1.26.0"],
    python_requires=">=3.10",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Topic :: System :: Automation",
    ],
)
