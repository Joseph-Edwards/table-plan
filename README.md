# table-plan

This repo contains a python script, `make_plan.py`, for constructing a community graph from a list of
people, and a list of up to three neighbours.

## How to use

The easiest way to use this script is with the help of [`uv`](https://docs.astral.sh/uv/):

```
uv run --script make_plan.py path/to/input.csv
```

This will run the script in an environment with the correct dependencies. It is also possible to run
the script without `uv`, (e.g. with `python make_plan.py`) but that requires creating an environment
with the required dependencies (see below).

## Dependencies

The script in this project requires:

- `matplotlib`
- `netgraph`
- `networkx`
- `pandas`

## Arguments and optional parameters

```
usage: TablePlanner [-h] [--image-output IMAGE_OUTPUT] [--community-output COMMUNITY_OUTPUT] filename

A basic script that outputs a nice table plan.

positional arguments:
  filename              The path to the csv file containing the table plan data. This csv file
                        must have eight columns in the order: name, email, preference one name,
                        preference one email, preference two name, preference two email,
                        preference three name, preference three email.

options:
  -h, --help            show this help message and exit
  --image-output IMAGE_OUTPUT
                        A path to a directory to store the community plots.
  --community-output COMMUNITY_OUTPUT
                        A path to a file to store the communities as text.
```

## Output

Depending on the parameters specified, the script will either display or write a community
graph partitioned by the preferences specified in the input csv file. Additionally, it will either
print or write the list of calculated partitions.
