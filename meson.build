project('kx', 'cpp',
    version: '0.0.1',
    default_options: [
        'warning_level=3',
        'cpp_std=c++17',
    ]
)

incdir = include_directories('include')

kxview_proj = subproject('kxview')
kxview_dep = kxview_proj.get_variable('kxview_dep')

kxstate_proj = subproject('kxstate')
kxstate_dep = kxstate_proj.get_variable('kxstate_dep')

kxinput_proj = subproject('kxinput')
kxinput_dep = kxinput_proj.get_variable('kxinput_dep')
