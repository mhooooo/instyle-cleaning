export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const token = process.env.SLACK_BOT_TOKEN;
  const channel = process.env.SLACK_CHANNEL || 'C0APBRPJ129';

  if (!token) {
    return res.status(500).json({ error: 'SLACK_BOT_TOKEN not configured' });
  }

  try {
    const { text } = req.body;
    if (!text) {
      return res.status(400).json({ error: 'Missing text' });
    }

    const slackRes = await fetch('https://slack.com/api/chat.postMessage', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ channel, text, unfurl_links: false })
    });

    const result = await slackRes.json();

    if (result.ok) {
      return res.status(200).json({ ok: true });
    } else {
      return res.status(400).json({ ok: false, error: result.error });
    }
  } catch (e) {
    return res.status(500).json({ ok: false, error: e.message });
  }
}
