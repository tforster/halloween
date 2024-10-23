# C4 Builder <!-- omit in toc -->

A Drag-n-Drop builder for C4 diagrams.

## Table of Contents <!-- omit in toc -->

- [Getting Started](#getting-started)
  - [Local Prerequisites](#local-prerequisites)
  - [Installing local dependencies](#installing-local-dependencies)
- [Usage](#usage)
- [High Level Architecture Overview](#high-level-architecture-overview)
- [JET Policies](#jet-policies)
- [Authors](#authors)
- [License](#license)

## Getting Started

These instructions will give you a copy of the project up and running on your local machine for development and testing purposes.

### Local Prerequisites

Requirements for the software and other tools to build, test and push. Note the versions were current at the time of writing. Later versions should work but YMMV.

- [Cloudflare Wrangler 3.22.1](https://github.com/cloudflare/workers-sdk): Wrangler is Cloudflare's CLI. It is referenced in package.json and will be automatically installed on `git install`. _Note that we prefer to run CLIs in containers but Cloudflare does not yet offer a Wrangler Docker image, hence the need to install as a project dependency._
- [Docker Desktop 4.19.0](https://www.docker.com/products/docker-desktop/): Required to run several utilities without clouding the local workstation with unnecessary files.
- [Doppler 3.67.0](https://docs.doppler.com/docs/install-cli): We use Doppler to manage secrets. Note that Doppler is included in the Dev container.
- [Git v2.34.1](https://git-scm.com/): JET's Source Control protocol.
- [Node v21.6.2 and NPM v10.2.4](https://nodejs.org/): Underlying tooling provider.

### Installing local dependencies

1. Clone this repository `git clone git@ssh.dev.azure.com:v3/techsmarts/7Cats/C4Builder`
2. `cd` into the new directory and install all dependencies `npm install`
3. Log in to Doppler `doppler login`
4. Ensure Doppler is configured for the project with `doppler setup`.

## Usage

Powershell
usbipd attach --wsl --busid 1-4

Linux
/home/tforster/.local/bin/ampy --port /dev/ttyUSB0 run boot.py

## High Level Architecture Overview

This repo, the data, code and build scripts will create a very lean set of web assets intended to be deployed to a static web server provided by [Cloudflare Pages](https://pages.cloudflare.com/). No server-side language is required as there is no server-side processing. Everything is handled in the web client.

Dynamic actions to store and retrieve data are implemented using [Cloudflare Workers](https://developers.cloudflare.com/workers/).

Building a new site on a local machine typically takes well under one second which makes the edit-and-preview, and build-for-deployment steps quick and easy.

The building of the webapp leverages an open source highly performant and serverless-ready text file compiler called Gilbert, fka WebProducer. It is streams based, merging an incoming data stream with a stream of templates to create a stream of output files. While skewed towards web files it can handle any text file type with the appropriate templates. Gilbert is wrapped in a Javascript file, coincidentally called gilbert.js and can be run from the command line as `nodejs gilbert.js`. Step-through debugging is also available for VSCode by selecting the gilbert debug profile and pressing [F5].

Gilbert.js converts the stream of json data, representing the raw data, into an array of Gilbert friendly URIs by utilising a custom data transformation class found in `transform.js`. This transformer implements a transformation stream to be as fast and memory efficient as possible. The transformer (and by extension gilbert.js and Gilbert) adhere to the Joy philosophy of lean architecture with no frameworks, and minimal libraries and dependencies. The transformer does leverage the following dev dependency due to its specialisation and 1000's of hours of iteration.

- **[Vinyl](https://github.com/gulpjs/vinyl)**: The vinyl library is used to quickly support reading and writing streams of files on the local filesystem. As this library is ageing and has some minor security flaws† we may create our own replacement in the future.

† Remember that all Gilbert processing takes place on the developers workstation. None of the Gilbert infrastructure is required nor deployed to the servers. Any minor security flaws in a library such as Vinyl are constrained to the developers workstation.

For greater technical detail please consult the developer guide in [docs/developer-guide.md](./docs/developer-guide.md)

## JET Policies

While this is a closed source and private project both current and future team members should still observe our policies on contribution, code of conduct and versioning.

- [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.
- [Code of Conduct](./CODE_OF_CONDUCT.md) to learn more about how we foster an open and welcoming environment.
- [Semantic Versioning](http://semver.org/). We use Semantic versioning. A [CHANGELOG.md](./CHANGELOG.md) can be found in this repo as well as all commits, which are tagged using SemVer.

## Authors

This product is being created by Jake, Erika and Troy from Seven Cats Productions

- **Jake Edwards** - _did something_
- **Erika Maginn** - _Also did something_
- **Troy Forster** - _Did something else_

## License

This project is private to Seven Cats and unlicensed.
