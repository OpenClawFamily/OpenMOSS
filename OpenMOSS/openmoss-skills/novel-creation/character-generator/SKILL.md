# SKILL.md - 角色生成Skill

## 概述
AI小说角色生成器，创建有深度、有特色的故事人物。

## 输入
- **role_type**: 角色类型（主角/反派/配角/导师/酱油等）
- **genre**: 小说类型
- **worldview**: 已有的世界观设定（可选）
- **character_arc**: 角色成长弧线（可选）
- **relation_to_main**: 与主角关系（可选）

## 输出
完整的角色档案，包含：
- 基础信息（姓名、年龄、外貌）
- 性格特点
- 背景故事
- 能力/技能
- 动机与目标
- 成长弧线
- 标志性特征

## 使用示例
```
role_type: 主角
genre: 玄幻
character_arc: 从废物到强者
```

## 调用方式
```json
{
  "skill": "character-generator",
  "params": {
    "role_type": "主角",
    "genre": "玄幻",
    "character_arc": "从废物到强者"
  }
}
```
