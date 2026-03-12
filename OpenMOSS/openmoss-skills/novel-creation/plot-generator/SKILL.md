# SKILL.md - 情节生成Skill

## 概述
AI小说情节生成器，设计引人入胜的故事线和情节发展。

## 输入
- **plot_type**: 情节类型（升级/复仇/探案/恋爱/战争/冒险等）
- **pacing**: 节奏（快节奏/中等/慢热）
- **chapter_count**: 预计章节数
- **worldview**: 世界观设定
- **characters**: 主要角色信息
- **twist_needed**: 是否需要反转（是/否/随机）

## 输出
完整的情节大纲，包含：
- 主线剧情
- 支线剧情
- 关键转折点
- 高潮设计
- 悬念设置
- 章节概要

## 使用示例
```
plot_type: 升级
pacing: 快节奏
chapter_count: 100
twist_needed: 是
```

## 调用方式
```json
{
  "skill": "plot-generator",
  "params": {
    "plot_type": "升级",
    "pacing": "快节奏",
    "chapter_count": 100,
    "twist_needed": "是"
  }
}
```

## 注意事项
- 升级类情节需设置合理的实力等级体系
- 每10章设置一个小高潮
- 每30章设置一个大转折
