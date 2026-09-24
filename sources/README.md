# sources/

The papers behind every fdbx skill. Only this README and `manifest.json` are
tracked: the papers themselves are copyrighted, so each person rebuilds the
library locally.

```bash
python3 scripts/fetch_sources.py      # downloads what is missing, extracts per-page text
python3 scripts/check_provenance.py   # confirms every cited anchor is on its cited page
```

After fetching:

```
sources/
├── manifest.json            key → file, url, page offset, citation, licence
├── <key>.pdf | <key>.html   the source as published
└── pages/<key>/NNN.txt      text of PDF page NNN (HTML sources: one file)
```

**Page numbers.** Skills cite printed page numbers (`p. 7`). `page_offset` in
the manifest converts them: printed page = PDF page + offset. Where a source
prints no page numbers, the manifest says `p. N` means PDF page N. HTML sources
are cited by section (`§ Heading`).

To check a claim yourself, open the skill's `references/provenance.md`, find
the row, open the PDF at the cited page and search for the anchor phrase.
