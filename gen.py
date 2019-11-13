#!/usr/bin/env python3

import os
import re

import jinja2


def snake_case(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def ensure_list(x):
    if x is None:
        x = []
    elif not isinstance(x, list):
        x = [x]

    return x


def gen_filename(base, ns, name, suffix):
    if base:
        return os.path.join(base, *ns, snake_case(name) + suffix)
    else:
        return os.path.join(*ns, snake_case(name) + suffix)


def include_header(ns, mod, suffix):
    path = "/".join(ns) + f"/{ snake_case(mod) }{ suffix }"
    return f'#include "{ path  }"'


def include_guard(children):
    children = ensure_list(children)

    def _include_guard(ns, cls, suffix):
        _inc_guard = f"{ '_'.join(ns).upper() }_{ snake_case(cls.name).upper() }{ suffix.replace('.', '_').upper() }_INCLUDED"
        yield f"#ifndef { _inc_guard }"
        yield f"#define { _inc_guard }"
        yield ""
        for child in children:
            yield from child(ns, cls, suffix)
        yield f"#endif // { _inc_guard }"
        yield ""

    return _include_guard


def namespace(children=None):
    children = ensure_list(children)

    def _namespace(ns, cls, suffix):
        _ns = '::'.join(ns)
        yield f"nanespace { _ns }"
        yield "{"
        for child in children:
            yield from child(ns, cls, suffix)
        yield f"}} // namespace { _ns }"
        yield ""

    return _namespace


def class_fwd_decl(child=None):
    print(f"child={child}")
    def _class_fwd_decl(ns, cls, suffix):
        yield "    // Forward declaration"
        yield f"    class { cls.name };"
        yield ""
        if child:
            yield from child(ns, cls, suffix)

    return _class_fwd_decl


def gen_doc(indent, cls=None, func=None):
    yield f"{ indent }/** Brief description."
    yield f"{ indent }  *"
    yield f"{ indent }  * Detailed description."
    if func and func.args:
        yield f"{ indent }  *"
        for arg in func.args:
            yield f"{ indent }  * @param { arg.name } Description."
    if func and func.return_type:
        yield f"{ indent }  *"
        yield f"{ indent }  * @return { func.return_type.fmt() } Description."
    yield f"{ indent }  */"

def fun_name(fn, cls=None):
    if not cls:
        return fn.name
    else:
        if isinstance(fn, Constructor):
            fn_name = cls.name
        elif isinstance(fn, Destructor):
            fn_name = f"~{ cls.name }"
        else:
            fn_name = fn.name
        return fn_name

def gen_fun_decl(indent, i_mul, cls=None):
    if cls:
        for fn in cls.methods:
            yield from gen_doc(indent*i_mul, func=fn)
            if fn.virtual:
                yield f"{ indent*i_mul }virtual"
            if fn.return_type:
                yield f"{ indent*i_mul }{ fn.return_type.fmt() }"

            yield f"{ indent*i_mul }{ fun_name(fn, cls) }(" + ("" if fn.args else (")" if fn.const or fn.abstract else ");"))
            if fn.args:
                for i, arg in enumerate(fn.args):
                    yield f"{ indent*(i_mul+1) }{ arg.type.fmt() } { arg.name }" + ("" if i == (len(fn.args) - 1) else ",")
                yield f"{ indent*i_mul }" + (")" if fn.const or fn.abstract else ");")
            ending = None
            if fn.const:
                if fn.abstract:
                    ending = "const = 0;"
                else:
                    ending = "const;"
            elif fn.abstract:
                ending = "= 0;"
            if ending:
                yield f"{ indent*i_mul }{ ending }"


def include_self(children=None):
    children = ensure_list(children)

    def _include_self(ns, mod, suffix):
        yield f'#include "{ gen_filename(None, ns, mod.name, ".hpp") }"'
        yield ""

        for child in children:
            yield from child(ns, mod, suffix)

    return _include_self


def class_decl(child=None):
    print(f"child={child}")
    def _class_decl(ns, cls, suffix):
        indent = ' '*4
        yield from gen_doc(indent)
        yield f"{ indent }class { cls.name }"
        if cls.bases:
            yield f"{ indent*2 }: public { cls.bases[0].fmt() }"
            for base in cls.bases[1:]:
                yield f"{ indent*2 }, public { base.fmt() }"
        yield f"{ indent }{{"
        if cls.methods:
            yield f"{ indent }public:"
            yield from gen_fun_decl(indent, 2, cls)
        yield f"{ indent }}}; // class { cls.name }"
        if child:
            yield from child(ns, cls, suffix)

    return _class_decl

def include_dep(dep, suffix):
    if isinstance(dep, Primitive):
        return

    if suffix.endswith('.hpp'):
        if isinstance(dep, FwdDep):
            yield dep.type.as_fwd_include()
        elif isinstance(dep, SrcDep):
            return
        else:
            yield dep.type.as_include()
    else:
        if isinstance(dep, (FwdDep, SrcDep)):
            yield dep.type.as_include()


def include_deps(children=None):
    children = ensure_list(children)

    def _include_deps(ns, cls, suffix):
        if cls:
            for dep in cls.deps:
                yield from include_dep(dep, suffix)
        yield ""

        for child in children:
            yield from child(ns, cls, suffix)

    return _include_deps


def fun_def_debug(ns, fn, cls=None):
    if cls:
        if isinstance(fn, Constructor):
            return f"{ '::'.join(ns) }::{ cls.name } created."
        elif isinstance(fn, Destructor):
            return f"{ '::'.join(ns) }::{ cls.name } destroyed."

    return f"{ '::'.join(ns) }::{ fn.name } called."


def class_def(children=None):
    children = ensure_list(children)

    def _class_def(ns, cls, suffix):
        if cls:
            for fn in cls.methods:
                indent = " "*4
                if fn.virtual:
                    yield "/* virtual */"
                if fn.return_type:
                    yield f"{ fn.return_type.fmt() }"
                yield f"{ cls.name }::{ fun_name(fn, cls) }(" + ("" if fn.args else ")")
                if fn.args:
                    for i, arg in enumerate(fn.args):
                        yield f"{ indent }{ arg.type.fmt() } { arg.name }" + ("" if i == (len(fn.args) - 1) else ",")
                    yield ")"
                if fn.const:
                    yield "const"
                if isinstance(fn, Constructor):
                    if cls.bases:
                        yield f"{ indent }: { cls.bases[0].cls }()"
                        for base in cls.bases[1:]:
                            yield f"{ indent }, { base.cls }()"

                yield "{"
                yield f"{ indent }std::cout << { fun_def_debug(ns, fn, cls) } << std::endl;"
                yield f"}} // method { cls.name }::{ fun_name(fn, cls) }"
                yield ""

        for child in children:
            yield from child(ns, cls, suffix)
    return _class_def

header_fwd = include_guard(namespace(class_fwd_decl()))
header = include_guard([
    include_deps(),
    namespace(class_decl())
    ])
#header_fwd = include_guard(class_fwd_decl())
source = include_self([
    include_deps(),
    namespace(class_def())
    ])


def write_file(filename, content):
    print(f'{filename}')
    print('-'*10)
    for line in content:
        print(f"{line}")


class Obj:
    def gen(self, ns=[], inc_dir='include', src_dir='src'):
        pass


def ensure_path(base, ns):
    path = os.path.join(base, *ns)
    print(f"path = { path }")

    os.makedirs(path, exist_ok=True)


class Namespace:
    def __init__(self,
                 name,
                 objs,
                 ):
        self.name = name
        self.objs = objs

    def gen(self, ns=[], inc_dir='include', src_dir='src'):
        _ns = [n for n in ns]
        _ns.append(self.name)

        print(f"Namespace { '::'.join(_ns) }")
        ensure_path(inc_dir, _ns)
        ensure_path(src_dir, _ns)

        for o in self.objs:
            o.gen(_ns)


class CodeFile:
    def __init__(self,
                 *,
                 classess=None,
                 funcs=None,
                ):
        if not classes:
            classes = []
        self.classes = classes

        if not funcs:
            funcs = []
        self.funcs = funcs


class HeaderFwd(CodeFile):
    def __init__(self,
                 *args,
                 **kwargs
                ):
        super().__init__(*args, **kwargs)


class Header(CodeFile):
    def __init__(self,
                 *args,
                 **kwargs
                ):
        super().__init__(*args, **kwargs)


class Source(CodeFile):
    def __init__(self,
                 *args,
                 **kwargs
                ):
        super().__init__(*args, **kwargs)


class Function:
    def __init__(self,
                 name,
                 return_type,
                 args=[],
                 *,
                 template=False,
                ):
        self.name = name
        self.template = template
        self.return_type = return_type
        self.args = args


class Method(Function):
    def __init__(self,
                 name,
                 return_type,
                 args=[],
                 *,
                 template=False,
                 virtual=False,
                 abstract=False,
                 const=False,
                ):
        super().__init__(
                name,
                return_type,
                args,
                template=template
        )
        self.virtual = virtual
        self.abstract = abstract
        self.const = const


class Constructor(Method):
    def __init__(self,
                 args=[],
                 *,
                 template=False
                ):
        super().__init__(
            'Constructor',
            None,
            args,
            template=template,
            virtual=False,
        )


class Destructor(Method):
    def __init__(self,
                 *,
                 virtual=True,
                ):
        super().__init__(
            'Destructor',
            None,
            template=False,
            virtual=virtual,
        )

class Primitive:
    def __init__(self, cls):
        self.cls = cls

    def fmt(self) -> str:
        return f"{ self.cls }"


void = Primitive('void')


class Type:
    def __init__(self, ns, cls):
        self.ns = ensure_list(ns)
        self.cls = cls

    def fmt(self) -> str:
        return f"{ '::'.join(self.ns) }::{ self.cls }"

    def as_include(self):
        return f'#include "{ gen_filename(None, self.ns, self.cls, ".hpp") }"'

    def as_fwd_include(self):
        return f'#include "{ gen_filename(None, self.ns, self.cls, "_fwd.hpp") }"'


class Pointer(Type):
    def __init__(self, *args):
        super().__init__(*args)

    def fmt(self) -> str:
        return f"{ super().fmt() } *"


class Std(Type):
    def __init__(self, header):
        super().__init__(ns=None, cls=header)

    def as_include(self):
        return f"#include <{ self.cls }>"

    def as_fwd_include(self):
        return

class Dep:
    def __init__(self, type_):
        self.type = type_

    def __repr__(self):
        return f"Dep({self.type})"


class FwdDep(Dep):
    def __init__(self, type_):
        super().__init__(type_)

    def __repr__(self):
        return f"FwdDep({self.type})"


class SrcDep(Dep):
    def __init__(self, type_):
        super().__init__(type_)

    def __repr__(self):
        return f"SrcDep({self.type})"


class Arg:
    def __init__(self, type_, name):
        self.type = type_
        self.name = name


class Class(Obj): #(HeaderFwd, Header, Source):
    def __init__(self,
                 name,
                 *,
                 virtual=True,
                 methods=None,
                 bases=None,
                ):
        #super().__init__(classes=[self])
        self.name = name
        self.virtual = virtual
        self.methods = ensure_list(methods)

        self.bases = ensure_list(bases)
        self.deps = [SrcDep(Std('iostreams'))]
        fwds = []
        deps = []
        srcdeps = []

        def add_dep(x):
            if x is None:
                return
            if not isinstance(x, Primitive):
                if isinstance(x, Pointer):
                    fwds.append(FwdDep(x))
                else:
                    deps.append(Dep(x))

        for m in self.methods:
            add_dep(m.return_type)
            for a in m.args:
                add_dep(a.type)

        if fwds:
            self.deps.extend(fwds)
        if deps:
            self.deps.extend(deps)
        for b in self.bases:
            self.deps.append(Dep(b))
        print(f"{self!r}")
        print(f"deps = { self.deps }")

    def __repr__(self):
        return f"Class({self.name}, bases={self.bases}, methods={self.methods})"

    def gen(self, ns, inc_dir='include', src_dir='src'):
        print(f"Class { '::'.join(ns) }::{ self.name }")
        write_file(
            gen_filename(inc_dir, ns, self.name, '_fwd.hpp'),
            header_fwd(ns, self, '_fwd.hpp')
        )

        write_file(
            gen_filename(inc_dir, ns, self.name, '.hpp'),
            header(ns, self, '.hpp')
        )
        src_ns = ns
        if 'kx' in ns:
            src_ns = [x for x in ns if x != 'kx']
        write_file(
            gen_filename(src_dir, src_ns, self.name, '.cpp'),
            source(ns, self, '.cpp')
        )


configs = [
    {
    'data': [
        Namespace('kx',[
            Namespace('platform', [
                Class('Application'),
            ]),  # Namespace platform
            Namespace('rend', [
                Class('Renderer',
                    methods=[
                        Constructor(),
                        Destructor()
                ]),  # Class Renderer
            ]),  # Namespace rend
            Namespace('state', [
                Class('State',
                    methods=[
                        Constructor(),
                        Destructor(),
                        Method('Update',
                            void,
                            args=[
                                Arg(
                                    Type(
                                        ['kx', 'common'],
                                        'Time',
                                    ),
                                    't'
                            )],
                            const=False,
                            virtual=True,
                            abstract=True
                        ),
                        Method('Draw',
                            void,
                            args=[
                                Arg(
                                    Pointer(
                                        ['kx', 'rend'],
                                        'Renderer',
                                    ),
                                    'renderer'
                            )],
                            const=True,
                            virtual=True,
                            abstract=True
                        ),
                    ]  # methods
                ),  # Class State
            ]),  # Namespace state
        ])  # Namespace kx
    ],
    'include_dir': 'include',
    'source_dir': 'src',
    },  # kx
    {
    'data': [
        Namespace('ex43',[
            Class('MenuState',
                bases=Type(['kx', 'state'], 'State'),
                methods=[
                    Constructor(),
                    Destructor(),
                ],  # methods
            )  # Class MenuState
        ])  # Namespace ex43
    ],
    'include_dir': 'examples/ex43',
    'source_dir': 'examples/ex43',
    },  # case study 4.3
]


def gen_fwd_header(env, ns, cls):
    tmpl = env.get_template('header_fwd.tmpl')
    content = tmpl.render(ns=ns, cls=cls)
    write_file(
        os.path.join('include', 'kx', ns, f'{snake_case(cls.name)}_fwd.hpp'),
        content
    )


def gen_header(env, ns, cls):
    tmpl = env.get_template('header.tmpl')
    content = tmpl.render(ns=ns, cls=cls)
    write_file(
        os.path.join('include', 'kx', ns, f'{snake_case(cls.name)}.hpp'),
        content
    )


def gen_source(env, ns, cls):
    avail = [
        'include_class_header.tmpl',
        'namespace_begin.tmpl',
        'class_definition.tmpl',
        'namespace_end.tmpl',
    ]
    tmpl = env.get_template('source.tmpl')
    content = tmpl.render(ns=ns, cls=cls)
    write_file(
        os.path.join('src', ns, f'{snake_case(cls.name)}.cpp'),
        content
    )


def main():
    env = jinja2.Environment(
            loader=jinja2.FileSystemLoader('templates'),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,
    )
    for config in configs:
        for obj in config['data']:
            obj.gen(
                inc_dir=config['include_dir'],
                src_dir=config['source_dir']
            )
#        for cls in ns.classes:
#            for g in [gen_fwd_header, gen_header, gen_source]:
#                g(env, ns.name, cls)


main()
