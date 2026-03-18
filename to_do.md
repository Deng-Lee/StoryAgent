# StorySage 重构待办

## 总体目标

让当前实现与简历中的系统描述尽量对齐，优先完成以下能力：

1. 将 prompt 资产内化为应用内的 Skill / Runtime 层
2. 将当前 XML 工具协议逐步迁移到原生 Function Calling
3. 为 `SessionScribe` 增加 SFT 数据导出、训练与推理接入闭环
4. 补齐可复现的评测流程与结果产出

---

## 第一阶段：Prompt Skill 内化

### 阶段目标

在不改变当前 Agent 行为、不影响 XML 工具调用链路的前提下，将各 Agent 中分散的 prompt 资产重构为应用内可组合的 skill 模块。

### 已完成回填（2026-03-18）

已完成的增量：

- 已新增基础运行时文件：
  - `src/utils/prompt_templates.py`
  - `src/utils/skill_loader.py`
  - `src/utils/prompt_runtime.py`
- 已新增最小可用的 skill 目录与资产：
  - `src/skills/shared/`
  - `src/skills/interviewer/normal/`
  - `src/skills/interviewer/baseline/`
- 已完成 `Interviewer` 的第一批迁移：
  - `src/agents/interviewer/interviewer.py` 已通过 `PromptRuntime` 组装 prompt
  - 旧 `src/agents/interviewer/prompts.py` 仍保留为兼容层和回退入口
- 已新增测试：
  - `tests/test_prompt_runtime.py`
  - `tests/test_interviewer_prompt_bundle.py`
- 已完成验证：
  - `python3 -m unittest discover -s tests -p 'test_*.py'`

当前状态说明：

- 第一阶段的基础设施已经落地，且 `Interviewer` 已作为首个迁移样板接入新 runtime
- `SessionScribe`、`Planner`、`SectionWriter`、`SessionCoordinator` 仍未迁移
- 第一阶段整体尚未完成，后续应继续按既定顺序推进其余 agent

新增进展回填：

- 已完成 `SessionScribe` 的第一批迁移：
  - `src/agents/session_scribe/session_scribe.py` 的 `update_memory_question_bank` 路径已通过 `PromptRuntime` 组装 prompt
  - 旧 `src/agents/session_scribe/prompts.py` 仍保留为兼容层和回退入口
- 已完成 `SessionScribe` 的第二批迁移：
  - `src/agents/session_scribe/session_scribe.py` 的 `update_session_agenda` 路径已通过 `PromptRuntime` 组装 prompt
  - `tests/test_session_scribe_prompt_bundle.py` 已覆盖 `update_memory_question_bank` 与 `update_session_agenda` 两条迁移路径的等价性
- 已完成 `SessionScribe` 的第三批迁移：
  - `src/agents/session_scribe/session_scribe.py` 的 `consider_and_propose_followups` 路径已通过 `PromptRuntime` 组装 prompt
  - `tests/test_session_scribe_prompt_bundle.py` 已覆盖 `SessionScribe` 三条 prompt 路径与 legacy prompt 的等价性
- 已完成 `Planner` 的第一批迁移：
  - `src/agents/biography_team/planner/planner.py` 的 `add_new_memory_planner` 路径已通过 `PromptRuntime` 组装 prompt
  - 旧 `src/agents/biography_team/planner/prompts.py` 仍保留为兼容层和回退入口
- 已完成 `Planner` 的第二批迁移：
  - `src/agents/biography_team/planner/planner.py` 的 `user_add_planner` 路径已通过 `PromptRuntime` 组装 prompt
  - `tests/test_planner_prompt_bundle.py` 已覆盖 `add_new_memory_planner` 与 `user_add_planner` 两条迁移路径的等价性
- 已新增 `SessionScribe` skill 资产：
  - `src/skills/session_scribe/update_memory_question_bank/`
  - `src/skills/session_scribe/update_session_agenda/`
  - `src/skills/session_scribe/consider_and_propose_followups/`
- 已新增 `Planner` skill 资产：
  - `src/skills/planner/add_new_memory_planner/`
  - `src/skills/planner/user_add_planner/`
