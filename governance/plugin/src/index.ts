/**
 * Governance Enforcer Plugin
 * 
 * Uses the before_tool_call hook to enforce role-based tool allow-lists.
 * Supports two modes:
 * - shadow (default): logs violations but allows execution
 * - enforce: blocks unauthorized tool calls
 */

import type { OpenClawPluginService, PluginHookBeforeToolCallEvent, PluginHookToolContext, PluginHookBeforeToolCallResult } from "openclaw/plugin-sdk"

interface EnforcementConfig {
  version: string
  enabled: boolean
  roles: Record<string, { allow: string[] }>
}

interface PluginConfig {
  enabled?: boolean
  configPath?: string
}

let enforcementConfig: EnforcementConfig | null = null
let pluginConfig: PluginConfig = {}

// Load enforcement config from workspace
async function loadEnforcementConfig(configPath?: string): Promise<void> {
  try {
    // Dynamic import for fs (Node.js only)
    const fs = await import('fs/promises')
    const path = await import('path')
    
    const configFile = configPath || process.env.WORKSPACE 
      ? path.join(process.env.WORKSPACE!, 'governance', 'enforcement.json')
      : path.join(__dirname, '..', '..', 'governance', 'enforcement.json')
    
    const content = await fs.readFile(configFile, 'utf-8')
    enforcementConfig = JSON.parse(content)
    
    console.log(`[governance-plugin] Loaded enforcement config: v${enforcementConfig.version}, enabled: ${enforcementConfig.enabled}`)
  } catch (err) {
    console.error('[governance-plugin] Failed to load enforcement config:', err)
    enforcementConfig = null
  }
}

// Check if tool is allowed for agent
function checkToolAllowed(agentId: string, toolName: string): { allowed: boolean; reason?: string } {
  if (!enforcementConfig) {
    // No config loaded - allow all (fail open)
    return { allowed: true }
  }
  
  const roleConfig = enforcementConfig.roles[agentId]
  
  // No config for this agent - allow (preserves behavior for unknown agents)
  if (!roleConfig) {
    return { allowed: true }
  }
  
  const allowedTools = roleConfig.allow || []
  
  if (allowedTools.includes(toolName)) {
    return { allowed: true }
  }
  
  return {
    allowed: false,
    reason: `Tool '${toolName}' not in ${agentId} allow-list: [${allowedTools.join(', ')}]`
  }
}

// Format log entry
function formatGovernanceLog(agentId: string, toolName: string, result: { allowed: boolean; reason?: string }, mode: string): object {
  return {
    timestamp: new Date().toISOString(),
    event: 'governance_enforcement',
    agentId,
    tool: toolName,
    mode,
    configEnabled: enforcementConfig?.enabled ?? false,
    result: result.allowed ? 'allowed' : 'denied',
    reason: result.reason
  }
}

export const governanceEnforcer: OpenClawPluginService = {
  name: 'governance-enforcer',
  
  async start(config: PluginConfig): Promise<void> {
    pluginConfig = config || {}
    await loadEnforcementConfig(pluginConfig.configPath)
    console.log('[governance-plugin] Governance Enforcer started')
  },
  
  async stop(): Promise<void> {
    console.log('[governance-plugin] Governance Enforcer stopped')
  },
  
  // Hook: before_tool_call - intercepts tool calls before execution
  async before_tool_call(event: PluginHookBeforeToolCallEvent, ctx: PluginHookToolContext): Promise<PluginHookBeforeToolCallResult | void> {
    const agentId = ctx.agentId || 'unknown'
    const toolName = event.toolName
    
    const result = checkToolAllowed(agentId, toolName)
    
    const mode = (enforcementConfig?.enabled ?? false) ? 'enforce' : 'shadow'
    const logEntry = formatGovernanceLog(agentId, toolName, result, mode)
    
    if (!result.allowed) {
      // Tool is NOT in allow-list
      if (enforcementConfig?.enabled) {
        // Enforcement mode: block the tool call
        console.error(`[governance] DENIED: ${JSON.stringify(logEntry)}`)
        return {
          block: true,
          blockReason: result.reason
        }
      } else {
        // Shadow mode: log but allow
        console.log(`[governance] SHADOW: ${JSON.stringify(logEntry)}`)
        // Don't block in shadow mode - just log
        return
      }
    }
    
    // Tool is allowed - log for audit trail
    console.log(`[governance] ALLOWED: ${JSON.stringify(logEntry)}`)
    
    // Don't return anything - let the tool call proceed
    return
  }
}

// Export default
export default governanceEnforcer
