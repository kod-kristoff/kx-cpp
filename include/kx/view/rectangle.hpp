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

        inline Scalar height() const {return _height;}
        inline Scalar width() const { return _width; }

        inline Position const * position() const
        {
            return _position;
        }
    private:
        Position *  _position;
        Scalar      _height;
        Scalar      _width;
    };
}
#endif

