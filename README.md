# table-plan

This repo contains a python script, `make_plan.py` for constructing a community graph from a list of
people, and a list of up to three neighbours.

## How to use

The easiest way to use this script is with the help of [`uv`](https://docs.astral.sh/uv/):

```
uv run --script make_plan.py path/to/input.csv
```

This will run the script in an environment with the correct dependencies. It is also possible to run
the script without `uv`, but that requires creating an environment with the required dependencies
(see below).

## Dependencies

The script in this project requires:

- `matplotlib`
- `netgraph`
- `networkx`
- `pandas`

## Arguments and optional parameters

**positional arguments:**
filename The path to the csv file containing the table plan data.

**options:**
-h, --help show this help message and exit
--image-output IMAGE_OUTPUT
A path to a directory to store the community plots
--community-output COMMUNITY_OUTPUT
A path to a file to store the communities as text