- 已新增测试：
  - `tests/test_session_scribe_prompt_bundle.py`
  - `tests/test_planner_prompt_bundle.py`
- 为了让 `unittest discover` 稳定解析 `src/utils` 包，已新增：
  - `src/utils/__init__.py`
- 本次验证：
  - `python3 -m unittest discover -s tests -p 'test_*.py'`

本阶段剩余未完成内容：

- `Planner` 的 `user_comment_planner`
- `SectionWriter` 迁移
- `SessionCoordinator` 迁移
- 第一阶段总体验收与缺失 fallback 路径的进一步覆盖

### 需要新增的目录

- `src/skills/`
- `src/skills/shared/`
- `src/skills/interviewer/`
- `src/skills/session_scribe/`
- `src/skills/planner/`
- `src/skills/section_writer/`
- `src/skills/session_coordinator/`

### 需要新增的文件

- `src/utils/prompt_runtime.py`
  - `PromptModule`
  - `PromptBundle`
  - `PromptRuntime`
  - `build_prompt_bundle(agent_name, mode, task)`
  - `render_prompt(bundle, variables)`

- `src/utils/skill_loader.py`
  - `load_skill_text(path)`
  - `load_skill_pack(agent_name)`
  - `load_shared_modules()`

- `src/utils/prompt_templates.py`
  - 通用 prompt 格式化工具
  - 安全变量替换工具

### Skill 模块结构

每个 Agent 的 skill 包优先拆成以下模块：

- `persona.md`
- `policy.md`
- `tool_rules.md`
- `output_contract.md`
- `examples.md`（可选）

### 第一阶段实现方案细节

#### 1. 设计原则

- 第一阶段只重构 prompt 资产的存储和组装方式，不改变 agent 的业务流程、工具集合、事件流记录方式和 XML tool calling 协议
- skill 驱动的是 prompt composition layer，不是整个 agent runtime；agent 仍然负责收集运行时上下文、调用模型、执行工具
- 所有迁移都要求可回退：skill 文件缺失、加载失败或渲染异常时，自动退回旧 `prompts.py` 实现
- 迁移目标是“行为等价”，不是“文案重写”；现有 prompt 内容优先原样拆分，不在第一阶段顺手优化 prompt 策略

#### 2. 为什么放到 `src/skills/`

- 当前 prompt 资产实际包含 persona、policy、tool usage rules、output contract 等稳定能力片段，语义上更接近 skill，而不是一次性模板
- 放在 `src/skills/` 后，可以把共享规则沉淀到 `src/skills/shared/`，把 agent 私有规则沉淀到各自目录，便于复用与组合
- 后续 `PromptRuntime` 可以按 `agent_name + mode + task` 选择 skill 模块进行组装，为第二阶段 Function Calling 和第三阶段 SFT 保留清晰边界
- 这一步并不把系统改造成“完全由 skill 调度的 agent”，只是把 prompt 文本资产做成可加载、可组合、可回退的 skill 包

#### 3. 推荐目录形态

建议将目录进一步细化为“共享模块 + agent 模块 + task 变体”三层：

- `src/skills/shared/`
  - `safety.md`
  - `tool_calling_xml.md`
  - `response_style.md`
- `src/skills/interviewer/`
  - `baseline/`
    - `persona.md`
    - `policy.md`
    - `tool_rules.md`
    - `output_contract.md`
  - `normal/`
    - `persona.md`
    - `policy.md`
    - `tool_rules.md`
    - `output_contract.md`
- `src/skills/session_scribe/`
  - `update_memory_question_bank/`
  - `update_session_agenda/`
  - `consider_and_propose_followups/`
- `src/skills/planner/`
  - `add_new_memory_planner/`
  - `user_add_planner/`
  - `user_comment_planner/`
- `src/skills/section_writer/`
  - `normal/`
  - `baseline/`
  - `user_add/`
  - `user_update/`
- `src/skills/session_coordinator/`
  - `summary/`
  - `questions/`
  - `topic_extraction/`

