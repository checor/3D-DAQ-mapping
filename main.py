# -*- coding: utf-8 -*-
"""
Created on Fri Aug 21 09:30:49 2015

@author: URBINS
"""

#Entought imports
from traits.api import HasTraits, Float, Range, Bool, Enum, Instance, \
                       Property, List
from traitsui.api import View, Group, Item, HSplit, VSplit, InstanceEditor, \
                         TableEditor, Handler
from traitsui.menu import MenuBar, Menu, Action
from tvtk.pyface.scene_editor import SceneEditor
from mayavi.core.ui.engine_view import EngineView
from mayavi.tools.mlab_scene_model import MlabSceneModel

class Probe(HasTraits):
    """A class for a probe, the physical ubication of a sensor. Can be a single
    one or an array of probes, defined by the user and modified with dynamic
    forms."""
    #General traits
    x = Float()
    y = Float()
    z = Float()
    
    Type = Enum('Temperature')    
    
    Array = Bool(False)
    
    #Traits for array probes only
    x_angle = Float()
    y_angle = Float()
    z_angle = Float()
    
    x_qty = Range(0)
    y_qty = Range(0)
    z_qty = Range(0)

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
                     Item(name = 'y_qty'),
                     Item(name = 'z_qty'),
                     Item(name = 'y_qty'),
                     label = "Array info",
                     show_border  = True,
                     enabled_when = 'Array == True')
    
    view = View(Group(gen_view,
                      arr_view),
                title = "Add / Edit probe",
                buttons = [ "OK" ])

class ProbePicker(HasTraits):
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
    
    #Probe adding techniques
    def add_probe ( self, info ):
        """ Add a new probe """
        new = Probe()
        ui  = new.edit_traits( kind = 'livemodal' )
        if ui.result:
            info.object.employees.append( new )
    
    #Actions for menus
    def quit_(self):
        pass #Still not implemented
    
    #Menu
    menu1 = MenuBar(Menu(
                        Action( name= 'Quit', 
                                action = 'quit_' ),
                    name="File")
                    )
    
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
                                   show_label=False),
                              #Item Probe Space
                              Group(Item( 'probes',
                                   show_label = False,
                                   editor = TableEditor() ) ),
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
                menubar = menu1
                )

    def __init__(self, **traits):
        HasTraits.__init__(self, **traits)
        self.engine_view = EngineView(engine=self.scene.engine)

        # Hook up the current_selection to change when the one in the engine
        # changes.  This is probably unnecessary in Traits3 since you can show
        # the UI of a sub-object in T3.
        self.scene.engine.on_trait_change(self._selection_change,
                                          'current_selection')

        self.generate_data_mayavi()

    def generate_data_mayavi(self):
        """Shows how you can generate data using mayavi instead of mlab."""
        from mayavi.sources.api import ParametricSurface
        from mayavi.modules.api import Outline, Surface
        e = self.scene.engine
        s = ParametricSurface()
        e.add_source(s)
        e.add_module(Outline())
        e.add_module(Surface())

    def _selection_change(self, old, new):
        self.trait_property_changed('current_selection', old, new)

    def _get_current_selection(self):
        return self.scene.engine.current_selection

class ProbeHandler ( Handler ):
    """ Define the handler class for the HRDemo view. This class defines all
        of the handler methods for the menu and tool bar actions."""
    
    def quit ( self, info ):
        """ Quit the application. """
        info.ui.dispose()


#For test purposes only
prebees = [Probe()]
test = ProbePicker()
test.configure_traits()