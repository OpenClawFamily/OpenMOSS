# SKILL.md - AI小说创作助手

## 概述
整合型AI小说创作Skill，协同调用各专业模块完成小说创作全流程。

## 模块组成
本Skill体系包含以下子Skill：

### 1. 世界观生成 (worldview-generator)
- 功能：创建完整的小说世界设定
- 适用：开篇设定世界背景

### 2. 角色生成 (character-generator)
- 功能：创建有深度的故事人物
- 适用：需要新角色时调用

### 3. 情节生成 (plot-generator)
- 功能：设计故事线和情节发展
- 适用：规划章节大纲

### 4. 润色修改 (polish-editor)
- 功能：提升文本质量
- 适用：初稿完成后的修改

## 使用流程

### 第一阶段：世界观设定
```
→ 调用 worldview-generator
→ 生成完整世界背景
```

### 第二阶段：角色创建
```
→ 调用 character-generator (可多次)
→ 为每个主要角色生成档案
```

### 第三阶段：情节规划
```
→ 调用 plot-generator
→ 生成章节大纲
```

### 第四阶段：内容创作
```
→ 基于大纲撰写正文
→ 过程中可调用角色生成补充角色
```

### 第五阶段：润色完善
```
→ 调用 polish-editor (可多次)
→ 优化全文质量
```

## 协同工作示例

```json
{
  "workflow": "novel-creation",
  "stages": [
    {
      "skill": "worldview-generator",
      "input": {"genre": "都市", "tone": "轻松", "scope": "中等"}
    },
    {
      "skill": "character-generator", 
      "input": {"role_type": "主角", "count": 3}
    },
    {
      "skill": "plot-generator",
      "input": {"chapter_count": 50}
    }
  ]
}
```

## 验收标准
- Skill体系完整可用
- 各Skill能协同工作
- 产出符合质量标准的小说内容