这样设计的目的，是把“稳定规则”与“任务型上下文入口”拆开，避免继续把不同任务混成一个大 prompt 文件。

#### 4. `PromptRuntime` 职责边界

`src/utils/prompt_runtime.py` 应只负责组装，不负责业务决策。建议职责如下：

- `PromptModule`
  - 表示单个 skill 文本模块
  - 字段建议包含：`name`、`content`、`source_path`、`required`
- `PromptBundle`
  - 表示一次 prompt 组装结果
  - 字段建议包含：`agent_name`、`mode`、`task`、`modules`、`fallback_used`
- `PromptRuntime`
  - 负责选择模块、拼接顺序、渲染模板、失败回退
  - 不负责查询 memory bank、事件流、question bank 等运行时数据
- `build_prompt_bundle(agent_name, mode, task)`
  - 决定这次 prompt 要加载哪些 shared / agent / task 模块
- `render_prompt(bundle, variables)`
  - 把 bundle 渲染成最终 prompt 字符串

建议固定组装顺序如下：

1. shared modules
2. agent persona
3. task policy
4. tool rules
5. output contract
6. optional examples
7. runtime-injected context blocks

这样做可以保证 prompt 结构稳定，测试也更容易做快照比对。

#### 5. `skill_loader.py` 具体职责

`src/utils/skill_loader.py` 建议尽量薄，只做加载，不做渲染：

- `load_skill_text(path)`
  - 读取 markdown 文本
  - 对不存在文件返回空值或抛出可控异常，不在这里决定 fallback
- `load_shared_modules()`
  - 加载所有共享模块
  - 共享模块应允许按名称过滤，避免每个 agent 都无差别加载全部内容
- `load_skill_pack(agent_name)`
  - 返回某 agent 的可用模块索引
  - 不直接生成最终 prompt，只提供 `PromptRuntime` 可消费的数据

加载层和运行时分离，是为了后续支持：

- 本地文件 skill
- 打包后的静态资源
- 未来可能的远端 prompt registry

#### 6. `prompt_templates.py` 具体职责

当前 `prompt_utils.format_prompt()` 只做简单占位符补齐，不足以支撑阶段一后的模块化拼装。`src/utils/prompt_templates.py` 建议补充：

- 模板渲染入口，例如 `safe_format_template(template, variables)`
- 缺失变量保护，避免单个模块中的占位符导致整个 prompt 渲染失败
- 空模块、空变量、重复空行的归一化处理
- 可选的 `join_sections(sections)`，统一 markdown 块之间的分隔规则

第一阶段不需要引入复杂模板引擎；保持 Python 原生字符串模板即可，重点是行为稳定和安全回退。

#### 7. 从旧 `prompts.py` 到新 skill 包的拆分方法

迁移时不要先“重写 prompt”，而要先做机械拆分：

- `persona.md`
  - 放角色设定、自我定位、语气风格
- `policy.md`
  - 放思考流程、任务目标、决策规则
- `tool_rules.md`
  - 放工具调用时机、调用顺序、工具参数约束
- `output_contract.md`
  - 放 XML 输出格式、标签约束、结构示例
- `examples.md`
  - 只放少量高价值例子；若当前无示例，可先不建

拆分原则：

- 先保持原文内容不变，只调整归类
- 如果某段同时包含 policy 和 output format，优先按“是否会影响 tool call 输出结构”来划分
- 与共享规则重复的内容，优先沉淀到 `src/skills/shared/`

#### 8. 各 Agent 的迁移切入点

推荐按以下顺序迁移：

1. `Interviewer`
2. `SessionScribe`
3. `Planner`
4. `SectionWriter`
5. `SessionCoordinator`

原因如下：

- `Interviewer` 的 `_get_prompt()` 已经把上下文收集与模板渲染相对清晰地分开，适合作为样板
- `SessionScribe` prompt 任务较多，但边界清楚，适合验证一个 agent 对应多个 task skill 的模式
- `Planner` 和 `SectionWriter` 都有明显的 task 类型，可自然映射到 `mode/task`
- `SessionCoordinator` 同时包含 summary、question rebuild、topic extraction 三类任务，最后迁移更稳妥

