#include <iostream>
#include <climits>
#include <fstream>
using namespace std;

const int MAX = 100;
int graph[MAX][MAX];
bool visited[MAX];
int dist[MAX];
char nodes[MAX];

int main() {
    int n, m;
    cout << "Enter number of nodes: ";
    cin >> n;

    cout << "Enter node names (single letters/numbers):\n";
    for (int i = 0; i < n; i++) {
        cin >> nodes[i];
    }

    // Initialize graph
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++)
            graph[i][j] = 0;

    cout << "Enter number of edges: ";
    cin >> m;

    // First write all edges to edges.txt
    ofstream fedges("edges.txt");
    cout << "Enter edges (from to weight):\n";
    for (int i = 0; i < m; i++) {
        char from, to;
        int weight;
        cin >> from >> to >> weight;
        if (weight < 0) {
        cout << "Negative weights not allowed in Dijkstra's algorithm.\n";
        i--; // So that the loop doesn't skip one input
        continue;
    }
        // Write to edges.txt immediately
        fedges << from << " " << to << " " << weight << endl;
        
        // Find indices for the algorithm
        int u = -1, v = -1;
        for (int j = 0; j < n; j++) {
            if (nodes[j] == from) u = j;
            if (nodes[j] == to) v = j;
        }
        
        if (u != -1 && v != -1) {
           if (graph[u][v] == 0 || weight < graph[u][v]) {
   				 graph[u][v] = weight;
   				 graph[v][u] = weight;
}// Undirected graph
        }
        else{
        	cout << "Invalid node name in edge: " << from << " " << to << endl;
		}
    }
    fedges.close();

    char source;
    cout << "Enter source node: ";
    cin >> source;
    
    int srcIndex = -1;
    for (int i = 0; i < n; i++) {
        if (nodes[i] == source) {
            srcIndex = i;
            break;
        }
    }

    if (srcIndex == -1) {
        cout << "Source node not found!\n";
        return 1;
    }

    // Dijkstra's algorithm
    for (int i = 0; i < n; i++) {
        dist[i] = INT_MAX;
        visited[i] = false;
    }
    dist[srcIndex] = 0;

    for (int count = 0; count < n-1; count++) {
        int minDist = INT_MAX, u = -1;
        for (int i = 0; i < n; i++) {
            if (!visited[i] && dist[i] < minDist) {
                minDist = dist[i];
                u = i;
            }
        }

        if (u == -1) break;
        visited[u] = true;

        for (int v = 0; v < n; v++) {
            if (!visited[v] && graph[u][v] && dist[u] != INT_MAX 
                && dist[u] + graph[u][v] < dist[v]) {
                dist[v] = dist[u] + graph[u][v];
            }
        }
    }

    // Write to output.txt
    ofstream fout("output.txt");
    fout << "Shortest distances from node " << source << ":\n";
    for (int i = 0; i < n; i++) {
        fout << "To node " << nodes[i] << ": ";
        if (dist[i] == INT_MAX)
            fout << "INF";
        else
            fout << dist[i];
        fout << endl;
    }
    fout.close();
    // Print header row
cout << "\t";
for (int i = 0; i < n; i++) {
    cout << nodes[i] << "\t";
}
cout << endl;

// Print rows with row labels
for (int i = 0; i < n; i++) {
    cout << nodes[i] << "\t";
    for (int j = 0; j < n; j++) {
        cout << graph[i][j] << "\t";
    }
    cout << endl;
}

    cout << "\nShortest paths written to output.txt\n";
    cout << "Graph edges written to edges.txt\n";

    return 0;
}
