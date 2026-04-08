"""
02 - 少样本提示 (Few-Shot Prompting)

少样本提示通过提供示例来引导模型理解任务。
适用于：
- 模型不熟悉的任务格式
- 需要特定输出结构
- 复杂或抽象任务

核心技巧：
- 示例数量：通常 2-5 个
- 示例质量比数量更重要
- 示例应覆盖典型场景
"""

try:
    from .utils import call_llm
except ImportError:
    from utils import call_llm


def basic_few_shot():
    """基本的少样本提示"""
    prompt = """请判断以下评论的情感是正面还是负面。

示例：
评论："这个电影太精彩了，结局完全没想到！"
情感：正面

评论："服务态度很差，等了一个小时才上菜。"
情感：负面

评论："一般般，没有特别的感觉。"
情感：中性

评论："产品还行，但包装太简陋了。"
情感："""

    result = call_llm(prompt)
    return result


def few_shot_with_reasoning():
    """带推理的少样本提示"""
    prompt = """在回复前，先进行一步步的推理分析。

示例：
评论："这个软件经常崩溃，浪费了我很多时间。"
推理：用户提到软件崩溃和时间浪费，这是负面体验。
情感：负面

评论："虽然价格贵，但质量确实很好。"
推理：价格贵但质量好，有正面也有负面，但整体评价是正面的。
情感：正面

评论："送货有点慢，但产品本身没问题。"
推理：送货慢是负面，但产品没问题说明质量可以接受。
情感：中性

评论："用了一周，续航确实比之前那款好。"
推理：用户明确对比并肯定了续航能力，这是正面反馈。
情感："""

    result = call_llm(prompt)
    return result


def few_shot_for_format():
    """少样本提示用于特定格式"""
    prompt = """将用户输入转换为指定格式。

输入示例：
"李白唐代诗人代表作静夜思"

输出示例：
{
    "name": "李白",
    "dynasty": "唐代",
    "occupation": "诗人",
    "representative_works": ["静夜思", "望庐山瀑布"]
}

输入：
"苏轼宋代文学家代表作念奴娇赤壁怀古水调歌头"

输出格式与上述相同。"""

    result = call_llm(prompt)
    return result


def main():
    print("=" * 60)
    print("少样本提示 (Few-Shot Prompting) 示例")
    print("=" * 60)

    print("\n【示例1】基本少样本提示")
    print("-" * 40)
    result = basic_few_shot()
    if result["success"]:
        print(f"回答：{result['data']}")

    print("\n【示例2】带推理的少样本提示")
    print("-" * 40)
    result = few_shot_with_reasoning()
    if result["success"]:
        print(f"回答：{result['data']}")

    print("\n【示例3】少样本提示用于特定格式")
    print("-" * 40)
    result = few_shot_for_format()
    if result["success"]:
        print(f"回答：{result['data']}")


if __name__ == "__main__":
    main()
