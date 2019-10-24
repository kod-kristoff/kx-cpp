#include "kx/view/view.hpp"

#include "kx/view/position.hpp"

#include <algorithm>


namespace kx::view
{
    struct ViewDeleter
    {
        inline void operator()(View * view)
        {
            delete view;
        }
    };

    struct ViewRenderer
    {
        Context * context;

        explicit inline ViewRenderer(Context * _context)
            : context(_context)
        {}

        inline void operator()(View const * view)
        {
            view->render(context);
        }
    };

    // ====
    // View
    // ====

    View::~View()
    {
        std::for_each(
            children.begin(),
            children.end(),
            ViewDeleter()
        );
    }
    
    /* virtual */
    void View::render(Context * context) const
    {
        std::for_each(
            children.begin(),
            children.end(),
            ViewRenderer(context)
        );
    }

    /* virtual */
    Position * View::create_position()
    {
        return new Position;
    }

    void View::add_child(View * const child)
    {
        children.push_back(child);
    }
    
    void View::remove_child(View * const child)
    {
        children.remove(child);
    }

    void View::remove_all_children()
    {
        children.clear();
    }
}
