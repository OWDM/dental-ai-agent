"""
Visualize the LangGraph Workflow
Shows the agent routing structure using LangGraph's native visualization.
"""

import os
from src.graph.workflow import create_workflow

def visualize_graph():
    """Visualize the LangGraph workflow"""

    print("=" * 80)
    print("🎨 Dental AI Agent - Graph Visualization")
    print("=" * 80)

    # Create the workflow
    print("\n⏳ Creating workflow...")
    app = create_workflow()

    # Get the graph
    graph = app.get_graph()
    print("✅ Workflow created successfully")

    # Generate PNG using native LangGraph method
    print("\n" + "=" * 80)
    print("📸 Generating Graph Visualization")
    print("=" * 80)

    try:
        print("\n⏳ Rendering graph...")
        
        # Draw using Mermaid
        png_data = graph.draw_mermaid_png()
        
        with open("graph_visualization.png", "wb") as f:
            f.write(png_data)
            
        print("✅ Graph saved as: graph_visualization.png")
        
        # Also save the Mermaid code for inspection
        mermaid_code = graph.draw_mermaid()
        with open("graph_diagram.mmd", "w") as f:
            f.write(mermaid_code)
        print("✅ Mermaid code saved to: graph_diagram.mmd")

    except Exception as e:
        print(f"❌ Visualization failed: {e}")
        print("\n💡 Note: You need 'grandalf' or a Mermaid renderer installed.")

    print("\n" + "=" * 80)
    print("✅ Visualization Complete!")
    print("=" * 80)
    
    if os.path.exists("graph_visualization.png"):
        print("\n🖼️  Graph Image:")
        print("   📁 Location: graph_visualization.png")
        print("\n   To view:")
        print("   • Linux:   xdg-open graph_visualization.png")
        print("   • macOS:   open graph_visualization.png")
        print("   • Windows: start graph_visualization.png")

if __name__ == "__main__":
    visualize_graph()
