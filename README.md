# Japanese Mode - 日语输出模式

![AstrBot](https://img.shields.io/badge/AstrBot-%3E%3D4.16.0-blue)

## 简介

让 AI 用日语回复，动作/神态描写保持中文，末尾附完整中文翻译。

## 效果示例

```
用户：在干嘛？
AI：（啃法棍）なに言ってるの、バカ～（翻译：你在说什么啊，笨蛋～）

用户：今天好累
AI：（叹气）ばか、疲れたなら早く寝なよ（翻译：笨蛋，累了就赶紧睡啦）
```

## 指令

| 指令 | 用途 |
|------|------|
| `/japanese on` | 开启日语模式 |
| `/japanese off` | 关闭日语模式 |
| `/japanese status` | 查看当前状态 |

## 工作原理

- 通过 `@filter.on_llm_request()` 在每次 LLM 请求前注入日语输出指令
- 不修改原有 system prompt（人设），只在末尾追加
- 默认开启，每个会话独立存储开关状态
- **token 开销**：每条回复末尾多一段中文翻译（约 30~50 字），对于 30 字级别的回复，开销可接受

## 兼容性

- AstrBot >= 4.16.0
- 无外部依赖
- 与 proactive_chat、smart_context 等插件兼容（日语指令对主动消息同样生效）

## 许可

MIT
