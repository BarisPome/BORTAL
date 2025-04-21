// src/mock/dashboardData.js

export const MOCK_DASHBOARD_DATA = {
    market_overview: {
      indices: [
        {
          name: 'BIST100',
          display_name: 'BIST 100',
          last_price: 9725.48,
          change: 145.82,
          change_percent: 1.52,
          date: '2023-06-15T17:30:00Z'
        },
        {
          name: 'BIST30',
          display_name: 'BIST 30',
          last_price: 10452.23,
          change: 198.36,
          change_percent: 1.93,
          date: '2023-06-15T17:30:00Z'
        },
        {
          name: 'BIST50',
          display_name: 'BIST 50',
          last_price: 8927.15,
          change: 102.45,
          change_percent: 1.16,
          date: '2023-06-15T17:30:00Z'
        }
      ],
      top_gainers: [
        {
          symbol: 'THYAO',
          name: 'Türk Hava Yolları',
          price: 183.75,
          change_percent: 7.82
        },
        {
          symbol: 'SASA',
          name: 'SASA Polyester',
          price: 388.25,
          change_percent: 5.64
        },
        {
          symbol: 'TUPRS',
          name: 'Tüpraş',
          price: 243.80,
          change_percent: 4.92
        },
        {
          symbol: 'KOZAL',
          name: 'Koza Altın',
          price: 456.20,
          change_percent: 4.15
        },
        {
          symbol: 'ASELS',
          name: 'Aselsan',
          price: 82.45,
          change_percent: 3.75
        }
      ],
      top_losers: [
        {
          symbol: 'FROTO',
          name: 'Ford Otosan',
          price: 512.30,
          change_percent: -2.84
        },
        {
          symbol: 'GARAN',
          name: 'Garanti Bankası',
          price: 40.88,
          change_percent: -2.35
        },
        {
          symbol: 'AKBNK',
          name: 'Akbank',
          price: 35.72,
          change_percent: -1.92
        },
        {
          symbol: 'EREGL',
          name: 'Ereğli Demir Çelik',
          price: 124.50,
          change_percent: -1.54
        },
        {
          symbol: 'YKBNK',
          name: 'Yapı Kredi Bankası',
          price: 28.44,
          change_percent: -1.25
        }
      ],
      market_stats: {
        advancing: 62,
        declining: 31,
        unchanged: 7,
        total_stocks: 100
      },
      as_of: new Date().toISOString()
    },
    user_watchlists: [
      {
        id: 1,
        name: 'Favori Hisselerim',
        is_default: true,
        stock_count: 8,
        top_stocks: [
          {
            symbol: 'THYAO',
            name: 'Türk Hava Yolları',
            price: 183.75,
            change_percent: 7.82
          },
          {
            symbol: 'ASELS',
            name: 'Aselsan',
            price: 82.45,
            change_percent: 3.75
          },
          {
            symbol: 'KCHOL',
            name: 'Koç Holding',
            price: 124.35,
            change_percent: 1.94
          },
          {
            symbol: 'GARAN',
            name: 'Garanti Bankası',
            price: 40.88,
            change_percent: -2.35
          },
          {
            symbol: 'SASA',
            name: 'SASA Polyester',
            price: 388.25,
            change_percent: 5.64
          }
        ]
      },
      {
        id: 2,
        name: 'Teknoloji',
        is_default: false,
        stock_count: 4,
        top_stocks: [
          {
            symbol: 'ASELS',
            name: 'Aselsan',
            price: 82.45,
            change_percent: 3.75
          },
          {
            symbol: 'LOGO',
            name: 'Logo Yazılım',
            price: 215.40,
            change_percent: 1.24
          },
          {
            symbol: 'NETAS',
            name: 'Netaş',
            price: 43.24,
            change_percent: 0.84
          },
          {
            symbol: 'KAREL',
            name: 'Karel Elektronik',
            price: 32.76,
            change_percent: -0.52
          }
        ]
      }
    ],
    user_portfolios: [
      {
        id: 1,
        name: 'Ana Portföy',
        is_default: true,
        currency: '₺',
        total_value: 287542.36,
        profit_loss: 18425.75,
        profit_loss_percent: 6.84,
        holding_count: 5,
        top_holdings: [
          { 
            symbol: 'THYAO', 
            name: 'Türk Hava Yolları', 
            quantity: 120, 
            value: 22050.00,
            weight: 7.67
          },
          { 
            symbol: 'GARAN', 
            name: 'Garanti Bankası', 
            quantity: 350, 
            value: 14308.00,
            weight: 4.98
          },
          { 
            symbol: 'ASELS', 
            name: 'Aselsan', 
            quantity: 200, 
            value: 16490.00,
            weight: 5.73
          },
          { 
            symbol: 'SASA', 
            name: 'SASA Polyester', 
            quantity: 80, 
            value: 31060.00,
            weight: 10.80
          },
          { 
            symbol: 'KCHOL', 
            name: 'Koç Holding', 
            quantity: 150, 
            value: 18652.50,
            weight: 6.49
          }
        ]
      },
      {
        id: 2,
        name: 'Emeklilik',
        is_default: false,
        currency: '₺',
        total_value: 124350.75,
        profit_loss: 8245.32,
        profit_loss_percent: 7.12,
        holding_count: 3,
        top_holdings: [
          { 
            symbol: 'TUPRS', 
            name: 'Tüpraş', 
            quantity: 180, 
            value: 43884.00,
            weight: 35.29
          },
          { 
            symbol: 'KOZAL', 
            name: 'Koza Altın', 
            quantity: 95, 
            value: 43339.00,
            weight: 34.85
          },
          { 
            symbol: 'PETKIM', 
            name: 'Petkim', 
            quantity: 1200, 
            value: 37127.75,
            weight: 29.86
          }
        ]
      }
    ],
    recent_news: [
      {
        id: 1,
        title: 'BIST100 Gün İçi Rekor Kırdı',
        source: 'Finans Portalı',
        date: '2023-06-15T12:45:00Z',
        url: '#',
        image_url: '/images/news/bist100-record.jpg'
      },
      {
        id: 2,
        title: 'Merkez Bankası Faiz Kararını Açıkladı',
        source: 'Ekonomi Haberleri',
        date: '2023-06-15T10:30:00Z',
        url: '#',
        image_url: '/images/news/central-bank.jpg'
      },
      {
        id: 3,
        title: 'THYAO Hisseleri Yeni Uçak Alımı Haberiyle Yükselişte',
        source: 'Borsa Gündem',
        date: '2023-06-15T09:15:00Z',
        url: '#',
        image_url: '/images/news/thyao-planes.jpg'
      },
      {
        id: 4,
        title: 'Teknoloji Şirketleri İkinci Çeyrek Beklentilerini Açıkladı',
        source: 'Teknoloji Dünyası',
        date: '2023-06-14T16:20:00Z',
        url: '#',
        image_url: '/images/news/tech-companies.jpg'
      },
      {
        id: 5,
        title: 'Petrol Fiyatları Son 3 Ayın En Yüksek Seviyesinde',
        source: 'Enerji Portalı',
        date: '2023-06-14T14:10:00Z',
        url: '#',
        image_url: '/images/news/oil-prices.jpg'
      }
    ],
    most_viewed: [
      {
        symbol: 'THYAO',
        name: 'Türk Hava Yolları',
        sector: 'Ulaştırma',
        price: 183.75,
        change_percent: 7.82,
        date: '2023-06-15T17:30:00Z'
      },
      {
        symbol: 'GARAN',
        name: 'Garanti Bankası',
        sector: 'Bankacılık',
        price: 40.88,
        change_percent: -2.35,
        date: '2023-06-15T17:30:00Z'
      },
      {
        symbol: 'SASA',
        name: 'SASA Polyester',
        sector: 'Kimya',
        price: 388.25,
        change_percent: 5.64,
        date: '2023-06-15T17:30:00Z'
      },
      {
        symbol: 'ASELS',
        name: 'Aselsan',
        sector: 'Savunma',
        price: 82.45,
        change_percent: 3.75,
        date: '2023-06-15T17:30:00Z'
      },
      {
        symbol: 'KCHOL',
        name: 'Koç Holding',
        sector: 'Holding',
        price: 124.35,
        change_percent: 1.94,
        date: '2023-06-15T17:30:00Z'
      }
    ]
  };