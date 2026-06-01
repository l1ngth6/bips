使用方式：

```
python3 gen_bip39_punch_table.py > bip39_table.txt
```

显式指定 BIP39 的 11 位：

```
python3 gen_bip39_punch_table.py --bits 11 > bip39_table.txt
```

如果你的终端里 `○` / `●` 导致错位，可以试：

```
python3 gen_bip39_punch_table.py --ambiguous-width 2 > bip39_table.txt
```

最稳妥的跨终端方案是改用 ASCII 符号：

```
python3 gen_bip39_punch_table.py --zero . --one x > bip39_table.txt
```

输出 Markdown 表格：

```
python3 gen_bip39_punch_table.py --format markdown > bip39_table.md
```

输出 TSV，方便导入 Excel / Numbers / LibreOffice：

```
python3 gen_bip39_punch_table.py --format tsv > bip39_table.tsv
```