##### `Interviewer`

- 保留 [baseline / normal] 两种行为分支
- `_get_prompt()` 继续负责收集：
  - `user_portrait`
  - `last_meeting_summary`
  - `chat_history`
  - `current_events`
  - `conversation_starter`
  - `tool_descriptions`
- 改造点仅为：
  - `get_prompt(prompt_type)` 替换为 `PromptRuntime.build_prompt_bundle("interviewer", mode=prompt_type, task="respond")`
  - 最终由 `render_prompt(bundle, format_params)` 产出 prompt

##### `SessionScribe`

- 保留三个任务入口：
  - `update_memory_question_bank`
  - `update_session_agenda`
  - `consider_and_propose_followups`
- 保留现有锁、异步并发、similar question feedback loop 和 XML 解析逻辑
- `_get_formatted_prompt()` 只负责：
  - 准备每个 task 的变量
  - 调用 `PromptRuntime`
- 不在第一阶段改变任何 tool call 解析或执行代码

##### `Planner`

- 将 `add_new_memory_planner`、`user_add_planner`、`user_comment_planner` 分别映射到独立 task skill
- `_get_formatted_prompt()` 继续负责收集：
  - `user_portrait`
  - `biography_structure`
  - `biography_content`
  - `style_instructions`
  - `missing_memories_warning`
- `PromptRuntime` 只接管模板来源和模块组装

##### `SectionWriter`

- 保留 `normal`、`baseline`、`user_add`、`user_update` 四种 prompt 类型
- `_get_plan_prompt()` 继续负责构造：
  - `section_identifier_xml`
  - `current_content`
  - `relevant_memories`
  - `plan_content`
  - `missing_memories_warning`
  - `tool_call_error`
- 基线模式仍沿用现有“整篇 biography 更新”路径，不提前与 normal 合并

##### `SessionCoordinator`

- 将 prompt 按职责拆为：
  - `summary`
  - `questions`
  - `topic_extraction`
- `_get_summary_prompt()` 与 `_get_questions_prompt()` 保留变量收集逻辑
- `extract_session_topics()` 中当前直接格式化 `TOPIC_EXTRACTION_PROMPT` 的路径，也统一切到 `PromptRuntime`

#### 9. 兼容层策略

第一阶段结束后，旧 `prompts.py` 不删除，而是承担兼容层职责：

- 方式 A：旧 `get_prompt()` 内部转发到 `PromptRuntime`
- 方式 B：agent 优先走 `PromptRuntime`，失败时 fallback 到旧 `get_prompt()`

推荐优先采用方式 B，原因是：

- 迁移期间更容易做新旧行为对比
- skill 文件不完整时风险更低
- 出问题时定位更直接，不会把兼容逻辑藏进旧模块内部

fallback 触发条件建议包括：

- skill 文件不存在
- 加载失败
- 渲染缺少关键变量
- 渲染结果为空或明显异常

#### 10. 测试策略

第一阶段测试不应只测“是否返回字符串”，而应测“迁移前后行为是否等价”。

建议测试分三层：

- `tests/test_prompt_runtime.py`
  - 测试 bundle 构建顺序
  - 测试 shared + agent + task 模块是否按预期加载
  - 测试缺失模块时是否正确 fallback
  - 测试变量缺失时的安全渲染行为
- `tests/test_interviewer_prompt_bundle.py`
  - 比较 `baseline` 与 `normal` 两种模式下的新旧 prompt 关键片段
  - 确认 `questions_and_notes` 只在 normal 模式出现
  - 确认 baseline 模式下 `recall` 不出现在工具描述中
- `tests/test_session_scribe_prompt_bundle.py`
  - 覆盖三个 task prompt
  - 验证 `similar_questions_warning`、`warning_output_format` 等动态片段仍在正确条件下出现

如果仓库内还没有稳定测试框架，可以先写最小单元测试和字符串快照测试，优先覆盖结构和关键约束，不急于做全量 golden file。

#### 11. 建议实施顺序

