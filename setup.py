import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="caddypy",
    version="1.0.0",
    author="Anuj Sharma",
    author_email="anujsharma9196@gmail.com",
    description="Python library for the Caddy server",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/anuj9196/caddypy",
    packages=setuptools.find_packages(),
    keywords=[
        'caddy', 'caddypy', 'caddy python', 'caddy server', 'python caddy server', 'caddy server python'
    ],
    install_requires=[
        'requests',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
