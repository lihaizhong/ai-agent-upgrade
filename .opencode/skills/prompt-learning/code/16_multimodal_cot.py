"""
16 - 多模态思维链 (Multimodal Chain-of-Thought)

多模态思维链结合文本和图像进行推理。
核心：利用视觉信息增强文本推理能力。

工作流程：
1. 接收文本问题和图像
2. 分别进行文本推理和图像分析
3. 融合多模态信息
4. 生成综合推理和答案

注意：这是一个简化框架，实际需要视觉模型支持。
"""

try:
    from .utils import call_llm
except ImportError:
    from utils import call_llm


class MultimodalCoT:
    def __init__(self):
        self.vision_capable = False

    def analyze_image(self, image_description: str) -> str:
        """分析图像内容（模拟）"""
        prompt = f"""描述以下图像的内容，包括：
1. 图像中的主要对象
2. 场景和背景
3. 任何文字或数据
4. 关键细节

图像描述：{image_description}"""

        result = call_llm(prompt)
        return result["data"] if result["success"] else ""

    def text_reasoning(self, question: str, image_analysis: str = "") -> str:
        """文本推理"""
        context = f"图像分析结果：{image_analysis}" if image_analysis else "无图像信息"

        prompt = f"""基于以下信息回答问题。

问题：{question}

{context}

请一步步推理，给出答案。"""

        result = call_llm(prompt)
        return result["data"] if result["success"] else ""

    def solve(self, question: str, image_description: str = None) -> dict:
        """多模态思维链解决问题"""
        print("=" * 60)
        print("多模态思维链 (Multimodal CoT)")
        print("=" * 60)

        image_analysis = ""

        if image_description:
            print("\n【步骤1】分析图像...")
            image_analysis = self.analyze_image(image_description)
            print(f"图像分析：{image_analysis[:200]}...")

        print("\n【步骤2】文本推理...")
        reasoning = self.text_reasoning(question, image_analysis)
        print(f"推理过程：{reasoning[:200]}...")

        print("\n【步骤3】生成答案...")
        final_prompt = f"""基于以下推理过程，给出最终答案。

推理过程：{reasoning}

最终答案："""

        result = call_llm(final_prompt)

        return {
            "success": result["success"],
            "image_analysis": image_analysis,
            "reasoning": reasoning,
            "answer": result["data"] if result["success"] else "",
        }


def main():
    print("=" * 60)
    print("多模态思维链 (Multimodal CoT) 示例")
    print("=" * 60)

    mcot = MultimodalCoT()

    example_1 = {
        "question": "图中显示的数据相比上一年是增长还是下降？",
        "image_description": "一个折线图，显示2020年到2024年的销售数据，Y轴是销售额，2020年销售额为100万，2024年上升到250万",
    }

    print("\n【示例】图表数据分析")
    print(f"问题：{example_1['question']}")

    result = mcot.solve(example_1["question"], example_1["image_description"])

    if result["success"]:
        print(f"\n最终答案：{result['answer']}")


if __name__ == "__main__":
    main()
