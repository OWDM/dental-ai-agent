"""
Visualize the LangGraph Workflow
Shows the agent routing structure, tools, and saves as enhanced image
"""

import os
from src.graph.workflow import create_workflow
from src.tools.booking_tools import booking_tools
from src.tools.management_tools import management_tools
from src.tools.rag_tool import rag_tools
from langchain_core.runnables.graph import CurveStyle, NodeStyles, MermaidDrawMethod


def print_tools_info():
    """Print detailed information about all tools"""
    print("\n" + "=" * 80)
    print("🛠️  AGENT TOOLS OVERVIEW")
    print("=" * 80)

    # FAQ Agent Tools
    print("\n📚 FAQ Agent Tools (RAG-based):")
    print("-" * 80)
    for tool in rag_tools:
        print(f"\n  🔹 {tool.name}")
        print(f"     Description: {tool.description[:100]}...")

    # Booking Agent Tools
    print("\n\n📅 Booking Agent Tools:")
    print("-" * 80)
    for tool in booking_tools:
        print(f"\n  🔹 {tool.name}")
        print(f"     Description: {tool.description[:100]}...")

    # Management Agent Tools
    print("\n\n⚙️  Management Agent Tools:")
    print("-" * 80)
    for tool in management_tools:
        print(f"\n  🔹 {tool.name}")
        print(f"     Description: {tool.description[:100]}...")

    # Summary
    total_tools = len(rag_tools) + len(booking_tools) + len(management_tools)
    print("\n" + "-" * 80)
    print(f"Total Tools: {total_tools}")
    print(f"  • FAQ Agent: {len(rag_tools)} tool(s)")
    print(f"  • Booking Agent: {len(booking_tools)} tool(s)")
    print(f"  • Management Agent: {len(management_tools)} tool(s)")
    print("=" * 80)


def create_custom_mermaid_with_tools():
    """Create a custom Mermaid diagram that includes tools for each agent"""

    # Build tool lists
    faq_tool_list = "\\n".join([f"📚 {t.name}" for t in rag_tools])
    booking_tool_list = "\\n".join([f"📅 {t.name}" for t in booking_tools])
    mgmt_tool_list = "\\n".join([f"⚙️ {t.name}" for t in management_tools])

    mermaid_code = f"""---
config:
  theme: base
  themeVariables:
    primaryColor: '#e3f2fd'
    primaryTextColor: '#1a1a1a'
    primaryBorderColor: '#1976d2'
    lineColor: '#424242'
    secondaryColor: '#fff3e0'
    tertiaryColor: '#e8f5e9'
---
graph TD
    Start([__start__])
    Router[Router<br/>Intent Classification]

    FAQ["FAQ Agent<br/>---<br/>{faq_tool_list}"]
    Booking["Booking Agent<br/>---<br/>{booking_tool_list}"]
    Management["Management Agent<br/>---<br/>{mgmt_tool_list}"]
    Placeholder[Placeholder Agent<br/>No tools]

    End([__end__])

    Start --> Router
    Router -.FAQ Intent.-> FAQ
    Router -.Booking Intent.-> Booking
    Router -.Management Intent.-> Management
    Router -.Other Intent.-> Placeholder
    Router -.Direct End.-> End

    FAQ --> End
    Booking --> End
    Management --> End
    Placeholder --> End

    style Start fill:#fff3e0,stroke:#f57c00,stroke-width:3px
    style End fill:#c8e6c9,stroke:#388e3c,stroke-width:3px
    style Router fill:#e1bee7,stroke:#8e24aa,stroke-width:2px
    style FAQ fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    style Booking fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    style Management fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    style Placeholder fill:#f5f5f5,stroke:#9e9e9e,stroke-width:2px
"""
    return mermaid_code


