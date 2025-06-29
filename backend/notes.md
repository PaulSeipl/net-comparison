# Provider

## Web Wunder

Sometimes not reachable

### Not Reachable:

```XML
<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">
    <SOAP-ENV:Header/>
    <SOAP-ENV:Body>
        <SOAP-ENV:Fault>
            <faultcode>SOAP-ENV:Server</faultcode>
            <faultstring xml:lang="en">Temporär nicht verfügbar</faultstring>
        </SOAP-ENV:Fault>
    </SOAP-ENV:Body>
</SOAP-ENV:Envelope>
```

### Offers:

Base Reponse

```XML
<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">
    <SOAP-ENV:Header/>
    <SOAP-ENV:Body>
        <Output xmlns:ns2="http://webwunder.gendev7.check24.fun/offerservice">
            <ns2:products>
                ...
            </ns2:products>
            ...
```

Normal Offer
````XML
<ns2:products>
    <ns2:productId>401</ns2:productId>
    <ns2:providerName>WebWunder Starter 20</ns2:providerName>
    <ns2:productInfo>
        <ns2:speed>20</ns2:speed>
        <ns2:monthlyCostInCent>2298</ns2:monthlyCostInCent>
        <ns2:monthlyCostInCentFrom25thMonth>2198</ns2:monthlyCostInCentFrom25thMonth>
        <ns2:contractDurationInMonths>12</ns2:contractDurationInMonths>
        <ns2:connectionType>DSL</ns2:connectionType>
    </ns2:productInfo>
</ns2:products>
```

Offer with percantage Voucher
```XML
<ns2:products>
    <ns2:productId>401</ns2:productId>
    <ns2:providerName>WebWunder Starter 20</ns2:providerName>
    <ns2:productInfo>
        <ns2:speed>20</ns2:speed>
        <ns2:monthlyCostInCent>2298</ns2:monthlyCostInCent>
        <ns2:monthlyCostInCentFrom25thMonth>2198</ns2:monthlyCostInCentFrom25thMonth>
        <ns2:voucher xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="ns2:percentageVoucher">
            <ns2:percentage>11</ns2:percentage>
            <ns2:maxDiscountInCent>10793</ns2:maxDiscountInCent>
        </ns2:voucher>
        <ns2:contractDurationInMonths>12</ns2:contractDurationInMonths>
        <ns2:connectionType>DSL</ns2:connectionType>
    </ns2:productInfo>
