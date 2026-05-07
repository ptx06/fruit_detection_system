// 水果类型翻译映射
export const fruitTypeTranslator: Record<string, string> = {
  'apple': '苹果',
  'banana': '香蕉',
  'orange': '橘子'
}

// 成熟度标签翻译映射
export const maturityTranslator: Record<string, string> = {
  // 苹果成熟度标签
  'freshapples': '成熟',
  'rottenapples': '过熟',
  'unripe apple': '未成熟',
  
  // 香蕉成熟度标签
  'freshbanana': '成熟',
  'rottenbanana': '过熟',
  'unripe banana': '未成熟',
  
  // 橘子成熟度标签
  'freshoranges': '成熟',
  'rottenoranges': '过熟',
  'unripe orange': '未成熟'
}

// 翻译水果类型
export function translateFruitType(type: string): string {
  return fruitTypeTranslator[type.toLowerCase()] || type
}

// 翻译成熟度标签
export function translateMaturity(maturity: string): string {
  return maturityTranslator[maturity] || maturity
}

// 简化的成熟度标签（用于筛选）
export const simplifiedMaturityLabels: Record<string, string> = {
  'unripe': '未成熟',
  'ripe': '成熟',
  'overripe': '过熟'
}

// 获取简化的成熟度标签
export function getSimplifiedMaturity(maturity: string): string {
  const lowerMaturity = maturity.toLowerCase()
  if (lowerMaturity.includes('unripe')) return 'unripe'
  if (lowerMaturity.includes('fresh')) return 'ripe'
  if (lowerMaturity.includes('rotten')) return 'overripe'
  return maturity
}