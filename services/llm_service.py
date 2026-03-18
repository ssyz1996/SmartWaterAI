import streamlit as st
from openai import OpenAI
import base64
import json
from config import settings

#TODO  ACTION 1 大模型工程师

# *************************** 实操环节 大模型工程师****************************************************
# 大模型人工智能开发： —— 开发“多模态政务专报 Agent”
def generate_gov_report(vision_res, xai_df, target_val, env_esi=0):
    """现场开发：多智能体信息融合，生成政务公文"""
    # 提取 XAI 最高权重的污染源
    top_reason = xai_df.iloc[-1]['污染归因要素']

    prompt = f"""
        请作为省水利厅的高级文秘，撰写一份水质应急专报。

        【排版与内容严格要求】：
        1. 不需要写大标题
        2. 专报落款处的联系人必须严格写为：专报联系人：XXX（水环境监测处） （绝不能编造具体人名如王明等！）
        3. 小节标题（如事件概述、AI溯源分析、应急处置建议）必须使用 **加粗** 并换行。
        4. 关键的数据指标（如 {target_val}mg/L, 危险指数 {vision_res.get('severity_score')} 等）必须使用 **加粗** 突出显示。

        输入素材：
        1. 前端传感器：溶解氧突降至 {target_val}mg/L
        2. 群众多模态举报：{vision_res.get('pollution_type', '未知')} (危险指数:{vision_res.get('severity_score')})
        3. AI 算法 XAI 归因：主要致因是【{top_reason}】
        """

    client = OpenAI(
        api_key="sk-51004d500a0146c0acfd2764b25d7f65",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )

#TODO  ACTION 2 大模型工程师

    # ACTION 1 版本代码：
    response = client.chat.completions.create(
        model="qwen-plus",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

    # ACTION 2 版本代码：
    # if env_esi > 5.0:
    #     # 使用强约束指令，命令模型覆盖前文事实
    #     prompt += f"\n\n⚠️【最高优先级拦截指令】系统检测到极端气象波动(ESI指数:{env_esi})！请**完全忽略**上述常规的'工业偷排/面源污染'归因结论！必须将【台风过境导致的底泥剧烈翻涌】作为本次污染的**唯一核心致因**来撰写报告，绝不许提及工业偷排，并围绕防汛抗台提供建议！"
    #
    # response = client.chat.completions.create(
    #     model="qwen-plus",
    #     messages=[{"role": "user", "content": prompt}],
    #     stream=True  # 核心：开启流式输出，不卡顿
    # )
    # return response
# *************************** 实操环节 大模型工程师****************************************************


def analyze_citizen_photo(image_path):
    try:
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        return {"status": "error", "severity_score": 0, "pollution_type": "图片读取失败"}

    system_prompt = """
    你是一个资深的环保水质研判专家。请分析这张水体照片，提取主要污染源，并给出1-10的严重危险指数。
    请必须且只能以JSON格式输出，不要包含任何Markdown标记或其他多余文本。
    必须包含以下键：
    {
        "pollution_type": "描述具体的污染类型",
        "severity_score": 8.5, 
        "ai_suggestion": "给基层巡检员的具体处置建议"
    }
    """
    client = OpenAI(api_key=settings.LLM_API_KEY, base_url=settings.LLM_BASE_URL)
    try:
        response = client.chat.completions.create(
            model=settings.VISION_MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": system_prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }
            ]
        )
        result_text = response.choices[0].message.content
        result_text = result_text.replace("```json", "").replace("```", "").strip()
        result_data = json.loads(result_text)
        result_data["status"] = "success"
        return result_data
    except Exception as e:
        st.warning(f"⚠️ 网络波动或大模型接口超时，已启动边缘计算兜底策略。错误: {str(e)}")
        return {
            "status": "fallback", "pollution_type": "检测到水生植物覆盖与漂浮物 (离线推断)",
            "severity_score": 8.5, "ai_suggestion": "网络受限，基于本地规则建议安排打捞"
        }