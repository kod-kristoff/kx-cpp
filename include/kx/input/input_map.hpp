#ifndef KX_INPUT_INPUT_MAP_HPP
#define KX_INPUT_INPUT_MAP_HPP

#include "kx/input/input.hpp"

namespace kx
{
namespace input
{
    class InputMap
    {
    public:
        virtual ~InputMap();

        virtual void handle_input(Input & input);
    };
}
}
#endif // KX_INPUT_INPUT_MAP_HPP
