/**
 * Discord notification utility for OpenClaw
 * Posts messages to configured Discord webhook
 */

/**
 * Post a message to Discord webhook
 * @param {string} channel - Channel identifier (dev, prod, etc.)
 * @param {string} message - Message content to post
 * @returns {Promise<boolean>} - True if successful, false otherwise
 */
export async function postToDiscord(channel, message) {
  const webhookUrl = process.env.DISCORD_WEBHOOK_OPENCLAW_DEV;
  
  if (!webhookUrl) {
    console.error('[discord] DISCORD_WEBHOOK_OPENCLAW_DEV not set');
    return false;
  }

  try {
    const response = await fetch(webhookUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ content: message }),
    });

    if (!response.ok) {
      console.error('[discord] Webhook error:', response.status, response.statusText);
      return false;
    }

    console.log('[discord] Posted to', channel, ':', message);
    return true;
  } catch (error) {
    console.error('[discord] Failed to post:', error.message);
    return false;
  }
}