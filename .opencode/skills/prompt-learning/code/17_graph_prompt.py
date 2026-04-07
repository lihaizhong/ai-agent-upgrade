"""
17 - 图提示 (Graph Prompting)

图提示利用图结构数据进行学习和推理。
核心：将图结构信息转换为模型可以理解的提示。

适用场景：
- 社交网络分析
- 知识图谱推理
- 分子结构分析
- 关系网络推理

注意：这是一个简化框架，展示了图提示的核心概念。
"""

from utils import call_llm


class GraphPrompting:
    def __init__(self):
        self.graph = {}

    def add_edge(self, from_node: str, to_node: str, relation: str = ""):
        """添加图边"""
        if from_node not in self.graph:
            self.graph[from_node] = []
        self.graph[from_node].append({"to": to_node, "relation": relation})

    def add_edges(self, edges: list):
        """批量添加边"""
        for edge in edges:
            if len(edge) == 2:
                self.add_edge(edge[0], edge[1])
            elif len(edge) == 3:
                self.add_edge(edge[0], edge[1], edge[2])

    def to_textual_description(self) -> str:
        """将图转换为文本描述"""
        lines = []
        for node, neighbors in self.graph.items():
            for neighbor in neighbors:
                if neighbor["relation"]:
                    lines.append(
                        f"{node} --[{neighbor['relation']}]--> {neighbor['to']}"
                    )
                else:
                    lines.append(f"{node} --> {neighbor['to']}")
        return "\n".join(lines)

    def query_path(self, from_node: str, to_node: str) -> str:
        """查询两个节点之间的路径"""
        prompt = f"""在以下图中，找出从节点 A 到节点 B 的路径。

图结构：
{self.to_textual_description()}

节点 A：{from_node}
节点 B：{to_node}

请找出所有可能的路径，并说明最短路径是什么。"""

        result = call_llm(prompt)
        return result["data"] if result["success"] else ""

    def node_properties(self, node: str) -> str:
        """推断节点属性"""
        prompt = f"""基于以下图结构，分析节点「{node}」的属性和特点。

图结构：
{self.to_textual_description()}

节点「{node}」的直接邻居有哪些？
它在图中可能扮演什么角色？"""

        result = call_llm(prompt)
        return result["data"] if result["success"] else ""

    def solve_task(self, task: str) -> dict:
        """使用图提示解决任务"""
        print("=" * 60)
        print("图提示 (Graph Prompting)")
        print("=" * 60)

        print(f"\n图结构：\n{self.to_textual_description()}")
        print(f"\n任务：{task}")

        prompt = f"""基于以下图结构，完成指定任务。

图结构：
{self.to_textual_description()}

任务：{task}

请一步步推理并给出答案。"""

        result = call_llm(prompt)

        return {
            "success": result["success"],
            "graph_description": self.to_textual_description(),
            "task": task,
            "answer": result["data"] if result["success"] else "",
        }


def social_network_example():
    """社交网络分析示例"""
    graph = GraphPrompting()

    edges = [
        ("张三", "李四", "朋友"),
        ("张三", "王五", "朋友"),
        ("李四", "王五", "同事"),
        ("李四", "赵六", "朋友"),
        ("王五", "赵六", "朋友"),
        ("王五", "孙七", "朋友"),
        ("赵六", "孙七", "同事"),
    ]

    graph.add_edges(edges)

    result = graph.solve_task(
        "找出所有可能的'朋友的朋友'关系，并识别出最可能互相认识但还不是直接朋友的人"
    )

    return result


def knowledge_graph_example():
    """知识图谱示例"""
    graph = GraphPrompting()

    edges = [
        ("苹果", "公司", "是"),
        ("苹果", "水果", "是"),
        ("水果", "植物", "属于"),
        ("公司", "库克", "CEO"),
        ("库克", "苹果", "领导"),
    ]

    graph.add_edges(edges)

    result = graph.solve_task("判断'苹果'在这里指的是公司还是水果？")

    return result


def main():
    print("=" * 60)
    print("图提示 (Graph Prompting) 示例")
    print("=" * 60)

    print("\n【示例1】社交网络分析")
    print("-" * 40)
    result = social_network_example()
    if result["success"]:
        print(f"\n答案：{result['answer']}")

    print("\n【示例2】知识图谱推理")
    print("-" * 40)
    result = knowledge_graph_example()
    if result["success"]:
        print(f"\n答案：{result['answer']}")


if __name__ == "__main__":
    main()
