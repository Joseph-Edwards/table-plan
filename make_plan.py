#!/usr/bin/env python3
#
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "matplotlib",
#     "netgraph",
#     "networkx",
#     "pandas",
# ]
# ///

import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import netgraph as ng

import argparse

# =============================================================================
# User arguments
# =============================================================================

parser = argparse.ArgumentParser(
    prog="TablePlanner",
    description="A basic script that outputs a nice table plan.",
)

parser.add_argument(
    "filename",
    type=str,
    help="The path to the csv file containing the table plan data.",
)

parser.add_argument(
    "--image-output",
    type=str,
    required=False,
    help="A path to a directory to store the community plots",
)

parser.add_argument(
    "--community-output",
    type=str,
    required=False,
    help="A path to a file to store the communities as text",
)
args = parser.parse_args()

file = args.filename

plt.rcParams["figure.dpi"] = 300


# =============================================================================
#  Helper functions
# =============================================================================


def format_email(x):
    "Get the username from an email"
    if pd.isna(x):
        return x
    return (x.split("@")[0]).lower().strip()


def make_nbs(row):
    "Extract the non-null values from a row"
    return [value for value in row if not pd.isnull(value)]


def len_lex(u):
    return (len(u), sorted(list(u)))


def make_com_plot(G, ax=None, res=1):
    "Make a community plot from a graph with a given resolution"
    if ax is None:
        _, ax = plt.subplots(1)
    # Partition G into communities (higher res means more communities)
    partition = nx.community.louvain_communities(G, resolution=res, threshold=0.0000001)

    partition.sort(key=lambda u: sorted(u))

    # Number of communities
    n_coms = len(partition)

    # Map the numbers 0, 1, ..., n_coms to a community
    com_to_node = {i: list(com) for i, com in enumerate(partition)}

    # Map each node to a number 0, 1, ..., n_coms to represent its community
    node_to_community = {
        node: com for com, nodes in com_to_node.items() for node in nodes
    }

    # colour the nodes according to their community
    cmap = plt.get_cmap("hsv")
    cmap = [cmap(i / max(n_coms - 1, 1)) for i in range(n_coms)]
    community_to_color = {
        com: list(col) for com, col in zip(set(node_to_community.values()), cmap)
    }
    node_color = {
        node: community_to_color[community_id]
        for node, community_id in node_to_community.items()
    }

    # G = nx.Graph(G)

    # Plot the graph
    tmp = ng.InteractiveGraph(
        G,
        node_layout="community",
        node_layout_kwargs={"node_to_community": node_to_community},
        node_size=3,
        node_edge_width=0.1,
        node_color=node_color,
        node_labels=True,
        node_label_fontdict={"size": 7},
        edge_width=0.5,
        edge_alpha=0.7,
        edge_layout="bundled",
        edge_layout_kwargs=dict(k=2000),
        prettify=True,
        # ax=ax,
        scale=(1.8, 1),
    )
    return partition, node_color


def plot_sub(G, node_set, col):
    "Plot a subgraph of a graph"
    S = G.subgraph(node_set)
    edge_to_weight = {(u, v): w["weight"] for u, v, w in S.edges.data()}
    ng.Graph(
        S,
        node_layout="spring",
        node_layout_kwargs={"edge_weights": edge_to_weight},
        node_size=3,
        node_edge_width=0.1,
        node_color=col,
        node_labels=True,
        node_label_fontdict={"size": 7},
        edge_width=0.5,
        edge_alpha=0.7,
        edge_layout="bundled",
        prettify=True,
    )


# =============================================================================
#  Import the data
# =============================================================================

col_names = [
    "name",
    "user",
    "name_1",
    "username_1",
    "name_2",
    "username_2",
    "name_3",
    "username_3",
]
df = pd.read_csv(
    file,
    index_col=None,
    header=0,
    names=col_names,
)

# Use the username of the guests as a unique id
guests = set(df["user"].map(format_email))


