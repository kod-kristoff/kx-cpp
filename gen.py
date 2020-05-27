#!/usr/bin/env python3

import copy
import itertools
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
        yield from cls.fwd_decl(ns)
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

def gen_fun_decl(fn, indent=None, i_mul=1, cls=None):
    if indent is None:
        indent = " "*4
    yield from gen_doc(indent*i_mul, func=fn)
    if isinstance(fn, Method) and fn.virtual:
        yield f"{ indent*i_mul }virtual"
    if fn.return_type:
        yield f"{ indent*i_mul }{ fn.return_type.fmt() }"
    if isinstance(fn, Method):
        yield f"{ indent*i_mul }{ fun_name(fn, cls) }(" + ("" if fn.args else (")" if fn.const or fn.abstract else ");"))
    else:
        yield f"{ indent*i_mul }{ fun_name(fn, cls) }(" + ("" if fn.args else ");")
    if fn.args:
        for i, arg in enumerate(fn.args):
            yield f"{ indent*(i_mul+1) }{ arg.type.fmt() } { arg.name }" + ("" if i == (len(fn.args) - 1) else ",")
        if isinstance(fn, Method):
            yield f"{ indent*i_mul }" + (")" if fn.const or fn.abstract else ");")
        else:
            yield f"{ indent*i_mul });"
            return
    if isinstance(fn, Method):
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
            for method in cls.methods:
                yield from gen_fun_decl(method, indent=indent, i_mul=2, cls=cls)
        if cls.members:
            yield f"{ indent }public:"
            for member in cls.members:
                yield f"{ indent*2 }/** A variable."
                yield f"{ indent*2 }  *"
                yield f"{ indent*2 }  * Details."
                yield f"{ indent*2 }  */"
                yield f"{ indent*2 }{ member.type.fmt() } { member.name }"
        yield f"{ indent }}}; // class { cls.name }"
        if child:
            yield from child(ns, cls, suffix)

    return _class_decl


def module_decl(children=None):
    children = ensure_list(children)

    def _module_decl(ns, mod, suffix):
        yield from mod.decl(ns)

        for child in children:
            yield from child(ns, mod, suffix)
    return _module_decl


def include_dep(dep, suffix):
    if isinstance(dep, Primitive):
        return

    if suffix.startswith('_fwd'):
        return
    if suffix.endswith('.hpp'):

        inc = dep.as_header_include()
        if inc:
            yield inc
    else:
        inc = dep.as_src_include()
        if inc:
            yield inc


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
                    inits = itertools.chain(
                        (f"{ b.cls }()" for b in cls.bases),
                        (f"{ m.name }({ 'nullptr' if isinstance(m.type, Pointer) else '' })" for m in cls.members )
                    )
                    for i, init in enumerate(inits):
                        yield f"{ indent }{ ':' if i == 0 else ',' } { init }"

                yield "{"
                yield f'{ indent }std::cout << "{ fun_def_debug(ns, fn, cls) }" << std::endl;'
                yield f"}} // method { cls.name }::{ fun_name(fn, cls) }"
                yield ""

        for child in children:
            yield from child(ns, cls, suffix)
    return _class_def


def module_def(children=None):
    children = ensure_list(children)

    def _module_def(ns, mod, suffix):
        yield from mod.src_def(ns)

        for child in children:
            yield from child(ns, mod, suffix)

    return _module_def


header_fwd = include_guard(namespace(class_fwd_decl()))
header = include_guard([
    include_deps(),
    namespace(
        #class_decl()
        module_decl()
    )
    ])
#header_fwd = include_guard(class_fwd_decl())
source = include_self([
    include_deps(),
    namespace(
        #class_def()
        module_def()
    )
    ])


def write_file(filename, content):
    print(f'{filename}')
    print('-'*10)
    for line in content:
        print(f"{line}")


class Obj:
    def __init__(self):
        self.deps = [SrcDep(Std("iostreams"))]

    def gen(self, ns=[], inc_dir='include', src_dir='src'):
        pass

    def fwd_decl(self, ns, indent=None):
        pass

    def decl(self, ns, indent=None):
        pass

    def src_def(self, ns, indent=None):
        pass

    def add_dep(self, x):
        if x is None:
            return
        if isinstance(x, Primitive):
            return

        if isinstance(x, Type):
            if isinstance(x, Pointer):
                y = FwdDep(x)
            else:
                y = HardDep(x)
        elif isinstance(x, Dep):
            y = x
        else:
            return

        for i, v in enumerate(self.deps):
            if y == v:
                if isinstance(v, SrcDep) and isinstance(y, FwdDep):
                    self.deps[i] = y
                    break
                elif isinstance(v, FwdDep) and isinstance(y, HardDep):
                    self.deps[i] = y
                    break
        else:
            self.deps.append(y)
        print(f"deps = {self.deps}")


