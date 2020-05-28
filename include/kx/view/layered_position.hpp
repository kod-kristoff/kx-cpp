#ifndef KX_VIEW_LAYERED_POSITION_HPP
#define KX_VIEW_LAYERED_POSITION_HPP

#include "kx/view/position.hpp"

namespace kx::view
{
    class LayeredPosition: public Position
    {
    public:

    public:
        int depth;
    };
}

#endif // KX_VIEW_LAYERED_POSITION_HPP
