#ifndef KX_GUI_GADGET_HPP
#define KX_GUI_GADGET_HPP

#include "kx/view/view_fwd.hpp"

namespace kx
{
namespace gui
{
    class InputMap;

    class Gadget
    {
    public:
        virtual ~Gadget();
    private:
        InputMap    * _input_map;
        View        * _view;
    };
}
}
#endif // KX_GUI_GADGET_HPP
