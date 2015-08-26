# -*- coding: utf-8 -*-
"""
Created on Fri Aug 21 09:30:49 2015

@author: URBINS
"""

#Entought imports
from traits.api import HasTraits, Float, Range, Bool, Enum, Instance, \
                       Property, List, on_trait_change
from traitsui.api import View, Group, Item, HSplit, VSplit, InstanceEditor, \
                         TableEditor, Handler
from traitsui.menu import MenuBar, Menu, Action, ToolBar
from traitsui.table_column import ObjectColumn
from tvtk.pyface.scene_editor import SceneEditor
from mayavi.core.ui.engine_view import EngineView
from mayavi.tools.mlab_scene_model import MlabSceneModel
from mayavi.mlab import points3d

class Probe(HasTraits):
    """A class for a probe, the physical ubication of a sensor. Can be a single
    one or an array of probes, defined by the user and modified with dynamic
    forms."""
    #General traits
    x = Float()
    y = Float()
    z = Float()
    
    Type = Enum('Temperature', 'Gauge', 'Other')    
    
    Array = Bool(False)
    
    #Traits for array probes only
    x_angle = Float()
    y_angle = Float()
    z_angle = Float()
    
    x_qty = Range(1)
    y_qty = Range(1)
    z_qty = Range(1)

    x_dist = Float()
    y_dist = Float()
    z_dist = Float()
    
    #View for editing the probe TODO
    gen_view = Group(Item(name = 'x'),
                     Item(name = 'y'),
                     Item(name = 'z'),
                     Item(name = 'Array'),
                     label = "General info",
                     show_border  = True)
    
    arr_view = Group(Item(name = 'x_angle'),
                     Item(name = 'y_angle'),
                     Item(name = 'z_angle'),
                     Item(name = 'x_qty'),
                     Item(name = 'y_qty'),
                     Item(name = 'z_qty'),
                     Item(name = 'x_dist'),
                     Item(name = 'y_dist'),
                     Item(name = 'z_dist'),
                     label = "Array info",
                     show_border  = True,
                     enabled_when = 'Array == True')
    
    view = View(Group(gen_view,
                      arr_view),
                title = "Add / Edit probe",
                buttons = [ "OK" ])

class ProbeHandler ( Handler ):
    """ Define the handler class for the Probe. This class defines all
        of the handler methods for the menu and tool bar actions."""
    
    def quit_ ( self, info ):
        """ Quit the application. """
        info.ui.dispose()

    def add_probe ( self, info ):
        """ Add a new probe. """
        new = Probe()
        ui  = new.edit_traits( kind = 'livemodal' )
        if ui.result:
            info.object.probes.append( new )
        
    def delete_probe ( self, info ):
        """ Delete an existing probee. """
        info.object.probe_selected
        info.object.probes.remove( info.object.probe_selected )
        info.object.probe_selected = None
        
    def show_about ( self, info ):
        """ Display the 'About' view. """
        self.edit_traits( view = 'about' )


class ProbeWindow(HasTraits):
    """The main menu por placing and viewing physical ubications of the probes
    """
    # The scene model.
    scene = Instance(MlabSceneModel, ())

    # The mayavi engine view.
    engine_view = Instance(EngineView)

    # The current selection in the engine tree view.
    current_selection = Property
    
    #Probe add
    probes = List(Probe)
    probe_selected = Instance(Probe)
    prob_done = False
    
    #Actions for menus
    def quit_(self):
        pass #Still not implemented
    
    #Menu
    menu1 = MenuBar(Menu(
                        Action( name= 'Quit', 
                                action = 'quit_' ),
                    name="File")
                    )
    #Toolbar parts
    add_action = Action( 
        name   = 'Add Probe...', 
        action = 'add_probe',
        #image  = ImageResource( 'add_employee', search_path = [ search_path ] )
    )
                     
# 'Delete an existing employee' action:
    delete_action = Action(
        name   = 'Delete Probe',
        action = 'delete_probe',
        enabled_when = 'object.selected is not None',
        #image  = ImageResource( 'delete_employee', search_path = [ search_path ] )
    )

    
    teditor = TableEditor(
        columns = [ ObjectColumn( name = 'x'),
                    ObjectColumn( name = 'y'),
                    ObjectColumn( name = 'z'),
                    ObjectColumn( name = 'Array')],
    selected     = 'probe_selected',
    sortable     = True,
    deletable    = False,
    editable     = False,
    configurable = False
    )  
    #Toolbar
    toolb = ToolBar(add_action, delete_action)                    
    ######################
    view = View(HSplit(VSplit(Item(name='engine_view',
                                   style='custom',
                                   resizable=True,
                                   show_label=False),
                              Item(name='current_selection',
                                   editor=InstanceEditor(),
                                   enabled_when='current_selection is not None',
                                   style='custom',
                                   springy=True,
                                   show_label=False
                                   ),
                              #Item Probe Space
                              Group(Item( 'probes',
                                   show_label = True,
                                   editor = teditor
                                        ),
                                        
                                   ),
                              ),
                       Item(name='scene',
                            editor=SceneEditor(),
                            show_label=False,
                            resizable=True,
                            height=500,
                            width=500),
                      ),
                resizable=True,
                scrollable=True,
                title = 'Probe picker',
                handler=ProbeHandler(),
                menubar = menu1,
                toolbar = toolb
                )

    def __init__(self, **traits):
        HasTraits.__init__(self, **traits)
        self.engine_view = EngineView(engine=self.scene.engine)
        # Hook up the current_selection to change when the one in the engine
        # changes.  This is probably unnecessary in Traits3 since you can show
        # the UI of a sub-object in T3.
        self.scene.engine.on_trait_change(self._selection_change,
                                          'current_selection')
        self.prob_done = True        
        self.generate_probes()
        
    @on_trait_change("probes")    
    def generate_probes(self):
        print "Changed"
        if self.prob_done:
            for i in self.probes:
                points3d(i.x, i.y, i.z)
            
    def _selection_change(self, old, new):
        self.trait_property_changed('current_selection', old, new)

    def _get_current_selection(self):
        return self.scene.engine.current_selection


#For test purposes only
if __name__ == "__main__":
    probs = [Probe(x=0, y=0, z=0), Probe(x=0, y=2, z=0),
             Probe(x=2, y=0, z=0), Probe(x=2, y=2,z=0),
             Probe(x=4, y=0, z=0), Probe(x=4, y=2,z=0),
             Probe(x=6, y=0, z=0), Probe(x=6, y=2,z=0)]
    test = ProbeWindow(probes=probs)#probes=probs)
    test.configure_traits()