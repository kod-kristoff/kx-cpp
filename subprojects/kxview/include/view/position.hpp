#ifndef KX_VIEW_POSITION_HPP
#define KX_VIEW_POSITION_HPP

#include "kx/view/types.hpp"

namespace kx::view
{
    class Position
    {
    public:
        Position() = default;
        virtual ~Position();

    public:
        Scalar x;
        Scalar y;
    };
}

#endif
