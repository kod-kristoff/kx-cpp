#include <list>

#include "kx/view/view.hpp"

namespace kx::view
{
    class Context;
    class LayeredPosition;

    class LayeredView : public View
    {
    public:
        virtual void render(Context * context) const;
        virtual LayeredPosition * create_position();
    };
}
