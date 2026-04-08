import chromium from '@sparticuz/chromium';
import puppeteer from 'puppeteer-core';

export const config = {
  maxDuration: 60,
};

export default async function handler(req, res) {
  // Allow file override via query param (e.g., ?file=sweetwater-proposal.html)
  const file = (req.query.file || 'sweetwater-proposal.html').replace(/[^a-zA-Z0-9_.-]/g, '');

  // Use the current deployment URL so the function always fetches the
  // HTML it was deployed alongside.
  const host = process.env.VERCEL_URL
    ? `https://${process.env.VERCEL_URL}`
    : 'https://instyle-cleaning.vercel.app';
  const url = `${host}/${file}`;

  // Friendly filename for the download
  const downloadName = file
    .replace(/\.html?$/i, '')
    .split('-')
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join('-') + '.pdf';

  let browser = null;
  try {
    browser = await puppeteer.launch({
      args: [
        ...chromium.args,
        '--hide-scrollbars',
        '--disable-web-security',
      ],
      defaultViewport: { width: 1240, height: 1754, deviceScaleFactor: 2 },
      executablePath: await chromium.executablePath(),
      headless: true,
    });

    const page = await browser.newPage();

    // Navigate and wait for everything to settle
    await page.goto(url, {
      waitUntil: ['load', 'networkidle0'],
      timeout: 45000,
    });

    // Ensure web fonts are fully loaded before taking the PDF
    await page.evaluateHandle('document.fonts.ready');

    // Hide the print bar / overlays during PDF rendering
    await page.addStyleTag({
      content: `
        .print-bar, .no-print, .deerflow-mark { display: none !important; }
        body { background: white !important; }
      `,
    });

    // Small delay so any CSS animations / paint settle
    await new Promise((r) => setTimeout(r, 500));

    const pdfBuffer = await page.pdf({
      format: 'A4',
      printBackground: true,
      preferCSSPageSize: true,
      displayHeaderFooter: false,
      margin: { top: '0', right: '0', bottom: '0', left: '0' },
    });

    await browser.close();
    browser = null;

    res.setHeader('Content-Type', 'application/pdf');
    res.setHeader('Content-Disposition', `inline; filename="${downloadName}"`);
    res.setHeader('Cache-Control', 'public, max-age=0, s-maxage=300, stale-while-revalidate=60');
    res.status(200).send(pdfBuffer);
  } catch (err) {
    if (browser) {
      try { await browser.close(); } catch {}
    }
    console.error('PDF generation failed:', err);
    res.status(500).json({
      error: 'PDF generation failed',
      message: err.message,
      url,
    });
  }
}
