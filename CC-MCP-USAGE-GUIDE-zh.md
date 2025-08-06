# 📚 CC-MCP 正确使用指南

## ⚠️ 重要提示

**CC-MCP 是基于"会话管理"的对话一致性维护系统。**
如果不正确使用，每次都会创建新会话，导致上下文丢失。

---

## 🚫 常见错误用法

```python
# ❌ 错误：不使用会话ID
await process_user_message("我想构建一个AI助手")
# → 自动创建新会话

await process_user_message("预算是5万美元")  
# → 又创建一个新会话，之前的上下文丢失！

await process_user_message("应该使用什么技术？")
# → 再次创建新会话...之前的对话全部被遗忘
```

**结果**：每条消息都在独立的会话中处理，完全丢失对话的一致性。

---

## ✅ 正确用法（必须步骤）

### 📋 基本工作流程

```python
# ✅ 正确：显式会话管理

# 1️⃣ 启动会话（必须！）
session_info = await start_session()
session_id = session_info["session_id"]
print(f"会话已启动: {session_id}")

# 2️⃣ 使用相同的会话ID继续对话
await process_user_message(
    message="我想构建一个AI助手",
    session_id=session_id  # 始终指定会话ID
)

await process_user_message(
    message="预算是5万美元",
    session_id=session_id  # 使用相同的会话ID
)

await process_user_message(
    message="应该使用什么技术？",
    session_id=session_id  # 继续使用会话ID
)

# 3️⃣ 结束会话（推荐）
await end_session(session_id=session_id)
```

---

## 🎯 在MCP客户端（Cline等）中的实际使用

### 1. 开始新任务

```javascript
// 步骤1：始终先启动会话
const session = await cc_mcp.start_session();
const sessionId = session.session_id;

// 步骤2：一致地使用会话ID
await cc_mcp.process_user_message({
    message: "用户的消息",
    session_id: sessionId
});
```

### 2. 长对话模式

```javascript
class CCMCPManager {
    constructor() {
        this.currentSessionId = null;
    }
    
    // 开始对话
    async startConversation() {
        const result = await cc_mcp.start_session();
        this.currentSessionId = result.session_id;
        console.log(`✅ CC-MCP会话已启动: ${this.currentSessionId}`);
        return this.currentSessionId;
    }
    
    // 处理消息
    async processMessage(message) {
        if (!this.currentSessionId) {
            await this.startConversation();
        }
        
        return await cc_mcp.process_user_message({
            message: message,
            session_id: this.currentSessionId  // 始终使用会话ID
        });
    }
    
    // 结束对话
    async endConversation() {
        if (this.currentSessionId) {
            await cc_mcp.end_session({
                session_id: this.currentSessionId
            });
            console.log(`✅ CC-MCP会话已结束: ${this.currentSessionId}`);
            this.currentSessionId = null;
        }
    }
}
```

---

## 📝 Cline推荐实现

### 任务执行的正确流程

```typescript
// 在Cline的任务执行上下文中
async function executeTaskWithCCMCP(userTask: string) {
    let sessionId: string | null = null;
    
    try {
        // 1. 启动会话（任务开始时始终执行）
        const sessionResult = await useMcpTool(
            "cc-mcp",
            "start_session",
            {}
        );
        sessionId = sessionResult.session_id;
        console.log(`CC-MCP会话已启动: ${sessionId}`);
        
        // 2. 处理用户消息
        const processResult = await useMcpTool(
            "cc-mcp",
            "process_user_message",
            {
                message: userTask,
                session_id: sessionId  // 必需！
            }
        );
        
        // 3. 后续对话使用相同的会话ID
        // ... 继续使用相同的sessionId ...
        
        // 4. 获取调试信息（如需要）
        const debugInfo = await useMcpTool(
            "cc-mcp",
            "get_debug_info",
            {
                message: userTask,
                session_id: sessionId
            }
        );
        
    } finally {
        // 5. 任务完成时结束会话
        if (sessionId) {
            await useMcpTool(
                "cc-mcp",
                "end_session",
                {
                    session_id: sessionId
                }
            );
            console.log(`CC-MCP会话已结束: ${sessionId}`);
        }
    }
}
```

---

## 🔧 会话管理最佳实践

### 1. 会话生命周期管理

```python
# 推荐模式：使用上下文管理器自动管理（Python示例）
class CCMCPSession:
    def __init__(self):
        self.session_id = None
    
    async def __aenter__(self):
        result = await start_session()
        self.session_id = result["session_id"]
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session_id:
            await end_session(self.session_id)
    
    async def process(self, message):
        return await process_user_message(message, self.session_id)

# 使用示例
async with CCMCPSession() as session:
    await session.process("我想构建一个AI助手")
    await session.process("预算是5万美元")
    # 会话自动结束
```

### 2. 会话状态保存和恢复

```python
# 导出会话状态
context_data = await export_context(session_id=current_session_id)

# 稍后恢复
new_session = await start_session()
await import_context(
    json_state=json.dumps(context_data["data"]),
    session_id=new_session["session_id"]
)
```

### 3. 多会话管理

```python
# 并行管理多个独立对话
sessions = {}

# 用户A的会话
sessions["user_a"] = (await start_session())["session_id"]
await process_user_message("构建一个Web应用", sessions["user_a"])

# 用户B的会话
sessions["user_b"] = (await start_session())["session_id"]
await process_user_message("构建一个移动应用", sessions["user_b"])

# 每个会话独立维护上下文
```

---

## 📊 会话管理检查清单

### ✅ 必需项目
- [ ] 任务开始时调用 `start_session()`
- [ ] 将会话ID保存在变量中
- [ ] 在所有 `process_user_message` 调用中指定会话ID
- [ ] 任务完成时调用 `end_session()`

### 🎯 推荐项目
- [ ] 使用错误处理确保会话终止
- [ ] 长对话定期使用 `export_context` 备份
- [ ] 根据需要使用 `get_session_stats` 检查状态
- [ ] 使用 `list_sessions` 监控未终止的会话

---

## 🚨 故障排除

### 问题1：上下文未保留
**原因**：未指定会话ID，或每次使用不同的会话ID
**解决方案**：始终使用相同的会话ID

### 问题2：内存使用增加
**原因**：会话未终止而留存
**解决方案**：始终调用 `end_session()`，或定期使用 `list_sessions()` 检查并删除不必要的会话

### 问题3：之前的对话上下文丢失
**原因**：启动了新会话
**解决方案**：使用 `export_context` 保存之前的会话状态，并使用 `import_context` 恢复到新会话

---

## 📚 总结

要最大化CC-MCP的价值：

1. **始终从 `start_session()` 开始**
2. **一致地使用会话ID**
3. **任务完成时使用 `end_session()` 结束**

遵循这三个基本规则，即使在长对话中也能完美维护上下文，显著提高AI响应质量。

---

## 🔗 相关文档

- [README.md](README.md) - CC-MCP概述（英文）
- [README-ja.md](README-ja.md) - 日文文档
- [README-zh.md](README-zh.md) - 中文文档
- [session_manager.py](session_manager.py) - 会话管理实现

---

**重要**：遵循本指南使用CC-MCP，将显著提高AI助手的对话质量和一致性。