class Fmtable:
    def fmt_fwd_decl(self):
        pass

    def fmt_decl(self):
        pass

    def fmt_def(self):
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


class Function(Obj):
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
        self.abstract = False

    def decl(self, ns, indent=None):
        yield from gen_fun_decl(self, indent=indent)

    def src_def(self, ns, indent=None):
        indent = " "*4
        if self.return_type:
            yield f"{ self.return_type.fmt() }"
        yield f"{ self.name }(" + ("" if self.args else ")")
        if self.args:
            for i, arg in enumerate(self.args):
                yield f"{ indent }{ arg.type.fmt() } { arg.name }" + ("" if i == (len(self.args) - 1) else ",")
            yield ")"

        yield "{"
        yield f'{ indent }std::cout << "{ fun_def_debug(ns, self) }" << std::endl;'
        yield f"}} // function { self.name }"
        yield ""


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


class Type:
    def __init__(self, *args):
        self.cls = args[-1]
        self.ns = args[:-1]

    def __repr__(self):
        return f"Type({self.ns}, {self.cls})"

    def fmt(self) -> str:
        if self.ns:
            return f"{ '::'.join(list(self.ns)) }::{ self.cls }"
        else:
            return f"{ self.cls }"

    def as_include(self):
        return f'#include "{ gen_filename(None, self.ns, self.cls, ".hpp") }"'

    def as_fwd_include(self):
        return f'#include "{ gen_filename(None, self.ns, self.cls, "_fwd.hpp") }"'


class Primitive(Type):
    def __init__(self, cls):
        super().__init__(cls)

    def fmt(self) -> str:
        return f"{ self.cls }"


void = Primitive('void')

class Pointer(Type):
    def __init__(self, *args):
        super().__init__(*args)

    def fmt(self) -> str:
        return f"{ super().fmt() } *"


class Std(Type):
    def __init__(self, header):
        super().__init__(header)

    def as_include(self):
        return f"#include <{ self.cls }>"

    def as_fwd_include(self):
        return


class TypeDef(Obj):
    def __init__(self, type_, name):
        self.type = type_
        self.name = name

    def fmt(self):
        return f"typedef {self.type.fmt()} {self.name};"

    def decl(self, indent=None):
        if indent is None:
            indent = "    "

        yield f"{indent}{self.fmt()}"


class Dep:
    def __init__(self, type_):
        self.type = type_

    def __repr__(self):
        return f"Dep({self.type})"

    def __eq__(self, other):
        return isinstance(other, Dep) and self.type == other.type

    def __hash__(self):
        return hash(repr(self))

    def as_header_include(self):
        pass

    def as_src_include(self):
        pass


class HardDep(Dep):
    def __init__(self, type_):
        super().__init__(type_)

    def __repr__(self):
        return f"HardDep({self.type})"

    def as_header_include(self):
        return self.type.as_include()


class FwdDep(HardDep):
    def __init__(self, type_):
        super().__init__(type_)

    def __repr__(self):
        return f"FwdDep({self.type})"

    def as_header_include(self):
        return self.type.as_fwd_include()

    def as_src_include(self):
        return self.type.as_include()


class SrcDep(FwdDep):
    def __init__(self, type_):
        super().__init__(type_)

    def __repr__(self):
        return f"SrcDep({self.type})"

    def as_src_include(self):
        return self.type.as_include()


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
                 members=None,
                ):
        super().__init__()
        self.name = name
        self.virtual = virtual
        self.methods = ensure_list(methods)

        self.bases = ensure_list(bases)
        self.members = ensure_list(members)

        for m in self.methods:
            self.add_dep(m.return_type)
            for a in m.args:
                self.add_dep(a.type)

        for m in self.members:
            self.add_dep(m.type)

        print(f"{self!r}")
        print(f"deps = { self.deps }")

    def __repr__(self):
        return f"Class({self.name}, bases={self.bases}, methods={self.methods})"

    def fwd_decl(self, ns, indent=None):
        yield "    // Forward declaration"
        yield f"    class { self.name };"
        yield ""

    def decl(self, ns, indent=None):
        _class_decl = class_decl()
        yield from _class_decl(ns, self, ".hpp")

    def src_def(self, ns, indent=None):
        _class_def = class_def()
        yield from _class_def(ns, self, ".hpp")

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


