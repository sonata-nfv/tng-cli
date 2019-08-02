[![Join the chat at https://gitter.im/sonata-nfv/Lobby](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/sonata-nfv/Lobby)
[![Documentation Status](https://readthedocs.org/projects/tng-cli/badge/?version=latest)](https://tng-cli.readthedocs.io/en/latest/index.html)
<p align="center"><img src="https://github.com/sonata-nfv/tng-api-gtw/wiki/images/sonata-5gtango-logo-500px.png" /></p>

# tng-cli

This repository contains two python3 packages:

* `tnglib` is a library with functions that help a 5GTANGO user interface with the 5GTANGO Service Platform or V&V
* `tngcli` wraps the `tnglib` library in a CLI-tool

## Installation

To install both packages manually, with permissions:

```
git clone https://github.com/sonata-nfv/tng-cli.git
cd tng-cli
python3 setup.py install
```
Automated installation using pip3, with permissions:

```
pip3 install git+https://github.com/sonata-nfv/tng-cli
```

## Usage

To use the library, add `import tnglib` to your python script. Documentation on all supported function calls can be found [here](https://tng-cli.readthedocs.io/en/latest/index.html)

To use the CLI-tool, see its help for detailed information about all the arguments:

```
tng-cli -h
```

The tool supports a set of subcommands. For there usage, so the local subcommand help:

```
tng-cli <subcommand> -h
```

The tool needs to know which 5GTANGO Service Platform or V&V you want to interface with. For this, you should use the `-u` argument:

```
tng-cli -u <URL_TO_SP> package --list
```

As it is cumbersome to have to specify this argument for every command, you can make it available through the `SP_PATH` env parameter:

```
export SP_PATH=<URL_TO_SP>
```

It will than persist troughout your terminal session.

### Examples

Some examples on how to use the CLI-tool.

To obtain a list of all available packages:

```
tng-cli package --list
```

To obtain a list of all running network services:

```
tng-cli service --instance
```

To instantiate a new network service:

```
tng-cli service --instantiate <SERVICE_UUID>
```

To upload a new policy descriptor:

```
tng-cli policy --create <PATH_TO_DESCRIPTOR>
```

## License

This 5GTANGO component is published under Apache 2.0 license. Please see the LICENSE file for more details.

---
#### Lead Developers

The following lead developers are responsible for this repository and have admin rights. They can, for example, merge pull requests.

- Thomas Soenen ([@tsoenen](https://github.com/tsoenen))

#### Feedback-Channel

* Please use the GitHub issues to report bugs.