def visualize_graph():
    """Visualize the LangGraph workflow with enhanced styling"""

    print("=" * 80)
    print("🎨 Dental AI Agent - Enhanced Graph Visualization")
    print("=" * 80)

    # Create the workflow
    print("\n⏳ Creating workflow...")
    app = create_workflow()

    # Get the graph
    graph = app.get_graph()
    print("✅ Workflow created successfully")

    # Print tools information
    print_tools_info()

    # Try enhanced PNG generation with styling
    print("\n" + "=" * 80)
    print("📸 Generating Enhanced Graph Visualization")
    print("=" * 80)

    try:
        print("\n⏳ Rendering graph with custom styling...")

        # Try to use enhanced parameters with correct imports
        try:
            from langchain_core.runnables.graph import CurveStyle, NodeStyles, MermaidDrawMethod

            # Custom Mermaid theme configuration
            frontmatter_config = {
                "config": {
                    "theme": "base",
                    "themeVariables": {
                        "primaryColor": "#e3f2fd",       # Light blue for nodes
                        "primaryTextColor": "#1a1a1a",   # Dark text
                        "primaryBorderColor": "#1976d2", # Blue borders
                        "lineColor": "#424242",          # Dark gray lines
                        "secondaryColor": "#fff3e0",     # Light orange
                        "tertiaryColor": "#e8f5e9",      # Light green
                        "background": "#ffffff",         # White background
                        "mainBkg": "#e3f2fd",           # Node background
                        "secondBkg": "#fff3e0",         # Start node
                        "tertiaryBkg": "#c8e6c9",       # End node
                    }
                }
            }

            # Custom node styles with CSS-style fill
            node_styles = NodeStyles(
                default="fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#1a1a1a",
                first="fill:#fff3e0,stroke:#f57c00,stroke-width:3px,color:#1a1a1a",
                last="fill:#c8e6c9,stroke:#388e3c,stroke-width:3px,color:#1a1a1a"
            )

            # Generate with enhanced styling
            png_data = graph.draw_mermaid_png(
                curve_style=CurveStyle.LINEAR,
                node_colors=node_styles,
                wrap_label_n_words=9,
                output_file_path="graph_visualization.png",
                draw_method=MermaidDrawMethod.API,
                background_color="white",
                padding=15,
                frontmatter_config=frontmatter_config
            )
            print("✅ Enhanced styling applied!")
            print("   🎨 Custom theme: Blue agents, Orange start, Green end")

        except Exception as e:
            # Fallback to basic draw_mermaid_png
            print(f"⚠️  Enhanced styling failed: {e}")
            print("   Using basic rendering...")
            png_data = graph.draw_mermaid_png()
            with open("graph_visualization.png", "wb") as f:
                f.write(png_data)

        # Verify file was created
        if os.path.exists("graph_visualization.png"):
            file_size = os.path.getsize("graph_visualization.png")
            print(f"✅ Graph saved as: graph_visualization.png")
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
            print("=" * 80)
            print(mermaid_code)
            print("=" * 80)
            print("\n💡 To view as image:")
            print("   1. Go to https://mermaid.live")
            print("   2. Paste the code above")
            print("   3. Download as PNG/SVG")
        except Exception as e2:
            print(f"❌ Mermaid generation also failed: {e2}")

    # Print ASCII representation
    print("\n" + "=" * 80)
    print("📊 Graph Structure (ASCII)")
    print("=" * 80)
    try:
        ascii_graph = graph.draw_ascii()
        print(ascii_graph)
    except Exception as e:
        print(f"ASCII visualization not available: {e}")

    # Print node information
    print("\n" + "=" * 80)
    print("📋 Graph Nodes")
    print("=" * 80)
    nodes_list = list(graph.nodes)
    for i, node in enumerate(nodes_list, 1):
        node_type = "🔵" if node == "__start__" else "🟢" if node == "__end__" else "🟡"
        print(f"  {i}. {node_type} {node}")

    print("\n" + "=" * 80)
    print("🔗 Graph Edges (Routing)")
    print("=" * 80)
    for i, edge in enumerate(graph.edges, 1):
        print(f"  {i}. {edge.source} → {edge.target}")

    # Print workflow summary
    print("\n" + "=" * 80)
    print("📊 Workflow Summary")
    print("=" * 80)
    print(f"Total Nodes: {len(nodes_list)}")
    print(f"Total Edges: {len(graph.edges)}")
    print(f"Entry Point: router")
    print(f"Agents: FAQ, Booking, Management, Placeholder")

    # Generate custom visualization WITH TOOLS
    print("\n" + "=" * 80)
    print("🔧 Generating Enhanced Visualization WITH TOOLS")
    print("=" * 80)

    try:
        from langchain_core.runnables.graph_mermaid import draw_mermaid_png

        print("\n⏳ Creating custom diagram with tool information...")
        custom_mermaid = create_custom_mermaid_with_tools()

        # Save Mermaid code
        with open("graph_with_tools.mmd", "w") as f:
            f.write(custom_mermaid)
        print("✅ Mermaid code saved to: graph_with_tools.mmd")

        # Generate PNG from custom Mermaid
        print("⏳ Rendering custom diagram to PNG...")
        custom_png = draw_mermaid_png(
            custom_mermaid,
            output_file_path="graph_with_tools.png",
            draw_method=MermaidDrawMethod.API,
            background_color="white",
            padding=15
        )
        print("✅ Custom graph with tools saved as: graph_with_tools.png")

        if os.path.exists("graph_with_tools.png"):
            file_size = os.path.getsize("graph_with_tools.png")
            print(f"   File size: {file_size:,} bytes")

    except Exception as e:
        print(f"⚠️  Custom visualization failed: {e}")
        print("   Mermaid code saved to: graph_with_tools.mmd")
        print("   You can view it at: https://mermaid.live")

    print("\n" + "=" * 80)
    print("✅ Visualization Complete!")
    print("=" * 80)

    # Check if images were created
    if os.path.exists("graph_visualization.png"):
        print("\n🖼️  Standard Graph (workflow only):")
        print("   📁 Location: graph_visualization.png")

    if os.path.exists("graph_with_tools.png"):
        print("\n🖼️  Enhanced Graph (with tools):")
        print("   📁 Location: graph_with_tools.png")
        print("   ⭐ This version shows all tools for each agent!")

    print("\n   To view the graphs:")
    print("   • Linux:   xdg-open graph_with_tools.png")
    print("   • macOS:   open graph_with_tools.png")
    print("   • Windows: start graph_with_tools.png")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    visualize_graph()
