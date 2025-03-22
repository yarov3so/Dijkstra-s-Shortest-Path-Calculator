import streamlit as st
import pandas as pd
import copy

def comprehend(mystring):
    mystring = mystring.replace(" ", "")
    data_list = mystring.split(",")
    return data_list

def undirected(graph):
    undirected_graph = copy.deepcopy(graph)
    for node_1 in graph:
        for node_2 in graph[node_1]:
            if node_2 in undirected_graph:
                undirected_graph[node_2][node_1] = graph[node_1][node_2]
            else:
                undirected_graph[node_2] = {}
                undirected_graph[node_2][node_1] = graph[node_1][node_2]
    return undirected_graph

def shortest_path(dist, end):
    current = end
    path = [current]
    while dist[current]["prevnode"] != None:
        path.append(dist[current]["prevnode"])
        current = dist[current]["prevnode"]
    return path[::-1]

def sd_node(dict):
    dist_set = set([dict[key]['curr'] for key in dict])
    min_dist = min(dist_set)
    for key in dict:
        if dict[key]['curr'] == min_dist:
            return key

def df(dist, start):
    return pd.DataFrame(dist).T.rename(columns={"curr": f"Distance from \"{start}\"", "prevnode": "Previous Node"})

def make_graph():
    st.markdown("### Enter your graph nodes")
    nodes_str = st.text_input(" Enter all the nodes in the graph, separated by commas:", key="nodes")
    graph = {}

    if nodes_str:
        nodes = comprehend(nodes_str)
        for node in nodes:
            nbrs_node_str = st.text_input(f" Enter all the neighbours of \"{node}\" separated by commas:", key=f"nbrs_{node}")

            if nbrs_node_str:
                nbrs_node = comprehend(nbrs_node_str)
                graph[node] = {}

                for nbr in nbrs_node:
                    dist_val = st.text_input(f" Distance between \"{node}\" and \"{nbr}\":", key=f"dist_{node}_{nbr}")
                    if dist_val:
                        try:
                            graph[node][nbr] = float(dist_val)
                        except ValueError:
                            st.warning(f" Invalid distance for {node} -> {nbr}. Please enter a numeric value.")

        undirected_yn = st.text_input("Make the graph undirected? (yes/no):", key="undirected")
        if undirected_yn.lower() == "yes":
            graph = undirected(graph)

    return graph

def dijkstra():

    graph=make_graph()
    
    if not graph:
        st.warning("Graph is empty! Please input your graph.")
        st.stop()
        return

    st.markdown("### Registered Graph:")
    st.json(graph)

    start_node = st.text_input("Enter the starting node:", key="start_node")
    
    if start_node=="":
        st.stop()

    if start_node not in graph:
        st.warning("Starting node must be in the graph nodes!")
        st.stop()
        return

    dist = {}
    for node in graph:
        dist[node] = {"curr": float("inf"), "prevnode": None}

    dist[start_node]["curr"] = 0
    dist[start_node]["prevnode"] = None

    dist_unexp = copy.deepcopy(dist)
    current = sd_node(dist_unexp)

    st.markdown(f"### Initial unexplored nodes: {set(dist_unexp.keys())}")
    st.dataframe(df(dist, start_node))

    del dist_unexp[current]

    while len(dist_unexp) != 0:
        st.markdown(f"### Exploring node: {current}")

        for node in set(graph[current]).intersection(set(dist_unexp.keys())):
            dist_through_current = graph[current][node] + dist[current]["curr"]

            if dist_through_current < dist[node]["curr"]:
                st.markdown(f"- Updating distance of \"{node}\" from {dist[node]['curr']} -> {dist_through_current}")
                st.markdown(f"- Setting previous node of \"{node}\" to \"{current}\"")
                dist[node]["curr"] = dist_through_current
                dist[node]["prevnode"] = current

        st.markdown("### Updated distance table:")
        st.dataframe(df(dist, start_node))

        st.markdown(f"- Marking \"{current}\" as explored.")
        st.markdown(f"- Unexplored nodes: {set(dist_unexp.keys())}")

        current = sd_node(dist_unexp)
        del dist_unexp[current]

    st.markdown("### Final distance table:")
    st.dataframe(df(dist, start_node))

    st.markdown(f"You can now view the shortest paths from \"{start_node}\" to other nodes.")
    end_node = st.text_input("Enter destination node to see the shortest path:", key="destination_node")

    if end_node:
        if end_node not in dist:
            st.warning("Destination node not found in graph!")
            st.stop()
        else:
            path = shortest_path(dist, end_node)
            st.markdown(f"### Shortest path from \"{start_node}\" to \"{end_node}\": {path}")

    return df(dist, start_node)

st.title("Dijkstra's Shortest Path Calculator")

dijkstra()

