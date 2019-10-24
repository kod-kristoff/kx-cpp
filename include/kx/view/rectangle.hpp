#ifndef KX_VIEW_RECTANGLE_HPP
#define KX_VIEW_RECTANGLE_HPP

#include "kx/view/types.hpp"

namespace kx::view
{
    class Position;

    class Rectangle
    {
    public:
        ~Rectangle();
    public:
        Position *  position;
        Scalar      height;
        Scalar      width;
    };
}
#endif

