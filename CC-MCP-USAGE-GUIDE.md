# 📚 CC-MCP Proper Usage Guide

## ⚠️ Important Notice

**CC-MCP is a dialogue consistency maintenance system based on "session management".**
Without proper usage, a new session is created every time, and context is lost.

---

## 🚫 Common Incorrect Usage

```python
# ❌ Wrong: Using without session ID
await process_user_message("I want to build an AI assistant")
# → A new session is automatically created

await process_user_message("Budget is $50,000")  
# → Another new session is created, previous context is lost!

await process_user_message("What technologies should I use?")
# → Yet another new session... all previous conversation is forgotten
```

**Result**: Each message is processed in an independent session, completely losing conversation consistency.

---

## ✅ Correct Usage (Required Steps)

### 📋 Basic Workflow

```python
# ✅ Correct: Explicit session management

# 1️⃣ Start a session (Required!)
session_info = await start_session()
session_id = session_info["session_id"]
print(f"Session started: {session_id}")

# 2️⃣ Continue dialogue with the same session ID
await process_user_message(
    message="I want to build an AI assistant",
    session_id=session_id  # Always specify session ID
)

await process_user_message(
    message="Budget is $50,000",
    session_id=session_id  # Use the same session ID
)

await process_user_message(
    message="What technologies should I use?",
    session_id=session_id  # Continue using the session ID
)

# 3️⃣ End the session (Recommended)
await end_session(session_id=session_id)
```

---

## 🎯 Practical Usage with MCP Clients (Cline, etc.)

### 1. Starting a New Task

```javascript
// Step 1: Always start a session first
const session = await cc_mcp.start_session();
const sessionId = session.session_id;

// Step 2: Use the session ID consistently
await cc_mcp.process_user_message({
    message: "User's message",
    session_id: sessionId
});
```

### 2. Long Conversation Pattern

```javascript
class CCMCPManager {
    constructor() {
        this.currentSessionId = null;
    }
    
    // Start conversation
    async startConversation() {
        const result = await cc_mcp.start_session();
        this.currentSessionId = result.session_id;
        console.log(`✅ CC-MCP session started: ${this.currentSessionId}`);
        return this.currentSessionId;
    }
    
    // Process message
    async processMessage(message) {
        if (!this.currentSessionId) {
            await this.startConversation();
        }
        
        return await cc_mcp.process_user_message({
            message: message,
            session_id: this.currentSessionId  // Always use session ID
        });
    }
    
    // End conversation
    async endConversation() {
        if (this.currentSessionId) {
            await cc_mcp.end_session({
                session_id: this.currentSessionId
            });
            console.log(`✅ CC-MCP session ended: ${this.currentSessionId}`);
            this.currentSessionId = null;
        }
    }
}
```

---

## 📝 Recommended Implementation for Cline

### Correct Flow for Task Execution

```typescript
// In Cline's task execution context
async function executeTaskWithCCMCP(userTask: string) {
    let sessionId: string | null = null;
    
    try {
        // 1. Start session (Always execute at task start)
        const sessionResult = await useMcpTool(
            "cc-mcp",
            "start_session",
            {}
        );
        sessionId = sessionResult.session_id;
        console.log(`CC-MCP Session Started: ${sessionId}`);
        
        // 2. Process user message
        const processResult = await useMcpTool(
            "cc-mcp",
            "process_user_message",
            {
                message: userTask,
                session_id: sessionId  // Required!
            }
        );
        
        // 3. Use the same session ID for subsequent dialogue
        // ... Continue using the same sessionId ...
        
        // 4. Get debug info (if needed)
        const debugInfo = await useMcpTool(
            "cc-mcp",
            "get_debug_info",
            {
                message: userTask,
                session_id: sessionId
            }
        );
        
    } finally {
        // 5. End session when task completes
        if (sessionId) {
            await useMcpTool(
                "cc-mcp",
                "end_session",
                {
                    session_id: sessionId
                }
            );
            console.log(`CC-MCP Session Ended: ${sessionId}`);
        }
    }
}
```

---

## 🔧 Session Management Best Practices

### 1. Session Lifecycle Management

```python
# Recommended pattern: Automatic management with context manager (Python example)
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

# Usage example
async with CCMCPSession() as session:
    await session.process("I want to build an AI assistant")
    await session.process("Budget is $50,000")
    # Session automatically ends
```

### 2. Session State Save and Restore

```python
# Export session state
context_data = await export_context(session_id=current_session_id)

# Restore later
new_session = await start_session()
await import_context(
    json_state=json.dumps(context_data["data"]),
    session_id=new_session["session_id"]
)
```

### 3. Multi-Session Management

```python
# Manage multiple independent conversations in parallel
sessions = {}

# User A's session
sessions["user_a"] = (await start_session())["session_id"]
await process_user_message("Build a web app", sessions["user_a"])

# User B's session
sessions["user_b"] = (await start_session())["session_id"]
await process_user_message("Build a mobile app", sessions["user_b"])

# Each maintains context independently
```

---

## 📊 Session Management Checklist

### ✅ Required Items
- [ ] Call `start_session()` at task start
- [ ] Save the session ID in a variable
- [ ] Specify session ID in all `process_user_message` calls
- [ ] Call `end_session()` at task completion

### 🎯 Recommended Items
- [ ] Ensure session termination with error handling
- [ ] Periodically backup with `export_context` for long conversations
- [ ] Check status with `get_session_stats` as needed
- [ ] Monitor unterminated sessions with `list_sessions`

---

## 🚨 Troubleshooting

### Issue 1: Context Not Preserved
**Cause**: Not specifying session ID, or using different session IDs each time
**Solution**: Consistently use the same session ID

### Issue 2: Increasing Memory Usage
**Cause**: Leaving sessions without termination
**Solution**: Always call `end_session()`, or periodically check with `list_sessions()` and remove unnecessary sessions

### Issue 3: Previous Conversation Context Lost
**Cause**: Started a new session
**Solution**: Save previous session state with `export_context` and restore to new session with `import_context`

---

## 📚 Summary

To maximize CC-MCP's value:

1. **Always start with `start_session()`**
2. **Consistently use the session ID**
3. **End with `end_session()` when task completes**

By following these three basic rules, you can perfectly maintain context even in long conversations and dramatically improve AI response quality.

---

## 🔗 Related Documentation

- [README.md](README.md) - CC-MCP Overview
- [README-ja.md](README-ja.md) - Japanese Documentation
- [README-zh.md](README-zh.md) - Chinese Documentation
- [session_manager.py](session_manager.py) - Session Management Implementation

---

**Important**: By following this guide for CC-MCP usage, you will significantly improve dialogue quality and consistency of AI assistants.