# =============================================================================
#  Clean and wrangle the data
# =============================================================================

# Get the columns of just usernames
user_cols = ["user", "username_1", "username_2", "username_3"]
df[user_cols] = df[user_cols].map(format_email)

# View duplicates.
muliple_response = df[df.duplicated(subset=["name"], keep=False)]
if not muliple_response.empty:
    print("The following people submitted multiple responses")
    muliple_response

# Keep the last version of the duplicates
# May need to change this if it isn't the desired behaviour
df.drop_duplicates(subset=["name"], keep="last", inplace=True, ignore_index=True)

# Make user the index
df.set_index("user", inplace=True)
user_cols.remove("user")

# For each column of potential guests, check that "the person I would like to
# sit next to" is actually going to the meal
for col in user_cols:
    if not all(
        potential_guest in guests
        for potential_guest in df[col]
        if not pd.isnull(potential_guest)
    ):
        raise ValueError(
            f"The following people appear in column {col} but don't appear to have a ticket:\n"
            + str(
                set(
                    guest
                    for guest in df[col]
                    if guest not in guests and not pd.isnull(guest)
                )
            )
            + "\nPlease check the csv file, and run the script again",
        )


# =============================================================================
#  Make the graph
# =============================================================================

# Create a column to represent all neighbours
df["nbs"] = df.filter(["username_1", "username_2", "username_3"]).apply(
    make_nbs, axis=1
)

# Make this column a dictionary
d = dict(df["nbs"])

#  Construct all edges
edges = [(u, v) for u, nbs in d.items() for v in nbs]

# There are 4 different graphs:
#   * Normal graph
#   * Directed graph
#   * Weighted graph
#   * Multigraph
#
# Uncomment the graph type you want to use in the final algorithm. All give
# similar, but slightly different behaviour. Experiment and see what works best
# for you.

# G = nx.Graph()
# G.add_nodes_from(guests)
# G.add_edges_from(edges)

# D = nx.DiGraph()
# D.add_nodes_from(guests)
# D.add_edges_from(edges)

weighted_graph = nx.Graph()
weighted_graph.add_nodes_from(guests)
weighted_graph.add_weighted_edges_from([(u, v, 0) for u, v in edges])

for guest in guests:
    for pos, nb in enumerate(d[guest]):
        weighted_graph[guest][nb]["weight"] += 1 / (2 + 2 * pos)

# M = nx.MultiGraph()
# M.add_nodes_from(guests)
# M.add_edges_from(edges)


# =============================================================================
#  Make the plots
# =============================================================================

fig, axes = plt.subplots(1)

# Uncomment whichever of these that uses the graph you defined above:

# pD = make_com_plot(D, axes)
# axes.set_title(f"Digraph: {len(pD[0])} communities")

# pM = make_com_plot(M, axes)
# axes.set_title(f"Multigraph: {len(pM[0])} communities")

# pwG = make_com_plot(wG, axes)
# axes.set_title(f"Weighted Graph: {len(pwG[0])} communities")

# pG = make_com_plot(nx.Graph(G), axes)
# axes.set_title(f"Graph: {len(pG[0])} communities")

partition_weighted_graph, colours = make_com_plot(weighted_graph, axes, res=1.5)
axes.set_title(f"Weighted Graph: {len(partition_weighted_graph)} communities")

if args.image_output:
    plt.savefig(f"{args.image_output}/full_community.png")
    plt.clf()
else:
    plt.show()


partition_weighted_graph.sort(key=len_lex, reverse=True)
for i, s in enumerate(partition_weighted_graph):
    plot_sub(weighted_graph, s, colours)
    if args.image_output:
        plt.savefig(f"{args.image_output}/community_{i}.png")
        plt.clf()
    else:
        plt.show()

if args.community_output:
    with open(args.community_output, "w") as f:
        for part in partition_weighted_graph:
            f.write(f"{part}\n")
else:
    print(*partition_weighted_graph, sep="\n")
