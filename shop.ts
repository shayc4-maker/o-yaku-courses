export interface ShopCategory {
  id: string;
  label: string;
  en?: string;
}

export const SHOP_CATS: ShopCategory[] = [
  { id: 'all', label: 'הכל' },
  { id: 'trees', label: 'עצים', en: 'Trees' },
  { id: 'pots', label: 'כלי קרמיקה', en: 'Ceramics' },
  { id: 'tools', label: 'כלי עבודה', en: 'Tools' },
  { id: 'soil', label: 'מצע', en: 'Soil' },
  { id: 'pest', label: 'הדברה', en: 'Pest control' },
];

export interface ShopItem {
  cat: string;
  name: string;
  meta: string;
  price: number;
  stock: number;
}

// Client-side seed only — no payment or inventory backend yet (out of the approved live-data
// scope for this build). The prototype's shop is a "request an order" flow, not checkout.
export const SHOP_ITEMS: ShopItem[] = [
  { cat: 'trees', name: 'זית, חומר גלם', meta: 'גיל 8 · גובה 40 ס״מ', price: 420, stock: 3 },
  { cat: 'trees', name: 'ערער סן־חוזה, מעוצב', meta: 'גיל 12 · שוהין', price: 1150, stock: 1 },
  { cat: 'trees', name: 'פיקוס מיקרוקרפה', meta: 'גיל 6 · לפני עיצוב', price: 260, stock: 5 },
  { cat: 'trees', name: 'אורן שחור יפני', meta: 'גיל 15 · חומר גלם', price: 1800, stock: 0 },
  { cat: 'pots', name: 'כלי מלבן, גלזורה כחולה', meta: '32 × 24 × 8 ס״מ', price: 640, stock: 1 },
  { cat: 'pots', name: 'כלי אובאל, ללא גלזורה', meta: '28 × 20 × 6 ס״מ', price: 520, stock: 2 },
  { cat: 'pots', name: 'כלי עגול לשוהין', meta: 'קוטר 12 · גובה 5 ס״מ', price: 240, stock: 4 },
  { cat: 'pots', name: 'מוקו, גלזורה חמצון ברזל', meta: '30 × 22 × 7 ס״מ', price: 780, stock: 1 },
  { cat: 'tools', name: 'מזמרה קעורה', meta: 'פלדה שחורה · 180 מ״מ', price: 190, stock: 8 },
  { cat: 'tools', name: 'מזמרת עיצוב', meta: 'נירוסטה · 200 מ״מ', price: 220, stock: 6 },
  { cat: 'tools', name: 'חוט אלומיניום 2.5 מ״מ', meta: 'גליל 500 גרם', price: 65, stock: 20 },
  { cat: 'tools', name: 'קלשון שורשים', meta: 'שלוש שיניים', price: 85, stock: 7 },
  { cat: 'soil', name: 'אקדמה', meta: 'גרגר בינוני · 14 ליטר', price: 140, stock: 12 },
  { cat: 'soil', name: 'פומיס', meta: 'גרגר בינוני · 14 ליטר', price: 95, stock: 9 },
  { cat: 'soil', name: 'לבה שחורה', meta: 'גרגר קטן · 14 ליטר', price: 110, stock: 0 },
  { cat: 'soil', name: 'תערובת הסטודיו', meta: 'לעצים נשירים · 10 ליטר', price: 120, stock: 15 },
  { cat: 'pest', name: 'שמן נים', meta: '250 מ״ל · תרכיז', price: 55, stock: 10 },
  { cat: 'pest', name: 'סבון אשלגן', meta: '500 מ״ל · מוכן לשימוש', price: 42, stock: 14 },
  { cat: 'pest', name: 'קוטל פטריות נחושת', meta: '100 גרם', price: 68, stock: 6 },
];
