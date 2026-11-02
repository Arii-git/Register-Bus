Address format : AD+2 bits. -> Top 2 bits pick the region, the rest pick the box, of the data.
Region 0: DATA, the register file entries.
Region 1: offset 0 = CTRL, offset 1 = STATUS, offset 2 = INPUT, offset 3 = unmapped.
Region 2 and 3: unmapped (still)

Any access to an unmapped address sets err high.
