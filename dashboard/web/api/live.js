// Vercel function: tin crypto mới nhất cho tab Live (không thuộc kết quả nghiên cứu).
// Nguồn: RSS The Block (robots.txt cho phép) + GDELT DOC 2.0 API (chỉ tiêu đề + link). Không chấm FinBERT ở đây
// (Python/model không chạy trên Vercel); câu chuyện thị trường gán theo từ khóa và được ghi rõ trên giao diện.
// Server local (dashboard/server.py) vẫn trả cùng schema kèm điểm FinBERT.

const RSS = 'https://www.theblock.co/rss.xml'
const GDELT = 'https://api.gdeltproject.org/api/v2/doc/doc?query=' +
  encodeURIComponent('(bitcoin OR ethereum OR crypto OR cryptocurrency OR stablecoin OR solana OR xrp OR "bnb") sourcelang:english') +
  '&mode=artlist&format=json&maxrecords=60&sort=datedesc&timespan=6h'
const LIMIT = 40
export const config = { maxDuration: 25 }

const NARR = [   // thứ tự = thứ tự ưu tiên khi tiêu đề khớp nhiều nhóm; theo mô tả câu chuyện trong src/features/narrative.py
  ['security_hacks', /hack|exploit|stolen|steal|scam|fraud|breach|theft|drain|phishing|rug pull/i],
  ['regulation', /\bSEC\b|CFTC|regulat|lawsuit|\bban\b|\bbill\b|legislat|\blaw\b|court|sanction|\btax|lawmaker|senate|congress/i],
  ['etf_institutional', /\bETF|BlackRock|Fidelity|institution|asset manager|treasury compan|inflow|outflow|\bfund\b/i],
  ['stablecoins', /stablecoin|USDT|USDC|Tether|\bpeg\b|depeg/i],
  ['defi', /\bDeFi\b|lending|\bDEX\b|liquidity pool|staking|yield|Uniswap|Aave|decentralized finance/i],
  ['ai_tokens', /\bAI\b|artificial intelligence|AI agent/i],
  ['macro_monetary', /\bFed\b|Federal Reserve|interest rate|rate cut|rate hike|inflation|\bCPI\b|recession|tariff|jobs report|yields/i],
  ['price_speculation', /price|rall(y|ies)|surge|soar|plunge|crash|tumble|\bbull|\bbear|record high|all-time high|liquidat|trader|\$\d/i],
]
const ASSETS = [['BTC', /bitcoin|\bBTC\b/i], ['ETH', /ethereum|\bETH\b|\bether\b/i], ['SOL', /solana|\bSOL\b/i],
  ['BNB', /\bBNB\b|binance coin/i], ['XRP', /\bXRP\b|ripple/i]]

const narrative = (title) => (NARR.find(([, re]) => re.test(title)) ?? ['other'])[0]
const assets = (title) => ASSETS.filter(([, re]) => re.test(title)).map(([k]) => k)
const decode = (s) => s.replace(/<!\[CDATA\[|\]\]>/g, '').replace(/&amp;/g, '&').replace(/&#8217;|&rsquo;/g, '’')
  .replace(/&#8216;|&lsquo;/g, '‘').replace(/&quot;|&#8220;|&#8221;/g, '"').replace(/&#039;|&#39;/g, "'").trim()

async function get(url, ms = 8000) {
  const r = await fetch(url, { headers: { 'User-Agent': 'crypto-narrative-report (academic research dashboard)' },
    signal: AbortSignal.timeout(ms) })
  if (!r.ok) throw new Error(`${r.status} ${url}`)
  return r
}

export async function rss() {
  const xml = await (await get(RSS)).text()
  return [...xml.matchAll(/<item>([\s\S]*?)<\/item>/g)].map(([, it]) => {
    const tag = (t) => decode((it.match(new RegExp(`<${t}>([\\s\\S]*?)</${t}>`)) ?? [, ''])[1])
    const ts = new Date(tag('pubDate'))
    return { url: tag('link'), title: tag('title'), source: 'theblock', public_ts_utc: isNaN(ts) ? null : ts.toISOString() }
  })
}

export async function gdelt() {
  const text = await (await get(GDELT, 15000)).text()
  if (!text.trimStart().startsWith('{')) throw new Error('GDELT: vượt giới hạn truy vấn, dùng RSS')
  const j = JSON.parse(text)   // GDELT chậm 5–15 giây; giới hạn 1 truy vấn / 5 giây (CDN cache 30 giây)
  return (j.articles ?? []).map((a) => {
    const m = /^(\d{4})(\d{2})(\d{2})T(\d{2})(\d{2})(\d{2})Z$/.exec(a.seendate ?? '')
    return { url: a.url, title: a.title, source: a.domain, public_ts_utc: m ? `${m[1]}-${m[2]}-${m[3]}T${m[4]}:${m[5]}:${m[6]}.000Z` : null }
  })
}

export function merge(lists) {
  const seen = new Set()
  return lists.flat()
    .filter((x) => x.url && x.title && x.public_ts_utc)
    .filter((x) => {
      const k = x.title.toLowerCase().replace(/\W+/g, ' ').trim()
      if (seen.has(x.url) || seen.has(k)) return false
      seen.add(x.url); seen.add(k)
      return true
    })
    .sort((a, b) => b.public_ts_utc.localeCompare(a.public_ts_utc))
    .slice(0, LIMIT)
    .map((x) => ({ ...x, public_ts_utc: x.public_ts_utc.replace('.000Z', 'Z'), narrative: narrative(x.title), assets: assets(x.title) }))
}

export default async function handler(req, res) {
  const settled = await Promise.allSettled([rss(), gdelt()])
  const ok = settled.filter((s) => s.status === 'fulfilled').map((s) => s.value)
  const body = { updated_utc: new Date().toISOString().replace(/\.\d+Z$/, 'Z'), feeds: ['theblock', 'gdelt'],
    scoring: 'keyword', items: merge(ok), errors: settled.filter((s) => s.status === 'rejected').map((s) => String(s.reason)) }
  res.setHeader('Cache-Control', 's-maxage=30, stale-while-revalidate=120')
  res.status(ok.length ? 200 : 502).json(body)
}
