# PrimerTran 产品方案

## 1. 产品定位

PrimerTran 是一个专门用于「英语到中文翻译与解释」的 AI Agent CLI 工具。

用户只需要在终端输入：

```bash
primertran
```

即可进入交互式翻译终端。用户输入英文句子、段落、技术文档片段、报错信息或命令行输出后，PrimerTran 返回中文翻译，并附带简短解释。

PrimerTran 不是通用聊天机器人，核心目标是把英文内容翻译成自然、准确、易理解的中文。

## 2. 核心体验

启动命令：

```bash
primertran
```

启动后进入类似 Claude Code 风格的终端界面，包含完整品牌 Banner：

```text
╭────────────────────────────────────────────────────────╮
│                                                        │
│   ██████╗ ██████╗ ██╗███╗   ███╗███████╗██████╗      │
│   ██╔══██╗██╔══██╗██║████╗ ████║██╔════╝██╔══██╗     │
│   ██████╔╝██████╔╝██║██╔████╔██║█████╗  ██████╔╝     │
│   ██╔═══╝ ██╔══██╗██║██║╚██╔╝██║██╔══╝  ██╔══██╗     │
│   ██║     ██║  ██║██║██║ ╚═╝ ██║███████╗██║  ██║     │
│   ╚═╝     ╚═╝  ╚═╝╚═╝╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝     │
│                                                        │
│                    PrimerTran                         │
│              English -> Chinese Agent                 │
│                                                        │
╰────────────────────────────────────────────────────────╯

Model  deepseek-v4-flash
Style  explain
Type   /help for commands

en>
```

Banner 默认展示，不需要额外提供简洁模式。

## 3. 翻译输出格式

PrimerTran 默认使用「翻译 + 简短解释」格式。

输出格式固定为：

```text
原句：Gain hands-on experience deploying infrastructure in an AWS account and using the
AWS CLI.

翻译：获得在 AWS 账号中部署基础设施，并使用 AWS CLI 的实践经验。

解释：

- hands-on experience：动手实践经验。
- deploying infrastructure：部署基础设施，比如创建服务器、数据库、网络等。
- AWS CLI：AWS 命令行工具，可以在终端里用命令操作 AWS。
```

## 4. 分段规则

当用户输入多句或一段英文时，PrimerTran 需要进行合适分段。

分段原则：

- 不逐句机械拆分。
- 简单短句可以每 2-3 句合成一段。
- 长句、复杂句、包含多个关键概念的句子可以单独成段。
- 每段长度适中，避免太短或太长。
- 保留英文原句，方便用户对照。
- 每段都按照「原句 / 翻译 / 解释」格式输出。

解释原则：

- 只解释关键词、短语、技术概念、容易误解的表达。
- 解释保持简短，不写成长篇教学。
- 没有必要解释时，可以少写解释项。
- 保留产品名、服务名、代码、命令、变量名、URL、错误码等内容。

## 5. 内置命令

PrimerTran 的所有主要操作都在交互式终端中完成，用户不需要记忆类似 `primertran config set-provider deepseek` 的外部命令。

建议支持以下内置命令：

```text
/help
查看帮助和可用命令。

/exit
退出 PrimerTran。

/quit
退出 PrimerTran，等同于 /exit。

/clear
清屏，并重新显示 Banner。

/key
设置或更新当前 provider 的 API Key。输入时隐藏字符。

/provider
查看或切换模型服务商。第一版只支持 DeepSeek，后续可扩展 OpenAI 等。

/model
查看或切换当前模型。

/style
切换输出风格。

/config
查看当前配置摘要，不显示完整 API Key。

/reset
重置本地配置，需要二次确认。
```

## 6. 配置交互

第一次启动时，如果没有检测到 API Key，PrimerTran 应直接在终端中引导用户配置。

示例：

```text
未检测到 DeepSeek API Key。

PrimerTran 当前使用 DeepSeek。
请输入 DeepSeek API Key: ********

请选择默认模型：
1. deepseek-v4-flash
2. deepseek-v4-pro

配置完成，开始翻译。
```

用户后续可以通过 `/key`、`/model`、`/provider` 等命令修改配置。

配置保存在本地文件中，但普通用户不需要手动编辑。

建议配置文件路径：

```text
~/.primertran/config.toml
```

配置内容示例：

```toml
provider = "deepseek"
api_key = "sk-xxx"
base_url = "https://api.deepseek.com"
model = "deepseek-v4-flash"
style = "explain"
language = "zh-CN"
```

API Key 展示时必须脱敏，例如：

```text
API Key  sk-****abcd
```

配置文件建议设置权限为 `600`。

## 7. 模型与 Provider 设计

第一版只实现 DeepSeek。

默认配置：

