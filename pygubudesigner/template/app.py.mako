<%inherit file="base.py.mako"/>
<%block name="class_definition" filter="trim">
class ${class_name}:
    def __init__(self, master=None):
        self.builder = builder = pygubu.Builder()
        builder.add_resource_path(PROJECT_PATH)
        builder.add_from_file(PROJECT_UI)
        self.mainwindow = builder.get_object('${main_widget}', master)
        %if tkvariables:
        
          %for var in tkvariables:
        self.${var} = None
          %endfor
        builder.import_variables(self, ${tkvariables})
        
        %endif
        %if has_ttk_styles:
        
        self.setup_ttk_styles()
        
        %endif
        builder.connect_callbacks(self)
    
    def run(self):
        self.mainwindow.mainloop()
    %if has_ttk_styles:
    
    def setup_ttk_styles(self):
        # ttk styles configuration
        self.style = style = ttk.Style()
${ttk_styles}
    %endif

${callbacks}\
</%block>
