project('kxview', 'cpp',
    default_options: [
        'cpp_std=c++17',
    ]
)

incdir = include_directories('../../include')

kxview = library('kxview',
    sources: [
        'context.cpp',
        'layered_view.cpp',
        'position.cpp',
        'rectangle.cpp',
        'view.cpp',
    ],
    include_directories: incdir,
)

kxview_dep = declare_dependency(
    imclude_directories: incdir,
    link_with: kxview,
)
