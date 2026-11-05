import json

d = json.load(open('parsed.json', encoding='utf-8'))
rows = d['rows']
data = rows[1:]

COL = {'id':0,'date_s':2,'model_s':5,'year_s':7,'price_s':9,'mileage_s':11,
       'pay_s':13,'city_s':15,'state_s':17,'salesperson':18,'delivery_s':20}

def family(model):
    m = model.lower()
    if m.startswith('911'): return '911'
    if m.startswith('718'): return '718'
    if m.startswith('cayenne'): return 'Cayenne'
    if m.startswith('macan'): return 'Macan'
    if m.startswith('taycan'): return 'Taycan'
    if m.startswith('panamera'): return 'Panamera'
    return 'Outro'

def delivery_group(s):
    if s == 'Delivered': return 'Entregue'
    if s == 'Cancelled': return 'Cancelado'
    return 'Em andamento'

recs = []
for r in data:
    model = r[COL['model_s']]
    recs.append({
        'id': int(r[COL['id']]),
        'model': model,
        'family': family(model),
        'year': int(r[COL['year_s']]),
        'price': round(float(r[COL['price_s']])),
        'mileage': round(float(r[COL['mileage_s']])),
        'payment': r[COL['pay_s']],
        'city': r[COL['city_s']],
        'state': r[COL['state_s']],
        'delivery': r[COL['delivery_s']],
        'deliveryGroup': delivery_group(r[COL['delivery_s']]),
    })

# sanity
from collections import Counter
print("families:", Counter(x['family'] for x in recs))
print("delivery groups:", Counter(x['deliveryGroup'] for x in recs))
print("n:", len(recs), "any Outro family?", [x['model'] for x in recs if x['family']=='Outro'])
print("revenue:", sum(x['price'] for x in recs))

json.dump(recs, open('data.json','w',encoding='utf-8'), ensure_ascii=False)
# also a compact single-line version for embedding
open('data.min.json','w',encoding='utf-8').write(json.dumps(recs, ensure_ascii=False, separators=(',',':')))
print("bytes:", len(open('data.min.json',encoding='utf-8').read()))
