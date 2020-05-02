import bpy
import bmesh

# show UI
### add Tool Panel
class RBG_PT_MenuAddBonesTools(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Rigid Body Gen"
    # bl_context = "mesh_edit"
    bl_label = "Soft Engine"


    @classmethod
    def poll(cls, context):
        return context.mode in {'EDIT_MESH'}

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        col.operator(RBG_OT_AddBonesOnEdges.bl_idname, text="Adding Bones On Edges", icon='BONE_DATA')


# add bones
class RBG_OT_AddBonesOnEdges(bpy.types.Operator):

    bl_idname = "bone_gen.add_bones_onedges"
    bl_label = "Execute Soft Engine"
    bl_description = "Execute Soft Engine"
    bl_options = {'REGISTER', 'UNDO'}

    # def __init__(self):

    # def draw(self, context):

    ###
    def execute(self, context):
        
        object = bpy.context.object
        mesh = object.data
        
        bm = bmesh.from_edit_mesh(mesh)
        
        obamt = createArmature('armature', object.location)
        self.report({'INFO'}, str(obamt))
        
        
        bpy.ops.object.mode_set(mode='EDIT')
        
        eo = bpy.context.edit_object
        mw = eo.matrix_world

        vlist = [e for e in bm.verts if e.select]


       #create Rigidbody object
        for v in vlist:
            wvco = mw @ v.co
            bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=8, radius=0.01, calc_uvs=False, enter_editmode=False, align='WORLD', location=wvco, rotation=(0.0, 0.0, 0.0))
            
            #view setting
            rc = bpy.context.active_object
            rc.name = "rc." + str(v.index)
            rc.show_in_front = True
            rc.display_type = 'WIRE'
            rc.show_in_front = True
            rc.display.show_shadows = False
            rc.hide_render = True
            rc.hide_render = True
            
            ### Set Rigid Body
            bpy.ops.rigidbody.object_add()
            rc.rigid_body.type = "ACTIVE"
            rc.rigid_body.collision_shape = "SPHERE"
            rc.rigid_body.kinematic = False
            rc.rigid_body.mass = 1.0
            rc.rigid_body.friction = 0.5
            rc.rigid_body.restitution = 0.5
            rc.rigid_body.linear_damping = 0.5
            rc.rigid_body.angular_damping = 0.5 

        #create bones
        bpy.context.view_layer.objects.active = obamt[0]
        bpy.ops.object.mode_set(mode='EDIT')
        for v in vlist:
            self.report({'INFO'}, str(v))
              
            bone = obamt[1].edit_bones.new('softbone.' + str(v.index))
            bone.head = v.co
            bone.tail = bone.head + 0.1 * v.normal
#            obamt[0].update_tag(refresh={'OBJECT'})

        #new CHILD_OF
        bpy.ops.object.posemode_toggle()
        for v in vlist:
                       
            co = obamt[0].pose.bones['softbone.' + str(v.index)].constraints.new("CHILD_OF")
            tgt = bpy.data.objects['rc.' + str(v.index)]
            co.target = tgt
#            bpy.ops.constraint.childof_set_inverse(constraint=co.name, owner='BONE')
            co.inverse_matrix = mw @ tgt.matrix_world.inverted()   
            obamt[0].update_tag(refresh={'OBJECT'})
#            bpy.context.scene.update()

            
        bpy.ops.object.mode_set(mode='OBJECT')
        
        for e in bm.edges:
            if (e.select == True):
                print(e)
                self.report({'INFO'}, str(e))
                self.report({'INFO'}, str(e.verts[0].co))
                
                mid = (e.verts[0].co + e.verts[1].co) / 2
                wmid = mw @ mid
                self.report({'INFO'}, str(mid))
                
#        self.report({'INFO'}, str(mw))
#        self.report({'INFO'}, str(object.location))
        
#                bpy.ops.mesh.primitive_cube_add(size=0.1, calc_uvs=True, enter_editmode=False, align='WORLD', location=wmid, rotation=(0.0, 0.0, 0.0))
                bpy.ops.object.empty_add(type='PLAIN_AXES', radius=0.1, align='WORLD', location=wmid)

                
#                createBones(amt, e.verts)
#                
#        bpy.ops.object.mode_set(mode='OBJECT')
        
#        for ed in bpy.context.active_object.data.edges:
#            
#            if (ed.select == True):
#                print("edge index:{0: 2} v0:{0} v1:{1}".format(ed.index, ed.vertices[0], ed.vertices[1]))
        return {'FINISHED'}


def createArmature(name, loc):
    # アーマチュアとオブジェクトを作成
    amt = bpy.data.armatures.new(name+'Amt')
    ob = bpy.data.objects.new(name, amt)
    ob.location = loc
#    ob.show_name = True
 
    # シーンにオブジェクトをリンクしアクティブ化
    scn = bpy.context.collection
    scn.objects.link(ob)
    bpy.context.view_layer.objects.active = ob
#    ob.select_set(state=True)
 
    return [ob,amt]

def createBones(amt, verts):
 
    bone = amt.edit_bones.new('Bone')
    bone.head = verts[0].co
    bone.tail = verts[1].co
    
    return


classes = [
     RBG_PT_MenuAddBonesTools,
     RBG_OT_AddBonesOnEdges
]

# クラスの登録
def register():
     for cls in classes:
         bpy.utils.register_class(cls)

# クラスの登録解除
def unregister():
     for cls in classes:
         bpy.utils.unregister_class(cls)


# main
if __name__ == "__main__":
     register()