class Module(Obj): #(HeaderFwd, Header, Source):
    def __init__(self,
                 name,
                 *ents,
                ):
        super().__init__()
        self.name = name
        self.ents = ents
        self.deps = [SrcDep(Std('iostreams'))]



        for m in self.ents:
            if isinstance(m, Function):
                self.add_dep(m.return_type)
                for a in m.args:
                    self.add_dep(a.type)
            elif isinstance(m, TypeDef):
                self.add_dep(m.type)
            elif isinstance(m, Class):
                for d in m.deps:
                    self.add_dep(d)

        print(f"{self!r}")
        print(f"deps = { self.deps }")

    def __repr__(self):
        return f"Module({self.name}, ents={self.ents})"

    def fwd_decl(self, ns, indent=None):
        for ent in self.ents:
            ent_fwd_decl = ent.fwd_decl(ns)
            if ent_fwd_decl:
                yield from ent_fwd_decl

    def decl(self, ns, indent=None):
        for ent in self.ents:
            ent_decl = ent.decl(ns)
            if ent_decl:
                yield from ent_decl

    def src_def(self, ns, indent=None):
        for ent in self.ents:
            ent_src_def = ent.src_def(ns)
            if ent_src_def:
                yield from ent_src_def

    def gen(self, ns, inc_dir='include', src_dir='src'):
        print(f"Module { '::'.join(ns) }::{ self.name }")
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


State_update_abstract = Method('update', void,
    args=[
        Arg(Type('kx', 'core','Time',), 't')
    ],
    const=False,
    virtual=True,
    abstract=True
)

State_update = copy.copy(State_update_abstract)
State_update.abstract = False

State_draw_abstract = Method('draw',void,
    args=[
        Arg(Pointer('kx', 'rend', 'Renderer'), 'renderer')
    ],
    const=True,
    virtual=True,
    abstract=True
)

State_draw = copy.copy(State_draw_abstract)
State_draw.abstract = False

State_on_enter = Method('on_enter', void, virtual=True)
State_on_leave = Method('on_leave', void, virtual=True)

StateFactory_create_abstract = Method('create',
    Pointer(Type('kx', 'state', 'State')),
    args=[
        Arg(Pointer(Primitive('char const')), 'name')
    ],
    const=False,
    virtual=False,
    abstract=True
)

StateFactory_create = copy.copy(StateFactory_create_abstract)
StateFactory_create.abstract = False

StateManager_switch_to_state = Method('switch_to_state',
    void,
    args=[
        Arg(Pointer('kx', 'state', 'State'), 'state')
    ],
)


configs = [
    {
    'data': [
        Namespace('kx',[
            Namespace('core',[
                Module('time',
                    TypeDef(Primitive('int'), 'Time'),
                    Function('get_time',
                        Primitive('Time')
                    ),
                ),  # Module time
            ]),  # Namespace common
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
                        State_draw_abstract,
                        State_update_abstract,
                        State_on_enter,
                        State_on_leave
                    ]  # methods
                ),  # Class State
                Class('StateManager',
                    methods=[
                        Constructor(),
                        Destructor(),
                        StateManager_switch_to_state,
                    ],  # methods
                    members=[
                        Arg(
                            Pointer(
                                'kx', 'state',
                                'State'
                            ),
                            'current_state'
                        )
                    ],  # members
                ),  # Class StateManager
                Class('StateFactory',
                    methods=[
                        StateFactory_create_abstract
                    ],  # methods
                ),  # Class StateFactory
            ]),  # Namespace state
        ])  # Namespace kx
    ],
    'include_dir': 'include',
    'source_dir': 'src',
    },  # kx
    {
    'data': [
        Namespace('ex43',[
            Class('ConcreteStateFactory',
                bases=Type('kx', 'state', 'StateFactory'),
                methods=[
                    Constructor(),
                    StateFactory_create,
                    ]
            ),  # Class ConcreteStateFactory
            Class('MenuState',
                bases=Type('kx', 'state', 'State'),
                methods=[
                    Constructor(),
                    Destructor(),
                    State_update,
                    State_draw,
                    State_on_enter,
                    State_on_leave
                ],  # methods
            ),  # Class MenuState
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
