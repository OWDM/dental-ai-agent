"""
Visualize the LangGraph Workflow
Shows the agent routing structure and saves as image
"""

import os
from src.graph.workflow import create_workflow


def visualize_graph():
    """Visualize the LangGraph workflow"""

    print("=" * 60)
    print("🎨 Dental AI Agent - Graph Visualization")
    print("=" * 60)

    # Create the workflow
    print("\n⏳ Creating workflow...")
    app = create_workflow()

    # Get the graph
    graph = app.get_graph()
    print("✅ Workflow created")

    # Try to save as PNG image
    print("\n📸 Generating graph image...")
    try:
        # Save as PNG
        png_data = graph.draw_mermaid_png()
        with open("graph_visualization.png", "wb") as f:
            f.write(png_data)
        print("✅ Graph saved as: graph_visualization.png")

        # Get file size
        file_size = os.path.getsize("graph_visualization.png")
        print(f"   File size: {file_size:,} bytes")

    except Exception as e:
        print(f"❌ PNG generation failed: {e}")
        print("\n💡 Trying alternative method...")

        # Fallback: Save Mermaid code
        try:
            mermaid_code = graph.draw_mermaid()
            with open("graph_diagram.mmd", "w") as f:
                f.write(mermaid_code)
            print("✅ Mermaid diagram saved to: graph_diagram.mmd")
            print("\n📋 Mermaid Code:")
            print("=" * 60)
            print(mermaid_code)
            print("=" * 60)
            print("\n💡 To view as image:")
            print("   1. Go to https://mermaid.live")
            print("   2. Paste the code above")
            print("   3. Download as PNG/SVG")
        except Exception as e2:
            print(f"❌ Mermaid generation also failed: {e2}")

    # Print ASCII representation
    print("\n📊 Graph Structure (ASCII):")
    print("=" * 60)
    try:
        ascii_graph = graph.draw_ascii()
        print(ascii_graph)
    except Exception as e:
        print(f"ASCII visualization not available: {e}")

    # Print node information
    print("\n" + "=" * 60)
    print("📋 Graph Nodes:")
    print("=" * 60)
    for node in graph.nodes:
        print(f"  • {node}")

    print("\n" + "=" * 60)
    print("🔗 Graph Edges:")
    print("=" * 60)
    for edge in graph.edges:
        print(f"  • {edge}")

    print("\n" + "=" * 60)
    print("✅ Visualization Complete!")
    print("=" * 60)

    # Check if image was created
    if os.path.exists("graph_visualization.png"):
        print("\n🖼️  Graph image saved successfully!")
        print("   Open: graph_visualization.png")
        print("\n   To view:")
        print("   - Linux: xdg-open graph_visualization.png")
        print("   - Mac: open graph_visualization.png")
        print("   - Windows: start graph_visualization.png")


if __name__ == "__main__":
    visualize_graph()
