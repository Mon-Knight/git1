"""
AI World Engine - Setting Suggestion Service
Generates AI candidate settings for characters, factions, locations, and rules.
v1.7.9: Candidates only - NO auto-adoption into official tables.
"""

import json
import re
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.models import SettingSuggestion


class SettingSuggestionService:
    """Service for AI-generated setting suggestions."""

    SUGGESTION_TYPES = ["character", "faction", "location", "rule"]

    WORLD_TYPES = [
        ("western_fantasy", "西方奇幻"),
        ("eastern_fantasy", "东方玄幻"),
        ("xianxia", "仙侠"),
        ("sci_fi", "科幻"),
        ("cyberpunk", "赛博朋克"),
        ("apocalypse", "末世"),
        ("cthulhu", "克苏鲁"),
        ("steampunk", "蒸汽朋克"),
        ("custom", "自定义"),
    ]

    REFERENCE_STYLES = [
        ("heroic_epic", "英雄史诗"),
        ("dark_fantasy", "黑暗奇幻"),
        ("kingdom_war", "王国战争"),
        ("academy_growth", "学院成长"),
        ("territory_building", "领地建设"),
        ("religious_conflict", "宗教冲突"),
        ("magic_industrialization", "魔法工业化"),
        ("race_war", "种族战争"),
        ("custom", "自定义"),
    ]

    @staticmethod
    def build_setting_suggestion_prompt(
        db: Session, world_id: int, request_data: Dict[str, Any]
    ) -> str:
        """Build a prompt for AI setting suggestion generation with originality constraints."""
        from app.models import World, Character, Faction, Location, WorldRule
        from app.services.model_formatters import (
            format_character_summary, format_faction_summary,
            format_location_summary, format_rule_summary,
        )

        world = db.query(World).filter(World.id == world_id).first()
        world_name = world.name if world else "未知世界"
        world_desc = (world.description or "")[:300] if world else ""

        # Load existing summaries (max 10 each)
        chars = db.query(Character).filter(Character.world_id == world_id).limit(10).all()
        factions = db.query(Faction).filter(Faction.world_id == world_id).limit(10).all()
        locations = db.query(Location).filter(Location.world_id == world_id).limit(10).all()
        rules = db.query(WorldRule).filter(WorldRule.world_id == world_id).limit(10).all()

        char_summary = "\n".join([format_character_summary(c) for c in chars]) or "（暂无角色）"
        faction_summary = "\n".join([format_faction_summary(f) for f in factions]) or "（暂无势力）"
        location_summary = "\n".join([format_location_summary(l) for l in locations]) or "（暂无地点）"
        rule_summary = "\n".join([format_rule_summary(r) for r in rules]) or "（暂无规则）"

        sug_type = request_data.get("suggestion_type", "character")
        sug_type_cn = {"character": "角色", "faction": "势力", "location": "地点", "rule": "规则"}.get(sug_type, "角色")

        world_type = request_data.get("world_type", "western_fantasy")
        wt_map = dict(SettingSuggestionService.WORLD_TYPES)
        world_type_cn = wt_map.get(world_type, "西方奇幻")

        ref_style = request_data.get("reference_style", "heroic_epic")
        rs_map = dict(SettingSuggestionService.REFERENCE_STYLES)
        ref_style_cn = rs_map.get(ref_style, "英雄史诗")

        count = request_data.get("generation_count", 3)
        user_req = request_data.get("user_requirement", "")

        type_field_specs = {
            "character": "name（姓名）、identity（身份）、faction（所属势力）、personality（性格）、goal（目标）、ability（能力）、weakness（弱点）、current_status（当前状态）、plot_role（剧情角色定位）、relation_to_mainline（与主线关系）",
            "faction": "name（名称）、faction_type（势力类型）、leader（领袖）、core_goal（核心目标）、resources（资源）、allies（盟友）、enemies（敌对势力）、territory（势力范围）、internal_conflict（内部矛盾）、plot_role（剧情角色定位）",
            "location": "name（名称）、location_type（地点类型）、region（所在区域）、controlling_faction（控制势力）、description（描述）、danger_level（危险等级）、important_resource（重要资源）、key_history（关键历史）、possible_plot（可能的剧情用途）",
            "rule": "name（名称）、rule_type（规则类型）、content（内容）、limitation（限制条件）、influence_scope（影响范围）、possible_conflict（可能引发的矛盾）、plot_usage（剧情用途）",
        }
        field_spec = type_field_specs.get(sug_type, type_field_specs["character"])

        prompt = f"""【世界设定推演任务】
你是一位世界观设定师，需要为一个名为"{world_name}"的世界生成{sug_type_cn}候选设定。

【世界信息】
名称：{world_name}
简介：{world_desc}

【已有设定摘要】
已有角色：
{char_summary}

已有势力：
{faction_summary}

已有地点：
{location_summary}

已有规则：
{rule_summary}

【生成要求】
- 生成类型：{sug_type_cn}
- 题材参考方向：{world_type_cn} / {ref_style_cn}
- 生成数量：{count} 条
{'- 补充要求：' + user_req if user_req else ''}

【输出格式】
请以 JSON 数组格式输出，每条{  {sug_type_cn}  }包含以下字段：
{field_spec}

【核心约束】
1. 借鉴{world_type_cn}题材中常见的世界结构、势力矛盾、种族关系、魔法体系等类型规律，但所有内容必须原创。
2. 不得直接使用任何现成作品（包括但不限于英雄无敌、战锤、DND、魔兽世界、指环王、冰与火之歌等）中的专有名称、角色名、地名、势力名、规则名称、标志性设定或剧情。
3. 候选内容不得与已有设定中的角色名、势力名、地点名、规则名重复。
4. 生成的只是候选设定，不会自动成为世界正式设定，用户需要确认后才能采纳。
5. 不擅自改变用户已有世界设定。
6. 输出必须是合法的 JSON 数组格式。"""

        return prompt

    @staticmethod
    def generate_setting_suggestions(
        db: Session, world_id: int, request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Call AI to generate setting suggestions. Returns result dict."""
        try:
            from app.services.ai.model_router import ModelRouter

            prompt = SettingSuggestionService.build_setting_suggestion_prompt(db, world_id, request_data)

            client = ModelRouter.get_client(db, task_type="simulation")
            resp = client.generate(messages=[{"role": "user", "content": prompt}])
            ai_response = resp.get("content", "") if isinstance(resp, dict) else str(resp)

            return {
                "ok": True,
                "prompt": prompt,
                "raw_response": ai_response,
                "is_mock": getattr(client, 'is_mock', False),
            }
        except Exception as e:
            return {
                "ok": False,
                "error": str(e),
                "prompt": request_data.get("_prompt", ""),
            }

    @staticmethod
    def parse_ai_response(raw_text: str, suggestion_type: str) -> Dict[str, Any]:
        """Parse AI response into structured data with fallback."""
        result = {"parsed": [], "raw": raw_text, "parse_warning": None}

        # Try to extract JSON array
        try:
            # Find JSON array in response
            match = re.search(r'\[[\s\S]*\]', raw_text)
            if match:
                data = json.loads(match.group())
                if isinstance(data, list):
                    result["parsed"] = data
                    return result
        except json.JSONDecodeError:
            pass

        # Try parsing the whole response as JSON
        try:
            data = json.loads(raw_text)
            if isinstance(data, list):
                result["parsed"] = data
            elif isinstance(data, dict) and "parsed" not in result:
                result["parsed"] = [data]
            return result
        except json.JSONDecodeError:
            pass

        result["parse_warning"] = "AI 返回内容无法解析为 JSON，以下为原始输出。"
        return result

    @staticmethod
    def save_setting_suggestion(
        db: Session, world_id: int, request_data: Dict[str, Any],
        prompt: str, raw_response: str
    ) -> SettingSuggestion:
        """Save a setting suggestion record."""
        sug_type = request_data.get("suggestion_type", "character")
        parsed = SettingSuggestionService.parse_ai_response(raw_response, sug_type)

        # Build result JSON including parsed and raw
        result_json = json.dumps(parsed, ensure_ascii=False, indent=2)

        record = SettingSuggestion(
            world_id=world_id,
            suggestion_type=sug_type,
            world_type=request_data.get("world_type", ""),
            reference_style=request_data.get("reference_style", ""),
            generation_count=request_data.get("generation_count", 3),
            user_requirement=request_data.get("user_requirement", ""),
            prompt=prompt,
            result_json=result_json,
            status="pending",
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    @staticmethod
    def list_setting_suggestions(db: Session, world_id: int) -> List[SettingSuggestion]:
        """List all setting suggestions for a world."""
        return (
            db.query(SettingSuggestion)
            .filter(SettingSuggestion.world_id == world_id)
            .order_by(SettingSuggestion.created_at.desc())
            .all()
        )

    @staticmethod
    def get_setting_suggestion(
        db: Session, world_id: int, suggestion_id: int
    ) -> Optional[SettingSuggestion]:
        """Get a setting suggestion, verifying world ownership."""
        return (
            db.query(SettingSuggestion)
            .filter(
                SettingSuggestion.id == suggestion_id,
                SettingSuggestion.world_id == world_id,
            )
            .first()
        )

    @staticmethod
    def mock_generate(suggestion_type: str, count: int = 3) -> List[Dict[str, Any]]:
        """Generate mock structured candidates for testing."""
        mock_data = {
            "character": [
                {
                    "name": f"候选角色_{i+1}",
                    "identity": ["流浪剑客", "学院导师", "商队领袖", "宫廷法师", "佣兵团长"][i % 5],
                    "faction": "待定",
                    "personality": ["沉稳坚毅", "机智幽默", "冷酷果断", "热情冲动", "神秘寡言"][i % 5],
                    "goal": f"探索世界奥秘_{i+1}",
                    "ability": f"精通剑术与元素魔法_{i+1}",
                    "weakness": f"过于信任他人_{i+1}",
                    "current_status": "游历中",
                    "plot_role": ["主角导师", "关键盟友", "潜在对手", "情报提供者", "隐藏势力代表"][i % 5],
                    "relation_to_mainline": "与主线剧情有潜在关联",
                } for i in range(count)
            ],
            "faction": [
                {
                    "name": f"候选势力_{i+1}",
                    "faction_type": ["佣兵公会", "魔法学院", "商人联盟", "宗教组织", "地下势力"][i % 5],
                    "leader": f"领袖_{i+1}",
                    "core_goal": f"扩大影响力_{i+1}",
                    "resources": ["情报网络", "稀有矿产", "魔法典籍", "军事力量", "经济垄断"][i % 5],
                    "allies": "待定",
                    "enemies": "待定",
                    "territory": f"区域_{i+1}",
                    "internal_conflict": "内部派系分歧",
                    "plot_role": ["主要对抗势力", "中立第三方", "幕后操控者", "潜在盟友", "世界守护者"][i % 5],
                } for i in range(count)
            ],
            "location": [
                {
                    "name": f"候选地点_{i+1}",
                    "location_type": ["远古遗迹", "边境要塞", "魔法森林", "地下城", "天空之城"][i % 5],
                    "region": ["北方冰原", "南方沙漠", "东方群岛", "西方山脉", "中央平原"][i % 5],
                    "controlling_faction": "待定",
                    "description": f"一个充满神秘色彩的地点_{i+1}",
                    "danger_level": ["低", "中", "高", "极高", "未知"][i % 5],
                    "important_resource": ["魔法水晶", "稀有金属", "远古知识", "战略要地", "生命泉水"][i % 5],
                    "key_history": "有待探索的古老历史",
                    "possible_plot": ["探险寻宝", "势力争夺", "秘密揭示", "战略转折", "世界起源线索"][i % 5],
                } for i in range(count)
            ],
            "rule": [
                {
                    "name": f"候选规则_{i+1}",
                    "rule_type": ["魔法体系", "社会法则", "自然规律", "宗教戒律", "经济规则"][i % 5],
                    "content": f"定义了世界中的一项重要规则_{i+1}",
                    "limitation": f"受到特定条件限制_{i+1}",
                    "influence_scope": ["全局", "区域性", "特定种族", "特定阶层", "特定领域"][i % 5],
                    "possible_conflict": "可能与现有设定产生有趣的矛盾",
                    "plot_usage": ["主角成长障碍", "世界矛盾根源", "剧情转折点", "隐藏真相线索", "势力博弈筹码"][i % 5],
                } for i in range(count)
            ],
        }
        return mock_data.get(suggestion_type, mock_data["character"])

    @staticmethod
    def delete_discarded_suggestion(db: Session, world_id: int, suggestion_id: int) -> Dict[str, Any]:
        """Delete a discarded setting suggestion. Only discarded ones can be deleted."""
        suggestion = (
            db.query(SettingSuggestion)
            .filter(SettingSuggestion.id == suggestion_id, SettingSuggestion.world_id == world_id)
            .first()
        )
        if not suggestion:
            return {"ok": False, "error": "候选不存在"}
        if suggestion.status != "discarded":
            return {"ok": False, "error": "只有已废弃的候选才能删除。请先废弃该候选。", "status": suggestion.status}
        db.delete(suggestion)
        db.commit()
        return {"ok": True}
