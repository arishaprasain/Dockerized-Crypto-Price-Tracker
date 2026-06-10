show databases;
use crypto_tracker;
show tables;
select * from prices;

describe prices;

SELECT coin, price_change_pct
FROM prices
WHERE fetched_at IN (
    SELECT MAX(fetched_at) 
    FROM prices 
    GROUP BY coin
)
ORDER BY price_change_pct DESC;

SELECT coin,
ROUND(100 - ((price_usd - low_24h) / (high_24h - low_24h)) * 100, 2) AS buy_signal
FROM prices
WHERE fetched_at IN (
    SELECT MAX(fetched_at)
    FROM prices
    GROUP BY coin
)
ORDER BY buy_signal DESC;


SELECT coin, price_usd, low_24h, high_24h, fetched_at
FROM prices
WHERE fetched_at IN (
    SELECT MAX(fetched_at)
    FROM prices
    GROUP BY coin
)