</ns2:products>
```

Offer with absolute Voucher


## VerbynDich

Generally very slow

Requests are "paginatated"

### Server Unreachable:

Status Code 503

### Offers:


#### VerbynDich Basic 25

```JSON
{
    "product": "VerbynDich Basic 25",
    "description": "Dieses einzigartige Angebot ist der perfekte Match für Sie. Für nur 30€ im Monat erhalten Sie eine DSL-Verbindung mit einer Geschwindigkeit von 25 Mbit/s. Zögern Sie nicht und schlagen Sie jetzt zu!\n\nBitte beachten Sie, dass die Mindestvertragslaufzeit 12 Monate beträgt. Ab 250GB pro Monat wird die Geschwindigkeit gedrosselt. Mit diesem Angebot erhalten Sie einen Rabatt von 12% auf Ihre monatliche Rechnung bis zum 24. Monat. Der maximale Rabatt beträgt 107€. Ab dem 24. Monat beträgt der monatliche Preis 29€.",
    "last": false,
    "valid": true
}
```

#### VerbinDyich Basic 100

```JSON
{
    "product": "VerbynDich Basic 100",
    "description": "Dieses einzigartige Angebot ist der perfekte Match für Sie. Für nur 40€ im Monat erhalten Sie eine Cable-Verbindung mit einer Geschwindigkeit von 100 Mbit/s. Zögern Sie nicht und schlagen Sie jetzt zu!\n\nBitte beachten Sie, dass die Mindestvertragslaufzeit 12 Monate beträgt. Ab 250GB pro Monat wird die Geschwindigkeit gedrosselt. Mit diesem Angebot erhalten Sie einen Rabatt von 12% auf Ihre monatliche Rechnung bis zum 24. Monat. Der maximale Rabatt beträgt 107€. Ab dem 24. Monat beträgt der monatliche Preis 41€.",
    "last": false,
    "valid": true
}
```

#### VerbinDyich Basic 200

```JSON
{
    "product": "VerbynDich Basic 200",
    "description": "Dieses einzigartige Angebot ist der perfekte Match für Sie. Für nur 45€ im Monat erhalten Sie eine Cable-Verbindung mit einer Geschwindigkeit von 200 Mbit/s. Zögern Sie nicht und schlagen Sie jetzt zu!\n\nBitte beachten Sie, dass die Mindestvertragslaufzeit 12 Monate beträgt. Ab 250GB pro Monat wird die Geschwindigkeit gedrosselt. Mit diesem Angebot erhalten Sie einen Rabatt von 12% auf Ihre monatliche Rechnung bis zum 24. Monat. Der maximale Rabatt beträgt 107€. Ab dem 24. Monat beträgt der monatliche Preis 47€.",
    "last": false,
    "valid": true
}
```

#### VerbinDyich Basic 500

```JSON
{
    "product": "VerbynDich Basic 500",
    "description": "Dieses einzigartige Angebot ist der perfekte Match für Sie. Für nur 50€ im Monat erhalten Sie eine Fiber-Verbindung mit einer Geschwindigkeit von 500 Mbit/s. Zögern Sie nicht und schlagen Sie jetzt zu!\n\nBitte beachten Sie, dass die Mindestvertragslaufzeit 12 Monate beträgt. Ab 250GB pro Monat wird die Geschwindigkeit gedrosselt. Mit diesem Angebot erhalten Sie einen Rabatt von 12% auf Ihre monatliche Rechnung bis zum 24. Monat. Der maximale Rabatt beträgt 107€. Ab dem 24. Monat beträgt der monatliche Preis 48€.",
    "last": false,
    "valid": true
}
```

#### VerbinDyich Basic 1000

```JSON
{
    "product": "VerbynDich Basic 1000",
    "description": "Dieses einzigartige Angebot ist der perfekte Match für Sie. Für nur 57€ im Monat erhalten Sie eine Fiber-Verbindung mit einer Geschwindigkeit von 1000 Mbit/s. Zögern Sie nicht und schlagen Sie jetzt zu!\n\nBitte beachten Sie, dass die Mindestvertragslaufzeit 12 Monate beträgt. Ab 250GB pro Monat wird die Geschwindigkeit gedrosselt. Mit diesem Angebot erhalten Sie einen Rabatt von 12% auf Ihre monatliche Rechnung bis zum 24. Monat. Der maximale Rabatt beträgt 107€. Ab dem 24. Monat beträgt der monatliche Preis 56€.",
    "last": false,
    "valid": true
}
```

#### VerbinDyich Premium 25

```JSON
{
    "product": "VerbynDich Premium 25",
    "description": "Dieses einzigartige Angebot ist der perfekte Match für Sie. Für nur 39€ im Monat erhalten Sie eine DSL-Verbindung mit einer Geschwindigkeit von 25 Mbit/s. Zusätzlich sind folgende Fernsehsender enthalten RobynTV+. Zögern Sie nicht und schlagen Sie jetzt zu!\n\nBitte beachten Sie, dass die Mindestvertragslaufzeit 12 Monate beträgt. Mit diesem Angebot erhalten Sie einen Rabatt von 12% auf Ihre monatliche Rechnung bis zum 24. Monat. Der maximale Rabatt beträgt 107€.",
    "last": false,
    "valid": true
}
```

#### VerbinDyich Premium 50

```JSON
{
    "product": "VerbynDich Premium 50",
    "description": "Dieses einzigartige Angebot ist der perfekte Match für Sie. Für nur 44€ im Monat erhalten Sie eine DSL-Verbindung mit einer Geschwindigkeit von 50 Mbit/s. Zusätzlich sind folgende Fernsehsender enthalten RobynTV+. Zögern Sie nicht und schlagen Sie jetzt zu!\n\nBitte beachten Sie, dass die Mindestvertragslaufzeit 12 Monate beträgt. Mit diesem Angebot erhalten Sie einen Rabatt von 12% auf Ihre monatliche Rechnung bis zum 24. Monat. Der maximale Rabatt beträgt 107€. Ab dem 24. Monat beträgt der monatliche Preis 46€.",
    "last": false,
    "valid": true
}
```

#### VerbinDyich Premium 100

```JSON
{
    "product": "VerbynDich Premium 100",
    "description": "Dieses einzigartige Angebot ist der perfekte Match für Sie. Für nur 49€ im Monat erhalten Sie eine Cable-Verbindung mit einer Geschwindigkeit von 100 Mbit/s. Zusätzlich sind folgende Fernsehsender enthalten RobynTV+. Zögern Sie nicht und schlagen Sie jetzt zu!\n\nBitte beachten Sie, dass die Mindestvertragslaufzeit 12 Monate beträgt. Mit diesem Angebot erhalten Sie einen Rabatt von 12% auf Ihre monatliche Rechnung bis zum 24. Monat. Der maximale Rabatt beträgt 107€. Ab dem 24. Monat beträgt der monatliche Preis 48€.",
    "last": false,
    "valid": true
}
```

#### VerbinDyich Premium 200

```JSON
{
    "product": "VerbynDich Premium 200",
    "description": "Dieses einzigartige Angebot ist der perfekte Match für Sie. Für nur 54€ im Monat erhalten Sie eine Cable-Verbindung mit einer Geschwindigkeit von 200 Mbit/s. Zusätzlich sind folgende Fernsehsender enthalten RobynTV+. Zögern Sie nicht und schlagen Sie jetzt zu!\n\nBitte beachten Sie, dass die Mindestvertragslaufzeit 12 Monate beträgt. Mit diesem Angebot erhalten Sie einen Rabatt von 12% auf Ihre monatliche Rechnung bis zum 24. Monat. Der maximale Rabatt beträgt 107€. Ab dem 24. Monat beträgt der monatliche Preis 55€.",
    "last": false,
    "valid": true
}
```

#### VerbinDyich Premium 500

```JSON
{
    "product": "VerbynDich Premium 500",
    "description": "Dieses einzigartige Angebot ist der perfekte Match für Sie. Für nur 59€ im Monat erhalten Sie eine Fiber-Verbindung mit einer Geschwindigkeit von 500 Mbit/s. Zusätzlich sind folgende Fernsehsender enthalten RobynTV+. Zögern Sie nicht und schlagen Sie jetzt zu!\n\nBitte beachten Sie, dass die Mindestvertragslaufzeit 12 Monate beträgt. Mit diesem Angebot erhalten Sie einen Rabatt von 12% auf Ihre monatliche Rechnung bis zum 24. Monat. Der maximale Rabatt beträgt 107€. Ab dem 24. Monat beträgt der monatliche Preis 57€.",
    "last": false,
    "valid": true
}
```

#### VerbinDyich Premium 1000

```JSON
{
    "product": "VerbynDich Premium 1000",
    "description": "Dieses einzigartige Angebot ist der perfekte Match für Sie. Für nur 65€ im Monat erhalten Sie eine Fiber-Verbindung mit einer Geschwindigkeit von 1000 Mbit/s. Zusätzlich sind folgende Fernsehsender enthalten RobynTV+. Zögern Sie nicht und schlagen Sie jetzt zu!\n\nBitte beachten Sie, dass die Mindestvertragslaufzeit 12 Monate beträgt. Mit diesem Angebot erhalten Sie einen Rabatt von 12% auf Ihre monatliche Rechnung bis zum 24. Monat. Der maximale Rabatt beträgt 107€.",
    "last": false,
    "valid": true
}
```

#### VerbinDyich Premium 25 Young

```JSON
{
    "product": "VerbynDich Premium 25 Young",
    "description": "Dieses einzigartige Angebot ist der perfekte Match für Sie. Für nur 35€ im Monat erhalten Sie eine DSL-Verbindung mit einer Geschwindigkeit von 25 Mbit/s. Zusätzlich sind folgende Fernsehsender enthalten RobynTV+. Zögern Sie nicht und schlagen Sie jetzt zu!\n\nBitte beachten Sie, dass die Mindestvertragslaufzeit 12 Monate beträgt. Dieses Angebot ist nur für Personen unter 27 Jahren verfügbar. Mit diesem Angebot erhalten Sie einen Rabatt von 12% auf Ihre monatliche Rechnung bis zum 24. Monat. Der maximale Rabatt beträgt 107€. Ab dem 24. Monat beträgt der monatliche Preis 36€.",
    "last": false,
    "valid": true
}
```

#### VerbinDyich Premium 50 Young

```JSON
{
    "product": "VerbynDich Premium 50 Young",
    "description": "Dieses einzigartige Angebot ist der perfekte Match für Sie. Für nur 40€ im Monat erhalten Sie eine DSL-Verbindung mit einer Geschwindigkeit von 50 Mbit/s. Zusätzlich sind folgende Fernsehsender enthalten RobynTV+. Zögern Sie nicht und schlagen Sie jetzt zu!\n\nBitte beachten Sie, dass die Mindestvertragslaufzeit 12 Monate beträgt. Dieses Angebot ist nur für Personen unter 27 Jahren verfügbar. Mit diesem Angebot erhalten Sie einen Rabatt von 12% auf Ihre monatliche Rechnung bis zum 24. Monat. Der maximale Rabatt beträgt 107€. Ab dem 24. Monat beträgt der monatliche Preis 38€.",
    "last": false,
    "valid": true
}
```

#### VerbinDyich Premium 100 Young

```JSON
{
    "product": "VerbynDich Premium 100 Young",
    "description": "Dieses einzigartige Angebot ist der perfekte Match für Sie. Für nur 45€ im Monat erhalten Sie eine Cable-Verbindung mit einer Geschwindigkeit von 100 Mbit/s. Zusätzlich sind folgende Fernsehsender enthalten RobynTV+. Zögern Sie nicht und schlagen Sie jetzt zu!\n\nBitte beachten Sie, dass die Mindestvertragslaufzeit 12 Monate beträgt. Dieses Angebot ist nur für Personen unter 27 Jahren verfügbar. Mit diesem Angebot erhalten Sie einen Rabatt von 12% auf Ihre monatliche Rechnung bis zum 24. Monat. Der maximale Rabatt beträgt 107€.",
    "last": false,
    "valid": true
}
```

#### VerbinDyich Premium 200 Young

```JSON
{
    "product": "VerbynDich Premium 200 Young",
    "description": "Dieses einzigartige Angebot ist der perfekte Match für Sie. Für nur 50€ im Monat erhalten Sie eine Cable-Verbindung mit einer Geschwindigkeit von 200 Mbit/s. Zusätzlich sind folgende Fernsehsender enthalten RobynTV+. Zögern Sie nicht und schlagen Sie jetzt zu!\n\nBitte beachten Sie, dass die Mindestvertragslaufzeit 12 Monate beträgt. Dieses Angebot ist nur für Personen unter 27 Jahren verfügbar. Mit diesem Angebot erhalten Sie einen Rabatt von 12% auf Ihre monatliche Rechnung bis zum 24. Monat. Der maximale Rabatt beträgt 107€. Ab dem 24. Monat beträgt der monatliche Preis 52€.",
    "last": false,
    "valid": true
}
```

#### VerbinDyich Premium 500 Young

```JSON
{
    "product": "VerbynDich Premium 500 Young",
    "description": "Dieses einzigartige Angebot ist der perfekte Match für Sie. Für nur 55€ im Monat erhalten Sie eine Fiber-Verbindung mit einer Geschwindigkeit von 500 Mbit/s. Zusätzlich sind folgende Fernsehsender enthalten RobynTV+. Zögern Sie nicht und schlagen Sie jetzt zu!\n\nBitte beachten Sie, dass die Mindestvertragslaufzeit 12 Monate beträgt. Dieses Angebot ist nur für Personen unter 27 Jahren verfügbar. Mit diesem Angebot erhalten Sie einen Rabatt von 12% auf Ihre monatliche Rechnung bis zum 24. Monat. Der maximale Rabatt beträgt 107€. Ab dem 24. Monat beträgt der monatliche Preis 54€.",
    "last": false,
    "valid": true
}
```

#### VerbinDyich Premium 1000 Young

```JSON
{
    "product": "VerbynDich Premium 1000 Young",
    "description": "Dieses einzigartige Angebot ist der perfekte Match für Sie. Für nur 61€ im Monat erhalten Sie eine Fiber-Verbindung mit einer Geschwindigkeit von 1000 Mbit/s. Zusätzlich sind folgende Fernsehsender enthalten RobynTV+. Zögern Sie nicht und schlagen Sie jetzt zu!\n\nBitte beachten Sie, dass die Mindestvertragslaufzeit 12 Monate beträgt. Dieses Angebot ist nur für Personen unter 27 Jahren verfügbar. Mit diesem Angebot erhalten Sie einen Rabatt von 12% auf Ihre monatliche Rechnung bis zum 24. Monat. Der maximale Rabatt beträgt 107€. Ab dem 24. Monat beträgt der monatliche Preis 62€.",
    "last": true,
    "valid": true
}
```

