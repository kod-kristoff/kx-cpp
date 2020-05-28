project('kxinput', 'cpp',
    default_options: [
        'cpp_std=c++17',
    ]
)

incdir = include_directories('../../include')

kxinput = library('kxinput',
    sources: [
        'input.cpp',
        'input_map.cpp',
    ],
    include_directories: incdir,
)

kxinput_dep = declare_dependency(
    include_directories: incdir,
    link_with: kxinput,
)
