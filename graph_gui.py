import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
import time
import os
from PIL import Image, ImageTk

class GraphVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Shortest Path Visualizer")
        self.root.geometry("1600x1000")
        self.root.configure(bg="#faf3eb")  # Light aesthetic brown
        
        # Style Configuration
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure(".", background="#faf3eb", foreground="#5a4a42")
        self.style.configure("TFrame", background="#faf3eb") 
        self.style.configure("TLabel", background="#faf3eb", foreground="#5a4a42", 
                   font=("Arial", 13))
        self.style.configure("TButton", font=("Arial", 13), padding=8,  # Increased font size
                   background="#a78a7f", foreground="#ffffff")
        self.style.map("TButton", 
              background=[("active", "#8a7166")],
              foreground=[("active", "white")])
        self.style.configure("Title.TLabel", font=("Arial", 18, "bold"))
        
        # Create main frames
        self.header_frame = ttk.Frame(root, padding="15")
        self.header_frame.pack(fill=tk.X)
        
        self.graph_frame = ttk.Frame(root)
        self.graph_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        self.control_frame = ttk.Frame(root, padding="15")
        self.control_frame.pack(fill=tk.X)
        
        self.results_frame = ttk.Frame(root, padding="15")
        self.results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        ttk.Label(self.header_frame, text="Shortest Path Visualizer", 
                 style="Title.TLabel").pack()
        
        # Graph display frames (side by side)
        self.original_frame = ttk.LabelFrame(self.graph_frame, text="Original Graph", 
                                           padding="15")
        self.original_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        self.animated_frame = ttk.LabelFrame(self.graph_frame, text="Shortest Path Animation", 
                                           padding="15")
        self.animated_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Add separate labels for frame titles with larger font
        ttk.Label(self.original_frame, text="Original Graph", 
                 font=("Arial", 12)).pack()
        ttk.Label(self.animated_frame, text="Shortest Path Animation",
                 font=("Arial", 12)).pack()
        
        # Original graph
        self.original_fig = plt.figure(figsize=(8, 6), dpi=100, facecolor="#f9f1e9")
        self.original_canvas = FigureCanvasTkAgg(self.original_fig, master=self.original_frame)
        self.original_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Animated graph
        self.animated_fig = plt.figure(figsize=(8, 6), dpi=100, facecolor="#f9f1e9")
        self.animated_canvas = FigureCanvasTkAgg(self.animated_fig, master=self.animated_frame)
        self.animated_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Control buttons
        btn_style = {"style": "TButton", "width": 18}
        self.load_btn = ttk.Button(self.control_frame, text="🔄 LOAD GRAPH", 
                                  command=self.load_graph, **btn_style)
        self.load_btn.pack(side=tk.LEFT, padx=10)
        
        self.animate_btn = ttk.Button(self.control_frame, text="▶️ ANIMATE PATHS", 
                                    command=self.animate_shortest_path, 
                                    state=tk.DISABLED, **btn_style)
        self.animate_btn.pack(side=tk.LEFT, padx=10)
        
        # Results display
        self.results_text = tk.Text(self.results_frame, height=10, wrap=tk.WORD, 
                                  font=("Consolas", 12), bg="white", fg="#5a4a42",
                                  insertbackground="#5a4a42", padx=10, pady=10)
        self.scrollbar = ttk.Scrollbar(self.results_frame, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=self.scrollbar.set)
        
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = ttk.Label(root, textvariable=self.status_var, 
                                   relief=tk.SUNKEN, anchor=tk.W, 
                                   font=("Arial", 11))
        self.status_bar.pack(fill=tk.X)
        
        # Graph data
        self.G = nx.Graph()
        self.shortest_paths = {}
        self.source_node = ""
        
    def load_graph(self):
        """Load graph data from edges.txt and output.txt"""
        try:
            # Clear previous data
            self.G.clear()
            self.shortest_paths.clear()
            self.results_text.delete(1.0, tk.END)
            self.status_var.set("Loading graph data...")
            self.root.update()
            
            # Read edges and build graph
            if not os.path.exists("edges.txt"):
                messagebox.showerror("Error", "edges.txt not found! Run C++ program first.")
                return
            
            with open("edges.txt", "r") as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) == 3:
                        u, v, w = parts
                        self.G.add_edge(u, v, weight=int(w))
            
            # Read shortest paths
            if not os.path.exists("output.txt"):
                messagebox.showerror("Error", "output.txt not found! Run C++ program first.")
                return
            
            with open("output.txt", "r") as f:
                lines = f.readlines()
                if lines:
                    self.source_node = lines[0].split("node ")[1].split(":")[0].strip()
                    for line in lines[1:]:
                        if "To node" in line:
                            parts = line.split()
                            node = parts[2].strip(":")
                            dist = parts[-1]
                            self.shortest_paths[node] = dist
            
            # Verify nodes exist in graph
            missing_nodes = [node for node in self.shortest_paths if node not in self.G.nodes()]
            if missing_nodes:
                messagebox.showwarning("Warning", f"Nodes in output not found in graph: {', '.join(missing_nodes)}")
            
            # Draw original graph
            self.draw_original_graph()
            self.animate_btn.config(state=tk.NORMAL)
            
            # Show results
            self.results_text.insert(tk.END, "✅ Graph loaded successfully!\n\n")
            self.results_text.insert(tk.END, f"🔷 Source node: {self.source_node}\n")
            self.results_text.insert(tk.END, "🔷 Shortest paths:\n")
            for node, dist in self.shortest_paths.items():
                if node in self.G.nodes():
                    self.results_text.insert(tk.END, f"  • To {node}: {dist}\n")
                else:
                    self.results_text.insert(tk.END, f"  • To {node}: {dist} (node not in graph)\n")
            
            self.status_var.set("Graph loaded successfully!")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load graph: {str(e)}")
            self.status_var.set("Error loading graph")
    
    def draw_original_graph(self):
        """Draw the original graph"""
        self.original_fig.clf()
        ax = self.original_fig.add_subplot(111, facecolor="#f5f6fa")
        
        pos = nx.spring_layout(self.G, seed=42)  # Fixed layout for consistency
        
        # Draw with nice styling
        nx.draw_networkx_nodes(self.G, pos, node_size=700, 
                             node_color="#487eb0", alpha=0.9, ax=ax)
        nx.draw_networkx_edges(self.G, pos, width=2, 
                             edge_color="#7f8c8d", alpha=0.7, ax=ax)
        nx.draw_networkx_labels(self.G, pos, font_size=12, 
            font_family='Arial', font_color="#000000", font_weight='bold', ax=ax)
        
        edge_labels = nx.get_edge_attributes(self.G, 'weight')
        nx.draw_networkx_edge_labels(self.G, pos, edge_labels=edge_labels, 
        font_color="#000000", font_size=11, font_family='Arial', ax=ax,
        bbox=dict(facecolor='white', edgecolor='gray', boxstyle='round,pad=0.3', alpha=0.9))

        
        ax.set_title("Original Graph", fontsize=12, color="#2f3640")
        ax.axis('off')
        self.original_canvas.draw()
    
    def animate_shortest_path(self):
        """Animate the shortest paths with visual effects"""
        if not self.shortest_paths:
            messagebox.showwarning("Warning", "No shortest paths to animate!")
            return
        
        self.results_text.insert(tk.END, "\n🌟 Animating shortest paths...\n")
        self.results_text.see(tk.END)
        self.root.update()
        
        # Get layout positions (same as original for consistency)
        pos = nx.spring_layout(self.G, seed=42)
        
        for target_node, dist in self.shortest_paths.items():
            if dist == "INF" or target_node not in self.G.nodes():
                continue
                
            self.status_var.set(f"Animating path to {target_node}...")
            self.results_text.insert(tk.END, f"  🚀 Path to {target_node} (distance: {dist})...\n")
            self.results_text.see(tk.END)
            self.root.update()
            
            try:
                # Get the shortest path
                path = nx.shortest_path(self.G, source=self.source_node, 
                                       target=target_node, weight='weight')
                
                # Create a new figure for animation
                self.animated_fig.clf()
                ax = self.animated_fig.add_subplot(111, facecolor="#f5f6fa")
                
                # Draw entire graph first (light colors)
                nx.draw_networkx_nodes(self.G, pos, node_size=700, 
                                     node_color="#dcdde1", alpha=0.5, ax=ax)
                nx.draw_networkx_edges(self.G, pos, width=1, 
                                     edge_color="#dcdde1", alpha=0.5, ax=ax)
                
                # Highlight the path
                path_edges = list(zip(path[:-1], path[1:]))
                
                # Draw path nodes
                nx.draw_networkx_nodes(self.G, pos, nodelist=path, 
                                     node_size=800, node_color="#e84118", ax=ax)
                
                # Draw path edges
                nx.draw_networkx_edges(self.G, pos, edgelist=path_edges, 
                                     width=3, edge_color="#e84118", ax=ax)
                
                # Draw all labels
                nx.draw_networkx_labels(self.G, pos, font_size=10, 
                                      font_family='sans-serif', font_color="#2f3640", ax=ax)
                edge_labels = nx.get_edge_attributes(self.G, 'weight')
                nx.draw_networkx_edge_labels(self.G, pos, edge_labels=edge_labels, 
                    font_color="#000000", font_size=11, font_family='Arial', ax=ax,
                    bbox=dict(facecolor='white', edgecolor='gray', boxstyle='round,pad=0.3', alpha=0.9))
                                
                ax.set_title(f"Path to {target_node} (Distance: {dist})", fontsize=12, color="#2f3640")
                ax.axis('off')
                self.animated_canvas.draw()
                
                time.sleep(1.2)  # Pause for animation effect
                
            except Exception as e:
                self.results_text.insert(tk.END, f"  ❌ Error showing path to {target_node}: {str(e)}\n")
        
        # Final view showing all paths
        self.show_final_paths(pos)
        self.status_var.set("Animation complete!")
        self.results_text.insert(tk.END, "\n✅ All paths animated!\n")
    
    def show_final_paths(self, pos):
        """Show all shortest paths together"""
        self.animated_fig.clf()
        ax = self.animated_fig.add_subplot(111, facecolor="#f5f6fa")
        
        # Draw base graph
        nx.draw_networkx_nodes(self.G, pos, node_size=700, 
                             node_color="#dcdde1", alpha=0.5, ax=ax)
        nx.draw_networkx_edges(self.G, pos, width=1, 
                             edge_color="#dcdde1", alpha=0.5, ax=ax)
        
        # Collect all paths
        all_path_nodes = set()
        all_path_edges = set()
        
        for target_node, dist in self.shortest_paths.items():
            if dist == "INF" or target_node not in self.G.nodes():
                continue
            try:
                path = nx.shortest_path(self.G, source=self.source_node, 
                                       target=target_node, weight='weight')
                all_path_nodes.update(path)
                all_path_edges.update(zip(path[:-1], path[1:]))
            except:
                continue
        
        # Highlight all paths
        if all_path_nodes:
            nx.draw_networkx_nodes(self.G, pos, nodelist=list(all_path_nodes), 
                                 node_size=800, node_color="#e84118", ax=ax)
        
        if all_path_edges:
            nx.draw_networkx_edges(self.G, pos, edgelist=list(all_path_edges), 
                                 width=3, edge_color="#e84118", ax=ax)
        
        # Highlight source node differently
        nx.draw_networkx_nodes(self.G, pos, nodelist=[self.source_node], 
                             node_size=900, node_color="#4cd137", ax=ax)
        
        # Draw labels
        nx.draw_networkx_labels(self.G, pos, font_size=10, 
                              font_family='sans-serif', font_color="#2f3640", ax=ax)
        edge_labels = nx.get_edge_attributes(self.G, 'weight')
        nx.draw_networkx_edge_labels(self.G, pos, edge_labels=edge_labels, 
            font_color="#000000", font_size=11, font_family='Arial', ax=ax,
            bbox=dict(facecolor='white', edgecolor='gray', boxstyle='round,pad=0.3', alpha=0.9))
                
        ax.set_title("All Shortest Paths from Source", fontsize=12, color="#2f3640")
        ax.axis('off')
        self.animated_canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = GraphVisualizer(root)
    root.mainloop()