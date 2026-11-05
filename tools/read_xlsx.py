import zipfile, re, xml.etree.ElementTree as ET, sys, json

path = sys.argv[1]
NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"

z = zipfile.ZipFile(path)
names = z.namelist()

# shared strings
shared = []
if "xl/sharedStrings.xml" in names:
    root = ET.fromstring(z.read("xl/sharedStrings.xml"))
    for si in root.findall(f"{NS}si"):
        # concatenate all text nodes
        txt = "".join(t.text or "" for t in si.iter(f"{NS}t"))
        shared.append(txt)

# find sheets
wb = ET.fromstring(z.read("xl/workbook.xml"))
sheets = [(s.get("name"), s.get("sheetId")) for s in wb.iter(f"{NS}sheet")]
print("SHEETS:", sheets, file=sys.stderr)

def col_to_idx(ref):
    m = re.match(r"([A-Z]+)(\d+)", ref)
    letters = m.group(1)
    row = int(m.group(2))
    idx = 0
    for c in letters:
        idx = idx*26 + (ord(c)-64)
    return idx-1, row

# read first worksheet
sheet_path = "xl/worksheets/sheet1.xml"
root = ET.fromstring(z.read(sheet_path))
rows = {}
maxcol = 0
for row in root.iter(f"{NS}row"):
    for c in row.findall(f"{NS}c"):
        ref = c.get("r")
        t = c.get("t")
        cidx, ridx = col_to_idx(ref)
        maxcol = max(maxcol, cidx)
        v = c.find(f"{NS}v")
        val = None
        if v is not None:
            if t == "s":
                val = shared[int(v.text)]
            else:
                val = v.text
        else:
            # inline string
            is_ = c.find(f"{NS}is")
            if is_ is not None:
                val = "".join(tt.text or "" for tt in is_.iter(f"{NS}t"))
        rows.setdefault(ridx, {})[cidx] = val

allrows = []
for ridx in sorted(rows):
    r = rows[ridx]
    allrows.append([r.get(i) for i in range(maxcol+1)])

# print as JSON for downstream
out = {"nrows": len(allrows), "ncols": maxcol+1, "rows": allrows}
print(json.dumps(out, ensure_ascii=False))
