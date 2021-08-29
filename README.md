![aiotnb-icon](https://user-images.githubusercontent.com/3061779/124573615-4cc19c80-de7c-11eb-9705-951287866a15.png)

# aiotnb

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Code Style & Typing QA](https://github.com/AnonymousDapper/aiotnb/actions/workflows/main.yml/badge.svg)](https://github.com/AnonymousDapper/aiotnb/actions/workflows/main.yml)


A coroutine-based client for the TNB Network API


## Contributing

We welcome contributions, but please make sure your code is formatted properly.

Linting is handled by `black`, and imports are sorted according to `isort`.
Utilize `pre-commit` to lint and format before committing your contributions. This will save you time later.

Any public interfaces should be fully-typed (this is checked by `pyright`).

To run tests, execute `pytest` in the root of this repository.

To install within your development environment, use either;
`pip install -e .` or `python setup.py develop`

# Installation
Using `git-clone` and `pip`
`git clone https://github.com/AnonymousDapper/aiotnb && cd aiotnb`

Checkout this branch:
`git checkout bank-api`

## Install the requirements

Developer: `pip install -e .`

Regular: `python setup.py install`

### Installing using `git`+`pip`:
`pip install git+git://github.com/AnonymousDapper/aiotnb@bank-api`
