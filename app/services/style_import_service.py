"""
AI World Engine - Style Import Service
v2.4.0: TXT file upload, encoding detection, text cleaning, chunking,
AI style analysis, and style profile generation.
Only extracts abstract style rules — never copies original text.
"""

import hashlib
import json
import re
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple, BinaryIO
from sqlalchemy.orm import Session

from app.models import StyleProfile, StyleSourceAnalysis


def _utcnow():
    return datetime.now(timezone.utc)

def _safe_json_dumps(obj, default="{}"):
    try: return json.dumps(obj, ensure_ascii=False, indent=2)
    except: return default

# Max file size: 10MB
MAX_FILE_SIZE = 10 * 1024 * 1024
# Chunk size for analysis: ~5000 chars
CHUNK_SIZE = 5000
# Max chunks to analyze
MAX_CHUNKS = 6


class StyleImportService:
    """Service for TXT style import and analysis."""

    @staticmethod
    def detect_text_encoding(file_bytes: bytes) -> str:
        """Detect text encoding. Supports UTF-8, UTF-8-SIG, GBK."""
        # Try UTF-8-SIG (with BOM)
        if file_bytes[:3] == b'\xef\xbb\xbf':
            return 'utf-8-sig'
        # Try UTF-8
        try:
            file_bytes.decode('utf-8')
            return 'utf-8'
        except UnicodeDecodeError:
            pass
        # Try GBK
        try:
            file_bytes.decode('gbk')
            return 'gbk'
        except (UnicodeDecodeError, LookupError):
            pass
        raise ValueError("无法识别文件编码，请尝试 UTF-8 或 GBK 编码的 TXT 文件")

    @staticmethod
    def read_txt_file(file: BinaryIO) -> Tuple[str, str, int]:
        """Read TXT file, return (text, encoding, char_count)."""
        file_bytes = file.read()
        if not file_bytes:
            raise ValueError("文件为空")

        if len(file_bytes) > MAX_FILE_SIZE:
            raise ValueError(f"文件过大（最大 {MAX_FILE_SIZE // (1024*1024)}MB）")

        encoding = StyleImportService.detect_text_encoding(file_bytes)
        text = file_bytes.decode(encoding)
        char_count = len(text)
        if char_count < 100:
            raise ValueError("文件内容过短（少于100字），无法分析风格")
        return text, encoding, char_count

    @staticmethod
    def clean_style_source_text(text: str) -> str:
        """Clean source text: remove ads, normalize whitespace, keep structure."""
        lines = text.splitlines()
        cleaned = []
        for line in lines:
            stripped = line.strip()
            # Skip obvious ad lines
            if any(kw in stripped for kw in ['更多小说', '最新章节', 'www.', 'http://', '手机阅读', '加入书架']):
                continue
            cleaned.append(stripped)
        # Remove excessive blank lines (keep max 2 consecutive)
        result = []
        blank_count = 0
        for line in cleaned:
            if not line:
                blank_count += 1
                if blank_count <= 2:
                    result.append(line)
            else:
                blank_count = 0
                result.append(line)
        return '\n'.join(result)

    @staticmethod
    def split_text_for_style_analysis(text: str) -> List[str]:
        """Split text into chunks for analysis. Try chapter headers first, then by size."""
        # Try to split by chapter headers
        chapter_pattern = re.compile(r'^(第[零一二三四五六七八九十百千\d]+[章节回卷]|Chapter\s+\d+)', re.IGNORECASE | re.MULTILINE)
        chapters = re.split(chapter_pattern, text)
        # Filter empty and very short segments
        meaningful = [c for c in chapters if len(c) > 200]

        if len(meaningful) >= 3:
            # Sample: first, middle, last chapters, plus some from middle
            chunks = []
            n = len(meaningful)
            indices = [0]  # first
            if n > 2: indices.append(n // 2)  # middle
            if n > 1: indices.append(n - 1)  # last
            # Add more if available
            if n > 4: indices.append(n // 4)
            if n > 6: indices.append(3 * n // 4)
            for i in sorted(set(indices)):
                chunk = meaningful[i][:CHUNK_SIZE]
                if len(chunk) > 100:
                    chunks.append(chunk)
            if chunks:
                return chunks[:MAX_CHUNKS]

        # Fallback: split by character count
        chunks = []
        clean = text.replace('\n\n', '\n')
        for i in range(0, min(len(clean), MAX_CHUNKS * CHUNK_SIZE), CHUNK_SIZE):
            chunk = clean[i:i + CHUNK_SIZE]
            if len(chunk) > 100:
                chunks.append(chunk)
        return chunks[:MAX_CHUNKS]

    @staticmethod
    def build_chunk_style_prompt(chunk_text: str, chunk_index: int, total_chunks: int) -> str:
        """Build prompt for analyzing a single text chunk's style."""
        return f"""你是一位写作风格分析师。请分析以下文本片段（第 {chunk_index + 1}/{total_chunks} 块）的抽象写作风格特征。

**重要规则：**
- 只能提取抽象写作方法论，例如叙事节奏、段落结构、描写密度、对话比例、冲突推进方式等。
- 不得复制原文长句。
- 不得输出人物名、设定名、专有名词。
- 不得记住具体剧情桥段。
- 只输出该块的风格特征摘要。

**分析维度：**
1. 叙事人称（第几人称）
2. 句式风格（短句/长句/交替）
3. 段落长度（短/中/长）
4. 对话比例（高/中/低）
5. 描写密度（高/中/低）
6. 动作推进方式
7. 冲突呈现方式
8. 信息释放方式
9. 章节结构特征

**文本片段：**
{chunk_text[:CHUNK_SIZE]}
"""

    @staticmethod
    def build_final_style_profile_prompt(chunk_summaries: List[str]) -> str:
        """Build prompt for merging chunk analyses into a final style profile."""
        summaries_text = "\n---\n".join(chunk_summaries)
        return f"""你是一位写作风格分析师。请基于以下多个文本块的分析摘要，生成一份完整的写作风格画像 JSON。

**重要规则：**
- 只能输出抽象写作方法论。
- 不得复制原文句子。
- 不得使用原文中的人物名、设定名、专有名词。
- 不得描述具体剧情桥段。
- 这是写作指导，不是模仿某本小说的指南。

**各段分析摘要：**
{summaries_text}

**请输出以下 JSON 格式（只输出 JSON，不要有其他文字）：**
```json
{{
  "name": "风格画像名称（简洁）",
  "description": "整体风格概述（2-3句中文）",
  "narrative_person": "叙事人称",
  "narrative_distance": "叙事距离",
  "pacing": "节奏",
  "prose_density": "描写密度",
  "dialogue_ratio": "对话比例",
  "description_ratio": "描写比例",
  "sentence_style": "句式风格",
  "paragraph_style": "段落风格",
  "conflict_style": "冲突推进方式",
  "character_style": "人物塑造方式",
  "scene_style": "场景描写方式",
  "emotion_style": "情绪表达方式",
  "information_release_style": "信息释放方式",
  "foreshadowing_style": "伏笔方式",
  "chapter_opening_style": "章节开头习惯",
  "chapter_ending_hook_style": "章末钩子习惯",
  "style_rules": ["规则1", "规则2"],
  "do_rules": ["应做的1", "应做的2"],
  "avoid_rules": ["不得复制源文本专有名词", "避免使用源文本中的人物名"],
  "suitable_for": ["类型1"],
  "generation_prompt_snippet": "用于正文生成的简短约束文本（2-3句）"
}}
```
"""

    @staticmethod
    def generate_style_profile_from_txt(
        db: Session, world_id: int, file: BinaryIO, filename: str, request_data: Dict
    ) -> Tuple[StyleProfile, StyleSourceAnalysis]:
        """Full pipeline: read file → analyze → save style profile."""
        # Read and clean
        text, encoding, char_count = StyleImportService.read_txt_file(file)
        cleaned = StyleImportService.clean_style_source_text(text)

        # Hash
        file_hash = hashlib.sha256(cleaned.encode('utf-8')).hexdigest()[:32]

        # Chunk
        chunks = StyleImportService.split_text_for_style_analysis(cleaned)
        chunk_count = len(chunks)

        # Create analysis record
        analysis = StyleSourceAnalysis(
            world_id=world_id,
            source_filename=filename,
            source_file_hash=file_hash,
            source_file_size=len(text.encode(encoding)),
            source_char_count=char_count,
            encoding=encoding,
            chunk_count=chunk_count,
            sample_strategy=f"chapter+size:{CHUNK_SIZE}:max{MAX_CHUNKS}",
            analysis_status="analyzing",
            created_at=_utcnow(),
            updated_at=_utcnow(),
        )
        db.add(analysis)
        db.commit()
        db.refresh(analysis)

        # Analyze chunks (mock or real AI)
        from app.config import settings
        from app.services.settings_service import SettingsService
        config = SettingsService.get_effective_config(db)
        is_mock = not config.get("ai_enable_live") or config.get("ai_provider") == "mock"

        if is_mock:
            chunk_summaries, final_json = StyleImportService._mock_analyze(chunks, chunk_count)
        else:
            try:
                from app.services.ai.model_router import ModelRouter
                chunk_summaries = []
                for i, chunk in enumerate(chunks):
                    prompt = StyleImportService.build_chunk_style_prompt(chunk, i, chunk_count)
                    summary = ModelRouter.generate(prompt)
                    chunk_summaries.append(summary)
                final_prompt = StyleImportService.build_final_style_profile_prompt(chunk_summaries)
                raw_final = ModelRouter.generate(final_prompt)
                final_json = StyleImportService._parse_style_json(raw_final)
            except Exception as e:
                analysis.analysis_status = "failed"
                analysis.error_message = str(e)
                analysis.updated_at = _utcnow()
                db.commit()
                raise RuntimeError(f"风格分析失败: {str(e)}")

        # Update analysis record
        analysis.chunk_summaries_json = _safe_json_dumps(chunk_summaries)
        analysis.final_analysis_json = final_json
        analysis.raw_ai_summary = final_json
        analysis.analysis_status = "completed"
        analysis.updated_at = _utcnow()

        # Create style profile
        profile = StyleImportService.save_style_profile_from_analysis(
            db, world_id, analysis, final_json, request_data.get("profile_name", "")
        )
        analysis.style_profile_id = profile.id
        db.commit()

        return profile, analysis

    @staticmethod
    def _mock_analyze(chunks: List[str], chunk_count: int) -> Tuple[List[str], str]:
        """Mock style analysis returning stable results."""
        summaries = []
        for i in range(min(chunk_count, MAX_CHUNKS)):
            summaries.append(f"块{i+1}: 第三人称有限视角, 中快节奏, 对话比例中等偏高, 段落较短, 冲突驱动推进。")
        final = json.dumps({
            "name": "测试小说风格画像",
            "description": "中快节奏、冲突驱动、段落较短、动作与对话推动剧情。",
            "narrative_person": "第三人称有限视角",
            "narrative_distance": "贴近主角心理",
            "pacing": "中快",
            "prose_density": "中等",
            "dialogue_ratio": "中等偏高",
            "description_ratio": "中等",
            "sentence_style": "短句与中长句交替，动作句推动剧情",
            "paragraph_style": "段落较短，适合网文阅读",
            "conflict_style": "通过明确目标、阻碍和反转推进",
            "character_style": "人物通过行动和选择体现性格",
            "scene_style": "场景描写服务冲突，不做长篇静态铺陈",
            "emotion_style": "情绪表达克制，重视内心动机",
            "information_release_style": "分层释放信息",
            "foreshadowing_style": "轻量伏笔",
            "chapter_opening_style": "开篇快速进入矛盾",
            "chapter_ending_hook_style": "以危机或悬念结尾",
            "style_rules": ["保持中快节奏", "每段不超过5行", "对话占比40%左右"],
            "do_rules": ["用动作推进剧情", "每章结尾留悬念", "人物动机要清晰"],
            "avoid_rules": ["不得复制源文本专有名词", "避免使用源文本中的人物名", "不得大段环境描写"],
            "suitable_for": ["玄幻", "奇幻", "升级流"],
            "generation_prompt_snippet": "使用第三人称有限视角，中快节奏推进，段落简短，对话占比40%左右，每章结尾留悬念。人物通过行动体现性格，冲突驱动剧情。"
        }, ensure_ascii=False)
        return summaries, final

    @staticmethod
    def _parse_style_json(raw: str) -> str:
        """Parse AI response into valid style JSON."""
        # Try to extract JSON from code blocks
        match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', raw, re.DOTALL)
        if match:
            try:
                json.loads(match.group(1))
                return match.group(1)
            except: pass
        # Try direct parse
        try:
            json.loads(raw)
            return raw
        except: pass
        # Fallback
        return _safe_json_dumps({"parse_warning": "解析失败", "raw_text": raw[:1000]})

    @staticmethod
    def save_style_profile_from_analysis(
        db: Session, world_id: int, analysis: StyleSourceAnalysis,
        final_json: str, profile_name: str = ""
    ) -> StyleProfile:
        """Create or update a StyleProfile from analysis results."""
        data = {}
        try:
            data = json.loads(final_json)
        except: pass

        profile = StyleProfile(
            world_id=world_id,
            name=profile_name or data.get("name", "导入风格"),
            description=data.get("description", ""),
            narrative_pov=data.get("narrative_person", ""),
            pacing=data.get("pacing", ""),
            sentence_style=data.get("sentence_style", ""),
            paragraph_style=data.get("paragraph_style", ""),
            description_ratio=data.get("description_ratio", ""),
            dialogue_style=data.get("dialogue_ratio", ""),
            conflict_style=data.get("conflict_style", ""),
            character_style=data.get("character_style", ""),
            emotion_style=data.get("emotion_style", ""),
            opening_style=data.get("chapter_opening_style", ""),
            ending_hook_style=data.get("chapter_ending_hook_style", ""),
            info_release_style=data.get("information_release_style", ""),
            source_type="txt_analysis",
            source_analysis_id=analysis.id,
            style_rules_json=_safe_json_dumps(data.get("style_rules", [])),
            do_rules="\n".join(data.get("do_rules", [])) if isinstance(data.get("do_rules"), list) else data.get("do_rules", ""),
            avoid_rules="\n".join(data.get("avoid_rules", [])) if isinstance(data.get("avoid_rules"), list) else data.get("avoid_rules", ""),
            generation_prompt_snippet=data.get("generation_prompt_snippet", ""),
            is_active=True,
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
        return profile

    @staticmethod
    def apply_style_profile_to_prompt(profile: Optional[StyleProfile]) -> str:
        """Build a style constraint text for inclusion in generation prompts."""
        if not profile:
            return ""
        parts = []
        if profile.generation_prompt_snippet:
            parts.append(f"写作风格约束: {profile.generation_prompt_snippet}")
        if profile.narrative_pov:
            parts.append(f"叙事视角: {profile.narrative_pov}")
        if profile.pacing:
            parts.append(f"节奏: {profile.pacing}")
        if profile.sentence_style:
            parts.append(f"句式: {profile.sentence_style}")
        if profile.paragraph_style:
            parts.append(f"段落: {profile.paragraph_style}")
        if profile.dialogue_style:
            parts.append(f"对话: {profile.dialogue_style}")
        if profile.conflict_style:
            parts.append(f"冲突: {profile.conflict_style}")
        if profile.avoid_rules:
            parts.append(f"禁止: {profile.avoid_rules.replace(chr(10), '; ')}")
        if profile.forbidden_patterns:
            parts.append(f"避免: {profile.forbidden_patterns}")
        if parts:
            return "【写作风格要求】\n" + "\n".join(parts) + "\n\n"
        return ""
