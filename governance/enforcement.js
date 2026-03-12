/**
 * Governance Enforcement Module
 * 
 * Add to Gateway tool execution path:
 * - Import this module at Gateway startup
 * - Call enforceToolCall(agentId, toolName) before every tool execution
 * 
 * Location in Gateway: alongside tool-loop-detection in tool execution path
 */

const fs = require('fs')
const path = require('path')

// Load enforcement config
const ENFORCEMENT_CONFIG_PATH = process.env.WORKSPACE 
  ? path.join(process.env.WORKSPACE, 'governance', 'enforcement.json')
  : path.join(__dirname, 'workspace', 'governance', 'enforcement.json')

let enforcementConfig = {
  version: '1.0',
  enabled: false,
  roles: {}
}

function loadEnforcementConfig() {
  try {
    if (fs.existsSync(ENFORCEMENT_CONFIG_PATH)) {
      const content = fs.readFileSync(ENFORCEMENT_CONFIG_PATH, 'utf-8')
      enforcementConfig = JSON.parse(content)
      console.log(`[governance] Loaded enforcement config: v${enforcementConfig.version}, enabled: ${enforcementConfig.enabled}`)
    }
  } catch (err) {
    console.error('[governance] Failed to load config:', err.message)
  }
}

// Load at module init
loadEnforcementConfig()

/**
 * Check if a tool call is allowed for the given agent
 * @param {string} agentId - The agent ID (jarvis, alex, scout, etc.)
 * @param {string} toolName - The tool being called
 * @returns {object} - { allowed: boolean, reason?: string }
 */
function enforceToolCall(agentId, toolName) {
  const roleConfig = enforcementConfig.roles[agentId]
  
  // No config for this agent - allow (preserves behavior for unknown agents)
  if (!roleConfig) {
    return { allowed: true }
  }
  
  // Get allow list
  const allowedTools = roleConfig.allow || []
  
  // Check if tool is in allow list
  if (allowedTools.includes(toolName)) {
    return { allowed: true }
  }
  
  // Tool not in allow list - deny
  const result = { 
    allowed: false, 
    reason: `Tool '${toolName}' not in ${agentId} allow-list: [${allowedTools.join(', ')}]`
  }
  
  // Log violation
  const logEntry = {
    timestamp: new Date().toISOString(),
    agentId,
    tool: toolName,
    action: 'tool_call_denied',
    configEnabled: enforcementConfig.enabled,
    result: 'denied'
  }
  
  if (enforcementConfig.enabled) {
    // Enforce mode: actually block
    console.error(`[governance] DENIED: ${JSON.stringify(logEntry)}`)
    return result
  } else {
    // Shadow mode: log but allow
    console.log(`[governance] SHADOW: ${JSON.stringify(logEntry)}`)
    return { allowed: true, shadowWarning: result.reason }
  }
}

/**
 * Reload config (can be called at runtime)
 */
function reloadConfig() {
  loadEnforcementConfig()
}

module.exports = {
  enforceToolCall,
  reloadConfig,
  getConfig: () => enforcementConfig
}
