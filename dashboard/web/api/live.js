// Vercel function: tin crypto mới nhất cho tab Live (không thuộc kết quả nghiên cứu).
// Nguồn: lô GKG 15 phút của GDELT (cùng nguồn và cùng bộ lọc tiêu đề với nghiên cứu, src/data/news_gdelt.py) + RSS The Block
// (robots.txt cho phép). Chỉ tiêu đề + link. Không chấm FinBERT ở đây (Python/model không chạy trên Vercel); câu chuyện
// thị trường gán theo từ khóa và được ghi rõ trên giao diện. Server local (dashboard/server.py) trả cùng schema kèm FinBERT.
import { inflateRawSync } from 'node:zlib'

const RSS = 'https://www.theblock.co/rss.xml'
const GKG_LAST = 'https://data.gdeltproject.org/gdeltv2/lastupdate.txt'
const GKG_BATCHES = 4                       // 4 lô 15 phút ≈ 1 giờ gần nhất
const KEEP = /\b(bitcoin|btc|ethereum|eth|ether|crypto\w*|stablecoins?|solana|xrp|binance|bnb|blockchain|defi|altcoins?|memecoins?|tether|usdt|usdc|coinbase)\b/i
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

/** Giải nén tệp duy nhất trong zip (đọc kích thước nén từ central directory). */
export function unzip(buf) {
  const eocd = buf.lastIndexOf(Buffer.from([0x50, 0x4b, 0x05, 0x06]))
  const cd = buf.readUInt32LE(eocd + 16)
  const size = buf.readUInt32LE(cd + 20), local = buf.readUInt32LE(cd + 42)
  const start = local + 30 + buf.readUInt16LE(local + 26) + buf.readUInt16LE(local + 28)
  return inflateRawSync(buf.subarray(start, start + size)).toString('utf8')
}

const TITLE = /<PAGE_TITLE>(.*?)<\/PAGE_TITLE>/
export function parseGkg(csv) {
  return csv.split('\n').flatMap((line) => {
    const c = line.split('\t')
    const t = c.length > 26 ? decode((TITLE.exec(c[26]) ?? [, ''])[1]) : ''
    if (!t || !KEEP.test(t)) return []
    const d = c[1]   // giờ GDELT thấy bài (YYYYMMDDHHMMSS) = public_ts_utc khi không có giờ đăng hợp lệ
    return [{ url: c[4], title: t, source: c[3],
      public_ts_utc: `${d.slice(0, 4)}-${d.slice(4, 6)}-${d.slice(6, 8)}T${d.slice(8, 10)}:${d.slice(10, 12)}:${d.slice(12, 14)}.000Z` }]
  })
}

const stamp = (t) => t.toISOString().replace(/\D/g, '').slice(0, 14)

export async function gdelt() {
  const last = /(\d{14})\.gkg\.csv\.zip/.exec(await (await get(GKG_LAST)).text())[1]
  const t0 = Date.UTC(+last.slice(0, 4), +last.slice(4, 6) - 1, +last.slice(6, 8), +last.slice(8, 10), +last.slice(10, 12))
  // đúng dạng URL http trong lastupdate.txt; gọi https trực tiếp trả 404 từ Vercel
  const urls = Array.from({ length: GKG_BATCHES }, (_, i) =>
    `http://data.gdeltproject.org/gdeltv2/${stamp(new Date(t0 - i * 15 * 60000))}.gkg.csv.zip`)
  const batches = await Promise.allSettled(urls.map(async (u) => parseGkg(unzip(Buffer.from(await (await get(u, 15000)).arrayBuffer())))))
  const ok = batches.filter((b) => b.status === 'fulfilled').flatMap((b) => b.value)
  if (!ok.length) throw new Error('GDELT GKG: không tải được lô nào: ' + batches.map((b) => String(b.reason).slice(0, 120)).join(' | '))
  return ok
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
  const settled = await Promise.allSettled([gdelt(), rss()])
  const ok = settled.filter((s) => s.status === 'fulfilled').map((s) => s.value)
  const body = { updated_utc: new Date().toISOString().replace(/\.\d+Z$/, 'Z'), feeds: ['gdelt-gkg', 'theblock'],
    scoring: 'keyword', items: merge(ok), errors: settled.filter((s) => s.status === 'rejected').map((s) => String(s.reason)) }
  res.setHeader('Cache-Control', 's-maxage=60, stale-while-revalidate=300')   // GKG cập nhật 15 phút/lần
  res.status(ok.length ? 200 : 502).json(body)
}
