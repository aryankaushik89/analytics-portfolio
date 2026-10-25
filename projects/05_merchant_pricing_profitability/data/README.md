# Data notes

`synthetic_merchants.csv` contains 360 authored merchant-month records generated with a fixed seed. It does not contain names, account details, payment credentials or records from Moneris, Visa, Mastercard, an employer or any assessment.

The generator creates segment, channel, monthly processed sales, transaction count, average ticket, refund rate, international share, premium-card share and debit share. The values are plausible inputs for a pricing demonstration, not estimates of the Canadian market.

Recreate the file from the project root with:

```bash
python src/generate_data.py
```

The project code is MIT licensed. The synthetic data may be reused with attribution to this project. External reference pages remain subject to their publishers' terms.

