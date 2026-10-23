# Project working notes

This is an operational threshold project, not another generic fraud classifier. Keep the natural class balance, preserve the chronological split and never tune with the final test set. Fit preprocessing only on the training portion.

Use the authored synthetic transaction data only. Do not suggest that the records came from a bank, processor or employer. Review cost, customer-friction cost and recovery rate are scenario assumptions.

Keep the notebook readable: numbered sections, short cells, imports on separate lines, visible check tables and no assert statements. Automated assertions belong in `tests/`.

The dashboard must show how threshold and review capacity change the queue. Keep its presentation modest and make the controls, exports and empty states work.
