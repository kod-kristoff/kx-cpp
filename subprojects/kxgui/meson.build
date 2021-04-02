project('kxgui', 'cpp',
    default_options: [
        'cpp_std=c++17',
    ]
)

incdir = include_directories('../../include')

kxinput_proj = subproject('kxinput')
kxinput_dep = kxinput_proj.get_variable('kxinput_dep')

kxgui = library('kxgui',
    sources: [
        'input_map.cpp',
    ],
    include_directories: incdir,
    dependencies: kxinput_dep,
)

kxgui_dep = declare_dependency(
    include_directories: incdir,
    link_with: kxgui,
)