建议按以下小步推进，每一步都应保证可运行：

1. 新建 `src/skills/` 目录和最小 skill 文件骨架
2. 实现 `skill_loader.py`
3. 实现 `prompt_templates.py`
4. 实现 `prompt_runtime.py`
5. 先迁移 `Interviewer`
6. 补 `PromptRuntime` 和 `Interviewer` 测试
7. 再迁移 `SessionScribe`
8. 补 `SessionScribe` 测试
9. 迁移 `Planner`、`SectionWriter`、`SessionCoordinator`
10. 将旧 `prompts.py` 固化为兼容层

这样安排的目的是先用最简单 agent 验证 runtime 设计，再把多任务、多分支 agent 逐步迁入，避免一开始把改造面铺得太大。

#### 12. 第一阶段完成后的代码形态

完成后，代码职责应稳定为：

- `skills/`
  - 保存 prompt 资产文本
- `skill_loader.py`
  - 读取 skill 文本
- `prompt_runtime.py`
  - 根据 `agent_name + mode + task` 组装 bundle 并渲染
- agent 文件
  - 负责准备变量、记录事件、调用模型、执行工具
- 旧 `prompts.py`
  - 作为兼容层和回退入口

最终效果是：prompt 被 skill 模块驱动组装，但 agent runtime 仍保持当前形态不变。

### 需要修改的文件

- `src/agents/interviewer/interviewer.py`
  - 将 `_get_prompt()` 改为通过 `PromptRuntime` 组装
  - 保留 `baseline / normal` 两种行为分支

- `src/agents/session_scribe/session_scribe.py`
  - 将 prompt 构造逻辑改为通过 `PromptRuntime`
  - 保留当前 memory / question / follow-up 的执行流程

- `src/agents/biography_team/planner/planner.py`
  - 将 planner prompt 的组装迁移到 `PromptRuntime`

- `src/agents/biography_team/section_writer/section_writer.py`
  - 将 section 更新 prompt 的组装迁移到 `PromptRuntime`

- `src/agents/biography_team/session_coordinator/session_coordinator.py`
  - 将 summary / agenda 相关 prompt 的组装迁移到 `PromptRuntime`

### 需要保留为兼容层的文件

第一阶段不要删除以下文件，只将它们逐步改造成兼容层或转发层：

- `src/agents/interviewer/prompts.py`
- `src/agents/session_scribe/prompts.py`
- `src/agents/biography_team/planner/prompts.py`
- `src/agents/biography_team/section_writer/prompts.py`
- `src/agents/biography_team/session_coordinator/prompts.py`

### 需要新增的测试

- `tests/test_prompt_runtime.py`
- `tests/test_interviewer_prompt_bundle.py`
- `tests/test_session_scribe_prompt_bundle.py`

### 第一阶段验收标准

- `baseline / normal` 模式下的 prompt 行为保持不变
- 当前 XML 工具调用流程不受影响
- prompt 资产不再只存在于大段字符串常量中
- skill 模块缺失时，系统可以安全回退到旧实现

---

## 第二阶段：原生 Function Calling 运行时

### 阶段目标

将当前基于 XML 的工具调用协议逐步替换为结构化的 Function Calling 运行时，并在迁移期间保留 XML fallback。

### 需要新增的文件

- `src/utils/llm/types.py`
  - `ToolCall`
  - `AgentResponse`

- `src/utils/llm/router.py`
  - 模型路由逻辑
  - 原生工具调用与 XML fallback 选择逻辑

### 需要修改的文件

- `src/utils/llm/engines.py`
  - 支持返回结构化响应对象
  - 支持从模型响应中提取原生 tool calls

- `src/agents/base_agent.py`
  - 支持结构化 tool call 执行
  - 暂时保留 XML fallback

- `src/agents/interviewer/interviewer.py`
  - 作为第一批迁移目标
  - 将 `recall` 和 `respond_to_user` 切到原生 Function Calling

- `src/utils/llm/xml_formatter.py`
  - 迁移后降级为兼容层或 fallback 工具

### 建议迁移顺序

