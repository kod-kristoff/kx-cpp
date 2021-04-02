#include "kx/gui/input_map.hpp"

namespace kx
{
namespace gui
{
    InputMap::InputMap()
        : _gadget(nullptr)
    {}

    InputMap::InputMap(Gadget * gadget)
        : _gadget(gadget)
    {}
}
}
