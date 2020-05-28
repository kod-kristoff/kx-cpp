#ifndef KX_VIEW_VIEW_HPP
#define KX_VIEW_VIEW_HPP

#include <list>

#include "kx/view/rectangle.hpp"

namespace kx::view
{
    class View;
    typedef std::list<View *> ViewList;

    class Context;

    class Position;

    class View : public Rectangle
    {
    public:
        View() = default;

        virtual ~View();

        virtual void render(Context * context) const = 0;

        virtual Position * create_position();

        void add_child(View * const child);
        void remove_child(View * const child);
        void remove_all_children();

    private:
        ViewList children;
    };
}

#endif