1. `Interviewer`
2. `SessionScribe`
3. `Planner`
4. `SessionCoordinator`
5. `SectionWriter`

### 第二阶段验收标准

- `Interviewer` 的原生 Function Calling 路径可以稳定运行
- XML fallback 仍然可用
- 工具参数在执行前经过 schema 校验
- 工具运行时不再完全依赖字符串解析

---

## 第三阶段：SessionScribe SFT

### 阶段目标

为 `SessionScribe` 增加 SFT 数据导出、训练、推理与接入闭环，优先优化结构化动作生成能力。

### 需要新增的目录

- `scripts/export_sft/session_scribe/`
- `data/sft/session_scribe/`
- `configs/sft/session_scribe/`
- `src/models/policy/session_scribe/`

### 训练目标

- memory 切分
- memory 摘要生成
- metadata 抽取
- answered question 关联
- follow-up 决策

### 数据来源

- 现有 event stream 与 tool call 日志
- `user_agent` 生成的合成访谈轨迹
- teacher model 蒸馏数据
- 人工修订黄金样本

### 目标输出格式

训练目标不再使用 XML，而使用结构化 JSON / Function Calling 风格输出：

- `memory_actions`
- `question_actions`
- `agenda_actions`
- `follow_up`

### 运行时接入方式

- 为 `SessionScribe` 增加独立模型配置
- 用 policy model 负责结构化动作生成
- 输出校验失败时自动 fallback 到基座模型

### 需要修改的文件

- `src/agents/session_scribe/session_scribe.py`
- `src/utils/llm/engines.py`
- `src/agents/base_agent.py`

### 第三阶段验收标准

- 可以导出可用的 SFT 数据集
- 可以在本地运行离线评测
- 可以用影子模式对比 SFT 输出与当前 prompt 输出
- `SessionScribe` 可独立使用专用模型而不影响其他 Agent

---

## 第四阶段：四层记忆模型显式化

### 阶段目标

将当前隐式存在的分层记忆设计显式抽象出来，统一术语与上下文使用方式。

### 四层记忆

1. 用户画像记忆
2. 跨会话摘要与 agenda 记忆
3. 当前会话短期工作记忆
4. 基于检索的长期 episodic memory

### 需要新增的文件

- `src/context/memory_view.py`

### 主要职责

- 为 prompt 组装提供统一的记忆视图
- 明确摘要记忆和检索记忆之间的边界
- 让记忆流转更容易测试、解释和评估

### 第四阶段验收标准

- prompt builder 显式依赖四层记忆输入
- 代码术语与文档术语一致
- 记忆流转过程更容易观察和验证

---

## 第五阶段：可复现评测

### 阶段目标

将现有日志能力升级为可重复运行的 benchmark / evaluation 流程。

### 需要新增的文件

- `scripts/eval/run_benchmark.py`
- `scripts/eval/summarize_results.py`
- `docs/evaluation/RESULTS.md`

### 第一批先稳定的指标

- 问题重复度
- 响应延迟
- biography update time

### 第二批补充指标

- groundedness
- completeness
- SFT 结构化动作合法率
- memory 抽取准确率
- follow-up 决策准确率

### 第五阶段验收标准

- 可以跑出 baseline vs multi-agent 的对比结果
- 可以汇总成统一结果表
- 至少可以复现一套小规模内部 benchmark

---

## 推荐实施顺序

1. 第一阶段：Prompt Skill 内化
2. 第二阶段：先迁移 `Interviewer` 到原生 Function Calling
3. 第三阶段前半：完成 `SessionScribe` 数据导出与影子推理
4. 第三阶段后半：接入 `SessionScribe` SFT policy model
5. 第五阶段：补齐可复现评测结果

---

## 简历可自证的最小里程碑

如果希望简历中的亮点能被代码和结果支撑，至少需要完成以下内容：

- 完成第一阶段
- 完成 `Interviewer` 的 Function Calling 迁移
- 完成 `SessionScribe` 的 SFT 数据导出
- 完成 `SessionScribe` 的影子模式推理接入
- 输出一版可复现的评测报告
