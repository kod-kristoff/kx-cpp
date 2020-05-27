project('kxstate', 'cpp',
    default_options: [
        'cpp_std=c++17',
    ]
)

incdir = include_directories('../../include')

kxstate = library('kxstate',
    sources: [
        'state.cpp',
    ],
    include_directories: incdir,
)

kxstate_dep = declare_dependency(
    include_directories: incdir,
    link_with: kxstate,
)
