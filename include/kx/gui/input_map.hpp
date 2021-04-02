#ifndef KX_GUI_INPUT_MAP_HPP
#define KX_GUI_INPUT_MAP_HPP

#include "kx/input/input_map.hpp"

namespace kx
{
namespace gui
{
    class Gadget;

    class InputMap: input::InputMap
    {
    public:
        InputMap();
        explicit InputMap(Gadget * gadget);

        inline 
        Gadget const *
        gadget()
        const
        {
            return _gadget;
        }

        inline
        Gadget *
        gadget()
        {
            return _gadget;
        }
    private:
        Gadget * _gadget;
    };
}
}
#endif // KX_GUI_INPUT_MAP_HPP