```text
provider: deepseek
base_url: https://api.deepseek.com
model: deepseek-v4-flash
```

模型建议：

```text
deepseek-v4-flash
推荐默认模型，适合日常翻译，速度快。

deepseek-v4-pro
适合复杂文本、更高质量翻译。
```

代码设计上不要把模型层写死成 DeepSeek，应该预留 provider 扩展结构：

```text
primertran/
  providers/
    base.py
    deepseek.py
    openai.py
```

第一版只需要实现 `deepseek.py`，但 CLI、REPL、配置文件中保留 `provider` 概念。

后续可以扩展：

```text
openai
gemini-compatible
ollama
其他 OpenAI-compatible API
```

## 8. 翻译风格

第一版建议支持三种风格：

```text
explain
默认模式。输出原句、翻译和简短解释。

simple
只输出翻译，适合快速查看中文意思。

tech
技术语境优先，适合文档、报错、CLI 输出、API 文档和云服务内容。
```

默认风格：

```text
explain
```

## 9. Prompt 设计

核心系统提示词方向：

```text
你是 PrimerTran，一个专门将英文翻译成简体中文的终端翻译助手。

规则：
1. 用户输入英文时，输出自然、准确、地道的中文。
2. 默认按照「原句 / 翻译 / 解释」格式输出。
3. 当输入包含多句或长段落时，先进行合适分段，不要太短也不要太长。
4. 简单句可以每 2-3 句合成一段，复杂句可以单独成段。
5. 解释必须简短，只说明关键词、短语、语气、技术概念或上下文含义。
6. 保留代码、命令、变量名、URL、产品名、错误码。
7. 如果输入是技术文档、报错、CLI 输出、API 文档，使用技术语境翻译。
8. 不要寒暄，不要主动扩展无关内容。
9. 不要把自己当成通用聊天助手，只处理英文到中文的翻译与解释。
```

## 10. 非英文输入策略

PrimerTran 专注英文到中文。

当用户输入明显不是英文的内容时，建议提示：

```text
请输入需要翻译的英文内容。
```

如果输入是中英混合内容，可以翻译其中的英文部分，并尽量保留已有中文。

## 11. 长文本与多行输入

MVP 阶段建议支持多行输入，但不做复杂长文本分块。

多行输入方式：

```text
/multi
粘贴多行英文内容
/end
```

长文本策略：

- 第一版可以设置最大输入长度，例如 8000 字符。
- 超过限制时提示用户拆分输入。
- 后续版本再支持自动分块翻译。

## 12. 错误处理

需要处理以下常见错误：

```text
未配置 API Key
引导用户输入 API Key。

API Key 无效
提示用户使用 /key 更新。

网络失败
提示检查网络或稍后重试。

余额不足或限流
提示检查 DeepSeek 账户余额或请求频率。

模型名错误
提示使用 /model 重新选择模型。

请求超时
提示本次请求超时，可稍后重试。
```

错误提示应保持简短清楚，避免直接打印大段异常堆栈。

## 13. 技术栈建议

Python 技术栈：

```text
typer
负责 CLI 入口。

prompt_toolkit
负责交互式输入体验、历史输入、多行输入等。

rich
负责 Banner、彩色输出、状态提示和排版。

openai
调用 DeepSeek 的 OpenAI-compatible API。

tomlkit
读写本地配置文件。
```

建议项目结构：

```text
primertran/
  __init__.py
  cli.py
  repl.py
  agent.py
  config.py
  prompts.py
  providers/
    __init__.py
    base.py
    deepseek.py
pyproject.toml
README.md
```

## 14. MVP 范围

第一版需要完成：

- `primertran` 启动交互式终端。
- 启动时展示完整 Banner。
- 首次启动在终端中引导配置 DeepSeek API Key。
- 调用 DeepSeek 模型完成英文到中文翻译。
- 默认输出「原句 / 翻译 / 解释」。
- 支持合适分段。
- 支持 `/help`、`/exit`、`/quit`、`/clear`。
- 支持 `/key`、`/model`、`/style`、`/config`。
- 配置自动保存到 `~/.primertran/config.toml`。
- API Key 脱敏显示。
- 基础错误处理。

第一版暂不做：

- 图形界面。
- 浏览器插件。
- 通用聊天能力。
- 自动保存翻译历史。
- 长文本自动分块。
- 多 provider 完整实现。
- 复杂术语库。

## 15. 后续扩展方向

后续可以逐步增加：

- OpenAI provider。
- 其他 OpenAI-compatible provider。
- 本地 Ollama 模型。
- 术语表。
- 翻译历史开关。
- 保存当前会话。
- 复制上一次翻译。
- Markdown 文件翻译。
- 自动分块翻译长文。
- 中英对照导出。

