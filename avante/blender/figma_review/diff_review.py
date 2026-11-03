"""Figma review → Blender change report (no bpy needed).

    python3 figma_review/diff_review.py figma_review/baseline_v001.json CURRENT.json

CURRENT.json is the output of figma_signature.js (run read-only through the Figma MCP tool `use_figma`).
For every concept it lists the artwork layers whose signature changed, were added or were removed, maps each
copy node back to its Page 1 source id (review_map.json) and from there to what has to be regenerated in
Blender (variants_concepts.SPEC): which texture composite, which object, which concept. Only that concept is
listed; shared bottle, studio and other concepts are never affected.

It detects and routes changes. It does NOT apply them: re-exporting the edited layers, rebuilding the concept
and rendering are separate, Claude-run steps (README › "Figma design review").
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def load_spec():
    """SPEC from variants_concepts.py without importing bpy: exec only the colour constants and the dict."""
    src = open(os.path.join(ROOT, 'variants_concepts.py')).read()
    a = src.index("NAVY, GOLD"); b = src.index("\n\n\ndef resize")
    ns = {}
    exec(src[a:b], ns)
    return ns['SPEC']


def routes(spec):
    """original node id → (what, rebuild hint) per concept."""
    r = {}
    for cid, sp in spec.items():
        m = r.setdefault(cid, {})
        for L in sp['labels']:
            for nid, role in L['layers']:
                m[nid] = (f"{L['name']} layer ({role})",
                          f"re-export {nid}; composite {cid}_{L['name']} (COLOR / MASK-FOIL / HEIGHT-EMB); rebuild {cid}_{L['name']}")
        for P in sp['prints']:
            for nid in P['nodes']:
                m[nid] = (f"{P['name']} glass print", f"re-export {nid}; composite {cid}_{P['name']}; rebuild {cid}_{P['name']}")
        for D in sp['discs']:
            for nid, role in D['layers']:
                m[nid] = (f"{D['name']} {D['kind']} medallion ({role})", f"re-export {nid}; composite {cid}_{D['name']}; rebuild {cid}_{D['name']}")
        m.setdefault(sp['foil'], ('foil aim reference', 'recompute root foil_z (variants_stage aim)'))
    return r


def classify(cid, path, name, route):
    if cid == 'C01':
        return ('Concept 1 (v009 pipeline)', 'manual: C01 label is the rev D construction (Figma page 01 § L) built by build_avante_master; '
                'update rev D art, rebuild C01 only, confirm with the C01-vs-v009 signature check')
    if route:
        return route
    if path.startswith('0/1/'):
        return ('label ground / band colours (mask group)', 'update the band y-ranges and colours in SPEC[...]["labels"][...]["stops"]; rebuild that label')
    if path in ('0/0', '0/2') or path.startswith(('0/0/', '0/2/')) or name.startswith('Rectangle ') and path in ('0/3', '0/4', '0/5'):
        return ('bottle illustration / shading (Figma only)', 'no Blender change (the bottle is physical geometry, identical for all concepts)')
    if name in ('Rectangle 7',) or path in ('0/15', '0/16', '0/17') and name in ('Vector', 'Very Superior Old Pale'):
        return ('neck collar LBL-NECK-01', f'collar is a per-concept copy of the C01 collar (copy_collar); re-export and rebuild {cid}_LBL-NECK-01_Collar')
    return ('unmapped layer', 'inspect: new or unlisted artwork; add it to SPEC with a role before rebuilding')


def main(base_fn, cur_fn):
    base = json.load(open(base_fn)); cur = json.load(open(cur_fn))
    rmap = json.load(open(os.path.join(HERE, 'review_map.json')))
    rt = routes(load_spec())
    total = 0
    for cid in [k for k in cur if k in rmap['concepts']]:
        b, c = base.get(cid, {}), cur[cid]
        inv = {v: k for k, v in rmap['concepts'][cid]['original_to_copy'].items()}
        changed = [p for p in c if p in b and c[p]['sig'] != b[p]['sig']]
        added = [p for p in c if p not in b]
        removed = [p for p in b if p not in c]
        # a parent group changes when its children move; report the deepest changed layers first
        leaf = [p for p in changed if not any(q != p and q.startswith(p + '/') for q in changed)]
        print(f"\n{cid}: {len(leaf)} changed, {len(added)} added, {len(removed)} removed")
        for kind, paths, src in (('CHANGED', leaf, c), ('ADDED', added, c), ('REMOVED', removed, b)):
            for p in sorted(paths, key=lambda s: [int(x) for x in s.split('/')]):
                n = src[p]; orig = inv.get(b[p]['id'] if p in b else n['id'], '(new)')   # paths are stable; ids by baseline
                what, todo = classify(cid, p, n['name'], rt.get(cid, {}).get(orig))
                # export from the edited review copy, saved under the source id the pipeline expects
                todo = todo.replace(f're-export {orig}', f're-export {n["id"]} (review copy of {orig}, saved as {orig})')
                print(f"  {kind:8s} {p:8s} {n['id']:>9s} ← {orig:7s} {n['name'][:34]:34s} → {what}\n           {todo}")
                total += 1
        if not (leaf or added or removed):
            print('  no artwork changes since the baseline')
    print(f"\nTOTAL {total} layer change(s)")
    return total


if __name__ == '__main__':
    sys.exit(0 if main(*sys.argv[1:3]) >= 0 else 1)
