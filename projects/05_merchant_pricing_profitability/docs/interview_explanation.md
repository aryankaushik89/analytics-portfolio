# Interview explanation

I built this project to show how I would structure a merchant pricing decision without hiding the assumptions inside one blended rate.

The data is synthetic. Each row is a fictional merchant month with sales, transactions, refunds and payment mix. I split the economics into fee revenue and five cost components, then calculate contribution margin and a weighted effective rate. The three plans vary the volume markup, transaction fee and monthly fee.

The main result is that the Current plan has the strongest base contribution margin, while Growth has the lowest portfolio effective rate. The segment view shows that the monthly fee can make Growth relatively expensive for small merchants even though its volume markup is lower. I also hold the merchant price fixed and raise credit costs. A 100 basis point shock turns the Growth portfolio negative in this scenario.

I would not use this model as a real quote. The cost schedule is hypothetical and it leaves out support, fraud, hardware, tax and overhead. In a real setting I would replace the assumptions with governed contract and settlement data, reconcile the model to statements, and agree on a margin floor before changing any merchant terms.

