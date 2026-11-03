"""Avante variants master: staging for the one shared studio (also stored in the .blend as a text block).

stage('single', 'C05', cam)  the chosen concept stands on the v009 hero mark (origin), the other four are
                             hidden from render, so nothing else casts shadows or shows in reflections.
                             Every studio light, card and camera is the v009 rig, unchanged.
stage('lineup', None, cam)   all five stand on their lineup marks (CONCEPT_xx root 'lineup_x').

Camera-dependent cards follow the v009 rules (aim_studio): the brandy back card tracks the camera behind
each visible bottle, and the foil strip sits where the foil mirrors the camera. A concept's own foil
heights live on its root ('foil_z', 'emblem_z'); Concept 1 keeps the per-camera v009 values.
"""
import bpy, math
from mathutils import Vector

MM = 0.001
CONCEPTS = ['C01', 'C05', 'C06', 'C07', 'C10']
CONCEPT_AIM_CAMS = {'CAM_Hero', 'CAM_ThreeQuarter', 'CAM_Shoulder', 'CAM_Shoulder_34', 'CAM_Corner', 'CAM_Turntable'}


def _look_at(ob, target):
    d = Vector(target) - ob.location
    ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


def front_point(z, x=0.0):
    """Point on the front face (-Y) of the bottle at height z (m), from the glass mesh's own data."""
    import build_avante_master as B
    zm = z / MM
    return Vector((x, -B.width_at(zm) / 2 * MM, z)), (B.width_at(zm + 0.5) - B.width_at(zm - 0.5)) / 2


def mirror_card(card, cam, z, x=0.0):
    p, dw = front_point(z, x)
    n = Vector((0.0, -1.0, -dw)).normalized()
    v = cam.matrix_world.translation - p
    r = 2 * n.dot(v) * n - v
    if r.z < 0 and p.z + r.z < 0.02:  # mirror points into the floor: card stands on the table instead
        r *= (0.02 - p.z) / r.z
    card.location = p + r; _look_at(card, p)


def root(cid):
    return bpy.data.objects[cid + '_ROOT']


def stage(mode='single', concept='C01', cam=None):
    sc = bpy.context.scene
    cam = cam or sc.camera
    if isinstance(cam, str): cam = bpy.data.objects[cam]
    sc.camera = cam
    for cid in CONCEPTS:
        r = root(cid); col = bpy.data.collections['CONCEPT_' + cid[1:]]
        on = (mode == 'lineup') or cid == concept
        col.hide_render = not on; col.hide_viewport = not on
        r.location = (r['lineup_x'], 0.0, 0.0) if mode == 'lineup' else (0.0, 0.0, 0.0)
        rig = bpy.data.objects.get('RIG_BackCard_' + cid)
        if rig:  # lineup back cards: one behind each bottle; off in single mode (the v009 card serves)
            rig.hide_render = mode != 'lineup'
            rig.constraints[0].target = cam
            for ch in rig.children: ch.hide_render = mode != 'lineup'
    ap = bpy.data.objects.get('ENV_Floor_Lineup_Apron')
    if ap: ap.hide_render = mode != 'lineup'
    sw, swl = bpy.data.objects['ENV_Sweep'], bpy.data.objects.get('ENV_Sweep_Lineup')
    if swl: swl.hide_render = mode != 'lineup'; sw.hide_render = mode == 'lineup'
    v9 = bpy.data.objects['RIG_BackCard']; v9.constraints[0].target = cam
    bpy.data.objects['CRD_Brandy_Back'].hide_render = mode == 'lineup'
    strip, strip2 = bpy.data.objects['CRD_Foil_Strip'], bpy.data.objects['CRD_Foil_Strip_Roundel']
    lstrip = bpy.data.objects.get('CRD_Foil_Strip_Lineup')
    pstrip = bpy.data.objects.get('CRD_Foil_Strip_Print')
    if pstrip: pstrip.hide_render = True
    if mode == 'lineup':
        strip.hide_render = True; strip2.hide_render = True
        if lstrip:
            lstrip.hide_render = False
            mirror_card(lstrip, cam, cam.get('foil_aim_z', 0.11))
    else:
        if lstrip: lstrip.hide_render = True
        strip.hide_render = False
        r = root(concept)
        if concept == 'C01':  # v009 behaviour, exactly
            aim = cam.get('foil_aim_z', 0.137); aim2 = 0.0422
        else:
            # hero-type cameras look at the concept's own foil copy; macros carry their own aim height
            if cam.name in CONCEPT_AIM_CAMS or cam.get('lineup'): aim = r.get('foil_z', 0.12)
            else: aim = cam.get('foil_aim_z_' + concept, cam.get('foil_aim_z', r.get('foil_z', 0.12)))
            aim2 = r.get('emblem_z', 0.0422)
        mirror_card(strip, cam, aim)
        strip.active_material.node_tree.nodes['STRENGTH'].inputs[1].default_value = strip['base_strength'] * cam.get('foil_strength', 1.0)
        mirror_card(strip2, cam, aim2)
        strip2.hide_render = abs(aim - aim2) < 0.01
        if pstrip and concept != 'C01' and r.get('prints'):  # the active concept's gold glass prints
            lp = bpy.data.collections['LNK_Prints']
            for ob in list(lp.objects): lp.objects.unlink(ob)
            for ob in r['prints'].split(','): lp.objects.link(bpy.data.objects[ob])
            mirror_card(pstrip, cam, r['print_z']); pstrip.hide_render = False
        lnk = bpy.data.collections.get('LNK_Roundel')
        if lnk:  # the small strip lights only the active concept's emblem
            for ob in list(lnk.objects): lnk.objects.unlink(ob)
            for ob in r.get('emblems', '').split(','):
                if ob and ob in bpy.data.objects: lnk.objects.link(bpy.data.objects[ob])
    bpy.context.view_layer.update()
    return cam
