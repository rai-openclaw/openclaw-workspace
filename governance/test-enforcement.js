#!/usr/bin/env node
/**
 * Governance Enforcement Test Script
 * 
 * Tests the enforcement module to verify it correctly intercepts
 * tool calls based on agent allow-lists.
 * 
 * Run: node test-enforcement.js
 */

const path = require('path')

// Set workspace to load config
process.env.WORKSPACE = '/Users/raitsai/.openclaw/workspace'

const { enforceToolCall, getConfig, reloadConfig } = require('./enforcement.js')

console.log('='.repeat(60))
console.log('Governance Enforcement Test')
console.log('='.repeat(60))

// Test cases
const testCases = [
  // Jarvis tests - should be allowed (in allow-list)
  { agent: 'jarvis', tool: 'read', expected: 'allowed' },
  { agent: 'jarvis', tool: 'sessions_spawn', expected: 'allowed' },
  { agent: 'jarvis', tool: 'memory_search', expected: 'allowed' },
  // Jarvis tests - should be denied (NOT in allow-list)
  { agent: 'jarvis', tool: 'write', expected: 'denied' },
  { agent: 'jarvis', tool: 'edit', expected: 'denied' },
  { agent: 'jarvis', tool: 'exec', expected: 'denied' },
  
  // Alex tests - should be allowed
  { agent: 'alex', tool: 'read', expected: 'allowed' },
  { agent: 'alex', tool: 'write', expected: 'allowed' },
  { agent: 'alex', tool: 'edit', expected: 'allowed' },
  { agent: 'alex', tool: 'exec', expected: 'allowed' },
  // Alex tests - should be denied
  { agent: 'alex', tool: 'sessions_spawn', expected: 'denied' },
  
  // Scout tests - should be allowed
  { agent: 'scout', tool: 'read', expected: 'allowed' },
  { agent: 'scout', tool: 'exec', expected: 'allowed' },
  // Scout tests - should be denied
  { agent: 'scout', tool: 'write', expected: 'denied' },
  { agent: 'scout', tool: 'sessions_spawn', expected: 'denied' },
]

console.log('\nConfig loaded:', getConfig())
console.log('\nRunning test cases...\n')

let passed = 0
let failed = 0

testCases.forEach(({ agent, tool, expected }) => {
  const result = enforceToolCall(agent, tool)
  const isDenied = result.allowed === false
  const hasWarning = result.shadowWarning !== undefined
  
  // In shadow mode: allowed with warning = effectively denied (logged)
  // In enforce mode: allowed = allowed, denied = denied
  const isEffectivelyDenied = hasWarning || isDenied
  
  const status = (isEffectivelyDenied && expected === 'denied') || (!isEffectivelyDenied && expected === 'allowed')
    ? '✅ PASS'
    : '❌ FAIL'
  
  if (status === '✅ PASS') passed++
  else failed++
  
  console.log(`${status} | ${agent.padEnd(8)} | ${tool.padEnd(16)} | expected: ${expected.padEnd(8)} | ${hasWarning ? '⚠️ SHADOW' : '✓ allowed'} ${isDenied ? '(blocked)' : ''}`)
})

console.log('\n' + '='.repeat(60))
console.log(`Results: ${passed} passed, ${failed} failed`)
console.log('='.repeat(60))

// Show what would be logged for a violation
console.log('\nShadow mode is ENABLED - violations are logged but not blocked.')
console.log('Expected log format: [governance] SHADOW: {..."tool":"write","result":"denied"...}')
console.log('\nTo enable enforcement, set "enabled": true in governance/enforcement.json')

process.exit(failed > 0 ? 1 : 0)
