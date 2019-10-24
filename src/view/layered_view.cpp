#include "kx/view/layered_view.hpp"

#include "kx/view/layered_position.hpp"

namespace kx::view
{
    /* virtual */
    LayeredPosition * LayeredView::create_position()
    {
        return new LayeredPosition;
    }

    /* virtual */
    void LayeredView::render(Context * context)
    {

    }
}
