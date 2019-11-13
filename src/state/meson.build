project('kxview', 'cpp',
    default_options: [
        'cpp_std=c++17',
    ]
)

incdir = include_directories('../../include')

kx_view = library('kxview',
    sources: [
        'context.cpp',
        'position.cpp',
        'rectangle.cpp',
        'view.cpp',
    ],
    include_directories: incdir,
)

kx_view_dep = declare_dependency(
    imclude_directories: incdir,
    link_with: kx_view,
)
