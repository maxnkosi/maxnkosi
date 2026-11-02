import json, struct, sys
b = open(sys.argv[1], "rb").read()
n = struct.unpack("<I", b[12:16])[0]
j = json.loads(b[20:20+n])
print("meshes:", len(j.get("meshes", [])), [m["name"] for m in j["meshes"]])
print("animations:", len(j.get("animations", [])))
print("cameras:", len(j.get("cameras", [])), "lights ext:", "KHR_lights_punctual" in j.get("extensionsUsed", []))
for i, nd in enumerate(j["nodes"]):
    print(i, nd.get("name"), {k: nd[k] for k in ("rotation","translation","scale","children","mesh") if k in nd})
for m in j["meshes"]:
    p = m["primitives"][0]["attributes"]; print(m["name"], sorted(p))
    a = j["accessors"][p["POSITION"]]; print("  count", a["count"], "min", [round(x,3) for x in a["min"]], "max", [round(x,3) for x in a["max"]])
print("materials", json.dumps(j["materials"])[:600]); print("textures", j.get("textures"))
assert len(j["meshes"]) == 3 and not j.get("animations")
print("OK")
