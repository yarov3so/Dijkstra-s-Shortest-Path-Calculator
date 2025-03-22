import streamlit as st
import pandas as pd
import copy

def comprehend(mystring):
    mystring = mystring.replace(" ", "")
    data_list = mystring.split(",")
    return data_list

def try_int(num):
    
    num_int=None
    try:
        num_int=int(num)
    except:
        return num
    if num==num_int:
        return num_int
    elif (num<=0.1 and num>=0) or (num>=-0.1 and num<=0):
        return "{:.2g}".format(float(num))
    else:
        return round(float(num),2)

def undirected(graph):
    undirected_graph = copy.deepcopy(graph)
    for node_1 in graph:
        for node_2 in graph[node_1]:
            if node_2 in undirected_graph:
                if node_1 in graph[node_2]:
                    undirected_graph[node_2][node_1] = min(graph[node_2][node_1],graph[node_1][node_2])
                else:
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
    return pd.DataFrame(dist).T.sort_values(by=["curr"],ascending=True).rename(columns={"curr": f"Distance from \"{start}\"", "prevnode": "Previous Node"})

def make_graph():
    st.text("")
    st.markdown("##### Graph Initialization")
    nodes_str = st.text_input(" Enter all the nodes in the graph, separated by commas:", key="nodes")
    if nodes_str=="":
        st.stop()
    graph = {}

    if nodes_str:
        nodes = comprehend(nodes_str)
        for node in nodes:
            nbrs_node_str = st.text_input(f" Enter all the neighbours of \"{node}\", separated by commas (enter a single backspace to skip):", key=f"nbrs_{node}")
            if nbrs_node_str=="":
                st.stop()
            elif all(c == ' ' for c in nbrs_node_str) and len(nbrs_node_str) > 0:
                graph[node] = {}
            else:
                nbrs_node = comprehend(nbrs_node_str)
                graph[node] = {}
                for nbr in nbrs_node:
                    dist_val = st.text_input(f" Enter the single-edge distance between \"{node}\" and \"{nbr}\":", key=f"dist_{node}_{nbr}")
                    if dist_val=="":
                        st.stop()
                    if dist_val:
                        try:
                            if float(dist_val)<0:
                                st.warning("Only positive single-edge distances are allowed!")
                                st.stop()
                            graph[node][nbr] = float(dist_val)
                        except:
                            st.warning(f" Invalid distance for {node} -> {nbr}. Please enter a numeric value.")
                            st.stop()

        undirected_yn = st.text_input("Make the graph undirected? (yes/no):", key="undirected")
        if undirected_yn.lower() == "yes":
            graph = undirected(graph)
        elif undirected_yn.lower() == "no":
            pass
        elif undirected_yn.lower() == "":
            st.stop()
        else:
            st.warning("Invalid response!")
            st.stop()
            

    return graph

def dijkstra():

    st.markdown("This tool is a straightforward implementation of Dijkstra's algorithm for finding the shortest path from a node to any other node in a connected graph. Designed primarily as a learning tool, it focuses on clarity and simplicity to help students and beginners understand the core concepts behind the algorithm.")
    
    graph=make_graph()
    
    if not graph:
        st.warning("Graph is empty! Please input your graph.")
        st.stop()
        return
    st.text("")
    st.markdown("##### Registered Graph:")
    st.json(graph)
    st.text("")

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

    st.text("")
    st.markdown(f"##### Step-by-Step Breakdown of Dijkstra's Algorithm")
    st.text("")
    st.markdown(f"Initial unexplored nodes: {set(dist_unexp.keys())}")
    st.markdown(f"Current distances from \"{start_node}\" : ")
    st.dataframe(df(dist, start_node))

    del dist_unexp[current]

    while len(dist_unexp) != 0:
        st.text("")
        st.markdown(f"##### Exploring node: &nbsp; \"{current}\"")

        for node in set(graph[current]).intersection(set(dist_unexp.keys())):
            
            dist_through_current = graph[current][node] + dist[current]["curr"]

            if dist_through_current < dist[node]["curr"]:
                st.markdown(f"- Updating the distance of \"{node}\" from \"{start_node}\" : &nbsp; {try_int(dist[node]['curr'])} -> {try_int(dist[current]["curr"])} + {try_int(graph[current][node])} = {try_int(dist_through_current)} ")
                st.markdown(f"- Setting the previous node of \"{node}\" to \"{current}\" : &nbsp; \"{dist[node]["prevnode"]}\" -> \"{current}\" ")
                dist[node]["curr"] = dist_through_current
                dist_unexp[node]["curr"] = dist_through_current
                dist[node]["prevnode"] = current
                dist_unexp[node]["prevnode"] = dist_through_current

        st.markdown("The current distance table becomes:")
        st.dataframe(df(dist, start_node))

        st.markdown(f"- Marking \"{current}\" as explored")
        st.markdown(f"- Unexplored nodes: {set(dist_unexp.keys())}")
        
        current = sd_node(dist_unexp)
        st.markdown(f"From the unexplored nodes listed above, we select a node with the lowest current distance from \"{start_node}\" : &nbsp; \"{current}\" ")
        
        del dist_unexp[current]

    st.markdown("The distance table does not change when exploring the last remaining node, as it has no unexplored neighbours.")
    st.markdown("##### Final distance table:")
    st.dataframe(df(dist, start_node))

    st.text("")
    st.markdown(f"You can now view the shortest paths from \"{start_node}\" to other nodes.")
    end_node = st.text_input("Enter destination node to see the shortest path:", key="destination_node")

    if end_node=="":
        st.text("")
        st.markdown("""*Crafted by yarov3so*   
<a href="https://www.buymeacoffee.com/yarov3so" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="width: 9em; height: auto; padding-top: 0.7em; padding-bottom: 1em" ></a>  
See my other [Math Help Tools](https://mathh3lptools.streamlit.app)""",unsafe_allow_html=True)
        st.stop()
    if end_node not in dist:
        st.warning("Destination node not found in graph!")
        st.text("")
        st.markdown("""*Crafted by yarov3so*   
<a href="https://www.buymeacoffee.com/yarov3so" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="width: 9em; height: auto; padding-top: 0.7em; padding-bottom: 1em" ></a>  
See my other [Math Help Tools](https://mathh3lptools.streamlit.app)""",unsafe_allow_html=True)
        st.stop()
    else:
        path = shortest_path(dist, end_node)
        st.markdown(f"Shortest path from \"{start_node}\" to \"{end_node}\" : &nbsp; {path}")

        st.text("")
        st.markdown("""*Crafted by yarov3so*   
        <a href="https://www.buymeacoffee.com/yarov3so" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="width: 9em; height: auto; padding-top: 0.7em; padding-bottom: 1em" ></a>  
        See my other [Math Help Tools](https://mathh3lptools.streamlit.app)""",unsafe_allow_html=True)

    return None

st.title("Dijkstra's Shortest Path Calculator")

dijkstra()

